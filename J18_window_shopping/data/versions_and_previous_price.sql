SELECT
	product_id,
	valid_from,
	unit_price_cents,
	ROW_NUMBER() OVER (
		PARTITION BY product_id 
		ORDER BY valid_from) AS version_number,
	LAG(
		unit_price_cents,
		1,
		NULL) OVER (
			PARTITION BY product_id 
			ORDER BY valid_from) AS previous_price_cents
FROM catalog
ORDER BY product_id, version_number;