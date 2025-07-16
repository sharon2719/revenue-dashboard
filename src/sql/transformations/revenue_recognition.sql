-- Fixed Revenue Recognition Calculation
-- Updated to use correct table names from your BigQuery setup

WITH contract_metrics AS (
  SELECT 
    contract_id,
    client_name,
    total_value,
    CAST(start_date AS DATE) AS start_date,
    CAST(end_date AS DATE) AS end_date,
    payment_terms,
    
    -- Calculate contract duration in days
    DATE_DIFF(CAST(end_date AS DATE), CAST(start_date AS DATE), DAY) as contract_duration_days,

    -- Calculate days elapsed
    CASE 
      WHEN CURRENT_DATE() <= CAST(end_date AS DATE) THEN DATE_DIFF(CURRENT_DATE(), CAST(start_date AS DATE), DAY)
      ELSE DATE_DIFF(CAST(end_date AS DATE), CAST(start_date AS DATE), DAY)
    END as days_elapsed
  FROM `revenue_data.salesforce_contracts`
),

project_completion AS (
  SELECT 
    contract_id,
    AVG(completion_percentage) as avg_completion_percentage,
    COUNT(DISTINCT project_id) as total_projects,
    SUM(CASE WHEN completion_percentage = 100 THEN 1 ELSE 0 END) as completed_projects
  FROM `revenue_data.project_deliverables`
  GROUP BY contract_id
),

-- FIXED: Using correct table name 'harvest_time_entries'
time_based_completion AS (
  SELECT 
    pd.contract_id,
    SUM(ht.hours * ht.hourly_rate) as total_time_value,
    SUM(ht.hours) as total_hours_worked
  FROM `revenue_data.project_deliverables` pd
  JOIN `revenue_data.harvest_time_entries` ht ON pd.project_id = ht.project_id
  GROUP BY pd.contract_id
)

SELECT 
  cm.contract_id,
  cm.client_name,
  cm.total_value,
  cm.start_date,
  cm.end_date,
  
  -- Time-based recognition (for time & materials contracts)
  ROUND(
    CASE 
      WHEN cm.payment_terms = 'Time & Materials' THEN 
        COALESCE(tbc.total_time_value, 0)
      ELSE 0
    END, 2
  ) as time_based_revenue,
  
  -- Completion-based recognition (for fixed-price contracts)
  ROUND(
    CASE 
      WHEN cm.payment_terms = 'Fixed Price' THEN 
        cm.total_value * (COALESCE(pc.avg_completion_percentage, 0) / 100)
      ELSE 0
    END, 2
  ) as completion_based_revenue,
  
  -- Milestone-based recognition
  ROUND(
    CASE 
      WHEN cm.payment_terms = 'Milestone' THEN 
        cm.total_value * (COALESCE(pc.completed_projects, 0) / NULLIF(pc.total_projects, 0))
      ELSE 0
    END, 2
  ) as milestone_based_revenue,
  
  -- Total recognized revenue
  -- Total recognized revenue (MODIFIED SECTION)
ROUND(
    CASE 
        WHEN cm.payment_terms = 'Time & Materials' THEN COALESCE(tbc.total_time_value, 0)
        WHEN cm.payment_terms = 'Fixed Price' THEN cm.total_value * (COALESCE(pc.avg_completion_percentage, 0) / 100)
        WHEN cm.payment_terms = 'Milestone' THEN cm.total_value * (COALESCE(pc.completed_projects, 0) / NULLIF(pc.total_projects, 0))
        -- General case for other payment terms (e.g., Monthly, Net 30, Net 15, Quarterly)
        -- Assumes avg_completion_percentage is a relevant metric for recognition across all types not explicitly handled above
        ELSE cm.total_value * (COALESCE(pc.avg_completion_percentage, 0) / 100) 
    END, 2
) as total_recognized_revenue,

-- Remaining revenue to recognize (MODIFIED SECTION)
ROUND(
    cm.total_value - CASE 
        WHEN cm.payment_terms = 'Time & Materials' THEN COALESCE(tbc.total_time_value, 0)
        WHEN cm.payment_terms = 'Fixed Price' THEN cm.total_value * (COALESCE(pc.avg_completion_percentage, 0) / 100)
        WHEN cm.payment_terms = 'Milestone' THEN cm.total_value * (COALESCE(pc.completed_projects, 0) / NULLIF(pc.total_projects, 0))
        -- Also apply the same recognition logic for remaining revenue calculation
        ELSE cm.total_value * (COALESCE(pc.avg_completion_percentage, 0) / 100)
    END, 2
) as remaining_revenue,
  
  -- Additional metrics
  COALESCE(pc.avg_completion_percentage, 0) as avg_completion_percentage,
  COALESCE(tbc.total_hours_worked, 0) as total_hours_worked,
  CURRENT_DATE() as calculation_date

FROM contract_metrics cm
LEFT JOIN project_completion pc ON cm.contract_id = pc.contract_id
LEFT JOIN time_based_completion tbc ON cm.contract_id = tbc.contract_id
ORDER BY cm.total_value DESC;