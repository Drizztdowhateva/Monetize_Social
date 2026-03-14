# Sponsorship + Affiliate Playbook

Use this workflow to pitch sponsorships while keeping affiliate links as a measurable performance channel.

## 1. Build a Sponsor-Ready Offer Stack

Prepare these assets before outreach:
- Channel one-liner and niche focus
- Audience breakdown (size + demographics + intent)
- Last 30-day engagement summary
- Top content formats (short video, long-form, newsletter)
- Proof of affiliate conversion performance
- Clear disclosure language for paid + affiliate placements

## 2. Define Package Tiers

Create 3 tiers so brands can choose quickly:
- Starter: one sponsored post + affiliate link placement
- Growth: sponsored post series + pinned call-to-action + affiliate links
- Launch: sponsored post series + live mention + affiliate links + recap report

Track each package with:
- Flat sponsorship fee
- Affiliate commission or CPA terms
- Deliverables and timeline
- Usage rights and exclusivity limits

## 3. Build a Target List From Your Affiliate Data

1. Filter `data/templates/affiliate_master_fillable.csv` for programs with strong commission potential and niche fit.
2. Prioritize brands where you already have content traction.
3. Add top candidates to `data/templates/outreach_crm_lite.csv`.
4. Mark outreach stage: lead, contacted, negotiating, active, paused.

Priority sponsor targets for this workspace:
- Black Diamond Equipment
- Mining gear brands in your niche
- Colombia partners (tourism, outdoor, regional brands)
- Lenovo
- Amazon
- Sony
- Pioneer
- JL Audio
- Kenwood
- Fluke
- Google
- AWS
- Subaru Racing
- Blue-Point
- Snap-on
- Borla
- Carhartt
- Polaris
- Ski-Doo
- Kicker Audio
- Porsche Motorsport
- Ford Performance (Mustang)
- Chevrolet Performance
- Ducati
- KTM
- Boston Whaler
- Cigarette Racing
- Donzi Marine
- Milwaukee Tool
- Garmin
- Additional targets as they match audience fit and campaign goals

Top 10 focus set (high-performance + outdoor + flight + industry):
- Porsche Motorsport
- Ford Performance (Mustang)
- Chevrolet Performance
- Ducati
- Boston Whaler
- Cigarette Racing
- Donzi Marine
- Kicker Audio
- Milwaukee Tool
- Garmin

## 3A. Locate Sponsor Forms, Requirements, and Qualifications

Use `data/templates/sponsor_discovery_tracker.csv` to track sponsor research.

For each target brand:
1. Start on the official website and check footer links for `Partners`, `Affiliates`, `Creators`, `Media`, `PR`, or `Business`.
2. Use site search with terms: `affiliate`, `partner program`, `sponsorship`, `creator program`, `ambassador`.
3. If no public page is found, capture a direct contact route (`contact us` form, partnerships email, or LinkedIn partner manager).
4. Record all discovered form URLs and whether they are region-specific.
5. Extract and log qualification criteria:
	- Audience size minimums
	- Traffic or engagement expectations
	- Niche/content fit
	- Geographic restrictions
	- Required assets (media kit, analytics screenshots, company details)
	- Compliance requirements (disclosure and platform policy)
6. Mark each item with `Last Verified Date` and a confidence note (`public page`, `email confirmation`, or `pending verification`).

Qualification scoring (simple and repeatable):
- Fit Score (1-5): niche and audience match
- Readiness Score (1-5): assets and proof available now
- Access Score (1-5): easy application path and response likelihood
- Prioritize outreach where total score is 12+.

Vertical taxonomy (for focused prospecting):
- Auto/Racing
- Marine
- Motorcycle
- Tools
- Audio
- Outdoor
- Computers/Cloud
- Flight/Industrial

Budget feasibility step:
- Add `Estimated Investment Amount (USD)` for each sponsor in the tracker.
- In the GUI `Sponsors` tab, set your available investment budget.
- Enable affordable-only filtering to focus on targets within budget.
- Use the vertical filter and total-score ranking to prioritize the best feasible opportunities first.
- In `Hashtag Ads`, use `Top Sponsors -> Hashtags` so campaign hashtags reflect your current top-ranked sponsors.
- Use `Top Sponsors -> Captions` to generate first-draft campaign copy from ranked sponsor priorities.

## 4. Send a Hybrid Sponsorship + Affiliate Pitch

Use your outreach note to ask for both:
- A paid sponsorship placement
- Access to or improved terms in the affiliate program
- Custom landing page, coupon, or UTM tracking support
- Optional co-branded giveaway or product seeding for campaign lift

Message checklist:
- Why your audience matches the offer
- Proposed deliverable package
- Prior affiliate performance snapshot
- Requested next step (15-minute call or terms email)

## 5. Negotiate Measurement and Legal Terms

Before launch, confirm in writing:
- Campaign dates and deliverables
- Payment schedule and invoice terms
- Affiliate attribution window and commission rules
- Required disclosure language and platform compliance
- Reporting cadence (7-day and 30-day recap)

## 6. Launch and Optimize

- Publish sponsored content on schedule.
- Verify affiliate links, coupon codes, and UTM tags.
- Log campaign IDs in your tracker.
- Share early performance to unlock renewal or upsell.
- Propose a recurring sponsorship if conversions are strong.

## 7. Weekly Operating Cadence

- Monday: prospect 5 sponsor-fit brands from affiliate list
- Tuesday: send outreach and follow-ups
- Thursday: negotiate terms and prep creative briefs
- Friday: review clicks, sales, and sponsor reporting status

## 8. Sponsor Discovery Deliverables (Per Brand)

Before moving a brand to `contacted`, ensure these are logged:
- Program or sponsorship form URL
- Application method (web form, email, partner portal)
- Requirements and qualification notes
- Geographic availability and restrictions
- Decision maker/contact path

## 9. Weekly Automation Bundle

Run `Export Weekly Bundle` in the `Sponsors` tab to generate:
- `data/exports/top_sponsors_this_week.csv` (ranked sponsor queue)
- `data/exports/sponsor_followup_sequence.csv` (Day 0/3/7/14 outreach prompts)
- `data/exports/sponsor_attribution_pack.csv` (UTM links + coupon placeholders)
- `data/exports/sponsor_roi_model.csv` (investment and break-even estimates)
- `data/exports/sponsor_kanban_board.md` (status board)
- `data/exports/sponsor_dashboard_summary.csv` (vertical performance summary)
