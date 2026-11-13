-- SQLite. Input table: cells, with the CSV column names.
-- Preconditions: both variants in each segment, unique segment/variant keys,
-- positive users, and conversions between 0 and users. Validate with app.py first.
WITH typed AS (
  SELECT segment, variant, CAST(users AS INTEGER) AS users,
    CAST(conversions AS INTEGER) AS conversions
  FROM cells
), weights AS (
  SELECT segment, SUM(users) * 1.0 / (SELECT SUM(users) FROM typed) AS common_weight
  FROM typed GROUP BY segment
), rates AS (
  SELECT t.variant,
    SUM(t.conversions) * 1.0 / SUM(t.users) AS pooled_rate,
    SUM(w.common_weight * t.conversions * 1.0 / t.users) AS standardized_rate
  FROM typed t JOIN weights w USING(segment)
  GROUP BY t.variant
)
SELECT variant, pooled_rate, standardized_rate FROM rates ORDER BY variant;
