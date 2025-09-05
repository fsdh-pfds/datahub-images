# pylint: disable=broad-exception-caught

import asyncio
import ipaddress
import os
import random
import re
import time

import requests
from aiosmtpd.controller import Controller
from message_handling import parse_email
from notifications_python_client.notifications import NotificationsAPIClient

SMTP_HOSTNAME = os.getenv("SMTP_HOSTNAME", "127.0.0.1")
SMTP_PORT = int(os.getenv("SMTP_PORT", "2525"))

NOTIFY_API_KEY = os.getenv("NOTIFY_API_KEY")
NOTIFY_TEMPLATE_ID = os.getenv("NOTIFY_TEMPLATE_ID")
# GC Notify base (not GOV.UK)
NOTIFY_BASE_URL = os.getenv(
    "NOTIFY_BASE_URL", "https://api.notification.canada.ca"
)  # https://documentation.notification.canada.ca/en/start.html
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# Recipient allowlist: comma-separated domains OR a regex (takes precedence)
RECIPIENT_ALLOW_DOMAINS = {d.strip().lower() for d in os.getenv("RECIPIENT_ALLOW_DOMAINS", "").split(",") if d.strip()}
RECIPIENT_ALLOW_REGEX = os.getenv("RECIPIENT_ALLOW_REGEX", "")  # e.g., r".*@(?:ssc-spc\.gc\.ca|canada\.ca)$"
_recipient_allow_re = re.compile(RECIPIENT_ALLOW_REGEX) if RECIPIENT_ALLOW_REGEX else None

# Payload limits / backoff
MAX_BODY_CHARS = int(os.getenv("MAX_BODY_CHARS", "20000"))  # fail-safe guardrail
MAX_RETRIES = int(os.getenv("NOTIFY_MAX_RETRIES", "5"))
BACKOFF_BASE = float(os.getenv("NOTIFY_BACKOFF_BASE", "0.5"))  # seconds
BACKOFF_CAP = float(os.getenv("NOTIFY_BACKOFF_CAP", "8.0"))  # seconds

notifications_client = NotificationsAPIClient(NOTIFY_API_KEY, base_url=NOTIFY_BASE_URL) if NOTIFY_API_KEY else None


def is_private_ip(ip: str | None) -> bool:
    """Return True if IP is private/loopback/link-local; False otherwise."""
    if not ip:
        return False
    try:
        addr = ipaddress.ip_address(ip)
        return bool(addr.is_private or addr.is_loopback or addr.is_link_local)
    except ValueError:
        return False


def _recipient_allowed(address: str) -> bool:
    """Allow by regex (if set) or by domain list; otherwise allow."""
    if _recipient_allow_re:
        return bool(_recipient_allow_re.fullmatch(address))
    if RECIPIENT_ALLOW_DOMAINS:
        # Exact domain match (no subdomain) unless you list subdomains explicitly
        return any(address.endswith("@" + d) for d in RECIPIENT_ALLOW_DOMAINS)
    return True  # if no policy set, allow everything inside the private-IP boundary


async def _post_slack(subject: str, body: str, to: str):
    if not SLACK_WEBHOOK_URL:
        return
    payload = {"to": to, "subject": subject, "body": (body[:1000] if body else "")}

    # run in thread pool to avoid blocking the event loop
    def _do():
        r = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=5)
        r.raise_for_status()

    await asyncio.to_thread(_do)


async def _send_notify(to: str, subject: str, body: str, reference: str | None):
    if not notifications_client or not NOTIFY_TEMPLATE_ID:
        raise RuntimeError("Notify client not configured (missing NOTIFY_API_KEY or NOTIFY_TEMPLATE_ID)")

    personalisation = {"subject": subject, "body": (body[:MAX_BODY_CHARS] if body else "")}

    # retries with jitter for 429/5xx or network errors
    for attempt in range(MAX_RETRIES):
        try:
            return await asyncio.to_thread(
                notifications_client.send_email_notification,
                email_address=to,
                template_id=NOTIFY_TEMPLATE_ID,
                personalisation=personalisation,
                reference=(reference[:255] if reference else None),
            )
        except Exception as e:
            status = getattr(getattr(e, "response", None), "status_code", None)
            transient = status in (None, 429, 500, 502, 503, 504)
            if transient and attempt < MAX_RETRIES - 1:
                sleep = min(BACKOFF_CAP, BACKOFF_BASE * (2**attempt)) + random.uniform(0, 0.25)
                await asyncio.sleep(sleep)
                continue
            raise  # bubble up on final attempt or non-transient


class NotifyHandler:
    # pylint: disable=invalid-name
    async def handle_DATA(self, _server, session, envelope):
        print("Received email data")
        source_ip = session.peer[0] if session.peer else None
        if not is_private_ip(source_ip):
            return "550 Source IP unacceptable"

        parsed = parse_email(envelope.content)
        return await self._process_message(parsed)

    async def _process_message(self, parsed: dict) -> str:
        recipients = parsed.get("recipients", [])
        subject = parsed.get("subject") or ""
        body = parsed.get("body") or ""
        reference = parsed.get("message_id")

        if not recipients:
            return "550 No recipient found"
        if not subject or not body:
            return "550 Invalid email content"

        allowed = [r for r in recipients if _recipient_allowed(r)]
        if not allowed:
            return "550 Recipient not permitted"

        return await self._relay(allowed, subject, body, reference)

    async def _relay(self, allowed, subject, body, reference) -> str:
        try:
            notify_tasks = [_send_notify(to, subject, body, reference) for to in allowed]
            results = await asyncio.gather(*notify_tasks, return_exceptions=True)

            failures = [r for r in results if isinstance(r, Exception)]
            if len(failures) == len(allowed):
                for f in failures:
                    print(f"Notify relay failed: {repr(f)}")
                return "451 Temporary failure"

            for r in results:
                if not isinstance(r, Exception) and isinstance(r, dict) and "id" in r:
                    print(f"Relayed via GC Notify id={r['id']}")

            if SLACK_WEBHOOK_URL:
                slack_tasks = [_post_slack(subject, body, to) for to in allowed]
                _ = await asyncio.gather(*slack_tasks, return_exceptions=True)

            return "250 Message accepted"
        except Exception as e:
            print(f"Notify relay failed: {e}")
            return "451 Temporary failure"


if __name__ == "__main__":
    if not NOTIFY_API_KEY or not NOTIFY_TEMPLATE_ID:
        print("WARNING: NOTIFY_API_KEY and/or NOTIFY_TEMPLATE_ID not set; messages will be rejected.")
    controller = Controller(NotifyHandler(), hostname=SMTP_HOSTNAME, port=SMTP_PORT)
    print(f"Starting SMTP relay on port {SMTP_PORT}")
    controller.start()
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print("Stopping SMTP relay")
        controller.stop()
