from google.cloud import bigquery
import pandas as pd
import os

def setup_bigquery():
    """Set up BigQuery dataset and load mock data"""
    
    # Initialize BigQuery client
    client = bigquery.Client()
    
    # Dataset reference
    dataset_id = "revenue_data"
    dataset_ref = client.dataset(dataset_id)
    
    print(f"Setting up BigQuery dataset: {dataset_id}")
    
    # Load and upload each CSV file
    tables_to_create = [
        {
            'file': 'data/mock_data/salesforce_data.csv',
            'table_name': 'salesforce_contracts',
            'description': 'Contract data from Salesforce CRM'
        },
        {
            'file': 'data/mock_data/harvest_data.csv', 
            'table_name': 'harvest_time_entries',
            'description': 'Time tracking data from Harvest'
        },
        {
            'file': 'data/mock_data/projects_data.csv',
            'table_name': 'project_deliverables', 
            'description': 'Project and deliverable data'
        }
    ]
    
    successful_tables = []  # Track successfully created tables
    
    for table_info in tables_to_create:
        try:
            # Read CSV file
            df = pd.read_csv(table_info['file'])
            print(f"\n📊 Loading {table_info['table_name']}...")
            print(f"   Rows: {len(df)}, Columns: {len(df.columns)}")
            
            # Create table reference
            table_ref = dataset_ref.table(table_info['table_name'])
            
            # Configure the load job
            job_config = bigquery.LoadJobConfig(
                autodetect=True,  # Auto-detect schema
                write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,  # Overwrite if exists
                source_format=bigquery.SourceFormat.CSV,
                skip_leading_rows=1,  # Skip header row
            )
            
            # Load data from DataFrame
            job = client.load_table_from_dataframe(
                df, table_ref, job_config=job_config
            )
            
            # Wait for the job to complete
            job.result()
            
            # MODIFIED: Add detailed verification after table creation
            table = client.get_table(table_ref)
            print(f"✓ Table {table_info['table_name']} created successfully")
            print(f"   Rows: {table.num_rows}, Columns: {len(table.schema)}")
            print(f"   Column names: {[field.name for field in table.schema]}")
            
            # Check if table has data
            if table.num_rows > 0:
                print("✓ Table has data, proceeding...")
                successful_tables.append(table_info['table_name'])
            else:
                print("❌ Table is empty - data loading may have failed")
            
        # MODIFIED: Better exception handling
        except Exception as e:
            print(f"❌ Error creating table {table_info['table_name']}: {str(e)}")
            print(f"   Error type: {type(e).__name__}")
            continue  # Skip to next table instead of stopping
    
    # Only run test query if salesforce_contracts was created successfully
    if 'salesforce_contracts' in successful_tables:
        print("\n🔍 Testing with a sample query...")
        
        query = """
        SELECT 
            client_name,
            total_value,
            contract_type,
            status
        FROM `revenue_data.salesforce_contracts`
        WHERE status = 'Active'
        LIMIT 5
        """
        
        try:
            query_job = client.query(query)
            results = query_job.result()
            
            print("✓ Sample query results:")
            for row in results:
                print(f"   {row.client_name}: ${row.total_value:,} ({row.contract_type})")
        
        except Exception as e:
            print(f"❌ Error running test query: {str(e)}")
            print(f"   Error type: {type(e).__name__}")
    else:
        print("\n❌ Skipping test query - salesforce_contracts table not available")
    
    print("\n" + "="*50)
    print("BIGQUERY SETUP COMPLETE!")
    print("✓ Dataset created: revenue_data")
    print(f"✓ Tables created successfully: {', '.join(successful_tables)}")
    print("="*50)

if __name__ == "__main__":
    setup_bigquery()