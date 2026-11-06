# Pilot Proposal: AI-Assisted Work for Three Roles

**For:** L&D Manager (hypothetical stakeholder) · **Version:** 1.0 · **Date:** November 2026
**Evidence:** Anthropic Economic Index, Claude.ai and 1P API, 13–20 Nov 2025 · see the [dashboard](../dashboard/03_pilot_opportunities.png)

## Recommendation

Run a 6–8 week pilot in **three role–task areas**, with a human review on every AI output:

| # | Role | Task | Action | Why |
|---|---|---|---|---|
| 1 | Copy Writers | Edit or rewrite existing copy | **Training** | Highest score of 336 work tasks; success 93% (92–94%); 81% work use |
| 2 | Interpreters and Translators | Translate written materials | **Workflow pilot** | Success 87% (86–88%); businesses already automate 98% of this task via the API |
| 3 | Correspondence Clerks | Compose replies to customer correspondence | **Training** | Success 94% (93–95%); 66% work use; estimated speedup about 3.7× |

All three remain in the top 6 when the score is weighted 30/70 or 70/30 between usage and success, so the choice is robust.

## How the shortlist was built

1. **Eligible:** Core tasks for their occupation, with at least 100 Claude.ai conversations, at least 100 assessed for success, and at least 50% work use (not coursework or personal use).
2. **Scored:** 50% usage rank + 50% success rank. One row per task.
3. **Chose** three from different roles, so the pilot tests different kinds of work.
4. **Action:** *workflow pilot* where businesses already automate the task (API automation at least 80%); otherwise *training*.

## Pilot design: customer correspondence (detailed example)

The process change is shown in [`process_map.png`](process_map.png).

| | Today (AS-IS) | Pilot (TO-BE) |
|---|---|---|
| Drafting | Clerk writes every reply from scratch | AI drafts from an approved prompt template |
| Personal data | In the reply as needed | Removed before drafting when not needed |
| Quality check | Clerk proofreads own draft | Clerk reviews facts, amounts, tone and policy; edits or rewrites if needed |
| Sending | After proofreading | Only after human approval |

**Scope (to confirm with the team lead):** one correspondence team, 6–8 weeks, routine inquiries first; complaints and damage claims only after the first review.

## Success metrics

Measure a **2-week baseline before the pilot**, then the same metrics during it. Targets are agreed with the team lead after the baseline.

| Metric | How it is measured | Why it matters |
|---|---|---|
| Time per reply | Logged per reply, before vs during | Is the speedup real in our work? |
| Edit rate | Share of AI drafts changed substantially before sending | Is the AI draft good enough to save time? |
| Error rate | Replies corrected after sending, or escalated | Does quality hold? |
| Customer outcome | Follow-up complaints on pilot replies | Does the customer notice a difference? |
| Employee view | Short survey at weeks 2 and 6 | Will people keep using it? |

## Decision on review: option A or B

| | A: Human approves every draft (chosen) | B: Spot-check 1 in 5 drafts |
|---|---|---|
| Gains | Safe for personal data and money amounts; builds trust | Larger time savings |
| Risks | Smaller time savings | Errors reach customers; data protection risk |

**Choice: A.** The data shows success rates around 87–94% on these tasks, which means roughly 1 in 8 to 1 in 16 outputs still need correcting. B can be tested later if the edit and error rates are low.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Personal or financial data entered into the AI tool | IT approves the tool; clerks remove data not needed for the draft |
| Wrong amounts or facts in replies | Mandatory human review (option A) |
| Legal translations with errors | Expert review for legal documents; start with non-legal texts |
| Brand voice drifts in copy | Style guide in the prompt template; editor sign-off |
| Results do not transfer to our organisation | Evidence is from US occupations and one week of data; the pilot measures real outcomes before any rollout |

## Owners

| Area | Owner |
|---|---|
| Pilot sponsor and budget | L&D Manager |
| Day-to-day running and baseline | Team leads of the three roles |
| Tool approval and data handling | IT / Security |
| Measurement and reporting | Data Analyst |

## Decision needed

Approve a 6–8 week pilot in the three areas above, starting with customer correspondence, with a 2-week baseline and a review at week 4.

## Limitations of the evidence

One week of data · success is Claude's own assessment, not a verified outcome · users bring tasks they expect to work, so real success may be lower · small groups are hidden for privacy · US occupation definitions.
