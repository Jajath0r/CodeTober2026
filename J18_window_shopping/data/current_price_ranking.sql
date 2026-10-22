SELECT 
	product_id,
    name,
    unit_price_cents,
    ROW_NUMBER() OVER (
        ORDER BY unit_price_cents DESC,
         product_id) AS price_position
FROM catalog
WHERE valid_to IS NULL;