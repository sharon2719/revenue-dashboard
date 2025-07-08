import os
from google.cloud import bigquery

class ETLConfig:
    """Configuration for ETL pipeline"""
    
    def __init__(self):
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'revenue-dashboard-demo')
        self.dataset_id = 'revenue_data'
        self.client = bigquery.Client(project=self.project_id)
        
    # Table configurations
    TABLES = {
        'salesforce_contracts': {
            'schema': [
                bigquery.SchemaField('contract_id', 'STRING'),
                bigquery.SchemaField('client_name', 'STRING'),
                bigquery.SchemaField('total_value', 'FLOAT'),
                bigquery.SchemaField('start_date', 'DATE'),
                bigquery.SchemaField('end_date', 'DATE'),
                bigquery.SchemaField('payment_terms', 'STRING'),
            ]
        },
        'harvest_time_entries': {
            'schema': [
                bigquery.SchemaField('entry_id', 'STRING'),
                bigquery.SchemaField('project_id', 'STRING'),
                bigquery.SchemaField('employee', 'STRING'),
                bigquery.SchemaField('hours', 'FLOAT'),
                bigquery.SchemaField('hourly_rate', 'FLOAT'),
                bigquery.SchemaField('date', 'DATE'),
                bigquery.SchemaField('task_type', 'STRING'),
            ]
        },
        'project_deliverables': {
            'schema': [
                bigquery.SchemaField('project_id', 'STRING'),
                bigquery.SchemaField('contract_id', 'STRING'),
                bigquery.SchemaField('project_name', 'STRING'),
                bigquery.SchemaField('completion_percentage', 'FLOAT'),
                bigquery.SchemaField('deliverable_type', 'STRING'),
                bigquery.SchemaField('milstone_date)', 'DATE'),
            ]
        }
    }