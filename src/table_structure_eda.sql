-- server: STG_KEY
-- def: row names of the tables across the environments.
SELECT 
    TABLE_SCHEMA, 
    TABLE_NAME, 
    ORDINAL_POSITION, 
    COLUMN_NAME,  
    DATA_TYPE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME IN (
    'ctrl_pymt_batch_id',
    'prm_pymt_payout_delay',
    'prm_plan_mi_trailing',
    'pymt_prepaid_mi_trailing'
) 
ORDER BY
    TABLE_SCHEMA,
    ORDINAL_POSITION
AND TABLE_SCHEMA ~* 'dev_|prd_';


-- def: row count of the tables across the environments.
SELECT 
    TABLE_SCHEMA, 
    TABLE_NAME,
    COUNT(*) AS column_count
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME IN (
    'ctrl_pymt_batch_id',
    'prm_pymt_payout_delay',
    'prm_plan_mi_trailing',
    'pymt_prepaid_mi_trailing'
) 
AND TABLE_SCHEMA ~* 'dev_|prd_'
GROUP BY 
    TABLE_SCHEMA,
    TABLE_NAME
ORDER BY 
    TABLE_NAME,
    LEFT(TABLE_SCHEMA,3),
    SUBSTRING(TABLE_SCHEMA FROM 4 FOR 20) DESC;