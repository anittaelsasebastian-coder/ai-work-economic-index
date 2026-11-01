-- q1_usage_by_task.sql
-- Business question Q1: which tasks is AI used for most, on each platform?
-- Requirement: FR-01 (top tasks by usage share)
-- Source: data/processed/task_metrics.csv (built in step 4)
-- Check: cumulative_share at usage_rank 10 = 0.242 (Claude.ai) and 0.321 (API),
--        which reproduces Anthropic's published top-10 concentration.
-- Shares are kept as fractions (0.06 = 6%); Power BI formats them as percentages.

WITH real_tasks AS (
    SELECT platform, task, n, usage_share, success_rate, success_assessed,
           automation_share, augmentation_share, speedup
    FROM read_csv_auto('data/processed/task_metrics.csv')
    -- none / not_classified are placeholders, not tasks: kept in totals, never ranked
    WHERE lower(CAST(is_real_task AS VARCHAR)) = 'true'
),

ranked AS (
    SELECT *,
           RANK() OVER (PARTITION BY platform ORDER BY n DESC) AS usage_rank,
           SUM(usage_share) OVER (
               PARTITION BY platform ORDER BY n DESC
               ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
           ) AS cumulative_share
    FROM real_tasks
)

SELECT platform,
       usage_rank,
       task,
       n AS records,
       usage_share,
       cumulative_share,
       success_rate,
       success_assessed,
       automation_share,
       augmentation_share,
       speedup
FROM ranked
ORDER BY platform, usage_rank;