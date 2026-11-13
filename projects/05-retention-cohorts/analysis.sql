-- SQLite; load sample.csv into orders. First observed purchase defines cohort.
-- The recursive month grid includes observed zero-retention months, not future months.
WITH RECURSIVE
months(month) AS (
  SELECT MIN(substr(order_date, 1, 7)) FROM orders
  UNION ALL
  SELECT strftime('%Y-%m', date(month || '-01', '+1 month'))
  FROM months WHERE month < '2026-10'
),
first_purchase AS (
  SELECT customer_id, MIN(substr(order_date, 1, 7)) AS cohort
  FROM orders GROUP BY customer_id
),
cohort_sizes AS (
  SELECT cohort, COUNT(*) AS size FROM first_purchase GROUP BY cohort
),
active AS (
  SELECT f.cohort, substr(o.order_date, 1, 7) AS month,
         COUNT(DISTINCT o.customer_id) AS customers
  FROM orders o JOIN first_purchase f USING(customer_id)
  WHERE o.order_date <= '2026-10-31'
  GROUP BY f.cohort, substr(o.order_date, 1, 7)
)
SELECT c.cohort, m.month, c.size,
       COALESCE(a.customers, 0) AS active_customers,
       COALESCE(a.customers, 0) * 1.0 / c.size AS retention
FROM cohort_sizes c JOIN months m ON m.month >= c.cohort
LEFT JOIN active a ON a.cohort = c.cohort AND a.month = m.month
ORDER BY c.cohort, m.month;
