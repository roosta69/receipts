# Saleshandy Lead Finder — Applaud Operating Playbook

How to use Max's Saleshandy Lead Finder account to maximum effect for Applaud lead-gen.

**Source of truth verified 2026-05-20** from saleshandy.com/lead-finder/.

---

## What Saleshandy Lead Finder actually does

A B2B contact database (852M contacts / 42M companies) with 75+ search filters and built-in verification. Returns **verified email + verified phone + name + title + company** for any contact you unlock.

### Why this matters for us specifically

We already have **1,432 verified med spas with phone + website + GBP review count** (from the Apify pipeline). What we DON'T have is **direct owner-level email/phone** — we have practice front-desk numbers, not the owner's mobile.

Saleshandy fills exactly that gap.

### Pricing math (confirmed)

| Plan | $/mo | Credits | $/credit |
|---|---|---|---|
| Lead Starter | $49 | 2,500 | $0.020 |
| Lead Pro | $79 | 4,000 | $0.020 |

**Key:** 1 credit = 1 verified result. **$0 charged when they can't verify.** Unused credits roll over.

Compared to Apollo ($49/mo for 1,000 contacts = $0.049 each), Saleshandy is **~2.5× cheaper per verified lead**.

---

## Two tracks — run them in parallel

### Track A — Owner-level contacts at our existing 1,432 spas (highest ROI)

**Correction noted 2026-05-20:** Saleshandy's CSV Enrichment has TWO modes — Company mode (adds firmographics, doesn't return owner contacts) and People mode (needs first/last name + company, returns verified email/phone). Owner *discovery* at companies-we-already-have requires either People Enrichment (if we know the owner's name) or a 2-step Lead Finder flow.

**Three CSVs prepared on Desktop:**

1. `applaud-master-list.csv` — full 42-column master, all 1,432 rows. Reference / backup. **Not for Saleshandy upload.**

2. `applaud-known-owners-for-saleshandy.csv` — the 694 rows where we have owner first/last name. **Upload to People Enrichment.** Saleshandy matches the named person → returns verified email/phone. Expected ~50-70% hit rate (MD/PA-owned higher; solo NP lower).

3. `applaud-companies-for-saleshandy.csv` — all 1,432 rows, companies-only schema. **Upload as an Account List / Company List (NOT as enrichment).** No credits charged. Use this list as the company filter in Lead Finder step 2.

**Recommended flow:**

```
Step 1: Upload applaud-known-owners-for-saleshandy.csv → People Enrichment
        ~$8-10 spent, ~400-500 verified owner contacts returned

Step 2: Upload applaud-companies-for-saleshandy.csv → save as Account List
        $0 charged — this is just storage

Step 3: Lead Finder → filter: "Companies = Applaud Master Account List" +
        "Title = Owner OR Founder OR Medical Director ..." + Decision Maker = Yes
        ~$12-18 spent, ~600-900 owner contacts unlocked

Total expected: 1,000-1,400 verified owner contacts across the 1,432 practices for ~$20-30.
```

### Track B — Net-new lead discovery in adjacent verticals

**What:** Build saved searches using the 75+ filters to find healthcare practices we haven't scraped yet — dental, cosmetic derm, hair restoration, IV hydration, concierge medicine, etc.

**Why:** Applaud's live site sells to broader healthcare. Our existing scrape was med-spa-specific. Saleshandy lets us pull contact data from adjacent verticals without re-scraping Google Maps.

**Steps:**

1. Build a saved search per vertical (recipes below)
2. **Toggle "Net-new" filter ON** — auto-excludes practices already in your Saleshandy lead lists, prevents duplicate credit spend
3. Review the unlock count — Saleshandy shows result count BEFORE you unlock
4. Unlock in batches of 100-200 per vertical
5. Export to CSV
6. Run our existing pipeline ICP filter + dedup against `master-list.csv` (by company name + domain)

---

## Filter recipes (copy these into Saleshandy saved searches)

The filter UI groups search criteria. Below is the optimal combo per vertical.

### Recipe 1 — Med Spas (our core ICP)

```
Industry:              Hospitals and Health Care
                       Health, Wellness & Fitness
                       Medical Practices
Job title contains:    Owner, Founder, Co-founder, Medical Director,
                       Practice Owner, NP, FNP, Aesthetic Nurse
Decision Maker:        Yes
Seniority:             Owner / Founder / C-Level / VP
Company size:          1-10 employees (filters out chains)
Revenue:               < $5M (also filters multi-location)
Location:              United States
                       → drill to TX, FL, AZ, GA, TN, CA, NV, CO, WA, UT, NC, IL, VA
Company keywords:      "med spa" OR "medical spa" OR "aesthetic" OR "injectables"
                       OR "Botox" OR "Allē" (these surface med-spa-specific orgs)
```

**Expected:** 2,000-5,000 results across the 13 target states. Unlock 500-1,000 verified.

### Recipe 2 — Independent Dental Practice Owners

```
Industry:              Dentistry / Dental
Job title contains:    Owner, Founder, DDS, DMD, Practice Owner,
                       Practice Manager, Office Manager
Decision Maker:        Yes
Company size:          1-10 employees (solo + small group)
Revenue:               < $5M
Location:              United States
Company keywords:      "dental" OR "dentistry" — exclude "DSO" / "Heartland"
                       / "Aspen Dental" / "Smile Brands" (chain operators)
```

**Expected:** 8,000-15,000 raw, unlock the top 1,000 by relevance.

### Recipe 3 — Cosmetic Dermatology (med-spa-adjacent, high-WTP)

```
Industry:              Medical Practices / Hospitals and Health Care
Job title contains:    Owner, Founder, Dermatologist, Medical Director, MD
Decision Maker:        Yes
Company size:          1-25 employees
Location:              United States
Company keywords:      "cosmetic dermatology" OR "aesthetic dermatology"
                       OR "skin care clinic"
Exclude keywords:      "U.S. Dermatology" "Anne Arundel" "Forefront"
                       "Advanced Dermatology" "Epiphany" "Dermatology Associates"
                       (filter out the PE-rolled-up chains)
```

**Expected:** 3,000-6,000 raw.

### Recipe 4 — Hair Restoration Clinics

```
Industry:              Medical Practices
Job title contains:    Owner, Founder, Medical Director, MD
Company size:          1-25 employees
Location:              United States
Company keywords:      "hair restoration" OR "hair transplant" OR "FUE"
                       OR "Bosley" — exclude exact match "Bosley Medical"
```

**Expected:** 800-1,500 raw. Small TAM but $4-15K ticket = high value.

### Recipe 5 — IV Hydration / Wellness Clinics

```
Industry:              Health, Wellness & Fitness / Medical Practices
Job title contains:    Owner, Founder, Medical Director, NP, FNP
Company size:          1-15 employees
Location:              United States
Company keywords:      "IV hydration" OR "IV therapy" OR "wellness clinic"
                       OR "drip bar" OR "hydration lounge"
```

**Expected:** 2,500-4,000 raw.

### Recipe 6 — Concierge Medicine / Direct Primary Care

```
Industry:              Medical Practices / Hospitals and Health Care
Job title contains:    Owner, Founder, Physician, MD, Medical Director
Company size:          1-15 employees
Location:              United States
Company keywords:      "concierge medicine" OR "direct primary care" OR "DPC"
                       OR "membership medicine"
```

**Expected:** 1,500-3,000 raw. High WTP per customer.

### Recipe 7 — Audiology / Hearing Aid Clinics (independent only)

```
Industry:              Medical Practices / Health Care
Job title contains:    Owner, Founder, Audiologist, AuD, Practice Owner
Company size:          1-10 employees
Location:              United States
Company keywords:      "audiology" OR "hearing aid" OR "hearing center"
Exclude keywords:      "Costco" OR "Miracle-Ear" OR "Beltone"
                       OR "Connect Hearing" OR "HearUSA"
```

**Expected:** 1,200-2,500 raw. Older clientele, fantastic margins.

### Recipe 8 — Bonus: AI Search natural language

Saleshandy supports plain-English search via AI. When standard filters fall short, try:

> "Find owners of single-location medical aesthetic clinics in Sun Belt states with under 10 employees who personally inject patients."

Saleshandy translates this to filters automatically.

---

## Dedup against our existing master list

Saleshandy has a "Net-new" toggle that excludes their own historical unlock list. But we also need to dedup against **our** master-list.csv from the Apify pipeline.

Workflow:

1. Export new Saleshandy CSV → `saleshandy-batch-N.csv`
2. Run our merge script (extend `merge_to_all_leads.py`) to:
   - Match Saleshandy rows against our existing master by **company name + domain** (lowercased)
   - For matches → enrich the existing master row with Saleshandy's verified email + phone
   - For non-matches → add as new row with `source: saleshandy`
3. Push the updated `master-list.csv` to GitHub

We'll add a `source` field with values: `apify`, `agent_seed`, `merged`, `saleshandy`, `saleshandy_enriched`.

---

## Compliance checklist (don't skip)

Saleshandy gives us cell phones and personal emails. Before any outreach:

### For cold calls (TCPA + state mini-TCPA)
- **Landlines:** B2B exempt at federal level — can dial.
- **Mobile numbers:** manual dial only, no autodialer, no pre-recorded. State mini-TCPA in **FL, IN, OK, OR, TX** is more aggressive — respect 9am-9pm local windows.
- **National DNC + state DNC:** scrub before calling. Even B2B-applicable lists matter in IN/OK/TX.
- **Honor opt-outs immediately + permanently.**

### For cold email (CAN-SPAM, FTC § 465)
- Required: accurate sender info, working unsubscribe processed ≤10 business days, physical mailing address in footer, honest subject line.
- **B2B is NOT exempt** from CAN-SPAM. Penalty: $51,744 per violating email (2026 adjustment).
- No false header info, no false routing.

### For Applaud's specific compliance posture
- Never describe review gating in any outreach. Stick to the playbook-verified sample lines (`~/Desktop/applaud-social-launch/01_brand_voice_quickref.md`).
- Voice script: see `~/Desktop/review-agency/gtm/scripts.md`. Same compliance bright lines apply whether the lead came from Apify or Saleshandy.

---

## Workflow integration with our existing pipeline

```
Saleshandy CSV export
    ↓
saleshandy-batch-{date}.csv (raw, in ~/Desktop/review-agency/leads/saleshandy/)
    ↓
merge_to_all_leads.py (extended to handle Saleshandy schema)
    ↓
master-list.csv (with new source=saleshandy rows + enriched columns)
    ↓
all-leads.csv (regenerated)
    ↓
Push to GitHub → IMPORTDATA tabs auto-refresh in Sheets
```

I'll write the merge script extension when we run the first Saleshandy batch.

---

## Credit budget recommendation

**Month 1 plan: Lead Pro $79 = 4,000 credits**

Allocation:
- 600 credits: Track A enrichment of existing 1,432 master list (40% hit rate expected)
- 1,000 credits: Recipe 1 (Med spas — fill gaps + new states)
- 800 credits: Recipe 2 (Dental — net-new vertical)
- 400 credits: Recipe 3 (Cosmetic derm — net-new)
- 400 credits: Recipe 5 (IV hydration — net-new)
- 800 credits: reserve / experiment with Recipes 4, 6, 7, 8

**Total expected new contacts: ~3,200-3,800 verified.**

Combined with our existing 1,432, this puts us at **~4,600-5,200 contactable healthcare practices** within a month.

---

## KPIs to track per Saleshandy batch

When we run a batch, log these to compare against Apify-sourced leads:

| Metric | Apify-sourced | Saleshandy-sourced |
|---|---|---|
| Owner-level email coverage | 48.7% | Track per batch |
| Owner-level phone coverage | (front-desk only) | Track per batch |
| Connect rate on cold call | (TBD) | Track per batch |
| Demo-booked rate | (TBD) | Track per batch |
| Cost per closed deal | (Apify ~$0.003) | Saleshandy ~$0.020 = ~6× more |

The hypothesis: **Saleshandy leads convert 3-5× higher** because we're calling the actual owner's verified cell, not a receptionist. If true, the 6× higher per-lead cost is more than offset.

---

## Net-new opportunities Saleshandy unlocks

What we couldn't do with Apify alone:

1. **Find owners not on Google Maps** — some healthcare practices don't have GBP listings (uncommon but real, especially concierge medicine and B2B-style practices)
2. **Multi-location operators' regional managers** — Saleshandy has the org chart; useful for selling Applaud as an enterprise plan to multi-practice groups
3. **Verified mobile numbers** — Apify gives front-desk landlines; Saleshandy gives owner cell phones
4. **LinkedIn URL per contact** — useful for IG/LinkedIn outreach as a parallel channel
5. **Department + seniority filters** — finds Practice Managers (often the actual decision-influencer for SaaS purchases) we'd miss otherwise

---

## When NOT to use Saleshandy

- **Single-owner solo NP practices** — these owners often have no LinkedIn / no public business email. Apify + cold-call discovery is faster here.
- **Hyper-local territory mapping** — Saleshandy doesn't return GBP URL or review count, which are essential for the audit-style pitch ("your 31 vs their 134"). For that, stick with the Apify-scraped master.
- **Compliance-sensitive verticals where titles don't match** — Saleshandy maps to LinkedIn-style job titles. A FNP-C who calls herself "Aesthetic Injector" on LI might not match a "Medical Director" filter. Combine multiple title searches.

---

## First action

When Max next opens Saleshandy:

1. **Run Track A first** (CSV upload of master-list.csv) — fastest ROI, low credit spend
2. **Then run Recipe 1 (Med Spas)** as a saved search — biggest aligned vertical
3. **Export both CSVs** to `~/Desktop/review-agency/leads/saleshandy/` (I'll write a merge script when the first one lands)

Notes on what to capture from the first batch so we can tune subsequent runs:
- Unlock-rate per filter combo (how many results returned vs how many had verified contacts)
- Per-vertical credit cost
- Sample 20 leads manually to gut-check quality before unlocking a full batch
