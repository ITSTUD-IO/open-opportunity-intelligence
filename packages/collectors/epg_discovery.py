"""One-shot, read-only diagnostics for EPG's publicly served careers HTML.

No credentialed endpoints, browser bypasses or speculative API requests.
"""
from html.parser import HTMLParser
import json
import re
from urllib.parse import urljoin, urlparse

from packages.collectors.job_boards import fetch_text


class Assets(HTMLParser):
    def __init__(self):
        super().__init__()
        self.assets = []
        self.frames = []
        self.data_attrs = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "script" and a.get("src"):
            self.assets.append(a["src"])
        if tag == "iframe" and a.get("src"):
            self.frames.append(a["src"])
        for k, v in attrs:
            if k.startswith("data-") and v and re.search(r"job|career|api|vacanc|posting|recruit", k + " " + v, re.I):
                self.data_attrs.append([k, v[:160]])


def main():
    url = "https://www.epg-jobs.com/stellenangebote/berufserfahrene"
    html = fetch_text(url)
    parser = Assets()
    parser.feed(html)
    data = {
        "page": url,
        "html_bytes": len(html.encode()),
        "script_sources": [urljoin(url, x) for x in parser.assets],
        "iframes": [urljoin(url, x) for x in parser.frames],
        "relevant_data_attributes": parser.data_attrs[:30],
        "inline_api_hints": sorted(set(re.findall(
            r'.{0,80}(?:/api/|jobposting|jobs-ads|vacanc|stellenangebot|recruit).{0,100}',
            html, re.I)))[:30],
    }
    print("EPG_SOURCE_DISCOVERY " + json.dumps(data, ensure_ascii=False)[:16000])


if __name__ == "__main__":
    main()
