-- SELECT
--     activation_month,
--     lob,business,
--     incentive_id,
--     incentive_type,
--     incentive_period,
--     factor,
--     incentive_plan
-- FROM sdbstg.stg_pos_accrual_amt2 
-- WHERE business = 'CBD'
-- AND lob = 'POSTPAID FLEX'
-- AND incentive_type ='ACTIVATION'
-- ORDER BY incentive_id, incentive_period
-- LIMIT 20;

-- -- Table metadata.
-- SELECT table_catalog, table_schema, table_name, table_type FROM INFORMATION_SCHEMA.TABLES 
-- WHERE 
--     TABLE_NAME LIKE '%rep_prepaid_fin_accrual_program_template'
--     AND TABLE_SCHEMA = 'sdbrep';

-- -- Column metadata.
-- SELECT 
--     table_catalog,
--     table_schema,
--     table_name, 
--     column_name,
--     data_type,
--     column_default
-- FROM 
--     INFORMATION_SCHEMA.COLUMNS 
-- WHERE 
--     TABLE_NAME LIKE '%rep_prepaid_fin_accrual_program_template'
--     AND TABLE_SCHEMA = 'sdbrep';

-- Table contents, sample.
-- SELECT * FROM sdbprm.prm_incentive_plan 
-- WHERE 
--     incentive_plan ~* 'mykad program|migrant program|regional tactical';
select * 
from sdbrep.rep_prepaid_fin_accrual_program_template
WHERE 
    incentive_id::INTEGER IN (8221,8222, 8223)
    AND report_month_from >= (date_trunc('month', CURRENT_DATE) - INTERVAL '3' MONTH)
ORDER BY incentive_id, activation_month;

-- update sdbstg.stg_pos_accrual_amt2 a 
-- set factor = b.factor
-- from sdbprm.prm_pos_finance_accrual_forecast_factor b
-- where a.incentive_type  = b.incentive_type 
-- --a.incentive_id = b.incentive_id
-- and a.lob = b.lob 
-- and a.incentive_period = b.incentive_period
-- and a.business = b.business

-- applying accrual factor.
-- drop table if exists sdbstg.stg_pos_accrual_amt3;
-- create table sdbstg.stg_pos_accrual_amt3 as
-- select a.activation_month,
--        a.incentive_id, 
--        a.business, 
--        a.lob, 
--        a.incentive_plan,
--        coalesce(a.incentive_period,1) as incentive_period,
--        a.gl_code,
--        a.cost_center,
--        a.dealer_region ,
--        null::date as original_payout_date,
--        (((b.forecast_day/b.actual_day::decimal) * a.incentive_amt) * factor)::numeric(18) as accrued_amount
-- from sdbstg.stg_pos_accrual_amt2 a 
-- left join sdbrep.rep_pos_accrual_numerator b 
-- on a.incentive_id = b.incentive_id 
-- and coalesce(a.incentive_type,'') = coalesce(b.incentive_type,'') 
-- ; 

-- --Special Handling for Incentive_id 351, 352 - will refer to forecast_day/actual_day from Postpaid_Vas - 23
-- update sdbstg.stg_pos_accrual_amt3 c 
-- set accrued_amount = (((b.forecast_day/b.actual_day::decimal) * a.incentive_amt) * factor)::numeric(18)
-- from sdbstg.stg_pos_accrual_amt2 a ,sdbrep.rep_pos_accrual_numerator b 
-- --on a.incentive_id = b.incentive_id 
-- where a.incentive_id in ('351','352') and b.incentive_id = '23'
-- and a.incentive_id = c.incentive_id 
-- and a.incentive_period = c.incentive_period 
-- and a.activation_month = c.activation_month 
-- ; 