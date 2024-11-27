# Ad Hoc Program (Manual Accrual)

## Standard Adhoc Program Items
- MNP M2 (source: edis data)
- MyKad Reader Incentive (source: edis data)
- Program Payout (source: Shu Ting's email)
- Hotlink Prepaid (source: Shu Ting's email)
- Master Dealer Incentive (source: Raju's email)

> Note: Master Dealer payout month is M1, one month after activation month.

### MNP M2

When we say the source is edis data, we mean that the values should be extracted from the database itself.
Here is the query that needs to be run:

```sql
SELECT
    activation_month AS report_month_from,
    original_payout_date AS payout_month_from,
	original_payout_date AS payout_month_to,
	(original_payout_date + INTERVAL '1' MONTH) AS report_month_to,
	'ZCOM' AS dealer_region,
    SUM(amount) / (MAX(activation_date) - MIN(activation_date)) * 30 AS original_accrual_amt
FROM
    (
        WITH mykad AS (
            SELECT
                *
            FROM
                sdbsrc.src_prepaid_ocr
            WHERE
                idcapturedmethod = 'MyKad Reader'
        )
        SELECT
            a.cur_payout_date,
            get_payout_date(a.activation_date, d.mth_of_delay) AS original_payout_date,
            a.cur_process_date,
            'N' AS payment_status,
            'N' AS payout_status,
            a.batch_id,
            a.activation_month,
            C .lob,
            C .business,
            C .channel,
            C .category,
            C .incentive_id,
            C .incentive_plan,
            a.msisdn,
            a.activation_date,
            a.subscriber_id,
            a.subscriber_id_orig,
            a.rateplan,
            a.dealer_code,
            port_in_flag,
            post_to_pre_flag,
            e.evaluation_month AS evaluation_month,
            e.incentive AS cal_amount,
            e.incentive AS amount,
            a.awmi,
            b.idcapturedmethod,
            NULL,
            NULL,
            a.remark5,
            failed_reason,
            'N'
        FROM
            sdbstg.pre_crd_comm_transaction_6mths A
            INNER JOIN mykad b ON a.msisdn = b.msisdn
            AND a.activation_date = b.activation_date
            LEFT JOIN sdbprm.prm_incentive_plan C ON C .incentive_id = 8102
            LEFT JOIN sdbprm.prm_pymt_payout_delay d ON d.incentive_id = C .incentive_id
            LEFT JOIN sdbprm.prm_plan_mykad e ON e.incentive_id = C .incentive_id
            AND a.remark5 = e.dealer_class
            AND b.idcapturedmethod = e.idcapturedmethod
            AND a.rateplan = e.rate_plan
            AND a.awmi BETWEEN e.min_value
            AND e.max_value
            AND a.activation_date BETWEEN e.start_date
            AND e.end_date
        WHERE
            a.activation_date >= '2024-06-01'
    ) AS mykad_incentive
WHERE
    date_trunc('month', activation_date) = date_trunc('month', now())
GROUP BY
    1,2;
```

This is a general note on how to set the following parameters for edis-extracted queries:
```
activation_month = report month from
original_payout_date = payout_month_from, payout_month_to 
report_month_to = payout_month_to + 1 month
dealer region = ZCOM (default)
?column? = original accrual amt 
```

### MyKad Reader Incentive (in edis, same as mnp m2)

The same process as MNP M2, just a different query:

```sql
SELECT
    activation_month,
    original_payout_date,
    SUM(amount) / (MAX(activation_date) - MIN(activation_date)) * 30
FROM
    (
        SELECT
            A .cur_payout_date AS payout_date,
            get_payout_date(A .activation_date, C .mth_of_delay + 1) AS original_payout_date,
            A .cur_process_date AS process_date,
            'N' AS payment_status,
            'N' AS payout_status,
            A .batch_id,
            A .activation_month,
            'Prepaid' AS lob,
            'CBD' AS business,
            'dealer' AS channel,
            'HOTLINK' AS category,
            7,
            'MNP Incentive',
            A .msisdn,
            A .activation_date,
            A .subscriber_id,
            A .subscriber_id_orig,
            A .rateplan,
            A .dealer_code,
            A .port_in_flag AS mnp,
            A .post_to_pre_flag AS post2pre,
            2 AS evaluation_month,
            7.5 AS cal_amount,
            7.5 AS amount,
            'MNP Promotional Incentive' AS remark1,
            NULL AS remark2,
            NULL AS remark3,
            NULL AS remark4,
            A .remark5,
            --Migrant/Mass
            failed_reason AS failed_remark,
            'N' AS paid
        FROM
            sdbstg.pre_crd_comm_transaction_6mths A
            LEFT JOIN sdbprm.prm_pymt_payout_delay C ON C .incentive_id = 7
            AND C .appr_status = 1
        WHERE
            COALESCE(A .dealer_code, '') <> ''
            AND port_in_flag = 'Y'
            AND dealer_code_eligibility = 'Y'
            AND A .activation_date >= '2024-02-01'
            AND NOT EXISTS (
                SELECT
                    *
                FROM
                    (
                        SELECT
                            *,
                            ROW_NUMBER() OVER(
                                PARTITION BY subscriber_id
                                ORDER BY
                                    port_complete_dt DESC
                            ) AS row_num
                        FROM
                            sdbsrc.src_prepaid_mnp
                        WHERE
                            DATE(active_dt) >= get_activation_start_date()
                            AND upper(pre_post) = 'PREPAID'
                            AND get_months_between(DATE(active_dt), DATE(port_complete_dt)) <= 2
                    ) d
                WHERE
                    status <> 'AD'
                    AND row_num = 1
                    AND A .msisdn = d.msisdn
                    AND A .subscriber_id = d.subscriber_id
            )
    ) AS MNP_program
WHERE
    date_trunc('month', activation_date) = date_trunc('month', now())
GROUP BY
    1,
    2
```

- Program Payout
- Hotlink Prepaid (from shuting's email)
- master dealer (from raju's email)
note: master dlr payout is M1, one month after act month

if status as paid, 
	ignore
else if status as accrue, 
	check: 
		did gtm update the budget for accrual amount or change of payout date (either pay early or delay)?
		i.e., regional tactical in SEP-24 activation extend payout date to NOV-24
	if yes, report month also extend 1 more month in order to show in accrual report (finance requirement)
else if status as new, data input into accrual template

this month mykad program abit special due to consistent bonus program payout (jun - sept act and pay in nov)

due to prepaid program ady combine into one general program payout, we need to combine this new accrual to previous accrual and increase the budget

Usually I'll combine with the first/last activation month of the program depends on when gtm send to us
for this time, gtm send in quite late, so I'll combine this new jun-sept with last month 'paid' accrual

firstly ill increase the SEP activation accrual amount as 850,000(previous) + 300,000(new) = 1,150,000
then extend the 'payout date to' from OCT to NOV
and 'report month to' extend to DEC in order to show in report (finance requirement)

AFTER all these 4 done, and new scheme changes updated into prod
	- mnp m2 (do in edis)
	- mykad reader inc (in edis, same as mnp m2)
	- hotlink prepaid (from shuting's email)
	- master dealer (from raju's email)

then can send in email req to L2 to run prepaid accrual