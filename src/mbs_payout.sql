SELECT dealer_code, dealer_name, payout_status, incentive_type, adjustment_reason, SUM(final_amount)
FROM sdbpayment.pymt_postpaid_payment
WHERE payout_status ~* 'compute'
AND payout_date = date_trunc('month', CURRENT_DATE)
AND business = 'MBS'
GROUP BY 1,2,3,4,5
ORDER BY 1,6 DESC;
