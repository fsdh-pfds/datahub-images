import re
from bs4 import BeautifulSoup
from html_to_markdown import convert_to_markdown
from mailparser import parse_from_bytes


def parse_email(eml: bytes):
    response = {
        "recipients": [],
        "subject": "",
        "body": "",
    }

    parsed = parse_from_bytes(eml)

    if parsed.text_html:
        html = "".join(parsed.text_html)
        html = re.sub(r"<br\s*\/?>", "<br/>", html)
        html = re.sub(r"<style>[\s\S]*?</style>", "", html, flags=re.DOTALL)
        # Remove all script tags using BeautifulSoup (handles malformed tags & case)
        soup = BeautifulSoup(html, "html.parser")
        for script in soup.find_all("script"):
            script.decompose()
        html = str(soup)
        html = html.replace("<table", "<br/><br/><table")
        html = html.replace("</table>", "</table><br/>")
        body_markdown = convert_to_markdown(
            html,
            convert=["p", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li", "blockquote", "a", "br"],
            extract_metadata=False,
            strong_em_symbol="",
        )
        body_markdown = re.sub(r"\n +", "\n", body_markdown.strip())
        body_markdown = re.sub(r"\n\n\n+", "\n\n", body_markdown.strip())
        response["body"] = body_markdown
    elif parsed.text_plain:
        response["body"] = "\n\n".join(parsed.text_plain)

    subject = parsed.subject or "(no subject)"
    subject = re.sub(r"\s+", " ", subject).strip()
    response["subject"] = subject

    if parsed.to:
        response["recipients"].extend([addr for _, addr in parsed.to if addr and "@" in addr])
    if parsed.cc:
        response["recipients"].extend([addr for _, addr in parsed.cc if addr and "@" in addr])
    if parsed.bcc:
        response["recipients"].extend([addr for _, addr in parsed.bcc if addr and "@" in addr])

    response["recipients"] = list(set(response["recipients"]))  # Remove duplicates

    return response
