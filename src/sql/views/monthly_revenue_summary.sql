-- Monthly Revenue Recognition Summary
WITH monthly_data AS (
  SELECT 
    FORMAT_DATE('%Y-%m', start_date) as month,
    payment_terms,
    SUM(total_recognized_revenue) as monthly_recognized_revenue,
    SUM(remaining_revenue) as monthly_remaining_revenue,
    COUNT(*) as contracts_count
  FROM `revenue_data.revenue_recognition_current`
  WHERE start_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 12 MONTH)
  GROUP BY month, payment_terms
)

SELECT 
  month,
  payment_terms,
  monthly_recognized_revenue,
  monthly_remaining_revenue,
  contracts_count,
  -- Calculate month-over-month growth
  LAG(monthly_recognized_revenue) OVER (PARTITION BY payment_terms ORDER BY month) as prev_month_revenue,
  ROUND(
    ((monthly_recognized_revenue - LAG(monthly_recognized_revenue) OVER (PARTITION BY payment_terms ORDER BY month)) 
     / NULLIF(LAG(monthly_recognized_revenue) OVER (PARTITION BY payment_terms ORDER BY month), 0)) * 100, 2
  ) as mom_growth_percentage
FROM monthly_data
ORDER BY month DESC, payment_terms;