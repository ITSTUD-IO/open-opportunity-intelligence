"""Read-only discovery of EPG job listing delivery mechanism.

Prints sanitized structural hints, never executes arbitrary page JavaScript.
"""
import json
import re
import urllib.parse
from html.parser import HTMLParser
from packages.collectors.job_boards import fetch_text, epg_job_links


class Inspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = []
        self.iframes = []
        self.forms = []
        self.data_attrs = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "script" and a.get("src"):
            self.scripts.append(a["src"])
        if tag == "iframe" and a.get("src"):
            self.iframes.append(a["src"])
        if tag == "form" and a.get("action"):
            self.forms.append(a["action"])
        for k, v in attrs:
            if k.startswith("data-") and isinstance(v, str) and any(t in k.lower() for t in ("job", "url", "api", "endpoint")):
                self.data_attrs.append([k, v[:150]])


def main():
    url = "https://www.epg-jobs.com/stellenangebote/berufserfahrene"
    html = fetch_text(url)
    parser = Inspector()
    parser.feed(html)
    print("EPG_SOURCE_DIAGNOSTIC " + json.dumps({
        "page": url, "html_length": len(html), "static_job_links": len(epg_job_links(html)),
        "scripts": [urllib.parse.urljoin(url, x) for x in parser.scripts][:50],
        "iframes": [urllib.parse.urljoin(url, x) for x in parser.iframes][:20],
        "forms": [urllib.parse.urljoin(url, x) for x in parser.forms][:20],
        "data_attrs": parser.data_attrs[:30],
        "job_host_mentions": len(re.findall(r"jobs-ads\\.epg\\.com", html, re.I)),
        "job_keywords": sorted(set(re.findall(r"[\\w./:-]{0,70}(?:jobposting|joblist|jobboard|vacanc|stellenangebot|api/)[\\w./?=&:-]{0,100}", html, re.I)))[:25]
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
