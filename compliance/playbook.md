# Compliance Playbook

The legal posture for running this service. Operational, not lawyer-disclaimer. Read once, run by it always.

**Before customer #1: get a healthcare attorney to review the BAA template (Section 8) and customer agreement.** This document is the operational guardrail; the contracts are the legal instrument.

---

## 1. The four laws that govern us

| Law | What it controls | Penalty for us |
|---|---|---|
| **HIPAA** (45 CFR Parts 160, 164) | Patient health information handling; we touch it via spa CRM integration | $100–$50,000 per violation, up to $1.9M/year |
| **FTC 16 CFR Part 465** (Final Rule on Reviews, effective Oct 21, 2024) | Fake reviews, incentivized reviews, review suppression | Up to $51,744 per violation |
| **Google Business Profile policies** | Review acquisition mechanics on the platform | Profile suspension, mass review removal |
| **TCPA / state mini-TCPA** (FL, IN, OK, OR, TX) | B2B cold-calling and SMS to patients | $500–$1,500 per call/text federal; states stack |

---

## 2. The bright lines — never cross

These are project-ending if violated. Not negotiable.

1. ❌ **Never pay the reviewer anything.** Cash, gift cards, discounts, free service, contest entries, loyalty points. Any value flowing to the reviewer = banned.
2. ❌ **Never write fake reviews.** Not from agency accounts, not from staff accounts, not from "test" accounts. FTC § 465.2 = $51,744 per fake.
3. ❌ **Never gate by sentiment.** Cannot ask happy patients privately and unhappy ones offline. Cannot ask "rate us 1-10, only 8+ get the Google link." Banned by Google + FTC § 465.7.
4. ❌ **Never reply with PHI in public.** "Thanks Sarah, glad your Botox went well!" = HIPAA breach. The reply confirms (a) Sarah was a patient and (b) she had Botox. Both are protected.
5. ❌ **Never reuse a patient's photo without specific written consent.** Even if the patient posted it themselves in a review, the spa reposting it requires consent.
6. ❌ **Never solicit only positive sentiment.** No "leave us a 5-star review!" copy. Solicitation language must be sentiment-neutral.
7. ❌ **Never price by sentiment.** Charge per published review, not "per 5-star review." Pricing by sentiment contaminates into FTC § 465.4 (incentive conditioned on a particular sentiment).
8. ❌ **Never quote a Texas-spa patient review verbatim in spa-owned advertising.** Texas Medical Board § 164.052 treats testimonial reuse in physician ads as substantial legal risk.
9. ❌ **Never send patient-identifying SMS from agency-owned phone numbers.** Always send from the spa's CRM under a signed BAA.
10. ❌ **Never autodial a cellphone without express prior consent.** B2B landlines OK; mobile = manual dial only.

---

## 3. HIPAA — when it applies to us

Med spas touch HIPAA the moment they administer Botox, fillers, lasers, or hormone therapy (anything requiring physician supervision or a standing order). Cash-pay does NOT exempt them. Nearly every prospect spa is a covered entity or at minimum a hybrid entity with PHI in their patient flow.

**For us, this means we are a Business Associate** the moment we touch:
- Patient names + appointment data (review request workflow)
- Patient contact info from spa CRM
- Any PHI in reply text
- Patient session logs that show who came in when

**A signed BAA is non-negotiable with every spa client.** No BAA, no service. The BAA defines:
- What PHI we can access
- What we can do with it (review request operations only)
- How we secure it (encryption at rest + in transit)
- Breach notification obligations (within 60 days to the spa)
- Subcontractor BAAs (if we use VAs, they sign too)

A draft BAA template lives in `compliance/baa-template.md` (TBD — needs lawyer review before use).

---

## 4. Sentiment-neutral solicitation language

This is the load-bearing template. Use exactly this wording or close to it. Words that violate:

- "Five stars" / "5-star" → conditions on sentiment
- "Positive review" → conditions on sentiment
- "If you had a great experience" → conditions on sentiment
- "We need your help" → emotional manipulation
- "Discount for review" / any incentive offer → § 465.4 violation

### Approved SMS template (medical spa)

> Hi [Patient first name], it was great seeing you at [Spa name] today. If you have 30 seconds, we'd love an honest review of your experience: [review link]. Thanks — [Spa name]

Notes:
- "Honest review" = sentiment-neutral
- No procedure mention in the SMS
- No staff name unless the patient already mentioned them
- Send from the spa's existing CRM number; never from agency-owned number
- Send to all patients in a category (everyone who came in for an injectable visit), not just NPS-9+

### Approved email template

> Subject: A quick favor from [Spa name]
>
> Hi [Patient first name],
>
> Thanks for visiting [Spa name] this week. If you have 30 seconds, an honest review on Google means a lot: [link].
>
> Either way, thanks for trusting us.
>
> [Spa team / owner first name]

### Timing

24-72 hours post-visit for one-shot procedures. For multi-session series (laser hair removal, body contouring), wait until session 3 — not session 1 — to capture established satisfaction.

### Frequency

One request per visit. No follow-up "did you leave that review yet?" texts. Once is allowed; nagging is a Google policy violation.

---

## 5. Reply language — public review responses

The spa is the speaker; we draft. The content of the reply is the spa's voice and the spa is legally responsible.

### Approved positive-review reply (4-5 star)

> Thank you for the kind words — we're so glad you had a great experience. We appreciate you taking the time.

OR

> Thank you, this means a lot. Looking forward to seeing you again soon.

Variants are fine. Length is fine. **Do not name procedures, do not name staff, do not confirm patient identity.**

### Approved negative-review reply (1-3 star)

> We take all feedback seriously. Please contact our office manager at [number] so we can learn more about your experience.

OR

> Thank you for letting us know. We'd like to understand what happened — please reach out to [email] so we can address this directly.

**Critical:** Never confirm the person was a patient. Never address procedure specifics. Never argue.

### What requires human review (not automated)

- All 1-3 star reviews
- Any review that names a specific staff member
- Any review that mentions a specific procedure or outcome
- Any review that describes an adverse reaction (these need medical-director review BEFORE we reply)
- Any review that threatens legal action

For these, our system flags → owner or medical director gets notified → human composes reply → we publish.

---

## 6. Photos in reviews

If a patient posts their own before/after in their review on Google: that's the patient's disclosure. No HIPAA issue for the spa.

If the spa (or we on their behalf) **reposts** that image to social, the spa's website, or any owned channel: written, specific, scope-defined consent required.

Consent form must specify:
- Channels where the image will appear
- Duration of use
- Patient's ability to revoke
- Whether face/identifying features are shown

Template: TBD (needs lawyer). Until template exists, don't repost any patient image anywhere.

---

## 7. State medical board overlay

Top 5 ICP states (TX, FL, AZ, GA, TN) — what to know per state:

### Texas — strictest of the five
- **Tex. Occ. Code § 164.052 + Texas Medical Board ethics rules:** Testimonials carry "substantial legal risk." TMB defines testimonial broadly.
- **Practical:** Star ratings on Google are generally treated differently than quoted text. **Don't quote TX spa patient reviews verbatim in spa-owned advertising.** Reviews on Google as user-generated content sit in a grayer zone but TMB has gone after physician ads using testimonials.
- **For us:** Run our standard playbook. Flag TX spas in our CRM with a tag so we never reuse their patient text on the spa's website or our own marketing.

### Florida
- **64B8-11.001 + § 456.072(1)(a):** Testimonials permitted if not false, deceptive, or misleading.
- Written patient consent required for any image reuse.
- Before/after photos must include "results may vary" disclaimer when used in marketing.
- **FL TCPA mini-statute (FTSA):** Aggressive private right of action. Express written consent needed for marketing SMS to patients. Review request SMS (sent from spa's CRM, transactional in nature) sits in a safer category — but spa should have TCPA consent at intake regardless.

### California
- **Bus. & Prof. Code § 651:** Permitted if not misleading; no guaranteed outcomes; must disclose material facts. Violation = misdemeanor + license-actionable.
- We're not currently targeting CA in MVP — but if a spa from CA reaches out, the rules are stricter than TX/FL/AZ/GA/TN.

### Arizona
- Truthful-advertising standards. Arizona Medical Board requires written consent for image use.

### Georgia + Tennessee
- Truthful-advertising standards apply. No state-specific testimonial bans.

---

## 8. TCPA + state mini-TCPA for cold-calling

Federal TCPA:
- **Live calls to business landlines:** Not restricted. B2B is exempt from federal DNC for landlines.
- **Wireless numbers (cell):** Treated as residential regardless of business use. Autodialed or prerecorded calls require prior express consent. **Manual dial to a cell is generally OK** but state rules add restrictions.

State overlay:
- **Texas:** 9am-9pm Mon-Sat (effective Sept 2025)
- **Oregon:** 8am-8pm with 3-call cap (effective Jan 2026)
- **Florida:** FTSA — aggressive private right of action; even B2B benefits from caution
- **Indiana:** Strict B2B-applicable DNC rules
- **Oklahoma:** Recently expanded mini-TCPA

**Operational rules for us:**
- Hand-dial only (no autodialer, no prerecorded messages)
- Prefer business landlines; mobile only when no landline available
- Scrub against state DNC lists for the 12 states with B2B-applicable rules
- Log every opt-out in a CRM with date + source
- Respect callback opt-outs immediately and permanently
- Don't call before 9am or after 8pm prospect's local time (federal rule, plus state-specific narrower windows)

---

## 9. CAN-SPAM for cold email

B2B is **not exempt** from CAN-SPAM. Required:
- Accurate sender info (real name, real reply-to)
- Honest subject lines (no clickbait)
- Physical mailing address in footer
- Working unsubscribe processed within 10 business days
- No false header info, no false routing

Penalty: $51,744 per violating email (2025 adjustment).

---

## 10. Internal operational guardrails

For each customer, our internal process must:

1. **BAA signed before any data flow** — no exceptions, no "we'll get to it"
2. **PHI segregated** — patient data lives in spa's CRM; we access via API/integration, not bulk export
3. **Encryption** — TLS 1.2+ in transit, AES-256 at rest for any cached data
4. **Access logs** — every employee/VA who touches PHI logged with timestamp
5. **Subcontractor BAAs** — if we use VAs (offshore or US), they sign BAAs before touching anything
6. **Breach response plan** — written, tested, executable in <48 hours
7. **Annual HIPAA training** — for both founders and any contractors
8. **State-rule check per spa** — flag in CRM at onboarding (TX/FL/CA/AZ/GA + others if/when added)

---

## 11. Pre-customer-#1 checklist

Before signing the first paying customer, complete:

- [ ] Healthcare attorney review of BAA template
- [ ] Healthcare attorney review of customer agreement (especially: liability, indemnity, scope of work)
- [ ] Choose state of incorporation (Delaware default unless reason otherwise)
- [ ] LLC or C-Corp? (LLC for first 12 months, C-Corp if/when raising)
- [ ] HIPAA training completed (Tom + Max) — HHS HIPAA training portal or paid course (~$200 each)
- [ ] Encryption posture documented (which services we use: Stripe handles PCI, what handles PHI?)
- [ ] Breach response plan written (1-page is fine)
- [ ] Cyber liability insurance quote — most med spa BAAs require us carry it ($1M minimum typical)
- [ ] State DNC list subscriptions for FL, IN, OK, OR, TX
- [ ] Customer agreement clause: "Spa agrees not to offer reviewer incentives" — covers us if they go rogue

---

## 12. The compliance posture to put on the website

Word for word:
> Receipts operates under signed BAAs with every customer. We send sentiment-neutral review requests from your CRM, follow Google Business Profile policies on solicitation, and never incentivize reviewers. Our pricing structure is a service fee per published review — not a payment to reviewers, which is illegal under FTC 16 CFR § 465.4 — and we do not gate, filter, or steer review sentiment. Our reply templates are HIPAA-safe and never disclose patient or procedure information.

This is your differentiator vs. shady GRaaS providers. Wear it.
