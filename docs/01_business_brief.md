# Business Brief: AI Adoption and Workforce Planning

**Version:** 1.0 · **Date:** November 2026 · **Author:** Anitta Elsa Sebastian
**Status:** Draft. The stakeholder is hypothetical; the data is real and public.

---

## 1. Stakeholder

**Learning & Development (L&D) Manager** at a mid-sized organisation with office, technical and customer-facing roles.

The L&D manager owns next year's training budget and has been asked by leadership to "do something about AI". They need evidence, not hype, to decide where to start.

## 2. Problem statement

Employees already use AI tools, but the organisation does not know **which roles and tasks AI is actually being used for, how well it works on them, or where training or a workflow pilot would pay off first.** Without this evidence, the training budget risks being spread thinly or spent on tasks where AI performs poorly.

## 3. Decision to support

> The L&D manager must choose **three role–task combinations** to investigate for AI training or a small workflow pilot in the next planning cycle.

## 4. Business questions

| # | Question | Why it matters to the decision |
|---|----------|--------------------------------|
| Q1 | Where is AI being used across tasks and occupations? | Shows where demand already exists |
| Q2 | How do consumer (Claude.ai) and business (API) usage patterns differ? | Separates tasks people try by hand from tasks businesses already automate |
| Q3 | Which three role–task combinations deserve a training or pilot investigation, and with what cautions? | The decision itself |

## 5. Metrics (confirmed in data profiling)

| Metric | Definition | Used for |
|--------|------------|----------|
| Usage share | Share of conversations / API records mapped to a task | Q1, Q3 |
| Collaboration mix | Share of directive, task iteration, learning, validation, feedback loop | Q1, Q2 |
| Automation share | Directive + feedback loop as a share of classified conversations | Q2 |
| Speedup | Estimated human-only time ÷ human-with-AI time | Q3 (supporting) |
| Task success rate | Yes ÷ (yes + no); not-classified conversations excluded | Q3 |
| Core task flag | Whether O*NET marks the task as Core or Supplemental for the occupation | Q3 |

All metrics are available per task on both platforms (`onet_task::…` facets). Every metric is calculated once, in SQL, and reused in Power BI.

**Pipeline validation:** top-10 task share reproduces Anthropic's published figures (24.2% Claude.ai, 32.1% API), as do the major-group shares (e.g. Computer and Mathematical 36.1%).

## 6. Data sources

| Dataset | Source | Licence |
|---------|--------|---------|
| Anthropic Economic Index — Claude.ai, 13–20 Nov 2025 | [Hugging Face: Anthropic/EconomicIndex](https://huggingface.co/datasets/Anthropic/EconomicIndex) | CC-BY 4.0 |
| Anthropic Economic Index — 1P API, 13–20 Nov 2025 | Same | CC-BY 4.0 |
| O*NET Task Statements | Same repository (release 2025-03-27) | O*NET (CC-BY 4.0) |
| SOC 2019 structure | Same repository (release 2025-03-27) | Public domain |

## 7. Scope

**In scope**
- Global task-level usage on Claude.ai and the API
- Occupation and occupational-group roll-up (US SOC definitions)
- A shortlist of three role–task pilot candidates with evidence and cautions

**Out of scope (this version)**
- Country comparisons and regressions
- Forecasting or predictive models
- Job-displacement or wage-impact estimates
- Evidence about any specific European workforce

## 8. Deliverables

1. Python data-preparation pipeline with documented checks
2. SQL queries answering Q1–Q3
3. Three-page Power BI dashboard: AI usage overview · Roles and tasks · Pilot opportunities
4. Requirements workbook (stakeholders, requirements, user stories, KPIs, assumptions, traceability)
5. Before/after process map for the top pilot task
6. Pilot proposal and five-slide presentation

## 9. Success criteria

- The L&D manager can name three pilot candidates and explain *why* each was chosen, using numbers from the dashboard
- Every dashboard total reconciles with a saved SQL query
- Every recommendation states an owner, a success metric and a risk

## 10. Known limitations

- **One week of data.** No trends over time.
- **Classifier-generated measures.** Success, autonomy and collaboration are Claude's own assessments of anonymised conversations, not verified outcomes.
- **Selection bias.** Users bring tasks they expect AI to handle, so success rates may look higher than real-world performance.
- **Privacy filtering.** Tasks with very few conversations are removed before release.
- **US occupation definitions.** O*NET and SOC describe US jobs; results are indicative for other labour markets.
- **Unmapped conversations.** 6.5% of Claude.ai and 11.7% of API records match no O*NET task; they count in totals but are never ranked.
- **Mixed SOC versions.** The O*NET task file mixes SOC 2010 and 2019 codes. Major groups are reliable for all; minor groups exist only for 2019 codes (60% of Claude.ai usage), so the dashboard filters by major group.

## 11. Open assumptions

| Assumption | Status | How a real team would validate it |
|------------|--------|-----------------------------------|
| The organisation has roles similar to the shortlisted occupations | Unvalidated | Map shortlisted occupations to internal job titles with HR |
| A pilot can run for 6–8 weeks with one team | Unvalidated | Confirm with the team lead and IT |
| Time per task and error rate can be measured before and after | Unvalidated | Agree a baseline measurement with the team lead |
