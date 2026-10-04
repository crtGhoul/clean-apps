#!/usr/bin/env python3
"""Measure what fraction of sampled App Store listings are free with no IAP.
Statistical sample — does not write anything."""
import sys, time, json
sys.path.insert(0, "/home/hatch/workspace/clean-apps")
from sweep import itunes_search, offer_data, ad_signal, UA  # noqa

KEYWORDS = ["photo editor", "video editor", "vpn", "file manager",
            "notes app", "todo list", "music player", "podcast player",
            "keyboard", "calculator", "weather", "authenticator"]

seen, free, checked, clean = set(), 0, 0, 0
ad_breakdown = {"claims-ad-free": 0, "admits-ads": 0, "unknown": 0}

for kw in KEYWORDS:
    try:
        results = itunes_search(kw, limit=150)
    except Exception as e:
        print(f"search failed {kw}: {e}", file=sys.stderr)
        continue
    for r in results:
        tid = str(r.get("trackId"))
        if not tid or tid in seen:
            continue
        seen.add(tid)
        if r.get("price", 0) != 0:
            continue
        free += 1
        is_free, has_iap = offer_data(tid, r.get("trackViewUrl", ""))
        checked += 1
        time.sleep(1.0)
        if is_free and not has_iap:
            clean += 1
            ad_breakdown[ad_signal(r.get("description"))] += 1

print(json.dumps({
    "unique_listings_sampled": len(seen),
    "free": free,
    "listings_iap_checked": checked,
    "free_and_no_iap": clean,
    "pct_free_of_sample": round(100 * free / len(seen), 1) if seen else 0,
    "pct_no_iap_of_free": round(100 * clean / free, 1) if free else 0,
    "ad_signal_breakdown_of_clean": ad_breakdown,
}, indent=2))
