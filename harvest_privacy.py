#!/usr/bin/env python3
"""Harvest App Store privacy-nutrition data for every app in apps.json.

For each app: fetch the US storefront page, parse the App Privacy dialog,
and write a "privacy" object + "privacyCheckedDate" back into apps.json.

Output shape per app:
  {"tracksYou": bool, "linked": ["Category: data type", ...],
   "notLinked": [...], "notCollected": bool, "summary": "<plain English>"}

Polite to Apple: 1.5s between requests, backoff on 429/503 honoring
Retry-After, max 3 retries per app then privacy:null. Never crashes on one app.
"""
import json
import re
import sys
import time
import urllib.request
import urllib.error
import http.client

APPS_JSON = "/home/hatch/workspace/clean-apps/apps.json"
from datetime import datetime, timezone
CHECK_DATE = datetime.now(timezone.utc).strftime("%Y-%m-%d")
DELAY = 1.5

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

# most significant categories first
CAT_ORDER = ["Contact Info", "Location", "Financial Info", "Health & Fitness",
             "Sensitive Info", "Contacts", "User Content", "Browsing History",
             "Search History", "Identifiers", "Purchases", "Usage Data",
             "Diagnostics", "Other Data"]

TYPE_FRIENDLY = {
    "Email Address": "email address", "Phone Number": "phone number",
    "Name": "name", "Other User Contact Info": "contact info",
    "Precise Location": "precise location", "Coarse Location": "approximate location",
    "Device ID": "device ID", "User ID": "user ID", "Advertising Data": "advertising ID",
    "Product Interaction": "app usage", "Advertising": "ad interactions",
    "Crash Data": "crash reports", "Performance Data": "performance data",
    "Other Diagnostic Data": "diagnostic data",
    "Photos or Videos": "photos and videos", "Audio Data": "audio recordings",
    "Other User Content": "in-app content", "Customer Support": "support messages",
    "Gameplay Content": "gameplay content", "Emails or Text Messages": "messages",
    "Contacts": "contacts", "Purchase History": "purchase history",
    "Payment Info": "payment info", "Credit Score": "credit info",
    "Health": "health data", "Fitness": "fitness data",
    "Sensitive Info": "sensitive info", "Browsing History": "browsing history",
    "Search History": "search history",
}


def fetch(tid):
    """Fetch storefront HTML, validating it's the right app. Returns html or None."""
    url = f"https://apps.apple.com/us/app/x/id{tid}"
    backoff = 4
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            resp = urllib.request.urlopen(req, timeout=30)
            html = resp.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                wait = e.headers.get("Retry-After")
                time.sleep(float(wait) if wait and wait.isdigit() else backoff)
                backoff = min(backoff * 2, 60)
                continue
            return None
        except (http.client.IncompleteRead, http.client.RemoteDisconnected,
                urllib.error.URLError, TimeoutError, ConnectionError):
            time.sleep(backoff)
            backoff = min(backoff * 2, 60)
            continue
        # geo-redirect / wrong-page guard
        if f"id{tid}" in html and "App Privacy" in html:
            return html
        time.sleep(backoff)
        backoff = min(backoff * 2, 60)
    return None


def parse_privacy(html):
    """Parse the App Privacy dialog. Returns dict of section -> items."""
    m = re.search(r'<h1[^>]*>App Privacy</h1>(.*?)</dialog>', html, re.S)
    if not m:
        return None
    dlg = m.group(1)
    sections = {}
    if "has not provided details about its privacy practices" in dlg:
        sections["_noDetails"] = []
    parts = re.split(r'<h3[^>]*>(.*?)</h3>', dlg)
    for i in range(1, len(parts), 2):
        title = re.sub(r'<[^>]+>', '', parts[i]).strip()
        body = parts[i + 1]
        items = []
        seen = set()
        # detailed form: category-title spans with data-type sublists
        for cm in re.finditer(
                r'<span class="category-title[^"]*">([^<]+)</span>\s*<ul[^>]*>(.*?)</ul>',
                body, re.S):
            cat = cm.group(1).strip()
            for t in re.findall(r'<li[^>]*>(.*?)</li>', cm.group(2), re.S):
                t = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', t)).strip()
                if t and (cat, t) not in seen:
                    seen.add((cat, t))
                    items.append((cat, t))
        # simple form (tracking section): bare category names after icon span
        if not items:
            for cm in re.finditer(
                    r'<li[^>]*>\s*<span[^>]*>.*?</span>\s*([^<>{}]{2,60}?)\s*</li>',
                    body, re.S):
                cat = re.sub(r'\s+', ' ', cm.group(1)).strip()
                if cat and (cat, "") not in seen:
                    seen.add((cat, ""))
                    items.append((cat, ""))
        sections[title] = items
    return sections


def rank_key(item):
    cat = item[0]
    try:
        return CAT_ORDER.index(cat)
    except ValueError:
        return len(CAT_ORDER)


def fmt_items(items):
    return [f"{c}: {t}" if t else c for c, t in items]


def friendly(item):
    cat, t = item
    if t:
        return TYPE_FRIENDLY.get(t, t.lower())
    return TYPE_FRIENDLY.get(cat, cat.lower())


def build_summary(tracks_you, linked, not_linked, not_collected, no_details=False):
    if not_collected:
        return "Collects no data."
    if no_details and not (tracks_you or linked or not_linked):
        return "The developer hasn't shared privacy details with Apple yet."
    bits = []
    if tracks_you:
        track_cats = ", ".join(sorted({c for c, _ in tracks_you},
                                       key=lambda c: CAT_ORDER.index(c)
                                       if c in CAT_ORDER else 99))
        bits.append(f"Tracks you across other companies' apps and websites"
                    + (f" using {track_cats.lower()}" if track_cats else "") + ".")
    if linked:
        top = sorted(linked, key=rank_key)[:3]
        items = ", ".join("your " + friendly(x) for x in top)
        bits.append(f"Collects {items}, linked to your identity.")
    if not_linked:
        top = sorted(not_linked, key=rank_key)[:3]
        items = ", ".join("your " + friendly(x) for x in top)
        prefix = "Also collects" if linked else "Collects"
        suffix = ", not linked to you." if not linked else "."
        bits.append(f"{prefix} {items}{suffix}")
    if not tracks_you and (linked or not_linked):
        bits.append("Does not track you across other companies' apps and websites.")
    return " ".join(bits) if bits else "Privacy details unavailable."


def harvest_one(app):
    tid = str(app["appStoreId"])
    html = fetch(tid)
    if not html:
        return None
    sections = parse_privacy(html)
    if sections is None:
        return None
    track = sections.get("Data Used to Track You", [])
    linked = sections.get("Data Linked to You", [])
    not_linked = sections.get("Data Not Linked to You", [])
    not_collected = "Data Not Collected" in sections
    no_details = "_noDetails" in sections
    tracks_you = [x for x in track if x[0]]
    linked_s = sorted(linked, key=rank_key)[:8]
    not_linked_s = sorted(not_linked, key=rank_key)[:8]
    return {
        "tracksYou": bool(tracks_you),
        "linked": fmt_items(linked_s),
        "notLinked": fmt_items(not_linked_s),
        "notCollected": not_collected,
        "summary": build_summary(tracks_you, linked_s, not_linked_s, not_collected, no_details),
    }


def main():
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else None
    apps = json.load(open(APPS_JSON, encoding="utf-8"))
    targets = [a for a in apps if not a.get("privacy")]
    if limit is not None:
        targets = targets[:limit]
    full = partial = null = 0
    for n, app in enumerate(targets, 1):
        try:
            p = harvest_one(app)
        except Exception as e:  # never crash the run on one app
            print(f"[{n}/{len(targets)}] {app['name']}: ERROR {e}", flush=True)
            p = None
        app["privacy"] = p
        app["privacyCheckedDate"] = CHECK_DATE
        if p is None:
            null += 1
            print(f"[{n}/{len(targets)}] {app['name']}: null", flush=True)
        elif p["notCollected"] or p["linked"] or p["notLinked"] or p["tracksYou"]:
            full += 1
            print(f"[{n}/{len(targets)}] {app['name']}: OK - {p['summary'][:80]}", flush=True)
        else:
            partial += 1
            print(f"[{n}/{len(targets)}] {app['name']}: partial (no sections)", flush=True)
        time.sleep(DELAY)
    json.dump(apps, open(APPS_JSON, "w", encoding="utf-8"),
              indent=2, ensure_ascii=False)
    print(f"\nDONE: full={full} partial={partial} null={null} total={len(targets)}")


if __name__ == "__main__":
    main()
