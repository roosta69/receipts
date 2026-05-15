# Pricing Model

**Pay-per-review with a one-time setup fee.** Locked for MVP. Retainer pricing returns when we add services beyond review acquisition.

---

## The structure

| Component | Amount | When charged |
|---|---|---|
| **Setup fee** | $499 | One-time, on contract signing |
| **Per published review** | $35 | Monthly, billed for reviews verified that month |
| **Monthly cap** | $899 | Hard ceiling per spa per month |
| **Contract length** | Month-to-month | No annual commit |
| **Cancellation** | 30-day notice | Effective end of next billing cycle |

That's the entire pricing card.

## Setup fee — what it covers

The $499 is real work, not bullshit fee:

1. Pull the spa's full GBP profile + last 24 months of review history
2. Pull top 5 local competitor profiles (same data depth)
3. Run the gap analysis → deliver as PDF
4. CRM integration: connect to spa's PMS (Pabau, Aesthetic Record, Repeat MD, Symplast — whatever they use)
5. Sign and execute the BAA
6. Provision SMS sender on the spa's existing number (or get a new one provisioned via spa)
7. Load the sentiment-neutral request template into spa's outbound queue
8. Set up reply-monitoring + Slack/email alerts to founder

Roughly 6-8 hours of human work for first customer; drops to 2-3 hours by customer #10 as we tooling-up.

## Per-review pricing — the math

**$35 per published verified review.**

Why $35:
- Below $20 doesn't fund a 2-person team's labor + infra
- Above $50 invites pushback ("just hire a VA") and overpriced perception
- $35 lands in the middle of similar performance-based service pricing across review platforms (verified per founder research)
- 8 reviews/month at $35 = $280, in the same band as Birdeye/Podium $299/mo flat
- 20 reviews/month at $35 = $700, also in that same incumbent band
- 30 reviews/month at $35 = $1,050 — would exceed cap, billed at $899 instead

What counts as "published verified review":
- Review posted to the spa's Google Business Profile
- Posted by a real person (we screen for fake/spam patterns before billing)
- Reviewer is a confirmed patient (cross-referenced against the spa's appointment system)
- Survives the 7-day Google moderation window without removal
- Star rating is irrelevant for billing — we charge for both 5-star and 1-star reviews. Pricing by sentiment contaminates the legal posture into FTC § 465.4 territory.

## The cap — $899/mo

Hard ceiling per spa per month. Why:
- **Sales tool:** answers the "what's my worst case?" objection in one number
- **Reciprocal trust:** signals we're not trying to maximize per-customer extraction
- **Operational discipline:** at $899 we've delivered ~26 reviews — that's a good month. If we're delivering 50/mo we're either spamming or the spa hit a viral moment; either way, capping is correct
- **Above-incumbent ceiling:** $899 is at the top of Birdeye/Podium pricing — beyond that we're losing the price-comparison sale

## What this looks like for a real spa

Single-location NP-owned med spa, 30 patient visits/week (industry typical):

- Month 0: $499 setup
- Month 1: 6 reviews delivered (early ramp) → $210
- Month 2: 12 reviews delivered → $420
- Month 3: 14 reviews delivered → $490
- Month 4: 16 reviews delivered → $560
- Months 5-12: averaging 12-18 reviews/mo → $420-$630/mo

Year 1 revenue from this spa: $499 + ~$5,500 = ~$6,000.

At 167 spas to hit $1M ARR, the math is:
- 167 × $499 setup = $83K (one-time)
- 167 × $5,500 ARR = $918K (recurring)
- **Total Y1 contract value: ~$1.0M** if we hit ICP and keep 90% retention

## Cashflow shape

Pure pay-per-review without setup is a cashflow trap (work month 1, paid month 2-3). The $499 setup solves it:

- Customer #1 day 0: $499 in cash, covers 8 hours of setup labor
- Customer #1 day 30: ~$200-400 in review billing
- Break-even per customer: month 1 (covers labor)
- Profitable per customer: month 2 onward

For 2 founders at ~$3K/mo combined personal burn, we need ~12 customers signed in month 1 to be cashflow-positive. That's tight but achievable if we close 4-6 in the first 60 days from warm + early outreach.

## Annual contract option (deferred)

We could offer "10% off if you commit annually" — would lift LTV but defeats the "month-to-month, no contract" pitch advantage over Birdeye/Podium. **Don't add this until customer #25.** The contract-trauma wedge is too sharp to dilute.

## Add-on services (future, not MVP)

Once we have ~20 paying customers, layer:

- **Reputation defense** (+$199/mo) — fake-review monitoring, dispute filing, attack alerts
- **Reply-management premium** (+$99/mo) — owner-voice AI replies fine-tuned to the spa's brand voice
- **Local SEO bundle** (+$299/mo) — GBP optimization, citations, photo SEO
- **Instagram review aggregation** (+$149/mo) — pull positive Instagram comments + DMs for testimonial use

Each add-on is a separate SKU — never bundled into the base. Bundling kills the simplicity of the pitch.

## What we don't do

- **No discounts for multi-location** in MVP — keeps pricing simple. Multi-loc = multiply by location count.
- **No setup fee waivers** — the $499 filters out tire-kickers and funds the work
- **No per-review tiering by star rating** — illegal under FTC § 465.4 if priced by sentiment
- **No success-based bonuses** ("$100 if you hit 4.5 stars") — same legal risk
- **No revenue-share** — attribution is unprovable for med spas

## How to handle pricing pushback

**"$35 per review feels expensive — Birdeye charges $299 flat."**
> "Birdeye's $299/mo is a guaranteed bill regardless of results. Ours scales with delivery. 5 reviews = $175. 20 reviews = $700. If we don't perform, you don't pay. And no annual contract."

**"Can you do $25/review?"**
> "Below $30 doesn't cover the labor. We're already capping at $899/month so you're protected on the upside — that's the negotiation."

**"What if a review I don't want gets posted?"**
> "We charge for any verified real-patient review. We can't filter by star rating — that's actually FTC-illegal. But if a review is fake or spam, we dispute it free of charge and you're not billed."

**"Can I just pay setup and try it for one month?"**
> "Yes. $499 setup, no monthly minimum. If month 1 delivers 0 reviews, you owe nothing beyond the setup. Most spas see 5-15 in month 1."

**"Is the cap really $899?"**
> "Yes, hard ceiling. Worst case is $899/mo even if we deliver 50 reviews. We'd rather underprice than have you feel ripped off and churn."

## Stripe + billing setup

- **Stripe Billing** with usage-based metered pricing
- Setup fee = one-time invoice on day of contract signing
- Per-review billing = monthly invoice cycling on the customer's signup anniversary
- Daily review-count sync from our internal tracker → Stripe usage record
- Auto-bill at $899 cap; if review count exceeds cap, internal tracking continues but no overcharge

Implementation: ~2 hours once Max is ready. Until then, manual invoicing via Stripe dashboard for first 5 customers.
