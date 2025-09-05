import re
from typing import Any

from bs4 import BeautifulSoup
from html_to_markdown import convert_to_markdown
from mailparser import parse_from_bytes


def parse_email(eml: bytes) -> dict[str, Any]:
    """
    Parse a raw RFC-822 email and return:
      - recipients: list[str]
      - subject: str
      - body: str (Markdown if HTML was present, else plain text)
      - message_id: str | None
    """
    recipients: list[str] = []
    subject: str = ""
    body: str = ""
    message_id: str | None = None

    parsed = parse_from_bytes(eml)
    message_id = (parsed.message_id or "").strip() or None

    # Prefer HTML -> Markdown; fall back to plain text
    if parsed.text_html:
        html = "".join(parsed.text_html)

        # Normalize & strip risky content
        html = re.sub(r"<br\s*/?>", "<br/>", html, flags=re.IGNORECASE)
        html = re.sub(r"<style\b[^>]*>[\s\S]*?</style>", "", html, flags=re.IGNORECASE)

        soup = BeautifulSoup(html, "html.parser")
        # Strip more than just <script>
        for tag in soup.find_all(["script", "iframe", "form", "object", "embed"]):
            tag.decompose()
        html = str(soup)

        # Add spacing around tables so Markdown doesn't run together
        html = html.replace("<table", "<br/><br/><table").replace("</table>", "</table><br/>")

        md = convert_to_markdown(
            html,
            convert=["p", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li", "blockquote", "a", "br"],
            extract_metadata=False,
            strong_em_symbol="",  # keep emphasis out; change to "**" if you want bold
        )
        md = re.sub(r"\n +", "\n", md.strip())
        md = re.sub(r"\n\n\n+", "\n\n", md.strip())
        body = md
    elif parsed.text_plain:
        body = "\n\n".join(parsed.text_plain)

    # Subject
    subj = parsed.subject or "(no subject)"
    subject = re.sub(r"\s+", " ", subj).strip()

    # Recipients (To, Cc, Bcc) → list[str]
    for name_addr in parsed.to or []:
        _, addr = name_addr
        if addr and "@" in addr:
            recipients.append(addr)
    for name_addr in parsed.cc or []:
        _, addr = name_addr
        if addr and "@" in addr:
            recipients.append(addr)
    for name_addr in parsed.bcc or []:
        _, addr = name_addr
        if addr and "@" in addr:
            recipients.append(addr)

    # Dedupe while preserving order
    seen: set[str] = set()
    deduped: list[str] = []
    for r in recipients:
        rl = r.strip().lower()
        if rl and rl not in seen:
            seen.add(rl)
            deduped.append(r.strip())

    return {
        "recipients": deduped,
        "subject": subject,
        "body": body,
        "message_id": message_id,
    }
