-- q3_pilot_candidates.sql
-- Business question Q3: which role-task combinations deserve a training or pilot investigation?
-- Requirements: BR-01, FR-04
-- Source: data/processed/task_occupation.csv (step 6)
-- Rule (stated on the dashboard):
--   eligible = Core task for at least one occupation
--              AND >= 100 Claude.ai conversations AND >= 100 assessed for success
--              AND work share >= 0.5 (mainly used for work, not coursework or personal)
--   score    = 0.5 x percentile rank of usage + 0.5 x percentile rank of success rate
--   one row per task; the occupations it is Core for are listed together
-- Sensitivity: ranks are also shown with 0.3/0.7 and 0.7/0.3 weights.
-- Success interval: Wilson 95% (z = 1.96, z^2 = 3.8416).
-- Suggested action: 'Workflow pilot' when businesses already automate the task via the API
--   (API automation share >= 0.8 on >= 100 API records), otherwise 'Training'.

WITH occ AS (
    SELECT * FROM read_csv_auto('data/processed/task_occupation.csv')
),

api AS (
    SELECT task,
           MAX(automation_share) AS api_automation_share,
           MAX(n)                AS api_records
    FROM occ
    WHERE platform = 'api'
    GROUP BY task
),

-- Task-level metrics repeat on every occupation row, so MAX() just picks the value.
claude_tasks AS (
    SELECT task,
           MAX(n)                AS n,
           MAX(success_rate)     AS success_rate,
           MAX(success_assessed) AS success_assessed,
           MAX(automation_share) AS claude_automation_share,
           MAX(work_share)       AS work_share,
           MAX(speedup)          AS speedup,
           STRING_AGG(DISTINCT occupation, '; ')  FILTER (WHERE task_type = 'Core') AS occupations,
           STRING_AGG(DISTINCT major_group, '; ') FILTER (WHERE task_type = 'Core') AS major_groups,
           COUNT(DISTINCT onet_soc_code)          FILTER (WHERE task_type = 'Core') AS core_occupations
    FROM occ
    WHERE platform = 'claude_ai'
    GROUP BY task
),

eligible AS (
    SELECT c.*, a.api_automation_share, a.api_records
    FROM claude_tasks c
    LEFT JOIN api a USING (task)
    WHERE c.core_occupations > 0
      AND c.n >= 100
      AND c.success_assessed >= 100
      AND c.work_share >= 0.5
),

scored AS (
    SELECT *,
           PERCENT_RANK() OVER (ORDER BY n)            AS usage_pr,
           PERCENT_RANK() OVER (ORDER BY success_rate) AS success_pr
    FROM eligible
),

scores AS (
    SELECT *,
           0.5 * usage_pr + 0.5 * success_pr AS pilot_score,
           0.3 * usage_pr + 0.7 * success_pr AS score_success_weighted,
           0.7 * usage_pr + 0.3 * success_pr AS score_usage_weighted,
           (success_rate + 3.8416 / (2 * success_assessed)
             - 1.96 * SQRT(success_rate * (1 - success_rate) / success_assessed
                           + 3.8416 / (4 * success_assessed * success_assessed)))
             / (1 + 3.8416 / success_assessed)                         AS success_ci_lower,
           (success_rate + 3.8416 / (2 * success_assessed)
             + 1.96 * SQRT(success_rate * (1 - success_rate) / success_assessed
                           + 3.8416 / (4 * success_assessed * success_assessed)))
             / (1 + 3.8416 / success_assessed)                         AS success_ci_upper
    FROM scored
)

SELECT RANK() OVER (ORDER BY pilot_score DESC)            AS pilot_rank,
       RANK() OVER (ORDER BY score_success_weighted DESC) AS rank_if_success_weighted,
       RANK() OVER (ORDER BY score_usage_weighted DESC)   AS rank_if_usage_weighted,
       task,
       occupations,
       major_groups,
       n                       AS claude_records,
       work_share,
       success_rate,
       success_ci_lower,
       success_ci_upper,
       claude_automation_share,
       api_automation_share,
       api_records,
       speedup,
       pilot_score,
       CASE WHEN api_automation_share >= 0.8 AND api_records >= 100
            THEN 'Workflow pilot' ELSE 'Training' END AS suggested_action
FROM scores
ORDER BY pilot_rank;
