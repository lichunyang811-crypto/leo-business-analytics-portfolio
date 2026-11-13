-- SQLite. Input table: snapshots, with the CSV column names.
-- Preconditions: one row per customer/month, full rectangular snapshots,
-- consecutive months, and nonnegative integer mrr_cents. Validate in app.py first.
WITH history AS (
  SELECT customer_id, month, CAST(mrr_cents AS INTEGER) AS current_mrr,
    LAG(CAST(mrr_cents AS INTEGER)) OVER (
      PARTITION BY customer_id ORDER BY month
    ) AS previous_mrr,
    MAX(CASE WHEN CAST(mrr_cents AS INTEGER) > 0 THEN 1 ELSE 0 END) OVER (
      PARTITION BY customer_id ORDER BY month
      ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING
    ) AS previously_paid
  FROM snapshots
), bridge AS (
  SELECT month,
    SUM(previous_mrr) AS opening_mrr_cents,
    SUM(current_mrr) AS closing_mrr_cents,
    SUM(CASE WHEN previous_mrr = 0 AND previously_paid = 0 THEN current_mrr ELSE 0 END) AS new_cents,
    SUM(CASE WHEN previous_mrr = 0 AND previously_paid = 1 THEN current_mrr ELSE 0 END) AS reactivation_cents,
    SUM(CASE WHEN previous_mrr > 0 AND current_mrr > previous_mrr THEN current_mrr - previous_mrr ELSE 0 END) AS expansion_cents,
    SUM(CASE WHEN current_mrr > 0 AND current_mrr < previous_mrr THEN previous_mrr - current_mrr ELSE 0 END) AS contraction_cents,
    SUM(CASE WHEN previous_mrr > 0 AND current_mrr = 0 THEN previous_mrr ELSE 0 END) AS churn_cents
  FROM history
  WHERE previous_mrr IS NOT NULL
  GROUP BY month
)
SELECT *,
  (opening_mrr_cents + expansion_cents - contraction_cents - churn_cents) * 1.0 /
    NULLIF(opening_mrr_cents, 0) AS net_revenue_retention
FROM bridge
ORDER BY month;
