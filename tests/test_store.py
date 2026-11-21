from html.parser import HTMLParser
from pathlib import Path
import unittest
from urllib.parse import urlsplit, unquote

ROOT = Path(__file__).resolve().parents[1]
PAGES = list(ROOT.glob("*.html"))

class StorePage(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

class StoreLinks(unittest.TestCase):
    def test_local_routes_and_assets(self):
        files = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts}
        for page in PAGES:
            with self.subTest(page=page.name):
                document = StorePage()
                document.feed(page.read_text(encoding="utf-8-sig"))
                ids = [attrs["id"] for _, attrs in document.tags if "id" in attrs]
                self.assertEqual(len(ids), len(set(ids)))
                for tag, attrs in document.tags:
                    for key in ("src", "href"):
                        url = urlsplit((attrs.get(key) or "").strip())
                        if url.scheme or url.netloc:
                            continue
                        if url.path:
                            self.assertIn(unquote(url.path).removeprefix("./"), files)
                        elif url.fragment:
                            self.assertIn(url.fragment, ids)
    def test_order_fields_have_distinct_labels(self):
        page = StorePage()
        page.feed((ROOT / "track-your-order.html").read_text(encoding="utf-8-sig"))
        labels = {a["for"] for t, a in page.tags if t == "label" and "for" in a}
        inputs = {a["id"]: a.get("type") for t, a in page.tags if t == "input" and "id" in a}
        self.assertIn("billingEmail", labels)
        self.assertEqual(inputs["billingEmail"], "email")

if __name__ == "__main__":
    unittest.main()
