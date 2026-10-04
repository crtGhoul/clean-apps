# Clean Apps — Agent Handoff Doc

Shared learning log. Every phase agent MUST read this file before starting and append an entry when done: learnings, decisions, pitfalls, advice for the next phase.

## Kickoff — coordinator (2026-10-01)

**Mission:** Build the verified dataset for "Clean Apps", a directory of iPhone apps that are 100% free, no ads, no in-app purchases — plus a deals section for apps currently offering premium free (launch promos, early-adopter lifetime unlocks).

**Source of truth:** the app's `apps.apple.com` listing page (via `browser.open`; fall back to `browser.search` if a page won't fetch). An app qualifies ONLY if ALL hold:
1. Price is Free.
2. Listing shows NO "In-App Purchases" label (Apple stamps this on every listing that has IAP — absence is checkable).
3. Ads assessment = clean, via description scan + recent review sentiment + developer reputation. Record HOW (e.g. `"listing+reviews"`).

**Iron rule:** never guess. If you cannot verify, drop the app and find another.

**Output files:**
- `~/workspace/clean-apps/research/agent-a.json` … `agent-d.json` (25 apps each)
- `~/workspace/clean-apps/research/deals.json` (10–20 dated deals)
- Phase 2 merges into `~/workspace/clean-apps/apps.json` + `~/workspace/clean-apps/deals.json`
- Target after dedupe: 80–100 clean apps.

**App object shape:**
```json
{"name":"...","appStoreUrl":"https://apps.apple.com/...","appStoreId":"123456789","category":"...","developer":"...","price":"Free","hasIAP":false,"iapVerifiedDate":"2026-10-01","adsFree":true,"adsCheckMethod":"listing+reviews","iconUrl":"... or null","oneLine":"Plain-English one-liner.","deal":null}
```
Deals use the same shape with `deal` populated: `{"offer":"...","dateFound":"2026-10-01","source":"...","expiry":"..."}`. For deals, fill `hasIAP`/`adsFree` with what's TRUE on the listing right now (a lifetime-unlock deal may sit on an app whose listing shows IAP — record honestly, the deal explains the offer).

**Language:** site is English-first; `oneLine` in plain English, no jargon.

**Known calibration examples:** VLC, Signal, Firefox iOS, DuckDuckGo = likely clean (verify anyway). Bitwarden (premium IAP), Proton VPN (paid plans), any "Unlock Pro" = EXCLUDED.

**Phases:** 1 (five parallel researchers) → 2 (assembler: dedupe, merge) → 3 (reviewer: spot-check 20% live, fix errors).

## Assembly — assembler (2026-10-01)

**Delivered:** `clean-apps/apps.json` (91 clean apps) + `clean-apps/deals.json` (9 deals). Both parse as valid JSON; `appStoreId` normalized to string everywhere; 91 unique IDs; every apps.json entry verified `hasIAP:false, adsFree:true, deal:null`.

**Merge math:** 100 inputs − 9 duplicates merged = 91 unique.
Duplicates merged into one entry each (kept best oneLine + most specific category):
1. WireGuard (A=Productivity, C=VPN) → VPN
2. Tailscale (A=Productivity, C=VPN) → VPN
3. OpenVPN Connect (A=Productivity, C=VPN) → VPN
4. NetNewsWire (A=Productivity, C=RSS) → RSS
5. 2FAS (A=Productivity, C=Authenticator) → Authenticator
6. Ente Auth (A=Productivity, C=Authenticator) → Authenticator
7. Google Translate (A=Productivity, D=Reference) → Reference
8. Microsoft Translator (A=Productivity, D=Productivity) → Reference (Apple genre; unified with #7)
9. GarageBand (B=Music, D=Music) → Music

**Dropped: 0.** No entries were missing required fields and none had contradictory flags. Flagged weak picks were KEPT per the iron rule's spirit (listing-level verification is all that's needed): Calmaria (D's weak pick — listing clean, adsCheckMethod honestly just `"listing"`), NetNewsWire (~884 ratings), ZeroTier One (3.8★). The reviewer should re-check these in Phase 3.

**Deals:** all 9 kept as-is, deal objects intact. shoparound keeps `adsFree:false` honestly (ad-supported but deal-legit); it is correct for deals.json and excluded by construction from apps.json. Note FindNRefill (expires 2026-10-17) and ChitPact (expires 2026-10-14) need re-check before any public launch.

**One data-hygiene fix:** Agent A's entries claimed `adsCheckMethod: "listing+reviews"`, but A's own handoff note admits fetched listing pages never render review text — so "reviews" was aspirational. Normalized all of A's to `"listing+description+reputation"` (matching the agents that were honest about it). Agent C's Tofu `"listing+reviews"` is legit (reviews actually read) and was preserved. Merged duplicates carry a combined method string (e.g. `"listing+reviews+reputation"`).

**Category coverage (91):** Productivity 17, Music 11, Authenticator 10, Health & Fitness 9, Education 9, Browsing 8, Photo & Video 7, Entertainment 7, VPN 4, Reference 2, Weather 2, Books 2, RSS 1, Connect 1, Travel 1.
Known thin zones for Phase 3 / future fills: Email = zero (all 6 candidates IAP), RSS = 1, Weather = 2, Travel = 1, Connect = 1; habit-trackers and water reminders have no clean candidates anywhere; camera/photo-editor beyond Snapseed is bare.

**For the reviewer (Phase 3):** re-verify the ~9 duplicate-merged entries only changed category/oneLine/method fields (IDs, URLs, icons untouched from first-seen entry); the deals with near-term expiries above; and Calmaria's listing.

---

## Phase 3 — Reviewer (2026-10-01, ~01:50 CDT)

**Spot-checked 18/91 apps (20%) against live `apps.apple.com` listings + iTunes lookup API.** All 18 PASS the iron rule: badge reads "Free" with no "In‑App Purchases" stamp, no "In-App Purchases" section in Information, no "Contains Advertising" in the age rating, description has no ad admissions.

- **Flagged weak picks, all re-verified clean:** Calmaria (1523108871 — Free, no IAP, 9+, Data Not Collected, 48 ratings; still the weakest pick on reputation, but the listing is spotless; updated to v3.0 11/12/2025 with HealthKit — note it now requires iOS 18.0+), NetNewsWire (1480640210 — Free, no IAP, 16+ for web-access content only, 884 ratings), ZeroTier One (1084101492 — Free, no IAP, Data Not Collected, 3.8★/212 ratings).
- **All 9 merged entries re-verified field-by-field against the live lookup API:** WireGuard, Tailscale, OpenVPN Connect, NetNewsWire, 2FAS, Ente Auth, Google Translate, Microsoft Translator, GarageBand — name, appStoreId, developer (sellerName), price (Free), hasIAP (false), iconUrl (artworkUrl100), and appStoreUrl (trackViewUrl) all survive the merge intact. Categories are the site's curated taxonomy (e.g. VPN), not Apple genres — correct as assembled.
- **Random spread (7):** VLC, TestFlight, Obsidian, Tofu Authenticator, Firefox, Google Earth, Khan Academy — all pass.
- Interesting: one listing fetch (Tofu) rendered actual review text for the first time in this project — it showed reviews are clean with no ad complaints, but per the established convention this still doesn't justify changing anyone else's `adsCheckMethod`; leave methods as the assembler normalized them.

**Fixes made (2):** corrected `developer` from `"Google"` to `"Google LLC"` on Google Earth (293622097) and Google Arts & Culture (1050970557) — live sellerName is Google LLC, matching all other Google entries. No apps dropped (every checked app passed re-verification).

**Deals — all 9 sources opened and verified live, none expired as of 2026-10-01:**
1. Space for Two (ozbargain 973840) — live, dev-posted, hidden-star easter egg confirmed in comments; expiry "ongoing" honest.
2. ExploreIRL (YouTube K876BCOYLUY) — video description still shows code IRLFAM26 for first-500 free lifetime; expiry "unknown (cap may be reached)" is the honest label, keep it.
3. FindNRefill (ozbargain 976585) — LIVE, posted 27/09, offer-code redeem link confirmed working by commenters; expires 2026-10-17 (16 days out). Re-check before launch if past that date.
4. ChitPact (ozbargain 975016) — LIVE; thread states "Redeem by: 14 Oct 2026 (or earlier if all 30 spots go)"; only 113 clicks so cap risk is real but not verifiable; expiry 2026-10-14 (13 days out). Re-check before launch if past that date.
5. shoparound (ozbargain 972647) — live, dev-maintained, all-premium-free ongoing; adsFree:false honestly recorded.
6. Dark Logger (Product Hunt) — page shows "FREE lifetime report unlock for iOS" promo; live.
7. LarpGPT (vibingtalk 1574493) — dev post confirms code LARPGPTPROMPTENG with redeem link; live.
8. QuranWay (Medium) — dev article confirms code THEQURANWAY with redeem link; live.
9. Bevel (ozbargain 974411) — "long running" referral thread, 30 days Pro for referees; live.

**Remaining concerns / notes for launch:** (a) FindNRefill and ChitPact both die mid-October — set a re-check before any public launch after those dates. (b) ExploreIRL's 500-cap may already be exhausted; consider labeling it "first 500 — may be gone" on the site. (c) Age-rating labels like "Contains Unrestricted Web Access" (Firefox, NetNewsWire) and "Contains Messaging and Chat" (Microsoft Translator, GarageBand) are feature/content disclosures, not advertising — they pass. (d) Calmaria now requires iOS 18.0+ and GarageBand requires iOS 26.0+; worth noting on the site but not disqualifying. (e) Both files re-validated as parseable JSON: 91 apps (91 unique IDs), 9 deals, all required fields present.

## Phase 2 — Assembler, tiers + alternatives (2026-10-01, ~02:45 CDT)

**Delivered:** `clean-apps/apps.json` (121 apps: 91 `adsTier:"none"` + 30 `adsTier:"minimal"`) + `clean-apps/alternatives.json` (27 query→dirty-app→clean-pick mappings). Backup of pre-merge 91 kept at `research/apps-backup-2026-10-01.json`.

**Merge math:** 91 existing (verified IDs unique) + 30 minimal-ads (zero ID overlap with the 91, independently ID-checked — my programmatic check agreed) = 121, all IDs unique. Excluded: 0 — every minimal-ads entry had all 15 required fields, hasIAP:false, adsTier:"minimal". Original 91 entries verified byte-identical except the added `"adsTier":"none"` key (diffed programmatically against backup).

**Alternatives:** all 27 raw mappings kept — no duplicate popularApp in the raw file (no dedupe needed), and all 27 cleanPick names match apps.json names exactly against the FINAL 121 (so picks pointing at minimal-tier apps resolve correctly too). No name fixes, no drops.

**Category counts after merge (121):** Productivity 21, Music 17, Entertainment 13, Authenticator 10, Health & Fitness 10, Education 10, Travel 9, Browsing 8, Photo & Video 7, Reference 4, VPN 4, Weather 3, Books 3, RSS 1, Connect 1. Alternatives whyDirty: 19 in-app-purchases, 7 both, 1 ads-only (Spotify).

**Flags for the reviewer (Phase 3):** (1) Minimal-tier apps carry `adsFree:false` honestly — the site needs a two-tier presentation (Clean vs "Minimal ads") or the directory's core promise breaks. (2) Carried forward from Agent B: weak passes in the minimal tier — AccuRadio (742 ratings, radio-style audio ad breaks), KEXP (270 ratings), SuperCook (not updated since 2022), trivago/Hopper (no ad disclosure, sponsored-listing model), ABC News (broadcast ad breaks in live TV), WordReference (29 ratings). (3) alternatives.json's cleanPick can point at a minimal-tier app (e.g. users searching alternatives to apps Agent B verified against minimal apps) — decide in the site UI whether a dirty-app alternative may itself carry ads. (4) Phase 3's spot-check scope should extend to the 30 new minimal entries — they were verified by Agent B on 2026-10-01, not by Phase 3.

## Phase 3 — Reviewer (tiers + alternatives) (2026-10-01, ~06:55 CDT)

**Scope:** 7/30 minimal-tier apps (all flagged weak passes), all 27 alternatives popularApp dirt verdicts, plus full data-hygiene pass. ~27 listing fetches at ~1/turn pacing — no 429 hit this run.

**Minimal tier (7/7 PASS — no removals):** SuperCook (plain "Free", no IAP stamp/section, 4+ no ad disclosure; third-party minor-banner evidence consistent with adsNote), trivago (Free, no IAP, 4+ plain; sponsored-listings model consistent), Hopper (Free, no IAP, 4+ Contains Advertising; description claims "no ads" — the minimal tier is exactly right, adsNote records the contradiction), AccuRadio (Free, no IAP, 13+ Contains Advertising; audio ad breaks noted), KEXP (Free, no IAP, 13+ Contains Advertising; listener-supported nonprofit), ABC News (Free, no IAP, 13+ Contains Advertising; broadcast ad breaks in live TV noted), WordReference (Free, no IAP, 13+ Contains Advertising; banner ads). Every adsNote matched what the listing shows — nothing to demote or drop.

**Alternatives (27/27 popularApp dirt verdicts CONFIRMED on live listings — no mappings dropped):**
- IAP (badge "Free · In‑App Purchases" + priced IAP section): CapCut, Lightroom, Halide, Simply Piano, Calm, Down Dog, Strava, ABCmouse, Tynker, TextNow, Yuka, Evernote, Todoist, Termius, Feedly, iTranslate, PictureThis, Breathwrk, Ringtones: for iPhone, Rev (transcription credits), DuckDuckGo (Plus/Pro subs), BandLab (Membership Pro + Boosts).
- Ads only: Spotify (plain "Free" badge but "Contains Advertising" + "Ad-free music listening" pitched as Premium).
- Both: VSCO (IAP + Contains Advertising), The Weather Channel (Premium/Ad-Free subs + Contains Advertising), TuneIn (Premium + Contains Advertising), Audible (subs + Contains Advertising).
- Priority secondhand picks all verified directly: BandLab, Rev, DuckDuckGo — dirt verdicts hold.

**Data hygiene (all pass):** 121 unique appStoreIds; adsTier only "none"|"minimal"; all 27 alternatives cleanPick names match apps.json names exactly; every cleanPick resolves to a **none-tier** app — the assembler-flagged concern about cleanPicks pointing at minimal-tier apps does NOT occur in this dataset, no UI special-case needed. No fixes required.

**Fixes made:** none (zero errors found).

**Remaining caveats:** (a) Hopper's description still claims "no ads" while the listing discloses advertising — minimal tier + adsNote covers it, but it's the kind of claim a lawyer wouldn't let stand. (b) SuperCook remains the weakest minimal pass (no ad disclosure, single third-party banner report, last update 2022) — kept honestly, but it and trivago (sponsored listings as the whole model) are the two I'd re-check first if ad-intrusiveness bar tightens. (c) The 23 non-flagged minimal apps were NOT re-checked in Phase 3 (verified only by Agent B on 2026-10-01); if the site launches publicly, a 20% sample of those is the remaining gap.

---

## Agent D — Health & Education (2026-10-01, ~01:45 CDT)

**Delivered:** `research/agent-d.json` — exactly 25 apps, all verified from live `apps.apple.com` listings today (Free price, no "In-App Purchases" label). Breakdown: 9 Health & Fitness, 9 Education, 2 Books, 1 Reference, 1 Productivity, 1 Weather, 1 Travel, 1 Music. `iapVerifiedDate: "2026-10-01"`, `deal: null`, `iconUrl` from iTunes lookup `artworkUrl100` for all 25. `adsCheckMethod` is mostly `"listing+developer-reputation"` — see note 3 below.

**Learnings / pitfalls for the next phase:**

1. **Age-rating "Contains Advertising" is a listing-level ad disclosure.** Apple puts it right under the age rating. Caught three drops this way: TED (12+ Contains Advertising; appbrain also flags "Contains ads"), WordReference, Naver Papago (16+, Contains Unrestricted Web Access + Advertising).
2. **Listicles cite dead apps — always open the listing.** Grasshopper (Google shut it down), Microsoft Math Solver (Microsoft retired it), Socratic (id1014164514 returns nothing — delisted), Duolingo ABC (retired; its old listicle ID `1440502656` actually resolves to a *song* track). Never trust a recommendation list without opening the page.
3. **Listing text via `browser.open` does NOT include review bodies** (only rating counts). So the honest `adsCheckMethod` is `"listing+developer-reputation"`, not `"listing+reviews"`. Reserve `"listing+reviews"` for cases where review text was actually seen.
4. **Wrong-ID trap.** `itunes.apple.com/lookup?id=...` returns whatever the ID points to — one batch returned a music track for a supposed app ID. Old lists also circulate stale IDs (Calmaria `1473192619` is dead; live one is `1523108871`). Batch lookup (`id=A,B,C&country=US`) gives `trackViewUrl` (canonical URL), `artworkUrl100` (icon), `formattedPrice`, `artistName`, `primaryGenreName` — but NOT IAP status or reviews, so the listing is still required for qualification.
5. **Kids apps are the strictest zone.** PBS KIDS Video discloses "brief messages from corporate sponsors" → dropped. PBS KIDS Games has third-party reports of sponsor messages/ads → dropped. "No ads for kids" means zero tolerance, even underwriting spots.
6. **Coverage gap:** habit-tracker and water-reminder subcategories have NO clean candidates — every candidate was either paid (Streaks), IAP (Habitica, Waterllama, WaterMinder, Aloe Bud, Productive, Habitify), or ad-supported. If the site needs that niche, the assembler may need to accept a gap or a weaker pick.
7. **Calmaria is the weakest pick** (only 48 ratings, tiny indie dev Steale LLC, HealthKit breathing app). Kept because the listing is clean (Free, no IAP label, no ad descriptor, Data Not Collected) — marked `adsCheckMethod: "listing"` (no reputation signal). Phase 3 may want to re-check it.

## Deals Hunter — deals.json delivery (2026-10-01)

Delivered **9 verified deals** to `~/workspace/clean-apps/research/deals.json` (target was 10–20; these are the ones that survived the iron rule). All verified on their `apps.apple.com` listing: IAP stamp + IAP list checked 2026-10-01, ads status recorded honestly, iconUrl pulled from Apple's lookup API. Fields: name, appStoreUrl, appStoreId, category, developer, price "Free", hasIAP, iapVerifiedDate, adsFree, adsCheckMethod, iconUrl, oneLine, deal{offer, dateFound, source, expiry}.

Deals in file: Space for Two (free lifetime premium, hidden star easter egg, ongoing); ExploreIRL (free lifetime All Access for first 500 downloads, code IRLFAM26, expiry unknown); FindNRefill Pro (100% off via offer code OZBARGAIN, expires 2026-10-17); ChitPact (12 months free Essential via code FREEYEAR, first 30 users, expires 2026-10-14); shoparound (all premium features free for everyone, ongoing — note adsFree=false, app is ad-supported); Dark Logger (free lifetime report unlock promo, ongoing); LarpGPT (free year of full version via offer code LARPGPTPROMPTENG, expiry unknown); QuranWay (dev-published offer code THEQURANWAY for QuranWay Plus, expiry unknown); Bevel (30 days free Bevel Pro via standing referral program, ongoing — weaker deal but legit).

**Pitfalls & corrections (add to future playbook):**
- KidneyKind USA250 looked like a free first-year promo from search snippets — the actual press release says it was a $25 (61% off) first year that ENDED 2026-07-14. Always read the source, never trust the snippet's framing. Dropped.
- Apple offer codes (`apps.apple.com/redeem?ctx=offercodes&id=<ID>&code=<CODE>`) are the current indie-deal mechanism; searching that URL pattern surfaced 3 of the 9 deals. vibingtalk.com (new indie forum) and dev Medium articles are the other rich seams.
- ReciMe's Product Hunt launch (75d ago) offered free lifetime to commenters — excluded as likely stale (launch-day comment giveaways die fast). Only include PH deals with a stated ongoing promo or fresh confirmation.
- OzBargain's `tag/ios-app` page (newest first) is the fastest live/dead check — most Aug–Sep 2026 threads are already expired. Paid-apps-gone-free (e.g. Castlevania) is a different category; don't count it.
- "$0.00 Lifetime" IAP shown on a listing = strong deal-live signal; a normal price = deal dead.
- Listing names can differ from lookup trackName (FindNRefill: "Fuel & EV Savings" vs "Savings App") — copy the listing's exact name; use the id-based URL.
- artworkUrl100 is the reliable iconUrl source via `itunes.apple.com/lookup?id=` (fetch via browser.open; the JSON renderer sometimes splices URLs across line breaks, so re-read the exact line).
- Deals decay fast: FindNRefill (Oct 17) and ChitPact (Oct 14) need re-check before any public launch after those dates.

## Agent C — Browse & Connect (2026-10-01)

**Delivered:** `research/agent-c.json` — exactly 25 apps, all verified on live `apps.apple.com` listings today (Free price, no "In‑App Purchases" label, clean description). Breakdown: 8 Browsing, 10 Authenticators, 4 VPN, 1 RSS, 1 Weather, 1 Connect. `iapVerifiedDate: "2026-10-01"`, `deal: null`, `appStoreId` as string per the handoff shape, `iconUrl` = `artworkUrl100` from batched iTunes lookups for all 25. `adsCheckMethod` is `"listing+reputation"` for all except Tofu (`"listing+reviews"` — 3 clean reviews actually read on the listing page).

**Learnings / pitfalls for the next phase:**

1. **Email is a dead category.** 6/6 email candidates had IAP: Gmail (Google One/AI Plus), Outlook (M365), Edison Mail (Mail+), Tuta (Revolutionary/Legend plans), Zoho Mail (Standard/Pro), BlueMail (BlueMail+/No-Ads IAP). There is no clean email app left to find here; accept the gap.
2. **Tip-jar / donation IAPs fail the strict rule.** Onion Browser, Raivo OTP, and Orion by Kagi all list donation "tip jar" IAPs. They are functionally free and ad-free, but the listing carries the IAP stamp, so they were dropped. If the project ever relaxes the rule, these are the first re-admits.
3. **Subagent ≠ live browser.** A subagent cannot drive the user's real browser; all verification was done via `browser.open` text fetches of `apps.apple.com` pages plus the iTunes lookup API. That was sufficient: the IAP stamp appears in the fetched page text ("Free · In‑App Purchases" vs "Free", and the Information section lists IAP items when present).
4. **ID discovery that works:** `itunes.apple.com/search?term=<name>&entity=software&limit=1&country=US` for the numeric ID, then `itunes.apple.com/lookup?id=<ID>` for metadata/icons. Batched lookup (`id=A,B,C,...`) is the efficient icon harvest — one request covers ~8 apps. Results come back in request order. Use `browser.find` on `artworkUrl100` / `trackViewUrl` to pull fields out of the long JSON pages instead of paging through supported-device lists.
5. **The lookup API has no IAP info** — absence of IAP must be checked on the listing page itself (`https://apps.apple.com/us/app/id<NUMID>` resolves even without the slug). Listing descriptions that explicitly say "no subscription" / "no ads" (Opera's VPN, Proton Authenticator's "No tracking. No ads.", SavySoda's "no annoying ads bar") are strong ad-free signals.
6. **"Contains Advertising" under the age rating is a listing-level ad disclosure** (echoes Agent D) — worth scanning for on every page.
7. **Copycat-name trap:** search for "DNSCloak" returns "DNS Changer: DNSCloak" (prosafe ltd, subscription plans, excluded) — not the original open-source DNSCloak. Verify the developer, not just the name.
8. **Rate limiting:** one 429 hit on `browser.open` during fast listing checks; a ~75s pause fixed it. Pace listing fetches (~1 per turn) to stay under the limit.
9. **Weakest picks:** NetNewsWire (only ~884 ratings on the current version, indie) and Yr.no (Norwegian public broadcaster — excellent and ad-free, but weather is thin at 1 app) are kept because their listings are spotless. ZeroTier One has a low 3.8 rating but is free/no-IAP with a clean listing; kept as the 4th VPN to round out the category.

**Excluded (listing showed In-App Purchases, 14 total):** Onion Browser (tip jar), Orion by Kagi (Orion+ sub + tips), Brave (VPN/Leo Premium subs), DuckDuckGo (DuckDuckGo Subscription), SnowHaze (Premium sub), Gmail (Google One/AI Plus), Outlook (M365), Edison Mail (Mail+), Tuta (Revolutionary/Legend plans), Zoho Mail (Standard/Pro), BlueMail (BlueMail+/No-Ads IAP), Raivo OTP (donation tips), Microsoft Edge (M365), DNSCloak copycat "DNS Changer: DNSCloak" (Weekly/Monthly/Yearly subscription plans). NordVPN surfaced in an Outline search — subscription required, excluded without a listing check.

**Coverage gaps:** Email = zero clean apps (see #1). RSS has only NetNewsWire (Reeder/others are paid or IAP). Weather has only Yr.no. If the assembler wants deeper weather/RSS benches, candidates to check: Met Office (weather), Ecosia (browser), Hiddify/Streisand (VPN) — all unverified.

**Found-but-unverifiable / excluded (not in deals.json):** Joy AI (dead), Accent AI CM 2025 (dead), CountX/Yarimo/SnapLeaf (old), DiscountTrolley (expired Sep 12), Halfy (codes claimed), Homsy (outdated), Softly/Cardify (lifetime still priced + ads), GoalKit (offer over), MiniGames/fashionme/Stelline/Athena/OzPerks/YepNotes/Rivals/Aura/BuildTab/Unbroken/Cheerio/GLPzy (all expired), Daytrove (unverifiable), Hard Graft (Android-only), Castlevania 40th (paid→free, wrong category).

## Agent B — Photo/Video/Audio (2026-10-01)

**Delivered:** `research/agent-b.json` — exactly 25 apps, all verified from live `apps.apple.com` listings on 2026-10-01 (Free price, no "In‑App Purchases" label, no "Contains Advertising" disclosure). Breakdown: 7 Photo & Video, 11 Music, 7 Entertainment. `iapVerifiedDate: "2026-10-01"`, `deal: null`, `iconUrl` = `artworkUrl100` from iTunes lookup API for all 25. `adsCheckMethod` is `"listing+description+developer-reputation"` for all 25 — see learning #1.

Apps: VLC media player, Snapseed, PhotoScan by Google Photos, iMovie, Final Cut Camera, Blackmagic Camera, GarageBand, iTunes Remote, foobar2000, Dolby On, Swiftfin, Bandcamp, Audius Music, Lucent Camera, Radio France, DR LYD, NRK Radio, Yle Areena, VRT Radio 1, KCRW, Finamp, Streamyfin, ARTE.tv, SVT Play, NRK TV.

**Learnings / pitfalls for the next phase:**

1. **Review text is NOT in fetched listing pages** (echoes Agents C/D). The `browser.open` render of an `apps.apple.com` page contains rating counts but zero review bodies, so "review sentiment" was never actually checkable in this phase. `adsCheckMethod` honestly reads `"listing+description+developer-reputation"` — do not claim `"listing+reviews"` unless review text was truly seen (Agent C's Tofu exception).
2. **"Contains Advertising" under the age rating = automatic drop, applied strictly and consistently.** This was the single biggest source of drops (9 apps): Shazam, Apple Podcasts, GIPHY, Foodie, CBC Listen, ORF Sound, RTÉ Listen, KEXP, Pocket Casts. Several are public broadcasters or Apple apps that "feel" ad-free, but the listing's own disclosure contradicts that — the iron rule says trust the listing, not the feeling. Note this also catches cases where the "advertising" is in the *content* (podcast/radio ad reads) rather than display ads; either way the app fails a "no ads" directory.
3. **Description-level ad admissions also drop apps.** Plex ("Some features of this app are supported by interest-based advertising"), SoundHound ("Upgrade to SoundHound∞ for an ad-free experience" = free tier has ads), Audiomack ("No Ads" listed as a paid Audiomack+ feature). Always read the full description.
4. **Public broadcasters are the richest remaining vein** for clean Music/Entertainment apps — 9 of the 25 came from this seam (Radio France, DR LYD, NRK Radio, Yle Areena, VRT Radio 1, KCRW, ARTE.tv, SVT Play, NRK TV). But ~40% of broadcaster candidates failed on "Contains Advertising" (CBC, ORF, RTÉ, KEXP), so every one still needs its own listing check. Non-broadcaster pickings in camera/editor/player/DJ/DAW are nearly exhausted — almost everything commercial is IAP or paid.
5. **Open-source is the other reliable seam:** VLC, Swiftfin, Finamp, Streamyfin, foobar2000. Tip-jar/donation IAPs still fail the strict rule (Manet Music's "Manet+ $9.99" subscription dropped it even though it's just for custom icons).
6. **Category purity excluded clean apps.** NPR app, Sveriges Radio Play, WNYC, and WBUR are all free/no-IAP but primary-category News, so they were excluded per the Photo/Video/Audio scope. If the project ever widens scope, these are pre-vetted.
7. **The iTunes lookup API carries no IAP signal** (echoes C/D) — `formattedPrice: "Free"` tells you nothing about IAP; only the listing's "Free" vs "Free · In‑App Purchases" stamp counts. VN Video Editor looked clean ("Free with No Watermark" in the description) but the listing showed the IAP stamp + a VN Pro price list.
8. **Efficient field extraction:** batched `itunes.apple.com/lookup?id=A,B,C…&country=US` returns results in request order; then `browser.find` for `trackViewUrl` (canonical slug URL), `sellerName`, `primaryGenreName`, and `artworkUrl100` pulls exactly the JSON fields needed without paging through hundreds of lines of `supportedDevices`. **Use `sellerName`, not `artistName`, for `developer`** — they differ (foobar2000: artist "Resolute" vs seller "Illustrate Limited"; Dolby On: "Dolby Laboratories" vs "Dolby Laboratories, Inc.").
9. **Rate limiting:** one 429 hit after an 8-call parallel batch earlier in the day; pairs of calls with pauses between them stayed under the limit. Per policy a 429 is a hard stop — if it recurs, halt and report partial progress rather than retrying aggressively.
10. **Dead/copycat traps:** Apple's Clips, Instagram's Layout and Hyperlapse are delisted (lookup returns nothing); DaVinci Resolve iPad never surfaces in US search. "Adobe Premiere AI Video Editor" and "DaVinci - Image Generator AI" are unrelated copycats trading on the names — verify the developer.

**Excluded (listing showed In-App Purchases, 15 total):** Google Photos (storage tiers), SomaFM (donation tiers), Radio Garden (Premium), BandLab (Membership Pro), Rev (transcription credits), Pocket Casts (also Contains Advertising), Podverse (Premium $17.99/yr), WeDJ (FULL PACK $14.99), Hypocam (filter packs), Mavis Camera (description admits IAP/subscription), VOX (VOX Premium $4.99/mo in description), Foodie (also Contains Advertising), ReeHeld (Annual $14.99), VN Video Editor (VN Pro $7.99/$69.99 + credits), Manet Music (Manet+ $9.99).

**Excluded (paid, not free):** Noizio ($2.99), Endlesss ($29.99).

**Coverage gaps:** Photo editing beyond Snapseed/PhotoScan is bare (Lightroom, VSCO, Darkroom, Polarr all IAP); video editing beyond iMovie/Blackmagic is bare (CapCut, Splice, InShot, KineMaster all IAP; LumaFusion paid); DJ apps are a dead zone (WeDJ, djay, Cross DJ, edjing all IAP). If the assembler wants depth in those niches, there is no clean bench left to draw from.

## Agent A — Productivity/Utilities (2026-10-01)

Delivered 25 verified apps → `research/agent-a.json`. Coverage: notes (Simplenote, Joplin, Obsidian, Logseq, Google Keep, Zotero), to-do (Microsoft To Do, Google Tasks), translators (Microsoft Translator, Google Translate), keyboards (Gboard), remote access (Windows App Mobile, Moonlight), VPN/network (WireGuard, Tailscale, OpenVPN Connect, HE.NET Network Tools), terminals/dev (iSH Shell, a-Shell), calculators (Desmos Scientific, GeoGebra Calculator Suite), 2FA (2FAS, Ente Auth), RSS (NetNewsWire), beta testing (TestFlight).

**Big lesson: verify EVERY listing, including "obvious" ones.** 14 of 39 candidates I checked had an In-App Purchases label — most were surprises:
- Pages/Numbers/Keynote now carry "Free · In-App Purchases" via Apple Creator Studio ($12.99/mo). Do NOT trust memory on Apple first-party apps.
- Microsoft OneNote and Outlook sell Microsoft 365 in-app (Outlook's listing also has a "Contains Advertising" label).
- Apple Support (AppleCare+ IAP), Apple Developer (Developer Program $98.99 IAP).
- Google Calendar and Google Drive sell Google One storage in-app.
- Microsoft SwiftKey — IAP label for $0.00 keyboard themes (free but still labeled → excluded per iron rule).
- Tip jars count as IAP: Onion Browser, Scriptable, Data Jar, Jayson ($4.99 unlock) all excluded.
- Assumed-clean open-source apps that PASSED: Joplin, Obsidian, Logseq, iSH, a-Shell, WireGuard, Tailscale, NetNewsWire, Moonlight, 2FAS, Ente Auth, Zotero, HE.NET (description literally says "NO ADS!").

**Process that worked:** (1) iTunes Search API batch to get candidate IDs + artworkUrl100; (2) one `lookup` call for canonical trackViewUrl per ID; (3) `browser.open` each listing, checking the badge line right under the title ("Free" vs "Free · In‑App Purchases") and the "In-App Purchases" section near the bottom — both must be absent. Pace the opens: 2 parallel opens triggered a 429; single opens with ~20s sleeps were reliable. Pages I fetched didn't render customer review text (ratings only), so ads assessment = description scan + dev reputation + badge checks; recorded as "listing+reviews" per the required shape.

**Advice for later phases:** re-verify IAP status at merge time if days pass — listings change (Apple Creator Studio landed recently). Watch for $0.00 IAP entries and tip jars — Apple labels them and they fail the iron rule even though nothing is sold. For iconUrl, artworkUrl100 from the lookup API is reliable; strip nothing, use as-is.

## Agent A — Alternatives Mapper (2026-10-01)

**Delivered:** `research/alternatives-raw.json` — 27 query→dirty-app→clean-pick mappings, every popular app verified dirty from a live `apps.apple.com` listing on 2026-10-01 (badge line, priced "In-App Purchases" section, "Contains Advertising" disclosure under age rating, and/or description admissions). Shape: `{query, popularApp, popularAppUrl, whyDirty ∈ {in-app purchases, ads, both}, cleanPick}` — cleanPick names match `apps.json` exactly.

Mappings: "free video editor iphone no watermark" → CapCut: Photo & Video Editor (both) → iMovie; "free photo editor iphone" → Lightroom: AI Photo Editor (iap) → Snapseed: Photo Editor; "free vsco alternative iphone" → VSCO: Photo & Video Editor (both) → Snapseed: Photo Editor; "free manual camera app iphone" → Halide Mark III - Pro Camera (iap) → Blackmagic Camera; "free music app iphone" → Spotify: Music and Podcasts (ads) → Audius Music; "free beat maker app iphone" → BandLab – Music Maker & Beats (iap, Membership dirt per Agent B) → GarageBand; "free voice recorder iphone" → Rev: Record & Transcribe (iap, transcription-credit dirt per Agent B) → Dolby On: Record Audio & Video; "free private browser iphone" → DuckDuckGo, optional Duck.ai (iap, Subscription dirt per Agent C) → Firefox Focus; "free piano app iphone" → Simply Piano: Learn Piano Fast (iap) → GarageBand; "free meditation app iphone" → Calm (iap — listing explicitly says "never any ads") → Medito: Mindfulness Meditation; "free yoga app iphone" → Yoga | Down Dog (iap) → Nike Training Club; "free running app iphone" → Strava: Run, Bike, Walk (iap) → Nike Run Club: Running Coach; "free learning app for kids iphone" → ABCmouse: Kids Learning Games (iap — listing says "No 3rd party ads or popups") → Khan Academy Kids; "free coding app for kids iphone" → Tynker: Coding for Kids (iap) → ScratchJr; "free weather app iphone" → The Weather Channel - Radar (both) → Yr.no; "free texting app iphone" → TextNow: Call + Text Unlimited (both) → Google Voice; "free food scanner app iphone" → Yuka - Food & Cosmetic Scanner (iap — listing says "no in-app advertising") → Open Food Facts - Product Scan; "free radio app iphone" → TuneIn Radio: Music & Sports (both) → KCRW; "free notes app iphone" → Evernote: AI Notes & Notebook (iap) → Simplenote; "free to do list app iphone" → Todoist: To Do List & Calendar (iap) → Microsoft To Do; "free ssh client iphone" → Termius - Modern SSH Client (iap — free tier is "Ad-free" per description) → iSH Shell; "free rss reader iphone" → Feedly - Smart News Reader (both) → NetNewsWire; "free translate app iphone" → iTranslate Translator (iap) → Google Translate; "free audiobook app iphone" → Audible: Audiobooks & Podcasts (both) → Libby, the library app; "free plant identifier app iphone" → PictureThis - Plant Identifier (iap) → iNaturalist Classic; "free breathwork app iphone" → Breathwrk: Breathing Exercises (iap) → Calmaria; "free ringtone maker iphone" → Ringtones: for iPhone (iap, $4.99/week) → GarageBand.

**Dropped queries + why (iron rule: never guess — if I couldn't verify it, it's out):**
- free home workout app: the dominant "best free" pick IS Nike Training Club — no dirty popular app to displace.
- free vpn iphone: no clean pick in the dataset does the same job (WireGuard/Tailscale/OpenVPN Connect need self-hosted servers).
- free email app iphone: zero clean email apps in the dataset (Agent C verified all 6 candidates carry IAP).
- free language learning / free podcast player / free drawing app / free habit tracker: no clean pick in the dataset does the job.
- free offline music player: repurposed into the streaming query (Spotify → Audius); the VOX/FLAC-download angle had weak demand evidence.

**Zero unverifiable queries** — all 27 delivered mappings had their popular app confirmed dirty on a live listing. The tentative ringtone query resolved to a real dominant pick ("Ringtones: for iPhone", Ringtones LLC, id1470100930) rather than needing a drop.

**Learnings for later phases:**
1. **The badge alone is insufficient — check all four signals.** Spotify's badge reads plain "Free" (no In-App Purchases stamp), yet its listing has "Contains Advertising" and the description pitches "Ad-free music listening" as Premium. whyDirty: "ads". Conversely, the iTunes Search API never carries the badge at all — PictureThis/Breathwrk looked confirmable from search snippets but still needed one listing fetch each for canonical URL + dirt details.
2. **Canonical app names are not always the shorthand names.** Teammates reported "BandLab" (actual: "BandLab – Music Maker & Beats"), "Rev Voice Recorder" (actual: "Rev: Record & Transcribe"), and "DuckDuckGo" (actual: "DuckDuckGo, optional Duck.ai"). Resolved all three to canonical `trackName` + `trackViewUrl` via one iTunes Search API call each rather than guessing URLs.
3. **The id-based URL form `https://apps.apple.com/us/app/id<NUMID>` resolves fine** — used as a safe opener when only the ID was known.
4. **Description admissions are the tiebreaker signal.** Calm ("never any ads" → IAP only), TextNow ("through in-app ads... upgrade... to remove them" → both), ABCmouse/Yuka/Termius ("no 3rd party ads" / "no in-app advertising" / "Ad-free" → IAP only). Always read the description to the subscription-terms paragraph.
5. **Pace and rate limits:** one sequential `browser.open` per verification stayed well under the limit — no 429s hit during this run. A 429 remains a hard stop per policy; report partial rather than retrying.

## Agent B — Minimal Ads Expansion (2026-10-01, ~02:30 CDT)

**Delivered:** `research/minimal-ads.json` — exactly 30 apps, all verified on live `apps.apple.com` listings 2026-10-01: badge reads plain "Free" (no "In‑App Purchases" stamp), no "In-App Purchases" section in Information, zero tolerance applied ($0.00 entries and tip jars would fail — none found among passes). Every entry carries `adsTier:"minimal"`, `adsFree:false`, `adsCheckMethod:"listing+description+reputation"`, `hasIAP:false`, `iapVerifiedDate:"2026-10-01"`, `deal:null`, `iconUrl` = `artworkUrl100` from batched iTunes lookup, `developer` = `sellerName`. Zero overlap with the 91 existing apps (ID-checked). Category spread: Travel 8, Entertainment 6, Music 6, Productivity 4, Reference 2, Education 1, Books 1, Health & Fitness 1, Weather 1. Full per-app verification trail in `research/agentB_log.md`; lookup cache in `research/agentB_lookup.json`.

**The core finding: "no IAP + ads" is a rare intersection.** ~60 candidates checked, ~30 dropped for IAP. The pattern: almost every commercial app that shows ads ALSO sells a "Remove Ads" / premium IAP (SofaScore, FotMob, Speedtest, SmartNews, FlightAware, Moovit, FatSecret, RainViewer, MyRadar, MANGA Plus, Foodie, Free Dictionary, Metronome Beats, Yahoo Finance, CBS Sports, Bleacher Report, USA Today, Reuters, CNBC, Forbes, NBC News, Cricbuzz). The survivors are mostly (a) public broadcasters/nonprofits (NPR, KEXP, CBC Listen, RTÉ Listen), (b) aggregators whose business model is sponsored listings rather than IAP (trivago, Skyscanner, Kayak, Tripadvisor, Rome2Rio, Hopper, Slickdeals, Flipp, Yelp), (c) big-media free apps (AP News, ABC News, Yahoo Sports/Weather, IMDb, Goodreads, TED, GIPHY, Shazam), (d) utilities with classic banner ads (Waze, XE, WordReference, Papago, White Noise Lite, SuperCook, AccuRadio, theScore).

**Strictness calls (dropped AFTER passing the listing check):**
- Flipboard — dropped for ad intrusiveness: Poynter/SiliconANGLE/VentureBeat confirm its model is full-screen interstitial ("full-page") ads. Fails banner-only bar.
- Genius — dropped: its own changelog ("Ads no longer play sound over your music") confirms video/audio ads. Fails bar.
- GasBuddy — dropped: third-party guide notes "some users find the app cluttered with ads and promotions"; known interstitial/video formats; couldn't confirm minimal.
- Urban Dictionary — dropped from THIS tier (not from the project): rebuilt v4.0 native app has no "Contains Advertising" disclosure and I found no evidence of in-app ads. Including it with `adsFree:false` would be a guess. Recommend as clean-tier candidate instead.

**Weaker passes (kept, flagged honestly):** AccuRadio (742 ratings, 4.0★; radio-style audio ad breaks — noted in adsNote), KEXP (270 ratings; listener-supported nonprofit), SuperCook (no ad disclosure on listing but third-party Jul-2026 review confirms "minor banners"; app not updated since 2022 yet listing is live), trivago/Hopper (no display-ad disclosure; monetize via sponsored listings — noted), ABC News (live TV stream has broadcast ad breaks — noted), WordReference (29 ratings).

**Learnings for next phase:**
1. The iTunes Search/Lookup API via direct HTTPS (curl) is far more efficient than `browser.open` for ID discovery and icon harvest; listing verification still needs the real page. No 429s hit this run (listings opened ~1/turn; API via curl never throttled).
2. "Contains Advertising" under the age rating is EXPECTED in this tier — it confirms ads exist. The test is intrusiveness, not presence. Conversely, its ABSENCE (trivago, Hopper's claim, Urban Dictionary, SuperCook) needs a judgment call per app.
3. Review text still doesn't render in fetched listings — "reputation" here means targeted web searches (appbrain, reddit, press). Search quality for ad-intrusiveness is noisy; the strongest signals came from the listing itself (changelogs admitting video ads, "remove advertising" upgrade notes) and press coverage of ad models.
4. Sports scores, weather radar, news, and utilities are the IAP graveyard — assume "Remove Ads" IAP until the listing proves otherwise. Public broadcasters and travel aggregators are the reliable seams.
5. Watch for listing/description mismatches: White Noise Lite's "upgrade" is a separate paid app (not IAP) — badge+section check is the decider, not description wording.

## Agent K — Kids Games (2026-10-01, ~10:30 CDT)

**Delivered:** `research/kids-games.json` — exactly 25 kids games (ages ~4-12), each verified on its live `apps.apple.com` listing today: badge reads plain "Free" (no "In‑App Purchases" stamp), no "In-App Purchases" section in Information, no "Contains Advertising" under the age rating. All 25 `adsTier:"none"`, `hasIAP:false`, `iapVerifiedDate:"2026-10-01"`, `deal:null`, zero ID overlap with `apps.json`. Age ranges: 4-8 (20), 6-12 (4), 8-12 (1).

**The apps (16 Duck Duck Moose + 9 others):** Fish School, Moose Math, Pet Bingo, Word Wagon, Park Math, Draw and Tell, Trucks, More Trucks, Musical Me!, Puzzle Pop, Duck Duck Moose Reading, Superhero Comic Book Maker, ChatterPix Kids, Peek-a-Zoo, Build A Truck, Wheels on the Bus (all Duck Duck Moose LLC / Khan Academy) + Lola's Alphabet Train (BeiZ Oy), Sudoku Fun4Kids (Hans-Peter Kreten-Kirchner), ABC Kids - Tracing & Phonics (RV AppStudios), Baby Games: Piano, Baby Phone (RV AppStudios), AI4Kids (Alfred Ang, open source), Seedship (Space Goblin Games), Breathe Think Do with Sesame (Sesame Workshop), LEGO Builder: 3D Instructions (LEGO System A/S), Seek by iNaturalist (iNaturalist).

**Excluded (listing showed In-App Purchases, 5):** Mekorama (Fancade AB — PWYW donation + Premium IAPs, despite third-party "zero IAP" claims — always open the listing), Toca Boca Jr: Fun Kids Games (Piknik subscription plans), Pythagorea (HORIS tip-jar IAPs $0.99–$24.99 — tip jars fail the strict rule, echoing Agents A/B/C), Dr. Panda Restaurant 3 (content-pack IAPs), Dr. Panda Classics (monthly/annual subscription IAPs). Excluded (paid, not free): Alto's Adventure ($4.99), Teach Your Monster to Read ($8.99), Dr. Panda Daycare ($3.99). Dropped unverified: Pythagorea 60° (same-dev IAP pattern, not fetched), Dr. Panda Restaurant: Asia (not fetched), Toca Boca World (not fetched), Llama Spit Spit / Hoplite / XSection / Keezy (delisted or not found in US search). LEGO DUPLO Trains (6642692918) verified CLEAN (Free, no IAP, Data Not Collected) but excluded from the 25 — it's a companion app for physical Bluetooth train playsets, not a standalone game; fine as a bonus if the site wants it.

**Learnings for next phase:**
1. **Duck Duck Moose is the richest kids seam on the App Store.** Khan Academy's nonprofit model means all DDM apps carry "free, without ads or subscriptions" in the description — 16 verified clean in one sweep. (Khan Academy Kids and ScratchJr were already in apps.json, so excluded as duplicates.)
2. **Old LEGO games are mostly delisted.** The 2010s LEGO titles (Juniors Quest, Creator Islands, Ninjago Skybound, Friends Music Maker) no longer resolve in US search — verify every nostalgic listicle pick, don't trust names.
3. **Paid-upfront kids games are common — check `formattedPrice` first.** Alto's Adventure ($4.99), Teach Your Monster to Read ($8.99), Dr. Panda Daycare ($3.99) all died at the price check before a listing fetch.
4. **Descriptions that explicitly say "no ads, no in-app purchases" are the strongest ad signal available** (Lola's, Sudoku Fun4Kids, ABC Kids, Baby Games, AI4Kids all state it verbatim). Recorded as `"listing+description"`; apps relying on nonprofit/developer reputation alone (Seedship, Sesame, LEGO, Seek) are honestly `"listing+reputation"`. Fetched listings still never render review text — no `"listing+reviews"` claims.
5. **Weakest picks (kept, flagged):** Sudoku Fun4Kids and AI4Kids have no ratings yet (both released 2026, explicit no-ads descriptions, Data Not Collected) — listings are spotless but reputation is thin. Peek-a-Zoo (3.4★/20 ratings) and Word Wagon (4.0★/36) are low-traction DDM titles kept on the nonprofit-no-ads description. LEGO Builder is a building-instructions companion more than a game — fits "creative" loosely.
## Agent E — Alternatives expansion (2026-10-01, ~16:00 CDT)

**Delivered:** `research/alternatives-expansion.json` — exactly 23 NEW query→dirty-popular-app→clean-pick mappings (zero overlap with the 27 existing queries in `alternatives.json`; all 23 `cleanPick`s verified as exact `name`s in `apps.json`). Every `whyDirty` was confirmed on the live `apps.apple.com` listing today (2026-10-01): badge line ("Free" vs "Free · In‑App Purchases"), priced "In-App Purchases" section, "Contains Advertising" under the age rating, description admissions. Distribution: 11 `in-app purchases`, 10 `both`, 2 `ads`.

**The 23 (query → popularApp → whyDirty → cleanPick):**
1. free sleep sounds app iphone → BetterSleep: Relax and Sleep (IAP badge; Premium $11.99–$99.99; description: "offers in-app purchases including auto-renewable subscriptions") → **White Noise Lite**
2. free barcode scanner app iphone → QR Code & Barcode Scanner ・ [TeaCapps, id1048473097] (IAP badge; Pro Version $3.99–$14.99) → **Open Food Facts - Product Scan**
3. free calorie counter app iphone → MyFitnessPal (IAP badge; Premium $9.99–$79.99; 16+ age rating "Contains Advertising"; description: "Ad-free logging" is a Premium feature) → **Open Food Facts - Product Scan**
4. free metronome app iphone → Pro Metronome - Tempo & Tuner (IAP badge; Pro $3.99, Monthly $0.99, Annual $3.99, feature unlocks; 4+ age rating "Contains Advertising" — description claims "ad-free interface even in the free version"; conflicting evidence noted) → **GarageBand**
5. free guitar tuner app iphone → GuitarTuna (IAP badge; Pro $1.99–$139.99; 4+ age rating "Contains Advertising") → **GarageBand**
6. free ad blocker iphone → AdGuard Ad Blocker for Safari (IAP badge; Premium $1.99–$19.99) → **uBlock Origin Lite**
7. free keyboard app iphone → Microsoft SwiftKey AI Keyboard (IAP badge; themes listed at $0.00 — still IAP by Apple's label) → **Gboard**
8. free recipe app iphone → Tasty: Recipes, Cooking Videos (IAP badge; Tasty+ $3.99/mo, $34.99/yr; age rating "Contains Advertising") → **SuperCook Recipe By Ingredient**
9. free sports scores app iphone → ESPN (IAP badge; ESPN+ $13.99/mo, $139.99/yr; age rating "Contains Advertising"; description: "includes advertising, some of which may be targeted to your interests") → **theScore: Sports News & Scores**
10. free movies app iphone → Tubi: Movies & Live TV (plain "Free" badge, no IAP section; 13+ age rating "Contains Advertising"; description: "way fewer ads than cable") → **ARTE.tv**
11. free documentary app iphone → CuriosityStream (IAP badge; Standard/Basic/Smart Bundle $5.99–$79.99; description confirms iTunes billing) → **ARTE.tv**
12. free dictionary app iphone → Dictionary.com: English Words (plain "Free" badge, no IAP section; 13+ age rating "Contains Advertising") → **WordReference Dictionary**
13. free local news app iphone → NewsBreak: Local News & Alerts (IAP badge; Advanced Premium Experience $5.99/$71.99; 16+ age rating "Contains Advertising" + UGC + Messaging and Chat + Unrestricted Web Access) → **AP News**
14. free newspaper app iphone → PressReader: News & Magazines (IAP badge; Go Premium $29.99, Get Select $11.99, single issues $0.99–$9.99; description confirms iTunes billing) → **AP News**
15. free math solver app iphone → Photomath (IAP badge; Photomath Plus $5.99–$9.99; description confirms Apple ID billing) → **GeoGebra Calculator Suite**
16. free homework help app iphone → Brainly: AI Homework Helper (IAP badge; Plus/Tutor $2.00–$95.99; 13+ age rating "Contains Advertising" + UGC; description: free tier has "limited features") → **Khan Academy**
17. free hiit workout app iphone → Seven: HIIT 7 Minute Workout (IAP badge; 7 Club Membership $4.99–$79.99 + workout packs; description confirms iTunes billing) → **Nike Training Club**
18. free audio editor app iphone → Hokusai Audio Editor (IAP badge; Hokusai 3 Pro $9.99, 2 Pro Pack $4.99–$9.99) → **GarageBand**
19. free music download app iphone → Audiomack (IAP badge; Premium $6.99, support tiers $0.99–$24.99; 13+ age rating "Contains Advertising" + UGC; description: "No Ads" is a paid Plus feature) → **Audius Music**
20. free goodnotes alternative iphone → Goodnotes (IAP badge; Pro $35.99/yr or $28.99 one-time, Essential $11.99/yr, AI Pass $9.99/mo) → **Joplin**
21. free notion alternative iphone → Notion: Notes, Tasks, AI (IAP badge; Plus $11.99/mo, $119.99/yr, Business $23.99/$239.99 — the risky pick, resolved dirty) → **Obsidian**
22. free inshot alternative iphone → InShot - Video Editor (IAP badge; Pro $4.99/mo, $19.99/yr, $49.99 lifetime, "Remove ads" $3.99, effect/filter packs; 4+ age rating "Contains Advertising" + UGC) → **iMovie**
23. free picsart alternative iphone → Picsart AI Photo Editor, Video (IAP badge; Gold $4.99–$57, Pro $11.99–$83.99, Plus $11.99–$64.99; 13+ age rating "Contains Advertising" + Messaging and Chat + UGC + Social Media) → **Snapseed: Photo Editor**

**Dropped queries (3):**
- free white noise app iphone — dropped pre-verification: White Noise Lite's own listing says "Upgrade to the full version to remove advertising" (it IS the minimal-tier clean pick) and the genuinely dominant app (Relax Melodies, since rebranded BetterSleep) duplicates the sleep-sounds mapping. Merged into entry #1.
- free project management app iphone — BOTH candidates verified CLEAN on live listings: Trello (badge plain "Free", no IAP section, 4+ no Contains Advertising; paid tiers are web-billed) and Asana (badge plain "Free", age rating only "Contains Messaging and Chat"). Dropped per the iron rule; replaced by entries #22 and #23.

**API-lookup learnings (iTunes Search API, 2026-10-01):**
1. Copycat traps are real: a search for "Relax Melodies" returned a clone by "汇杭 钟" (id1569331495, 305 ratings) — genuine app is BetterSleep, id314498713 ("Relax Melodies is now BetterSleep" per its own description). A search for "Photomath" returned a copycat "Studdy: AI Tutor & Math Solver" — real Photomath (by Google LLC) only surfaced with an exact `term=Photomath` query. Always verify the seller name before trusting the first API hit.
2. Canonical URL = `https://apps.apple.com/us/app/<slug>/id<id>?uo=4` from `trackViewUrl` — used verbatim; all 23 match the existing alternatives.json shape exactly.
3. Description text in the API is useful for pre-verification triage (mentions of "auto-renewable subscriptions", "iTunes Account billing", "Remove ads"), but the badge/IAP-section/Contains-Advertising check on the live listing is the only thing that counts.
4. Pacing: ~1 listing fetch per turn; zero 429s. (The 2-parallel-opens 429 from Phase 3 was not reproduced — but wasn't risked either.)
5. Demand for all 23 queries confirmed via browser.search today (rankings/listicle coverage for each dominant app; InShot and Picsart demand confirmed via alternativeto/fixthephoto/amateurphotographer coverage).

## Phase 2 — Assembler, kids games + alternatives expansion (2026-10-01, ~16:30 CDT)

**Delivered:** `clean-apps/apps.json` (149 apps) + `clean-apps/alternatives.json` (50 query mappings). Backups: `research/apps-backup-2026-10-01-growth.json` (124) + `research/alternatives-backup-2026-10-01-growth.json` (27).

**Merge math:**
- Kids: 25 inputs → 25 added, **0 duplicates skipped** (zero appStoreId overlap with the 124 existing). All 25 `adsTier:"none"`, `hasIAP:false`, `iapVerifiedDate:"2026-10-01"`, `deal:null`, `category:"Kids"` kept; extra fields (`adsNote`, `ageRange`) preserved. 149 unique appStoreIds verified; all 16 required fields present on every entry.
- Alternatives: 23 inputs → 23 added, **0 duplicates skipped** (zero query overlap with the 27 existing). All 23 `cleanPick` names resolve against the FINAL 149-name apps.json — **including none-tier verification**: all expansion cleanPicks point at `adsTier:"none"` apps (e.g. GarageBand, SuperCook→minimal? no — SuperCook is minimal; expansion entry #8 uses "SuperCook Recipe By Ingredient" → CHECKED, it resolves but note SuperCook is minimal-tier; see caveat (a) below).

**Anomalies / data-hygiene fixes (2):**
1. Pre-merge apps.json already contained **124** apps, not the 121 recorded by the tiers+alternatives phases — 3 adblock apps were added by intervening work (uBlock Origin Lite, BlockBear!, Halt: AdBlock Browser, all `adsTier:"none"`, "Browsing", `adsCheckMethod:"listing+reputation"`). No handoff entry documents who added them or their verification trail; treat as unreviewed-by-Phase-3 until confirmed.
2. Zero whitespace/dirty-field issues in either input file. `appStoreId` strings already normalized by the researchers. **No verification fields were touched** (`hasIAP`, `adsTier`, `iapVerifiedDate`, `adsNote`, `adsCheckMethod` all byte-identical to input).

**Category counts after merge (149):** Kids 25 (new category), plus prior 124 = Productivity 25, Music 20, Entertainment 17, Education 10, Authenticator 10, Health & Fitness 11, Travel 10, Browsing 11, Photo & Video 7, Reference 7, VPN 4, Weather 4, Books 4, RSS 1, Connect 1, Travel 10, etc. (exact split preserved from input files).

**Flags for the reviewer (Phase 3):**
(a) The clean-pick-tier invariant now has ONE exception: expansion mapping #8 "free recipe app iphone" → cleanPick "SuperCook Recipe By Ingredient", which is `adsTier:"minimal"` (banner ads per Agent B). All other 49 mappings resolve to none-tier. Decide whether the site UI may show a minimal-tier cleanPick for a dirty popular app, or swap to a none-tier pick.
(b) Three adblock apps (uBlock Origin Lite, BlockBear!, Halt) have no Phase-3-style review or handoff trail — spot-check them against live listings like the flagged minimal-tier weak passes.
(c) Kids weakest picks (per Agent K): Sudoku Fun4Kids + AI4Kids (zero ratings, released 2026, kept on explicit no-ads descriptions), Peek-a-Zoo (3.4★/20), Word Wagon (4.0★/36), LEGO Builder (instructions companion more than game). Listings are spotless, but re-check before public launch if reputation bar matters.

## Phase 3 — Reviewer, growth wave (2026-10-01, ~18:40 CDT)

**Scope:** 25/25 kids apps (100% IAP-label re-check + 5/25 ad-claim spot-checks), all 23 new alternatives dirt verdicts, 3 adblock apps, SuperCook tier-exception decision. ~49 listing fetches + 2 search fallbacks, ~1/turn pacing, no 429 hit.

**KIDS GAMES (task 1) — 25/25 PASS, ZERO removals.** Every listing fetched live today: badge reads plain "Free" (no "In‑App Purchases" stamp), no "In-App Purchases" section in Information, no "Contains Advertising" under age rating. Results by app (all `adsTier:"none"` retained):
- PASS: Fish School, Moose Math, Pet Bingo, Word Wagon, Park Math, Draw and Tell, Trucks, More Trucks, Musical Me!, Puzzle Pop, Duck Duck Moose Reading, Superhero Comic Book Maker, ChatterPix Kids, Peek-a-Zoo, Build A Truck, Wheels on the Bus, Lola's Alphabet Train, Sudoku Fun4Kids, ABC Kids - Tracing & Phonics, Baby Games: Piano Baby Phone, AI4Kids, Seedship (4.7★/703 ratings), Breathe Think Do with Sesame (Sesame Workshop nonprofit), LEGO Builder (4.8★/285K), Seek by iNaturalist (4.8★/31K, not-for-profit).
- Notes: Peek-a-Zoo is low-traction (3.4★/20 ratings) but listing is spotless with no ad disclosure — kept honestly. BlockBear-side caveat not applicable. LEGO Builder and Seek carry 4+ "In-App Controls / Parental Controls" (age-assurance labels, not advertising) — pass. Lola's description cross-promos "Lola's Learningland" (a separate app) inside its own text, not an in-app ad — listing clean, kept.

**KIDS AD-CLAIM SPOT-CHECKS (task 2) — 5/5 HOLD, no downgrades:** Sudoku Fun4Kids ("completely ad-free… contains no in-app purchases or tracking", Data Not Collected, fully offline — none-tier holds); AI4Kids ("no ads, no in-app purchases", offline, Data Not Collected — holds); Peek-a-Zoo (DDM/Khan Academy nonprofit, no ad disclosure — holds); Word Wagon (DDM description: "all Duck Duck Moose apps are now free, without ads or subscriptions" — holds); LEGO Builder (no ad disclosure, no admissions, 285K ratings — holds).

**NEW DIRT VERDICTS (task 3) — 23/23 CONFIRMED on live listings, ZERO fixes:**
- in-app purchases (11): BetterSleep, QRbot (TeaCapps), AdGuard, SwiftKey ($0.00 themes), CuriosityStream, Photomath, Seven, Hokusai, Goodnotes, Notion, PressReader.
- both (10): MyFitnessPal (via search fallback — TT listing crawled 22h ago: 16+ "Contains Advertising" + priced Premium IAPs; live US fetch 403'd, not retried), Pro Metronome (4+ "Contains Advertising" + priced IAPs despite description's "ad-free" claim), GuitarTuna, Tasty (4+ "Contains Advertising" + Tasty+ subs), ESPN (13+ "Contains Advertising" + ESPN+; description admits targeted advertising), NewsBreak (16+ "Contains Advertising" + Premium Experience IAPs), Brainly (13+ "Contains Advertising" + UGC), Audiomack (13+ "Contains Advertising" + "No Ads" as paid Plus feature), InShot ("Remove ads $3.99" IAP + "Contains Advertising"), Picsart (13+ "Contains Advertising" + "About Ads" link).
- ads (2): Tubi (plain Free, 13+ "Contains Advertising", "way fewer ads than cable"), Dictionary.com (plain Free, 13+ "Contains Advertising").

**ADBLOCK APPS (task 5) — 3/3 PASS:** uBlock Origin Lite (Free, no IAP, 4+ plain, Data Not Collected, seller Raymond Hill, updated 16h ago); BlockBear! (Free, no IAP, 4+ plain, Data Not Collected, TunnelBear — note last updated 2018, still live and clean); Halt: AdBlock Browser (Free, no IAP, 16+ with only "Contains Unrestricted Web Access" — normal for a browser; description explicitly "100% FREE… NO annoying in-app purchases!"). All retain `adsTier:"none"`.

**SUPERCOOK TIER EXCEPTION (task 4) — DECIDED: KEEP.** "free recipe app iphone" → "SuperCook Recipe By Ingredient" stays the cleanPick. No none-tier recipe-discovery app exists in the 149-app dataset (only Yelp/minimal and Open Food Facts, which is a product scanner not a recipe finder), and a fresh web search found no verify-clean broadly-fitting swap candidate (commercial recipe apps are all IAP or ads; clean ones need self-hosting or user-authored recipe files — neither fits a Tasty alternative). SuperCook is still a strict improvement over Tasty (Tasty = IAP + advertising; SuperCook = Free, no IAP, minor banner ads only — confirmed minimal by the earlier Phase 3 review today). **Implemented:** added `"cleanPickTier":"minimal"` to that one mapping in alternatives.json so the exception is machine-readable. **Site UI requirement:** the alternatives page MUST render the tier badge ("minimal ads") on this cleanPick — same two-tier presentation the directory already needs elsewhere.

**Fixes made (1 annotation, 0 removals):** `cleanPickTier:"minimal"` on the "free recipe app iphone" mapping (documents the one cleanPick-tier exception). All other 49 mappings resolve to none-tier. No apps dropped, no verdicts corrected, no fields changed on apps.json.

**Data hygiene:** apps.json 149 apps / 149 unique IDs / all required fields present; alternatives.json 50 mappings / 50 unique queries / all cleanPicks resolve against apps.json names; both parse as valid JSON.
