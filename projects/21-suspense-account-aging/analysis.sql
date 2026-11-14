-- Case-level aging, not invoice FIFO: age starts at the first posting in the case.
WITH balances AS (
 SELECT case_id, MIN(posted_on) AS first_posting,
 SUM(CASE direction WHEN 'debit' THEN amount_cents ELSE -amount_cents END) AS net_cents
 FROM records WHERE posted_on <= '2026-10-31' GROUP BY case_id
)
SELECT case_id, first_posting, net_cents,
 CAST(julianday('2026-10-31') - julianday(first_posting) AS INTEGER) AS age_days
FROM balances WHERE net_cents <> 0 ORDER BY age_days DESC, case_id
