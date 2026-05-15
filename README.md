# Receipts

> *"Show me the receipts."* — every patient deciding which med spa to book.

Productized Google Reviews acquisition for US medical spas. Pay-per-review pricing. Two-founder ops (Tom + Max).

**Brand name:** Receipts (working name as of 2026-05-15 — change if a better one surfaces)
**Repo:** github.com/roosta69/receipts

**Wiki home:** [[Productized Review Agency]] in `~/Desktop/second brain/wiki/projects/`. This folder is the operational implementation.

## The pitch (in one line)

Your top 3 local competitors have 67 Google reviews. You have 22. We close the gap in 90 days, you pay per published review.

## Working product scope

What we deliver:
1. One-time competitive analysis (your spa vs. top 5 nearest competitors — review counts, star ratings, recency)
2. Post-visit review request automation (SMS via the spa's CRM, sentiment-neutral language, sent to all patients)
3. Reply management on the spa's behalf (HIPAA-safe templates; human review on 1-3 star)
4. Monthly report — where you started, where you are, vs. competitors

What we don't do (yet):
- AI reply drafting beyond the locked template set
- Theme analysis on review content
- Predictive intervention before bad reviews
- Instagram integration
- Fake-listing fraud detection
- Anything outside Google Business Profile reviews

Add features only after a paying customer asks. Build the rest as upsells, not as launch scope.

## Pricing model (locked for MVP)

- **$499 one-time setup** (competitor audit + CRM integration + BAA)
- **$35 per published verified review** thereafter (capped at $899/mo per spa)
- No annual contract. Monthly cancellable.

Math: an active spa generates 8-20 reviews/mo → $280-700 MRR. Lands in the same band as Birdeye/Podium ($299-599/mo) but with the "you only pay for what works" pitch.

Retainer-based pricing comes back when we add services beyond review acquisition.

## ICP (locked for MVP)

NP/RN-owned solo injector practices in TX, FL, AZ, GA, TN. $500K-$1.5M revenue, single location, 5-50 current Google reviews. See `leads/icp-and-methodology.md`.

## Sales channels (3 in parallel)

1. **Cold call** — Tue-Thu 10-11:30am and 4-5:30pm local. ~30 dials/founder/day.
2. **Instagram DM** — manual, founder-led, ~50-80 DMs/founder/day. Highest-conversion channel for this vertical.
3. **Partner channel** — sign as preferred reputation partner with one PMS (Pabau target) + white-label to 2-3 local SEO agencies.

See `gtm/scripts.md` for words.

## Folder map

```
review-agency/
├── README.md                 — this file
├── gtm/
│   └── scripts.md            — cold call + IG DM + cold email
├── pricing/
│   └── model.md              — pay-per-review structure + math
├── stats/
│   └── claims-bank.md        — every claim we make + primary source URL
├── compliance/
│   └── playbook.md           — HIPAA-safe templates, red lines, state map
├── leads/
│   ├── icp-and-methodology.md — ICP definition + how to scale the list
│   └── seed-list.csv         — verified starter list of US med spas
├── docs/                     — also served live via GitHub Pages
│   ├── copy.md               — homepage copy
│   └── index.html            — landing page (single file, editorial)
└── ops/                      — onboarding + monthly report templates (TBD)
```

## What's built by Max vs. Tom vs. agency

- **Max:** competitor scraper, review request engine, reply automation, monthly report generator. Software stack — already in progress per Tom 2026-05-15.
- **Tom:** sales script execution, lead list curation, founder content, customer onboarding calls.
- **External:** HIPAA BAA template (lawyer review before customer #1), incorporation, payment processing.

## Status (2026-05-15)

- Vertical locked: med spas
- Pricing model locked: pay-per-review
- Software: in progress (Max)
- Lead list: seed of ~50-75 spas (research-agent-generated, see `leads/seed-list.csv`)
- Website: copy drafted, single-page HTML drafted
- Cold-outreach: ready to start once seed list is verified and BAA template is reviewed

## Open items before customer #1

1. Lawyer review of BAA template + customer agreement
2. Incorporate (LLC, state TBD)
3. Stripe set up for $499 setup + per-review billing
4. Pull actual current Google review counts on top 5 cities to anchor pitch numbers per metro
5. First 10 personalized outreach attempts (5 cold call + 5 IG DM) — no scale until first customer
