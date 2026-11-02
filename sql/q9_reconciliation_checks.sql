-- q9_reconciliation_checks.sql
-- Requirement NFR-01: every key number reconciles, internally and with Anthropic's report.
-- Runs last (q9) because it reads the outputs of q1-q3.
-- Anthropic figures: Economic Index report "Economic primitives", 15 Jan 2026.

WITH tm      AS (SELECT * FROM read_csv_auto('data/processed/task_metrics.csv')),
     tm_real AS (SELECT * FROM tm WHERE lower(CAST(is_real_task AS VARCHAR)) = 'true'),
     occ     AS (SELECT * FROM read_csv_auto('data/processed/task_occupation.csv')),
     q1      AS (SELECT * FROM read_csv_auto('data/outputs/q1_usage_by_task.csv')),
     q2      AS (SELECT * FROM read_csv_auto('data/outputs/q2_platform_comparison.csv')),
     q3      AS (SELECT * FROM read_csv_auto('data/outputs/q3_pilot_candidates.csv')),

checks AS (
    SELECT 'Usage shares sum to 1 on each platform' AS check_name, 'internal' AS source,
           2.0 AS expected, (SELECT SUM(usage_share) FROM tm) AS actual, 0.002 AS tolerance
    UNION ALL
    SELECT 'Occupation split keeps every record', 'internal',
           (SELECT SUM(n) FROM tm_real), (SELECT SUM(n_alloc) FROM occ), 1
    UNION ALL
    SELECT 'Q2 total equals joined total (Claude.ai)', 'internal',
           (SELECT SUM(n_alloc) FROM occ WHERE platform = 'claude_ai'),
           (SELECT SUM(claude_records) FROM q2), 1
    UNION ALL
    SELECT 'Top-10 task share, Claude.ai', 'Anthropic: 24%', 0.24,
           (SELECT MAX(cumulative_share) FROM q1 WHERE platform = 'claude_ai' AND usage_rank <= 10), 0.01
    UNION ALL
    SELECT 'Top-10 task share, API', 'Anthropic: 32%', 0.32,
           (SELECT MAX(cumulative_share) FROM q1 WHERE platform = 'api' AND usage_rank <= 10), 0.01
    UNION ALL
    SELECT 'Top task share (fix software errors), Claude.ai', 'Anthropic: 6%', 0.06,
           (SELECT usage_share FROM q1 WHERE platform = 'claude_ai' AND usage_rank = 1), 0.005
    UNION ALL
    SELECT 'Computer and Mathematical share, Claude.ai', 'Anthropic: 36%', 0.36,
           (SELECT claude_usage_share FROM q2 WHERE major_group = 'Computer and Mathematical Occupations'), 0.01
    UNION ALL
    SELECT 'Computer and Mathematical share, API', 'Anthropic: 52%', 0.52,
           (SELECT api_usage_share FROM q2 WHERE major_group = 'Computer and Mathematical Occupations'), 0.01
    UNION ALL
    SELECT 'Overall success rate, Claude.ai', 'Anthropic: 67%', 0.67,
           (SELECT SUM(success_yes) / SUM(success_yes + success_no) FROM tm_real WHERE platform = 'claude_ai'), 0.02
    UNION ALL
    SELECT 'Overall success rate, API', 'Anthropic: 49%', 0.49,
           (SELECT SUM(success_yes) / SUM(success_yes + success_no) FROM tm_real WHERE platform = 'api'), 0.02
    UNION ALL
    SELECT 'Q3 duplicate tasks', 'internal', 0,
           (SELECT COUNT(*) - COUNT(DISTINCT task) FROM q3), 0
    UNION ALL
    SELECT 'Q3 rows breaking the eligibility rules', 'internal', 0,
           (SELECT COUNT(*) FROM q3 WHERE claude_records < 100 OR work_share < 0.5), 0
)

SELECT check_name,
       source,
       ROUND(CAST(expected AS DOUBLE), 4)                    AS expected,
       ROUND(CAST(actual AS DOUBLE), 4)                      AS actual,
       ROUND(ABS(CAST(actual AS DOUBLE) - expected), 4)      AS difference,
       CASE WHEN ABS(CAST(actual AS DOUBLE) - expected) <= tolerance
            THEN 'PASS' ELSE 'FAIL' END                      AS result
FROM checks;
