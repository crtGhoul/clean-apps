#!/usr/bin/env python3
"""Weekly App Store sweep for Clean Apps.

Enumerates free iOS apps via the iTunes Search API across a keyword list,
then checks each app's OWN storefront offer data (the same JSON that renders
the "In-App Purchases" label) for: isFree + hasInAppPurchases.

Apps passing both filters are written as candidates needing human ad-review
(Apple exposes no ads label — that step stays human).

Usage:
    python3 sweep.py --test           # 2 keywords, 10 results each, no writes
    python3 sweep.py                  # full run, writes sweep-candidates.json
    python3 sweep.py --version-check  # diff stored versions vs live, writes version-changes.json
"""

import json, re, sys, time, urllib.request, urllib.parse
from datetime import datetime, timezone

BASE = "/home/hatch/workspace/clean-apps"
APPS_JSON = f"{BASE}/apps.json"
DEALS_JSON = f"{BASE}/deals.json"
CANDIDATES_JSON = f"{BASE}/sweep-candidates.json"
VERSION_CHANGES_JSON = f"{BASE}/version-changes.json"

UA = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"}

# Broad category keywords — the sweep's net. Edit freely.
KEYWORDS = [
    "photo editor", "video editor", "vpn", "file manager", "notes app",
    "todo list", "music player", "podcast player", "keyboard", "calculator",
    "weather", "authenticator", "password manager", "rss reader",
    "ebook reader", "pdf reader", "document scanner", "habit tracker",
    "workout", "meditation", "language learning", "flashcards",
    "budget tracker", "expense tracker", "unit converter", "qr scanner",
    "metronome", "guitar tuner", "piano", "chess", "sudoku",
    "crossword", "solitaire", "white noise", "sleep sounds", "pomodoro",
    "timer", "voice recorder", "compass", "level tool", "drawing",
    "pixel art", "markdown editor", "code editor", "ssh client",
    "network scanner", "speed test", "battery", "widget",
    "lock screen widget", "countdown", "dice", "random picker",
]

PAGE_DELAY = 1.5   # politeness delay between storefront fetches
MAX_PER_RUN = 400  # cap on new candidates checked per run


def itunes_search(term, limit=200):
    q = urllib.parse.urlencode(
        {"term": term, "entity": "software", "limit": limit, "country": "US"})
    req = urllib.request.Request(f"https://itunes.apple.com/search?{q}", headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r).get("results", [])


def offer_data(track_id, url):
    """Fetch the storefront page, return (is_free, has_iap) from the app's
    own offer block, or (None, None) if undeterminable."""
    for attempt in range(2):
        try:
            req = urllib.request.Request(url.split("?")[0], headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                html = r.read().decode("utf-8", errors="replace")
            break
        except Exception:
            if attempt == 1:
                return None, None
            time.sleep(5)
    tid = str(track_id)
    # find every hasInAppPurchases occurrence, attribute to nearest preceding adamId
    best = None
    for m in re.finditer(r'"hasInAppPurchases":(true|false)', html):
        window = html[max(0, m.start() - 1200):m.start()]
        adams = re.findall(r'"adamId":"?(\d+)"?', window)
        if adams and adams[-1] == tid:
            free_m = re.search(r'"isFree":(true|false)', html[m.start():m.start() + 400])
            best = (free_m.group(1) == "true" if free_m else None,
                    m.group(1) == "true")
    if best:
        return best
    return None, None


def ad_signal(description):
    d = (description or "").lower()
    if any(s in d for s in ["ad-free", "ad free", "no ads", "without ads", "zero ads"]):
        return "claims-ad-free"
    if any(s in d for s in ["contains ads", "ad-supported", "ad supported", "ads help"]):
        return "admits-ads"
    return "unknown"


def load_known_ids():
    known = set()
    for path, key in ((APPS_JSON, None), (DEALS_JSON, None)):
        try:
            data = json.load(open(path))
            items = data if isinstance(data, list) else data.get("apps", data.get("deals", []))
            for a in items:
                for k in ("trackId", "id", "appId", "appStoreId"):
                    if a.get(k):
                        known.add(str(a[k]))
                url = a.get("url", "") or a.get("appUrl", "") or a.get("appStoreUrl", "")
                m = re.search(r"/id(\d+)", url)
                if m:
                    known.add(m.group(1))
        except FileNotFoundError:
            pass
    try:
        for c in json.load(open(CANDIDATES_JSON)):
            known.add(str(c["trackId"]))
    except FileNotFoundError:
        pass
    return known


def version_check():
    """Diff stored app versions against the live App Store.

    Writes version-changes.json: apps whose live version differs from the
    stored one. Those apps need priority re-verification — an update can
    add IAP or ads overnight. Updates the stored version + check date for
    unchanged apps is NOT done here; the Wednesday worker refreshes dates
    when it re-verifies.
    """
    apps = json.load(open(APPS_JSON))
    items = apps if isinstance(apps, list) else apps.get("apps", apps)
    ids = [str(a["appStoreId"]) for a in items]
    stored = {str(a["appStoreId"]): (a.get("version", ""), a.get("name", "")) for a in items}

    live = {}
    for i in range(0, len(ids), 150):
        chunk = ids[i:i + 150]
        url = f"https://itunes.apple.com/lookup?id={','.join(chunk)}&country=US&entity=software"
        req = urllib.request.Request(url, headers=UA)
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                for res in json.load(r).get("results", []):
                    live[str(res["trackId"])] = res.get("version", "")
        except Exception as e:
            print(f"[version-check] lookup failed for chunk {i // 150 + 1}: {e}", file=sys.stderr)
        time.sleep(1)

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    changes = []
    for tid, (old_v, name) in stored.items():
        new_v = live.get(tid)
        if not new_v:
            print(f"[version-check] no live data: {name} ({tid})", file=sys.stderr)
            continue
        if new_v != old_v:
            changes.append({
                "appStoreId": tid,
                "name": name,
                "oldVersion": old_v,
                "newVersion": new_v,
                "dateDetected": today,
                "status": "pending-reverify",
            })
            print(f"[version-check] CHANGED: {name}: {old_v} -> {new_v}")

    json.dump(changes, open(VERSION_CHANGES_JSON, "w"), indent=2, ensure_ascii=False)
    print(f"[version-check] done: {len(changes)} changed of {len(live)} checked; "
          f"wrote {VERSION_CHANGES_JSON}")
    return changes


def main():
    if "--version-check" in sys.argv:
        version_check()
        return
    test = "--test" in sys.argv
    keywords = KEYWORDS[:2] if test else KEYWORDS
    known = load_known_ids()
    seen, checked, candidates = set(), 0, []

    for kw in keywords:
        try:
            results = itunes_search(kw, limit=50 if test else 200)
        except Exception as e:
            print(f"[sweep] search failed for {kw!r}: {e}", file=sys.stderr)
            continue
        for r in results:
            tid = str(r.get("trackId"))
            if not tid or tid in known or tid in seen:
                continue
            seen.add(tid)
            if r.get("price", 0) != 0:  # paid upfront — not our beat
                continue
            if checked >= MAX_PER_RUN and not test:
                break
            url = r.get("trackViewUrl", "")
            is_free, has_iap = offer_data(tid, url)
            checked += 1
            time.sleep(PAGE_DELAY)
            if is_free is None:
                print(f"[sweep] undeterminable: {r.get('trackName')}", file=sys.stderr)
                continue
            if not is_free or has_iap:
                continue  # paywalled or IAP — excluded by the mission
            rel = r.get("releaseDate", "")[:10]
            try:
                age_days = (datetime.now(timezone.utc) -
                            datetime.fromisoformat(rel.replace("Z", "+00:00"))).days
            except Exception:
                age_days = None
            candidates.append({
                "trackId": tid,
                "name": r.get("trackName"),
                "url": url,
                "genre": r.get("primaryGenreName"),
                "rating": r.get("averageUserRating"),
                "ratingCount": r.get("userRatingCount"),
                "releaseDate": rel,
                "isNew": age_days is not None and age_days <= 90,
                "isFree": True, "hasIAP": False,
                "adSignal": ad_signal(r.get("description")),
                "descriptionSnippet": (r.get("description") or "")[:300],
                "dateFound": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
                "status": "pending-ad-review",
            })
            print(f"[sweep] candidate: {r.get('trackName')} ({r.get('primaryGenreName')}) "
                  f"adSignal={candidates[-1]['adSignal']} isNew={candidates[-1]['isNew']}")
        if checked >= MAX_PER_RUN and not test:
            break

    print(f"[sweep] done: {checked} listings checked, {len(candidates)} candidates")
    if test:
        return
    existing = []
    try:
        existing = json.load(open(CANDIDATES_JSON))
    except FileNotFoundError:
        pass
    existing.extend(candidates)
    json.dump(existing, open(CANDIDATES_JSON, "w"), indent=2, ensure_ascii=False)
    print(f"[sweep] wrote {len(existing)} total candidates to {CANDIDATES_JSON}")


if __name__ == "__main__":
    main()
