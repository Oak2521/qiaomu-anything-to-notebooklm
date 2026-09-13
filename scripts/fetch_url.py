#!/usr/bin/env python3
"""Read publicly accessible HTTP(S) text without proxies, credentials or bypasses."""
import argparse
from html.parser import HTMLParser
import re
import sys
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

MAX_BYTES = 5 * 1024 * 1024
GATE = re.compile(r"subscribe to (?:continue|read|access|unlock)|sign in to (?:continue|read)|"
                  r"verify (?:you are|that you are) human|captcha|订阅后阅读|付费阅读|登录后阅读", re.I)


class AccessRestricted(RuntimeError):
    pass


class PublicText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hidden = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.hidden += 1
        elif tag in ("p", "div", "br", "h1", "h2", "h3", "li", "article") and not self.hidden:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self.hidden:
            self.hidden -= 1

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def fetch(url, opener=urlopen):
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.hostname or parts.username or parts.password:
        raise ValueError("Expected an HTTP(S) URL without embedded credentials")
    request = Request(url, headers={"User-Agent": "PublicArticleReader/1.0", "Accept": "text/html,text/plain"})
    try:
        with opener(request, timeout=30) as response:
            raw = response.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise ValueError("Response exceeds 5 MiB; content was not extracted")
            content_type = response.headers.get_content_type()
            if content_type not in ("text/html", "application/xhtml+xml", "text/plain"):
                raise ValueError(f"Unsupported content type: {content_type}")
            body = raw.decode(response.headers.get_content_charset() or "utf-8", errors="replace")
    except HTTPError as exc:
        exc.close()
        if exc.code in (401, 402, 403, 429):
            raise AccessRestricted(f"HTTP {exc.code}: stop this path; access or rate limits require user action") from exc
        raise
    if content_type != "text/plain":
        parser = PublicText()
        parser.feed(body)
        body = "".join(parser.parts)
    if GATE.search(body):
        raise AccessRestricted("Possible login/paywall/verification page; no complete article claimed. Supply accessible text.")
    text = re.sub(r"[ \t]+", " ", body)
    text = re.sub(r"\n\s*\n", "\n\n", text).strip()
    if not text:
        raise ValueError("No readable text returned")
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    args = parser.parse_args()
    try:
        print(fetch(args.url))
    except AccessRestricted as exc:
        print(f"ACCESS_RESTRICTED: {exc}", file=sys.stderr)
        return 3
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
