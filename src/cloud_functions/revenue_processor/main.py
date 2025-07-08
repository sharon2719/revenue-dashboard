from datetime import datetime
import functions_framework
from google.cloud import bigquery
from flask import jsonify
import logging

@functions_framework.http
def process_revenue_recognition(request):
    """
    Cloud Function to process revenue recognition
    Triggered by HTTP request or Cloud Scheduler
    """
    
    try:
        client = bigquery.Client()

        query = """
        CREATE OR REPLACE TABLE `revenue_data.revenue_recognition_current` AS
        SELECT * FROM `revenue_data.revenue_recognition_view`
        """
        
        job = client.query(query)
        job.result()  # Wait for completion
        
        summary_query = """
        SELECT 
            COUNT(*) as contracts_processed,
            SUM(total_recognized_revenue) as total_revenue_recognized,
            CURRENT_TIMESTAMP() as processed_at
        FROM `revenue_data.revenue_recognition_current`
        """
        
        result = client.query(summary_query).result()
        summary = next(iter(result))
        
        return jsonify({
            'status': 'success',
            'message': 'Revenue recognition processed successfully',
            'contracts_processed': summary.contracts_processed,
            'total_revenue_recognized': float(summary.total_revenue_recognized),
            'processed_at': summary.processed_at.isoformat()
        }), 200

    except Exception as e:
        logging.error(f"Error processing revenue recognition: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@functions_framework.http
def health_check(request):
    """Simple health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()}), 200
