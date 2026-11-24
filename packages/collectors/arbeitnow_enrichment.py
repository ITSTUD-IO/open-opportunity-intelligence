"""Conservative, offline-only Arbeitnow enrichment primitives.

No external lookups, scraping or assumptions based on city names.
"""
import re
import unicodedata
from urllib.parse import urlparse, urlunparse

from packages.collectors.arbeitnow_quality import country_of, valid_https

COUNTRY_SUFFIXES = {
    "germany": "DE", "deutschland": "DE",
    "austria": "AT", "österreich": "AT",
    "switzerland": "CH", "schweiz": "CH", "suisse": "CH",
}


def country_evidence(item):
    """Return (country, provenance), never infer from a city or remote status."""
    explicit = country_of(item)
    if explicit:
        return explicit, "explicit_field"
    location = item.get("location")
    if isinstance(location, str):
        # Accept only a separate, spelled-out country suffix, not 'DE' in a street
        # or a German city name that may exist elsewhere.
        parts = re.split(r"[,|]", location)
        if len(parts) >= 2:
            suffix = parts[-1].strip().lower()
            if suffix in COUNTRY_SUFFIXES:
                return COUNTRY_SUFFIXES[suffix], "location_country_suffix"
    return None, "unverified"


def canonical_url(url):
    """Normalize only low-risk URL differences; never conflate different paths."""
    if not valid_https(url):
        return None
    parsed = urlparse(url)
    host = parsed.hostname.lower()
    port = parsed.port
    if port and port != 443:
        host += ":" + str(port)
    path = parsed.path or "/"
    return urlunparse(("https", host, path, "", parsed.query, ""))


def _fold(text):
    normalized = unicodedata.normalize("NFKC", str(text or "")).casefold()
    return " ".join(normalized.split())


def deduplication_keys(item):
    """Generate candidate identity keys; no automatic cross-employer merging."""
    slug = str(item.get("slug") or "").strip()
    keys = []
    if slug:
        keys.append("arbeitnow:slug:" + slug)
    url = canonical_url(item.get("url"))
    if url:
        keys.append("canonical_url:" + url)
    employer = _fold(item.get("company_name"))
    title = _fold(item.get("title"))
    location = _fold(item.get("location"))
    if employer and title and location:
        keys.append("candidate:" + "|".join((employer, title, location)))
    return keys


def audit_enrichment(items):
    rows = [item for item in items if isinstance(item, dict)]
    countries = {"DE": 0, "AT": 0, "CH": 0, "unknown": 0}
    provenance = {}
    key_owners = {}
    duplicate_candidates = 0
    for index, item in enumerate(rows):
        country, source = country_evidence(item)
        countries[country or "unknown"] += 1
        provenance[source] = provenance.get(source, 0) + 1
        for key in deduplication_keys(item):
            if key in key_owners and key_owners[key] != index:
                duplicate_candidates += 1
            else:
                key_owners[key] = index
    return {"sampled": len(rows), "countries": countries,
            "country_evidence": provenance,
            "duplicate_candidate_key_collisions": duplicate_candidates,
            "deduplication_status": "candidates_only_no_automatic_merging"}
