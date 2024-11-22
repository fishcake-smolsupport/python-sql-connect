SELECT b.pg1 AS product_group1, b.item_id AS kenan_id, b.item_desc AS kenan_desc,  a.category_type, a.item_id AS edis_id, a.item_desc AS edis_desc
FROM edis_list_full a 
INNER JOIN kenan_list_full b
	ON a.item_id = b.item_id AND a.category_type = b.category_type
ORDER BY category_type DESC;