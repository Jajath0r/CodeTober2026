WITH delta_cents AS (
	SELECT 
		catalog.product_id,
		catalog.valid_from,
		catalog.unit_price_cents,
		catalog.unit_price_cents - LAG(
			catalog.unit_price_cents,
			1,
			NULL) OVER (
				PARTITION BY catalog.product_id
				ORDER BY catalog.valid_from
			)as delta_cents
	FROM catalog
)
SELECT 
	product_id,
	valid_from,
	unit_price_cents,
	delta_cents,
	COALESCE(SUM(delta_cents) OVER (PARTITION BY product_id ORDER BY product_id, valid_from ROWS UNBOUNDED PRECEDING),0) AS cumulative_delta_cents
FROM 
	delta_cents
ORDER BY 
	product_id,
	valid_from
;