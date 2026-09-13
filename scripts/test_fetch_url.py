from email.message import Message
import io
import unittest
from urllib.error import HTTPError

from fetch_url import AccessRestricted, fetch


def response(text, content_type="text/html"):
    result = io.BytesIO(text.encode())
    result.headers = Message()
    result.headers["Content-Type"] = content_type + "; charset=utf-8"
    return result


class FetchTests(unittest.TestCase):
    def test_public_text_without_scripts_or_spoofed_headers(self):
        def opener(request, **kwargs):
            self.assertNotIn("Referer", request.headers)
            self.assertNotIn("Cookie", request.headers)
            self.assertNotIn("X-forwarded-for", request.headers)
            return response("<article><h1>Title</h1><p>中文 &amp; nested <b>body</b></p><script>privateScript</script></article>")
        text = fetch("https://example.org/article", opener)
        self.assertIn("中文 & nested body", text)
        self.assertNotIn("privateScript", text)

    def test_gate_is_not_success_and_does_not_retry(self):
        calls = []
        def opener(request, **kwargs):
            calls.append(request.full_url)
            return response("<p>Subscribe to continue reading</p>")
        with self.assertRaises(AccessRestricted):
            fetch("https://example.org/article", opener)
        self.assertEqual(len(calls), 1)

    def test_http_restriction_stops(self):
        def opener(request, **kwargs):
            raise HTTPError(request.full_url, 403, "Forbidden", {}, None)
        with self.assertRaises(AccessRestricted):
            fetch("https://example.org/article", opener)

    def test_invalid_and_credential_urls_never_request(self):
        def opener(*args, **kwargs):
            self.fail("must not make request")
        for url in ("file:///etc/passwd", "https://user:secret@example.org", "not-a-url"):
            with self.assertRaises(ValueError):
                fetch(url, opener)


if __name__ == "__main__":
    unittest.main()
