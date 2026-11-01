-- q2_platform_comparison.sql
-- Business question Q2: how do consumer (Claude.ai) and business (API) AI use differ?
-- Requirement: FR-03 (compare platforms by occupational group)
-- Source: data/processed/task_occupation.csv (built in step 6)
-- Method: tasks shared by k occupations contribute 1/k of their counts to each one,
--         so every rate is a weighted average and nothing is counted twice.
-- Usage share = share of records mapped to an occupation (none/not_classified excluded).
-- Check: Claude.ai usage share for Computer and Mathematical = 0.361.

WITH base AS (
    SELECT platform,
           major_group,
           n_alloc,
           success_yes / k_occupations                                AS yes_alloc,
           (success_yes + success_no) / k_occupations                 AS assessed_alloc,
           (collab_directive + collab_feedback_loop) / k_occupations  AS automation_alloc,
           (collab_directive + collab_feedback_loop + collab_task_iteration
            + collab_learning + collab_validation) / k_occupations    AS classified_alloc,
           speedup
    FROM read_csv_auto('data/processed/task_occupation.csv')
),

by_group AS (
    SELECT platform,
           major_group,
           SUM(n_alloc)                                                     AS records,
           SUM(n_alloc) / SUM(SUM(n_alloc)) OVER (PARTITION BY platform)    AS usage_share,
           SUM(yes_alloc) / NULLIF(SUM(assessed_alloc), 0)                  AS success_rate,
           SUM(automation_alloc) / NULLIF(SUM(classified_alloc), 0)         AS automation_share,
           SUM(speedup * n_alloc) FILTER (WHERE speedup IS NOT NULL)
             / NULLIF(SUM(n_alloc) FILTER (WHERE speedup IS NOT NULL), 0)   AS speedup
    FROM base
    GROUP BY platform, major_group
),

claude AS (SELECT * FROM by_group WHERE platform = 'claude_ai'),
api    AS (SELECT * FROM by_group WHERE platform = 'api')

SELECT COALESCE(c.major_group, a.major_group)    AS major_group,
       c.records                                 AS claude_records,
       a.records                                 AS api_records,
       c.usage_share                             AS claude_usage_share,
       a.usage_share                             AS api_usage_share,
       a.usage_share - c.usage_share             AS usage_share_diff,
       a.usage_share / NULLIF(c.usage_share, 0)  AS api_to_claude_ratio,
       c.success_rate                            AS claude_success_rate,
       a.success_rate                            AS api_success_rate,
       c.automation_share                        AS claude_automation_share,
       a.automation_share                        AS api_automation_share,
       a.automation_share - c.automation_share   AS automation_diff,
       c.speedup                                 AS claude_speedup,
       a.speedup                                 AS api_speedup
FROM claude c
FULL OUTER JOIN api a ON c.major_group = a.major_group
ORDER BY claude_usage_share DESC NULLS LAST;