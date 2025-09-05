# pylint: disable=broad-exception-caught
import re

from bs4 import BeautifulSoup
from html_to_markdown import convert_to_markdown
from mailparser import parse_from_bytes


def parse_email(eml: bytes):
    """
    Parse a raw RFC-822 email and return recipients, subject, body (as Markdown/plain),
    and message_id for downstream idempotency/reference.
    """
    response = {
        "recipients": [],
        "subject": "",
        "body": "",
        "message_id": None,  # NEW: expose Message-ID for Notify `reference`
    }

    parsed = parse_from_bytes(eml)
    response["message_id"] = (parsed.message_id or "").strip() or None  # NEW

    if parsed.text_html:
        html = "".join(parsed.text_html)

        # Normalize common broken HTML and remove inline styles
        html = re.sub(r"<br\s*/?>", "<br/>", html, flags=re.IGNORECASE)
        html = re.sub(r"<style\b[^>]*>[\s\S]*?</style>", "", html, flags=re.IGNORECASE)

        # Strip risky elements robustly (not just <script>)
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.find_all(["script", "iframe", "form", "object", "embed"]):  # NEW
            tag.decompose()
        html = str(soup)

        # Visual spacing around tables to avoid run-on markdown
        html = html.replace("<table", "<br/><br/><table").replace("</table>", "</table><br/>")

        body_markdown = convert_to_markdown(
            html,
            convert=["p", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li", "blockquote", "a", "br"],
            extract_metadata=False,
            strong_em_symbol="",  # keeps emphasis out; change if you want **bold**
        )
        body_markdown = re.sub(r"\n +", "\n", body_markdown.strip())
        body_markdown = re.sub(r"\n\n\n+", "\n\n", body_markdown.strip())
        response["body"] = body_markdown

    elif parsed.text_plain:
        response["body"] = "\n\n".join(parsed.text_plain)

    subject = parsed.subject or "(no subject)"
    subject = re.sub(r"\s+", " ", subject).strip()
    response["subject"] = subject

    # Collect recipients from To/Cc/Bcc and dedupe
    if parsed.to:
        response["recipients"].extend([addr for _, addr in parsed.to if addr and "@" in addr])
    if parsed.cc:
        response["recipients"].extend([addr for _, addr in parsed.cc if addr and "@" in addr])
    if parsed.bcc:
        response["recipients"].extend([addr for _, addr in parsed.bcc if addr and "@" in addr])

    response["recipients"] = list(set(response["recipients"]))

    return response
