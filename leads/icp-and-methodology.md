# ICP + Lead-List Methodology

How we define our ideal customer, where to find them, and how to scale the list from 50-75 (seed) to 5,000+ (operational).

---

## ICP — locked for MVP

A spa is in-ICP if **all** of these are true:

| Dimension | Spec |
|---|---|
| State | TX, FL, AZ, GA, or TN |
| Ownership | NP-owned, RN-owned, or PA-owned (NOT MD-owned, NOT chain) |
| Locations | Single location only |
| Service focus | Injectables (Botox/filler) primary; can include laser, body, IV, weight-loss as secondary |
| Annual revenue | $500K – $1.5M (proxy: 1 treatment room, 2-4 staff) |
| Current Google reviews | 5–50 (the gap we close) |
| Current star rating | ≥ 4.0 (we acquire reviews; we don't fix bad service) |
| Owner-operated | Owner is on-site at least 50% of the time |

Why this exact slice (full reasoning in [[Review Agency Vertical Targets]] in the wiki):

- **NP/RN/PA ownership in Sun Belt:** NPs gained full practice authority in 27 states; doubled from 11% to 23% of med spa owners 2019-2024 (AmSpa). They take their own calls. They live on Instagram. They get the math.
- **Single-location:** Multi-location chains have practice managers and procurement processes. Cycle is 3+ months, lower close rate, and they need integrations we don't have.
- **Sun Belt:** NP-friendly scope laws + lower commercial rent + high consumer aesthetic demand. CA + NY skipped (CPOM rules + saturated + jaded).
- **$500K-$1.5M:** $500/mo is 0.3-1% of revenue — no-brainer territory. Below this, $35/review feels expensive. Above $3M, spa already has marketing director and procurement process.
- **5-50 reviews:** Below 5 = too early-stage to care. Above 50 = already winning, harder pitch.
- **≥4.0 stars:** We don't reform bad service. If their existing reviews are sub-4.0, the underlying patient experience is the problem; reviews won't fix it.

---

## Out-of-ICP — explicit excludes

Don't pitch any of these:

- ❌ Multi-location chains (Ideal Image, LaserAway, SkinSpirit, Allergan-affiliated, Maverick MedSpas)
- ❌ MD-owned dermatology practices (different buyer, different incumbent — Healthgrades/Vitals own the ratings layer)
- ❌ Plastic surgery practices (RealSelf owns discovery, top surgeons have full marketing teams)
- ❌ Aesthetics-only / esthetician-led without medical (no injectables = lower margin = won't pay $500/mo)
- ❌ Spas in CA, NY, IL, MA (CPOM-strict, saturated, NP-restrictive)
- ❌ Spas with sub-4.0 stars (different problem; we can't fix bad service)
- ❌ Spas with 100+ reviews already (they've solved it; harder pitch)
- ❌ Spas inside a hospital, clinic chain, or "wellness center" multi-tenant building (decision is centralized)

---

## Lead-list scaling methodology

The seed list (`leads/seed-list.csv`) is the starting 50-75. To get to 1,000+ for sustained outreach, run this process:

### Method 1: Google Maps + Places API (highest yield)

1. **Build a city list:** TX, FL, AZ, GA, TN — pull every metro with population >100K
2. **For each metro, query Google Places Nearby Search** for `type=spa` with keyword `med spa` or `injectables`
3. **Filter by:**
   - `user_ratings_total` between 5 and 50 (our review band)
   - `rating` ≥ 4.0
   - Not in our chain blacklist (filter out by name pattern)
4. **For each match, pull `place_details`** → name, phone, website, GBP URL, address
5. **Manual qualification pass** — visit website, confirm NP/RN/PA-owned (not MD-owned, not chain). About page usually states.
6. **Enrich with Instagram handle + owner first name** — manual or via Apollo/Clearbit

Estimated cost: $300-800/mo for Places API + Apollo at moderate volume. Yield: 200-500 verified ICP-fit spas per state per month.

### Method 2: AmSpa Member Directory

AmSpa publishes a member directory (paywall). At ~$595/year for AmSpa membership, you get access to ~3,000 member spas with owner names + contact info. ROI obvious: even 1 customer pays it back.

Caveat: AmSpa members skew larger and more established than our ICP. Filter aggressively.

### Method 3: Instagram hashtag mining

Search hashtags:
- `#medspaowner`
- `#npinjector`
- `#rninjector`
- `#injectorlife`
- `#botoxlife`
- `#aestheticnurse`
- `#aestheticnursepractitioner`

For each owner-led account:
- Confirm they own a single spa (bio usually says "Owner @ XYZ Med Spa")
- Pull their spa name from the bio
- Cross-reference to Google Maps for the GBP listing
- Enrich

Estimated yield: 50-100 high-quality founder-led leads per week of mining. Slower than API but every lead is owner-operated by definition.

### Method 4: Local listicles + "best of" lists

For each metro, Google "best med spas in [city]" → pull listicle results from local publications (ModernLuxury, Voyage, CityBeat, etc.). These articles typically list 10-20 spas with brief descriptions, often noting ownership.

Yield: 5-15 per metro per article, very high quality.

### Method 5: Conference attendee lists

AmSpa Medical Spa Show (April, Vegas) and Aesthetic Next (September, Dallas) publish attendee/exhibitor lists. ~2,000 + 1,400 attendees respectively. Cross-reference attendees to LinkedIn for owner role + spa name.

Cost: Show pass ~$700-1,200 if you don't exhibit. Worth it once for the list alone (single-time cost = thousands of leads).

---

## CSV columns (the canonical schema)

Every row in any lead list, regardless of source, must have:

```
name              — spa name (e.g., "Skinly Aesthetics")
city              — city only, not metro (e.g., "Phoenix")
state             — 2-letter (e.g., "AZ")
owner_name        — first + last (e.g., "Sarah Patel")
owner_credential  — RN, NP, PA, MD, esthetician (filter by this)
services          — comma-separated (e.g., "botox,filler,laser,iv")
google_review_count — integer
google_star_rating  — float (4.6)
phone             — E.164 if possible (+18885551234)
website           — full URL
instagram_handle  — without @
gbp_url           — full Google Maps URL
notes             — free text (e.g., "founded 2022, very Instagram-active")
```

Optional but useful enrichment columns (add when scraped):
- `last_review_date` — was their most recent review > 90 days ago? (Recency signal)
- `monthly_review_velocity` — reviews/month over last 6 months
- `top3_competitor_avg_reviews` — pre-computed gap data for the pitch
- `lsa_present` — boolean — does the metro have Local Services Ads?
- `pms_used` — Pabau / AestheticRecord / RepeatMD / Symplast / unknown

---

## Lead qualification scoring

After enrichment, score each lead 0-100:

| Signal | Points |
|---|---|
| In-ICP (state + ownership + size + rating + review band) | +50 base |
| Single location confirmed | +10 |
| 5-25 reviews (most undertargeted) | +10 |
| 4.5+ stars | +5 |
| Last review > 60 days ago (review velocity tanking) | +10 |
| Active Instagram (3+ posts in last 30 days) | +5 |
| Owner first name found | +5 |
| Top-3 competitor avg > 50 reviews (clear gap) | +10 |
| Multiple chains in their metro (more competition) | +5 |
| Phone number on website | +5 |

Only outreach to leads scoring 70+. Below 70 = backfill list.

---

## Daily outreach allocation

Once seed list is live and scored:

- **Cold call:** Pull top 30 phone numbers each morning. 2 founders = 60 dials/day target.
- **Instagram DM:** Pull top 80 Instagram handles. 2 founders = 160 DMs/day target.
- **Email:** Pull top 100 email addresses (when found). Run through Smartlead/Instantly at 30-50/day per inbox.

After each outreach attempt, log outcome in CRM. Re-score weekly based on response data.

---

## When to revisit the ICP

After 100 outreach attempts (~50 conversations + 5-10 customers), audit:

- **Which sub-segment is closing?** RN vs NP vs PA. Adjust focus.
- **Which state is closing?** TX vs FL vs AZ vs GA vs TN. Concentrate.
- **Which review-count band is closing?** 5-15 vs 15-30 vs 30-50. Sharpen.
- **Are MD-owned spas leaking through?** If yes and they're closing, expand ICP. If yes and they're not, tighten filters.

ICP is not sacred. After 100 attempts, you have data. Use it.

---

## Methodology weakness to call out

- The single biggest data quality issue is **owner credential** — websites don't always state RN/NP/PA. Manual verification per lead is real work (~2 min each). Automation requires LLM-extraction from About pages with high error rate.
- Google Places API doesn't surface ownership info — every lead needs a website visit at minimum.
- Instagram is the cleanest source for owner-credential because owners self-describe in bios. Slower but higher-quality.
- AmSpa membership is the highest-leverage data acquisition we can do. Worth the $595.

---

## Seed list

See `leads/seed-list.csv`. Generated by research agent 2026-05-15. ~50-75 verified entries across TX/FL/AZ/GA/TN.
