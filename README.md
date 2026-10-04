# Clean Apps — iPhone directory of apps with no ads and no in-app purchases

Live site: https://muse.ai/s/clean-apps-xdxa5xixjxpxzxu2mt

A curated, verified directory of iPhone apps: **minimum ads, no paywall, no paid purchases**.
- **No ads** tier = zero ads, zero IAP.
- **Minimal ads** tier = zero IAP, banner-only non-intrusive ads.
- IAP status is machine-verified from the App Store listing; ad level is hand-verified
  (Apple exposes no ads label).

## What's in this repo

| Path | What it is |
|---|---|
| `apps.json` | 150 verified apps (fields: name, appStoreId, category, price, hasIAP, adsTier, version, …) |
| `deals.json` | Time-sensitive free-premium / lifetime-unlock deals (`deal.wasPrice`, `deal.dealKind`) |
| `knockoffs.json` | Flagged App Store knockoffs (feeds the checker's warning banner) |
| `traitors.json` | Apps that turned dirty after being listed (never silently deleted) |
| `alternatives.json` | 50 "clean alternative to X" mappings (SEO pages) |
| `sweep.py` | Weekly App Store sweep: keyword enumeration, IAP/offer-label checks, `--version-check` mode |
| `measure.py` | Directory measurement helpers |
| `backfill_versions.py` | One-time: backfill App Store versions into `apps.json` |
| `site/clean-apps.html` | Exported built copy of the live site (reference only — not the editable source) |
| `SITE_SPEC.md` | Original site spec |

## How the site relates to this repo

The public site is a Muse web artifact whose builder reads the JSON files in this
repo. Edits to the **site itself** (layout, checker logic, pages) go through the
site owner (Strider2) via the artifact builder — a pull request here cannot change
the live site directly. Improvements to **data, scripts, and automation** in this
repo are directly useful: better sweep coverage, smarter verification, new data
fields (with a note on how the site should render them).

## Automation around this repo

- Daily deal hunt + deal health checks (drop dead codes, flag weak ones)
- Every-2-hours Telegram deal-mirror watch
- Wednesday full verification: sweep candidates, version-diff re-verification,
  ad-traitor review scan, knockoff hunt
- Tuesday App Store sweep (`sweep.py`)

## For an AI agent picking this up

Good first tasks: expand `sweep.py` keyword coverage, harden offer-label parsing,
add new `deal` fields with rendering notes, grow the knockoff watchlist. Keep the
zero-IAP bar for the directory absolute; deals may carry an IAP label only when
the deal itself is a free premium/lifetime unlock.
