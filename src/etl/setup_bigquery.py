import os
from google.cloud import bigquery
import pandas as pd

# Define your Google Cloud Project ID and BigQuery Dataset ID
PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT', 'revenue-dashboard-demo')
DATASET_ID = 'revenue_data' #

# Initialize BigQuery client
client = bigquery.Client(project=PROJECT_ID)

# Define table schemas from your config.py
TABLES_SCHEMA = {
    'salesforce_contracts': {
        'schema': [
            bigquery.SchemaField('contract_id', 'STRING'),
            bigquery.SchemaField('client_name', 'STRING'),
            bigquery.SchemaField('total_value', 'FLOAT'),
            bigquery.SchemaField('start_date', 'DATE'),
            bigquery.SchemaField('end_date', 'DATE'),
            bigquery.SchemaField('payment_terms', 'STRING'),
            bigquery.SchemaField('contract_type', 'STRING'), # Added based on salesforce_data.csv
            bigquery.SchemaField('status', 'STRING'),       # Added based on salesforce_data.csv
            bigquery.SchemaField('monthly_value', 'FLOAT'), # Added based on salesforce_data.csv
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
            bigquery.SchemaField('billable', 'BOOL'), # Added based on harvest_data.csv
        ]
    },
    'project_deliverables': {
        'schema': [
            bigquery.SchemaField('project_id', 'STRING'),
            bigquery.SchemaField('contract_id', 'STRING'),
            bigquery.SchemaField('project_name', 'STRING'),
            bigquery.SchemaField('phase', 'STRING'),           # Added based on projects_data.csv
            bigquery.SchemaField('completion_percentage', 'FLOAT'),
            bigquery.SchemaField('deliverable_type', 'STRING'),
            bigquery.SchemaField('milestone_date', 'DATE'), # Corrected from milstone_date to milestone_date based on projects_data.csv
            bigquery.SchemaField('budget_allocated', 'FLOAT'), # Added based on projects_data.csv
            bigquery.SchemaField('actual_spent', 'FLOAT'),     # Added based on projects_data.csv
        ]
    }
}

def create_dataset():
    """Creates the BigQuery dataset if it doesn't exist."""
    dataset_ref = client.dataset(DATASET_ID)
    try:
        client.get_dataset(dataset_ref)
        print(f"Dataset '{DATASET_ID}' already exists.")
    except Exception:
        dataset = bigquery.Dataset(dataset_ref)
        dataset.location = "US" # You can choose your desired location
        client.create_dataset(dataset)
        print(f"Dataset '{DATASET_ID}' created.")

def create_table(table_name, schema):
    """Creates a BigQuery table with the specified schema, deleting it if it exists."""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
    table_ref = client.dataset(DATASET_ID).table(table_name) # Create a table reference

    try:
        # Check if table exists and delete it
        client.get_table(table_ref)
        print(f"Table '{table_name}' already exists. Deleting and recreating...")
        client.delete_table(table_ref) # Delete the table
        print(f"Table '{table_name}' deleted.")
    except Exception:
        print(f"Table '{table_name}' does not exist, creating new...")

    # Define table properties including partitioning if applicable
    table = bigquery.Table(table_id, schema=schema)
    if table_name == 'harvest_time_entries':
        # Add time partitioning for harvest_time_entries
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field='date' # Partition by the 'date' column
        )
    # Add partitioning for project_deliverables if it also has a date field to partition on
    elif table_name == 'project_deliverables' and 'milestone_date' in [f.name for f in schema]:
        table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field='milestone_date'
        )

    client.create_table(table)
    print(f"Table '{table_name}' created.")

def load_csv_to_table(csv_file_path, table_name, schema):
    """Loads data from a CSV file into a BigQuery table."""
    table_id = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"

    job_config = bigquery.LoadJobConfig(
        schema=schema,
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,  # Skip header row
        autodetect=False,     # Use provided schema
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE, # Overwrite existing data
    )

    with open(csv_file_path, "rb") as source_file:
        job = client.load_table_from_file(source_file, table_id, job_config=job_config)

    job.result() # Wait for the job to complete
    print(f"Loaded {job.output_rows} rows from '{csv_file_path}' into '{table_name}'.")

if __name__ == "__main__":
    create_dataset()

    # Create and load salesforce_contracts table
    create_table('salesforce_contracts', TABLES_SCHEMA['salesforce_contracts']['schema'])
    load_csv_to_table('data/mock_data/salesforce_data.csv', 'salesforce_contracts', TABLES_SCHEMA['salesforce_contracts']['schema'])

    # Create and load project_deliverables table
    create_table('project_deliverables', TABLES_SCHEMA['project_deliverables']['schema'])
    load_csv_to_table('data/mock_data/projects_data.csv', 'project_deliverables', TABLES_SCHEMA['project_deliverables']['schema'])

    # Create and load harvest_time_entries table
    create_table('harvest_time_entries', TABLES_SCHEMA['harvest_time_entries']['schema'])
    load_csv_to_table('data/mock_data/harvest_data.csv', 'harvest_time_entries', TABLES_SCHEMA['harvest_time_entries']['schema'])

    print("\nAll source data loaded into BigQuery.")

    # Instructions to trigger revenue recognition after data loading:
    print("\n--- NEXT STEPS ---")
    print("1. Ensure your 'app.py' and 'src/sql/transformations/revenue_recognition.sql' files")
    print("   contain the corrected SQL for 'total_recognized_revenue'.")
    print("2. Restart your Flask application (if running).")
    print("3. Trigger the revenue recognition table update by visiting:")
    print(f"   http://127.0.0.1:8080/api/refresh_revenue_table (if running Flask locally)")
    print("   OR run your 'pipeline.py' script again.")