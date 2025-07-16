from flask import Flask, render_template, jsonify, request
from google.cloud import bigquery
import pandas as pd
import plotly.graph_objs as go
import plotly.utils
import json
from datetime import datetime, timedelta
import os

app = Flask(__name__)

class DashboardData:
    def __init__(self):
        self.client = bigquery.Client()
        self.dataset_id = 'revenue_data'
        # Automatically create/update table on startup
        self.create_revenue_recognition_table()
    
    def create_revenue_recognition_table(self):
        """Create or update the revenue recognition table"""
        query = """
        CREATE OR REPLACE TABLE `revenue_data.revenue_recognition_current` AS
        -- Your existing SQL query here
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
            
            -- Remaining revenue to recognize
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
        ORDER BY cm.total_value DESC
        """
        
        try:
            job = self.client.query(query)
            job.result()  # Wait for completion
            print("Revenue recognition table created/updated successfully")
            return True
        except Exception as e:
            print(f"Error creating revenue recognition table: {str(e)}")
            return False
    
    def get_revenue_summary(self):
        """Get overall revenue summary"""
        query = """
        SELECT 
            COUNT(*) as total_contracts,
            SUM(total_value) as total_contract_value,
            SUM(total_recognized_revenue) as total_recognized_revenue,
            SUM(remaining_revenue) as total_remaining_revenue,
            ROUND(AVG(avg_completion_percentage), 2) as avg_completion_percentage,
            COUNT(DISTINCT client_name) as unique_clients
        FROM `revenue_data.revenue_recognition_current`
        """
        
        result = self.client.query(query).result()
        return next(iter(result))
    
    def get_revenue_by_payment_terms(self):
        """Get revenue breakdown by payment terms - JOIN with contracts table"""
        query = """
        SELECT 
            sc.payment_terms,
            COUNT(*) as contract_count,
            SUM(rrc.total_value) as total_contract_value,
            SUM(rrc.total_recognized_revenue) as total_recognized_revenue,
            -- Ensure no division by zero for recognition_percentage
            ROUND(SAFE_DIVIDE(SUM(rrc.total_recognized_revenue), SUM(rrc.total_value)) * 100, 2) as recognition_percentage
        FROM `revenue_data.revenue_recognition_current` rrc
        JOIN `revenue_data.salesforce_contracts` sc ON rrc.contract_id = sc.contract_id
        GROUP BY sc.payment_terms
        ORDER BY total_recognized_revenue DESC
        """
        
        results = self.client.query(query).result()
        return [dict(row) for row in results]
    
    def get_top_clients(self, limit=10):
        """Get top clients by recognized revenue"""
        query = f"""
        SELECT 
            client_name,
            COUNT(*) as contract_count,
            SUM(total_value) as total_contract_value,
            SUM(total_recognized_revenue) as total_recognized_revenue,
            SUM(remaining_revenue) as remaining_revenue
        FROM `revenue_data.revenue_recognition_current`
        GROUP BY client_name
        ORDER BY total_recognized_revenue DESC
        LIMIT {limit}
        """
        
        results = self.client.query(query).result()
        return [dict(row) for row in results]
    
    def get_monthly_trend(self, months=12):
        """Get monthly revenue trend"""
        query = f"""
        SELECT 
            FORMAT_DATE('%Y-%m', start_date) as month,
            SUM(total_recognized_revenue) as monthly_recognized_revenue,
            COUNT(*) as contracts_count
        FROM `revenue_data.revenue_recognition_current`
        WHERE start_date >= DATE_SUB(CURRENT_DATE(), INTERVAL {months} MONTH)
        GROUP BY month
        ORDER BY month
        """
        
        results = self.client.query(query).result()
        return [dict(row) for row in results]
    
    def get_contract_details(self):
        """Get detailed contract information with payment terms"""
        query = """
        SELECT 
            rrc.contract_id,
            rrc.client_name,
            rrc.total_value,
            rrc.total_recognized_revenue,
            rrc.remaining_revenue,
            rrc.avg_completion_percentage,
            sc.payment_terms,
            rrc.start_date,
            rrc.end_date
        FROM `revenue_data.revenue_recognition_current` rrc
        JOIN `revenue_data.salesforce_contracts` sc ON rrc.contract_id = sc.contract_id
        ORDER BY rrc.total_value DESC
        """
        
        results = self.client.query(query).result()
        return [dict(row) for row in results]
    
    def get_revenue_by_recognition_type(self):
        """Get revenue breakdown by recognition type"""
        query = """
        SELECT 
            sc.payment_terms,
            SUM(rrc.time_based_revenue) as time_based_revenue,
            SUM(rrc.completion_based_revenue) as completion_based_revenue,
            SUM(rrc.milestone_based_revenue) as milestone_based_revenue,
            SUM(rrc.total_recognized_revenue) as total_recognized_revenue
        FROM `revenue_data.revenue_recognition_current` rrc
        JOIN `revenue_data.salesforce_contracts` sc ON rrc.contract_id = sc.contract_id
        GROUP BY sc.payment_terms
        ORDER BY total_recognized_revenue DESC
        """
        
        results = self.client.query(query).result()
        return [dict(row) for row in results]

# Initialize data handler
data_handler = DashboardData()

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/summary')
def api_summary():
    """API endpoint for summary data"""
    try:
        summary = data_handler.get_revenue_summary()
        # Ensure division by zero is handled for recognition_rate
        recognition_rate = 0.0
        if summary.total_contract_value is not None and summary.total_contract_value != 0:
            recognition_rate = round((summary.total_recognized_revenue / summary.total_contract_value) * 100, 2)

        return jsonify({
            'total_contracts': summary.total_contracts,
            'total_contract_value': float(summary.total_contract_value),
            'total_recognized_revenue': float(summary.total_recognized_revenue),
            'total_remaining_revenue': float(summary.total_remaining_revenue),
            'avg_completion_percentage': float(summary.avg_completion_percentage),
            'unique_clients': summary.unique_clients,
            'recognition_rate': recognition_rate
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/payment_terms')
def api_payment_terms():
    """API endpoint for payment terms breakdown"""
    try:
        data = data_handler.get_revenue_by_payment_terms()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/top_clients')
def api_top_clients():
    """API endpoint for top clients"""
    try:
        limit = request.args.get('limit', 10, type=int)
        data = data_handler.get_top_clients(limit)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/monthly_trend')
def api_monthly_trend():
    """API endpoint for monthly trend data"""
    try:
        months = request.args.get('months', 12, type=int)
        data = data_handler.get_monthly_trend(months)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contracts')
def api_contracts():
    """API endpoint for contract details"""
    try:
        data = data_handler.get_contract_details()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recognition_types')
def api_recognition_types():
    """API endpoint for revenue recognition types breakdown"""
    try:
        data = data_handler.get_revenue_by_recognition_type()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/refresh_revenue_table')
def refresh_revenue_table():
    """Refresh the revenue recognition table"""
    try:
        success = data_handler.create_revenue_recognition_table()
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Revenue recognition table refreshed successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to refresh revenue recognition table'
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error refreshing table: {str(e)}'
        }), 500

@app.route('/api/initialize')
def initialize_dashboard():
    """Initialize the dashboard by creating necessary tables"""
    try:
        # Create the revenue recognition table
        table_created = data_handler.create_revenue_recognition_table()
        
        if table_created:
            # Test if we can query the table
            summary = data_handler.get_revenue_summary()
            return jsonify({
                'status': 'success',
                'message': 'Dashboard initialized successfully',
                'total_contracts': summary.total_contracts
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to initialize dashboard'
            }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error initializing dashboard: {str(e)}'
        }), 500

@app.route('/api/test')
def test_connection():
    """Test BigQuery connection and create table if needed"""
    try:
        # Test basic connection
        query = "SELECT 1 as test"
        result = data_handler.client.query(query).result()
        
        # Test if tables exist
        tables_query = """
        SELECT table_name 
        FROM `revenue_data.INFORMATION_SCHEMA.TABLES` 
        WHERE table_name IN ('revenue_recognition_current', 'salesforce_contracts', 'project_deliverables', 'harvest_time_entries')
        """
        tables_result = data_handler.client.query(tables_query).result()
        tables = [row.table_name for row in tables_result]
        
        # If revenue_recognition_current doesn't exist, create it
        if 'revenue_recognition_current' not in tables:
            print("Revenue recognition table not found, creating it...")
            data_handler.create_revenue_recognition_table()
            tables.append('revenue_recognition_current')
        
        return jsonify({
            'status': 'success', 
            'message': 'BigQuery connection working',
            'available_tables': tables
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)