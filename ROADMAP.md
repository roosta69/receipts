# Roadmap

What needs to happen, in order, from now to first $1M ARR. Living document — keep it honest. Mark items done with `- [x]` as they ship; don't move done items off the page (the diff history is part of the asset).

Phases are ordered by **prerequisite**, not by calendar:

1. **Phase 0 — Pre-customer-#1** (cannot legally sign anyone until this is done)
2. **Phase 1 — Customer 1 to 10** (operational shake-down, learn what we got wrong)
3. **Phase 2 — Customer 10 to 25** (process hardening + first leverage hires)
4. **Phase 3 — Customer 25+** (product expansion + vertical decisions)

---

## Phase 0 — Pre-customer-#1 (BLOCKING)

Don't sign customer #1 before everything in this section is checked off. The legal items are non-negotiable; the operational items are checkbook decisions.

### Legal (lawyer-blocked)

- [ ] Engage healthcare attorney with med-spa or aesthetics-clinic experience (NOT generalist business lawyer). Budget: $3-5K for the bundle below.
- [ ] BAA template review + revision
- [ ] Customer service agreement review (scope of work, liability cap, indemnification, termination, IP ownership)
- [ ] Subcontractor BAA template (for VAs in Phase 2 — but draft now so we don't bottleneck later)
- [ ] LLC formation — Delaware default unless reason otherwise. Use Stripe Atlas ($500) or Clerky.
- [ ] EIN registration (free via IRS.gov, takes ~10 min)
- [ ] Operating agreement between Tom and Max — equity split, voting, IP ownership, vesting schedule, drag-along, tag-along. Don't skip this; this is the single most common founder regret.
- [ ] Trademark search on "Receipts" brand for Class 35 (advertising/business services) and Class 42 (software). USPTO TESS search is free; consider trademark filing later if name sticks.

### Insurance + compliance

- [ ] Cyber liability insurance — $1M minimum coverage typical for med-spa BAA requirements. Shop Hiscox, Coalition, At-Bay.
- [ ] HIPAA training certificate (Tom + Max). HHS portal free; paid options via HIPAA Academy or Compliancy Group ~$200 each.
- [ ] Encryption posture documented — 1-page doc: what services touch PHI (Twilio? Postgres? S3?), how data flows, where it's encrypted at rest.
- [ ] Breach response plan — 1 page minimum: who to notify, in what order, within what timeframe (60 days max under HIPAA Breach Notification Rule).

### Operational setup

- [ ] Stripe account + metered billing configured
  - $499 one-time invoice on contract signing
  - $35-per-review usage-based metered pricing
  - $899/mo cap enforced via product config or our internal sync
- [ ] Domain registration: receipts.[tld]. Verify availability for .com, .co, .io, .so, .com.us. Buy the cleanest one.
- [ ] Email hosting: hello@, audits@, tom@, max@. Google Workspace ~$6/user/mo.
- [ ] Phone number provisioned (Google Voice free, OpenPhone $20/mo, or RingCentral). Use as both outbound cold-call number and inbound customer support.
- [ ] State DNC list subscriptions for FL, IN, OK, OR, TX (where state mini-TCPA stacks federal).
- [ ] Customer CRM — Airtable Free or HubSpot Free. Schema in `gtm/scripts.md`.
- [ ] Outreach tracking spreadsheet (or built into CRM). Log every dial, DM, email + outcome.

### Software (Max-owned)

- [ ] **Competitor scraper** — input: spa name + zip; output: top 5 nearest med spas with review counts, ratings, recency, reply rate. Used by GTM (audit deliverable) AND product (monthly report).
- [ ] **Review request engine** — Twilio (or similar) + scheduler. Sends from spa-provisioned number under BAA. Sentiment-neutral copy locked.
- [ ] **Reply system** — template library (5-10 HIPAA-safe replies for 4-5 star) + flagging system that sends 1-3 star reviews to founder Slack/email for human composition.
- [ ] **Monthly report generator** — auto-PDF: starting baseline, current state, vs. competitors, this month's review delta. Owner-friendly, not data-dump.
- [ ] **Stripe webhook integration** — log usage events for billing; sync review counts daily.
- [ ] **BAA-aware data segregation** — patient data lives in spa's CRM. We access via API/integration only. No bulk export. Logged access.

### Sales prep

- [ ] Pull actual current Google review counts for top 10 leads in `leads/seed-list.csv` (manual, 5 sec/each).
- [ ] Pull top-3-competitor review counts for those same 10 spas' cities. This becomes the audit content.
- [ ] Identify which of those 10 metros have Local Services Ads running (changes the CTR-gap math in the pitch).
- [ ] Generate 10 personalized audit PDFs for the first 10 outreach attempts.

---

## Phase 1 — Customer 1 to 10 (operational shake-down)

You will get things wrong. Document them.

### Outreach execution

- [ ] First 10 IG DMs (Tom's account, manual, hyper-personalized with competitor data per `gtm/scripts.md`)
- [ ] First 10 cold calls (Max in morning block, 10-11:30am local to prospect)
- [ ] First 5 partner channel conversations (Pabau referral program signup, then 2-3 local SEO agencies)
- [ ] Sign customer #1
- [ ] **Run end-to-end on customer #1**: BAA signed, CRM integrated, first request sent, first review published, first reply approved. Document every gap.
- [ ] Sign customers #2 through #10
- [ ] After customer #10, hold a 1-hour debrief: what's working, what's painful, what's the bottleneck

### Process refinement

- [ ] Refine cold call script after first 50 dials (data-driven, not guesswork)
- [ ] Refine IG DM opener after first 100 messages
- [ ] Identify which sub-segment is closing fastest (RN vs NP vs PA, by state) — adjust ICP filter
- [ ] Identify objections we didn't anticipate — add to the script
- [ ] Build internal dashboard: outreach × responses × audits sent × close rate by channel by week

### First retention signals

- [ ] By customer-#5's month 3: compute renewal rate (still active vs cancelled/churned)
- [ ] By customer-#10's month 3: identify any churn pattern (vertical sub-segment, state, specific issue)

### Phase 1 exit criteria

Move to Phase 2 when:
- ≥10 paying customers
- ≥3 customers past 90 days with no churn
- Average $400+ MRR per active customer
- Cold call OR IG DM has hit ≥1% close rate for ≥100 attempts

---

## Phase 2 — Customer 10 to 25 (process hardening)

Operational leverage time. Find the work that's repetitive enough to delegate.

### First leverage hires

- [ ] First offshore VA for review-request operations (Philippines/Pakistan, ~$5-8/hr full-time). Start with 20 hr/wk.
- [ ] **Subcontractor BAA signed with VA** (lawyer-blocking — make sure Phase 0 BAA covers this case).
- [ ] VA HIPAA training completion + documentation
- [ ] VA workflow: handles review-request scheduling, reply drafting for 4-5 star (we approve), monthly report generation
- [ ] Define escalation path: anything ambiguous → founder review

### Onboarding tightening

- [ ] Standardize onboarding: target <2 hours of founder time per new customer setup
- [ ] Build customer self-serve onboarding portal: BAA signing (DocuSign or similar) + CRM integration auth
- [ ] Pre-flight checklist for customer kickoff (BAA, CRM, payment method, timezone, brand voice samples)

### Lead-list scaling

- [ ] AmSpa membership ($595/yr) for member directory access
- [ ] Build automated lead-gen pipeline: Google Places API + manual qualification queue
- [ ] Hire VA for lead enrichment (~$5-7/hr × 20 hr/wk) — pulls and qualifies new leads to fill the queue
- [ ] Target: 200-500 qualified ICP-fit leads per state per month at sustained volume

### Financial milestones

- [ ] Hit $10K MRR (≈ 20-22 active customers at average spend)
- [ ] First profitability check: are we cashflow-positive after VA + insurance + tooling? If no, what's the gap?

### Phase 2 exit criteria

Move to Phase 3 when:
- ≥25 paying customers
- ≥$15K MRR
- VA producing reliable output with <10% founder rework
- Lead-gen pipeline producing ≥50 new qualified leads/week without founder time

---

## Phase 3 — Customer 25+ (product + vertical expansion)

Layer in upsells. Decide the long-term shape of the company.

### Product expansion (only when customers ask)

- [ ] **Reputation defense** add-on (+$199/mo) — fake-review monitoring, GBP dispute filing, attack alerts
- [ ] **Reply-management premium** (+$99/mo) — owner-voice AI replies fine-tuned per spa's brand voice
- [ ] **Local SEO bundle** (+$299/mo) — GBP optimization, citations, photo SEO
- [ ] **Instagram review aggregation** (+$149/mo) — pull positive IG comments + DMs for testimonial use

Each is a separate SKU. Never bundled into base. Never launched without explicit customer ask.

### Vertical expansion decision

- [ ] Validate top 2 adjacent verticals from [[Review Agency Vertical Targets]]:
  - In-home senior care (~20K non-medical agencies, $700-1500/mo WTP)
  - Hair restoration (~1,200 clinics, $1,000+/mo WTP)
- [ ] Pilot 5 customers in one adjacent vertical
- [ ] Decide: expand wedge or deepen med spa specialization

### Scaling decisions

- [ ] Hit $50K MRR (≈ 100 customers) — decision point: raise or stay bootstrapped?
- [ ] If raising: vertical-SaaS-focused funds, deck, intros. 5c(c) Capital is wrong fit (they fund PM); look at K9 Ventures, Bessemer SMB-focused, Elad Gil, vertical-SaaS angels.
- [ ] First full-time hire decision: sales rep vs ops manager vs developer
- [ ] Annual contract option launch (10% discount) — only after we have 25+ retention data points

### Brand work

- [ ] Trademark filing on "Receipts" if name has stuck through Phase 2
- [ ] Brand refresh if needed — we picked a working name fast, may want a designer pass at $50K MRR

---

## Risks + watch list

- **Hot category** — funded vertical SaaS could enter med-spa reputation in 12-18 months. Move fast in Phase 0/1.
- **Software single-point-of-failure** on Max. Document architecture in `software/architecture.md` (TBD) early in Phase 0.
- **Lawyer cost overrun pre-customer-#1** — budget $5-7K total for BAA + customer agreement + operating agreement + LLC formation. Find healthcare attorney with med-spa experience, NOT generalist.
- **HIPAA breach risk** — single biggest existential threat. Process discipline is the moat. One breach kills the company.
- **Vertical concentration** — all eggs in med spa. Mitigate in Phase 3 by validating one adjacent vertical.
- **Pay-per-review billing disputes** — what if customer disputes a published review's attribution to us? Service agreement needs clear attribution definition (lawyer item).

---

## Out of scope (do not let scope creep)

These have been suggested or considered and explicitly deferred. Don't pull them forward.

- **Multi-vertical launch** — locked to med spa for ≥6 months minimum
- **Full BI dashboard** — only review acquisition + reply management in MVP
- **Annual contracts at launch** — kills the pitch advantage; defer to Phase 3
- **Conferences** (AmSpa Vegas, Aesthetic Next Dallas) — defer until Phase 2 cashflow positive ($8-25K booth cost)
- **Paid ads** — never, until LTV proven >$10K
- **LinkedIn outbound** — owners aren't there
- **Building our own PMS / scheduling** — never. We integrate with theirs.
- **Custom-quoted enterprise pricing** — never. Productized only.

---

## Cadence

- Update this file at the end of each week
- Weekly founder sync to review what shipped and what's blocked
- Monthly review of phase-exit criteria — are we ready to move on?
