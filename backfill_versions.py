#!/usr/bin/env python3
"""Backfill current App Store versions into apps.json.

Batch-looks-up all app IDs via the iTunes lookup API (one call handles
~200 IDs) and stores `version` + `versionCheckedDate` per app.
Run once now, then sweep.py --version-check keeps it fresh.
"""
import json, time, urllib.request
from datetime import datetime, timezone

BASE = "/home/hatch/workspace/clean-apps"
APPS_JSON = f"{BASE}/apps.json"
UA = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"}

apps = json.load(open(APPS_JSON))
items = apps if isinstance(apps, list) else apps.get("apps", apps)
ids = [str(a["appStoreId"]) for a in items]
print(f"[backfill] {len(ids)} apps")

versions = {}
for i in range(0, len(ids), 150):
    chunk = ids[i:i + 150]
    url = f"https://itunes.apple.com/lookup?id={','.join(chunk)}&country=US&entity=software"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        for res in json.load(r).get("results", []):
            versions[str(res["trackId"])] = res.get("version", "")
    print(f"[backfill] chunk {i // 150 + 1}: {len(versions)} versions so far")
    time.sleep(1)

today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
missing = []
for a in items:
    v = versions.get(str(a["appStoreId"]))
    if v:
        a["version"] = v
        a["versionCheckedDate"] = today
    else:
        missing.append(a["name"])

json.dump(apps, open(APPS_JSON, "w"), indent=2, ensure_ascii=False)
print(f"[backfill] wrote versions for {len(items) - len(missing)}/{len(items)} apps")
if missing:
    print(f"[backfill] missing: {missing}")
