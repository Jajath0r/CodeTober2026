WITH mean_catalog AS(
	SELECT 
		product_id,
		name,
		AVG(unit_price_cents) as mean_price_cents
	FROM catalog
	WHERE valid_to IS NULL
)
SELECT 
	c.product_id,
	c.name,
	c.unit_price_cents,
	m.mean_price_cents,
	c.unit_price_cents - m.mean_price_cents as difference_to_mean_cents
FROM 
	catalog c,
	mean_catalog m
WHERE c.valid_to IS NULL
ORDER BY c.product_id;