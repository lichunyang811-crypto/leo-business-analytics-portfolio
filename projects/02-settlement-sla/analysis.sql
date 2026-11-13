-- SQLite; load sample.csv into observations with matching column names.
-- Same strict SLA threshold and excess-time rule as the Python implementation.
SELECT stage,
       COUNT(*) AS observations,
       AVG(CAST(minutes AS REAL)) AS mean_minutes,
       AVG(CASE WHEN CAST(minutes AS REAL) > CAST(sla_minutes AS REAL)
                THEN 1.0 ELSE 0.0 END) AS breach_rate,
       SUM(MAX(0, CAST(minutes AS REAL) - CAST(sla_minutes AS REAL))) AS excess_minutes
FROM observations
GROUP BY stage
ORDER BY stage;
