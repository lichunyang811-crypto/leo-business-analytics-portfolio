WITH items AS (SELECT DISTINCT basket_id, product FROM records),
freq AS (SELECT product, COUNT(*) AS baskets FROM items GROUP BY product),
pairs AS (
 SELECT a.product AS product_a,b.product AS product_b, COUNT(*) AS together
 FROM items a JOIN items b ON a.basket_id=b.basket_id AND a.product<b.product
 GROUP BY a.product,b.product HAVING COUNT(*)>=2
), n AS (SELECT COUNT(DISTINCT basket_id) AS total FROM items)
SELECT p.*, n.total AS basket_count, 1.0*together/n.total AS support,
 1.0*together/fa.baskets AS confidence_a_to_b, 1.0*together/fb.baskets AS confidence_b_to_a,
 1.0*together*n.total/(fa.baskets*fb.baskets) AS lift
FROM pairs p JOIN freq fa ON fa.product=p.product_a JOIN freq fb ON fb.product=p.product_b CROSS JOIN n
ORDER BY lift DESC, together DESC, product_a, product_b
