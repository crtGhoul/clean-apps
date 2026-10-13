#!/usr/bin/env python3
"""Deal-hunt App Store verifier: iTunes Lookup API (country=US) for live price,
seller, version, ratings, icon, and description. The 'In-App Purchases' label and
content advisories are checked separately via the apps.apple.com listing text.

Usage: python3 deal_lookup.py <appStoreId> [<appStoreId> ...]
"""
import json
import sys
import urllib.parse
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}


def lookup(ids):
    q = urllib.parse.urlencode({"id": ",".join(ids), "country": "US", "entity": "software"})
    req = urllib.request.Request(f"https://itunes.apple.com/lookup?{q}", headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["results"]


def main():
    ids = sys.argv[1:]
    if not ids:
        print("usage: deal_lookup.py <appStoreId> [...]")
        sys.exit(1)
    for chunk_start in range(0, len(ids), 50):
        for app in lookup(ids[chunk_start : chunk_start + 50]):
            desc = (app.get("description") or "").replace("\n", " ")
            print("=" * 78)
            print(f"name        : {app.get('trackName')}")
            print(f"id          : {app.get('trackId')}")
            print(f"price       : {app.get('formattedPrice')}  (raw price={app.get('price')})")
            print(f"seller      : {app.get('sellerName')}")
            print(f"version     : {app.get('version')}  ({app.get('currentVersionReleaseDate','')[:10]})")
            print(f"rating      : {app.get('averageUserRating')} ({app.get('userRatingCount')} ratings)")
            print(f"genre       : {app.get('primaryGenreName')}")
            print(f"minOS       : {app.get('minimumOsVersion')}")
            print(f"advisory    : {app.get('contentAdvisoryRating')}")
            print(f"icon        : {app.get('artworkUrl100')}")
            print(f"url         : {app.get('trackViewUrl')}")
            print(f"description : {desc[:900]}")


if __name__ == "__main__":
    main()
