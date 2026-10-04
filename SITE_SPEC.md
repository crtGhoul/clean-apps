# SITE_SPEC — Clean Apps directory

## What this is
A public directory of iPhone apps verified to be 100% free with no ads and no
in-app purchases, plus a deals section for apps currently offering premium
free (e.g. free lifetime unlocks for early users). English-first, phone-first.

## Data (in this folder — use verbatim, do not re-scrape)
- `apps.json` — 91 verified apps. Fields: name, appStoreUrl, appStoreId,
  category, developer, price ("Free"), hasIAP (false), iapVerifiedDate,
  adsFree (true), adsCheckMethod, iconUrl, oneLine.
- `deals.json` — 9 free-premium/lifetime deals. Fields include dateFound,
  source, expiry. NOTE: deals are time-sensitive — display the date found and
  any expiry prominently, with a "verify before you grab it" note. One deal
  (shoparound) is ad-supported and flagged honestly — present it as
  "free premium, but has ads," never in the main directory.
- Categories present: Productivity, Music, Authenticator, Health & Fitness,
  Education, Browsing, Photo & Video, Entertainment, VPN, Reference, Weather,
  Books, RSS, Connect, Travel.

## Pages
1. **Home** — hero ("iPhone apps with no ads, no in-app purchases. Verified."),
   live search across all apps, category chips, featured/curated picks,
   deals strip, trust line ("91 apps verified 2026-10-01 · re-checked weekly").
2. **Browse / category views** — filter by category, search.
3. **App detail** — icon, name, developer, category, one-liner, App Store
   link (big touch target), "Verified clean" badge with verification date,
   what "verified" means for this app (IAP label absent + ad check method).
4. **Deals** — the 9 premium offers as cards: what the offer is, date found,
   expiry/countdown if known, source link, "grab it" App Store link.
5. **How we verify (methodology)** — plain-language: Apple labels in-app
   purchases on every listing so we re-check weekly; Apple has no ads label
   so ads status is hand-verified per app; what happens when an app goes
   dirty (traitor flag). Honest about limits: 20% of apps live spot-checked,
   rest rest on listing verification; dead zones noted (no clean email apps
   found, thin RSS/Weather/Travel).
6. **About** — one paragraph: why this exists, free forever, no ads on the
   site itself.

## Design
Phone-first (most visitors on iPhone), clean and fast, light + dark mode,
big touch targets, no ads, no trackers, no newsletter popups. App icons from
iconUrl. Fast client-side search. This site eats its own dogfood: zero
dark patterns.

## Trust details to get right
- Every app card shows its verification date.
- Deals show date found + expiry; never present expired deals as live.
- The "traitor" concept: a visible spot for apps that USED to be clean
  (empty for now — the weekly re-check will fill it).
- Link out to the App Store with the official appStoreUrl for each app.
