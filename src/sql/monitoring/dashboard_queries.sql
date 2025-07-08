-- Query 1: Daily Revenue Recognition Trend
SELECT 
    DATE(calculation_date) as date,
    SUM(total_recognized_revenue) as daily_recognized_revenue,
    COUNT(*) as contracts_processed
FROM `revenue_data.revenue_recognition_current`
WHERE calculation_date >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY date
ORDER BY date DESC;

-- Query 2: Revenue by Payment Terms
SELECT 
    payment_terms,
    COUNT(*) as contract_count,
    SUM(total_value) as total_contract_value,
    SUM(total_recognized_revenue) as total_recognized_revenue,
    ROUND((SUM(total_recognized_revenue) / SUM(total_value)) * 100, 2) as recognition_percentage
FROM `revenue_data.revenue_recognition_current`
GROUP BY payment_terms
ORDER BY total_recognized_revenue DESC;

-- Query 3: Top Clients by Revenue
SELECT 
    client_name,
    COUNT(*) as contract_count,
    SUM(total_value) as total_contract_value,
    SUM(total_recognized_revenue) as total_recognized_revenue,
    SUM(remaining_revenue) as remaining_revenue
FROM `revenue_data.revenue_recognition_current`
GROUP BY client_name
ORDER BY total_recognized_revenue DESC
LIMIT 10;