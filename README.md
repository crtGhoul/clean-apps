# Clean Apps — verified iPhone apps with no ads and no in-app purchases

Live: [GitHub Pages](https://crtghoul.github.io/clean-apps/) · [Cloudflare mirror](https://clean-apps.pages.dev)

A curated, verified directory of iPhone apps: **no ads, no paywalls, no paid purchases**.
- **No ads** tier = zero ads, zero IAP.
- **Minimal ads** tier = zero IAP, banner-only non-intrusive ads.

165 verified apps · 50 "clean alternative to X" comparisons · daily deal hunt for free-premium / lifetime-unlock offers.

## How verification works

Every app earns its listing; nothing is taken on the developer's word.

1. **IAP check (machine):** the App Store listing must show no "In-App Purchases" label. Apple stamps this label on every listing that has IAP, so its absence is checkable and absolute. Zero tolerance — one IAP and the app is out.
2. **Ads check (hand):** Apple exposes no ads label, so a human reviews the app description, recent review sentiment, and the developer's reputation. Genuinely ad-free → "no ads" tier; banner-only and non-intrusive → "minimal ads" tier; interstitials, video/rewarded ads, or ad-spam complaints → rejected.
3. **Re-verification (weekly):** every Wednesday the full directory is re-checked against live listings. Apps that added IAP, went paid, or added intrusive ads are flagged as **traitors** — logged permanently in `traitors.json`, removed from the clean listings, never silently deleted.
4. **Knockoff watch:** known App Store impersonators (fake "ChatGPT"/"Claude"/"Midjourney" subscription traps) are tracked in `knockoffs.json` and the site's checker warns on them.

Deal entries may carry an IAP label only when the deal itself makes premium/lifetime access free — the directory bar stays strict no-IAP.

## Suggest an app / report a traitor

- **Suggest an app:** https://forms.gle/BxijEgntGuCnaL4a7
- **Report an app that turned dirty** (added ads, IAP, or a paywall after being listed): open an issue in this repo with the app name, its App Store link, and what changed. Verified reports go into `traitors.json`.

## What's in this repo

| Path | What it is |
|---|---|
| `index.html` | The live site — self-contained built export of Clean Apps, served by GitHub Pages (4.4MB, all assets inlined) |
| `apps.json` | 165 verified apps (fields: name, appStoreId, category, price, hasIAP, adsTier, version, catchLabel, privacy, …) |
| `deals.json` | Time-sensitive free-premium / lifetime-unlock deals (`deal.wasPrice`, `deal.dealKind`, `deal.firstTimeFree`) |
| `knockoffs.json` | Flagged App Store knockoffs (feeds the checker's warning banner) |
| `traitors.json` | Apps that turned dirty after being listed (never silently deleted) |
| `alternatives.json` | 52 "clean alternative to X" mappings with `popularAppAnnualCost` (site renders 50; SEO pages show "switching saves $X/yr") |
| `bad_actors.json` | Developers rejected on sight (deal + submission pipelines auto-reject) |
| `deal-blocklist.json` | User-killed deals never to re-add |
| `sweep.py` | Weekly App Store sweep: keyword enumeration, IAP/offer-label checks, `--version-check` mode |
| `sweep-candidates.json` | Sweep candidates awaiting Wednesday human ad-review |
| `sweep-rotation.json` | Keyword-rotation state for the Tuesday sweep |
| `harvest_privacy.py` | Harvests App Store privacy-nutrition labels into `apps.json` |
| `deal_lookup.py` | Deal lookup helpers |
| `measure.py` | Directory measurement helpers |
| `backfill_versions.py` | One-time: backfill App Store versions into `apps.json` |
| `SITE_SPEC.md` | Original site spec |

## How the site relates to this repo

The public site is a Muse web artifact; `index.html` here is its built export, refreshed automatically by the daily sync. Edits to the **site itself** (layout, checker logic, pages) go through the site owner (Strider2) via the artifact builder — a pull request here cannot change the live site directly. Improvements to **data, scripts, and automation** in this repo are directly useful: better sweep coverage, smarter verification, new data fields (with a note on how the site should render them).

## Automation around this repo

- Daily deal hunt + deal health checks (drop dead codes, flag weak ones)
- Every-2-hours Telegram deal-mirror watch
- Wednesday full verification: sweep candidates, version-diff re-verification,
  ad-traitor review scan, knockoff hunt
- Tuesday App Store sweep (`sweep.py`)
- Daily GitHub Pages refresh (`index.html` re-exported when the site changes)

## For an AI agent picking this up

Good first tasks: expand `sweep.py` keyword coverage, harden offer-label parsing,
add new `deal` fields with rendering notes, grow the knockoff watchlist. Keep the
zero-IAP bar for the directory absolute; deals may carry an IAP label only when
the deal itself is a free premium/lifetime unlock.

## License

MIT — see [LICENSE](LICENSE).
