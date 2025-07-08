import pandas as pd
from google.cloud import bigquery
from datetime import datetime, timedelta
import logging
from config import ETLConfig

class RevenuePipeline:
    """Main ETL pipeline for revenue recognition"""
    
    def __init__(self):
        self.config = ETLConfig()
        self.client = self.config.client
        self.dataset_id = self.config.dataset_id
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def create_revenue_recognition_table(self):
        """Create the main revenue recognition table"""
        
        # Read the SQL file
        with open('src/sql/transformations/revenue_recognition.sql', 'r') as file:
            sql_query = file.read()
        
        # Create table from query
        table_id = f"{self.config.project_id}.{self.dataset_id}.revenue_recognition_current"
        
        job_config = bigquery.QueryJobConfig(
            destination=table_id,
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        )
        
        query_job = self.client.query(sql_query, job_config=job_config)
        query_job.result()  # Wait for the job to complete
        
        self.logger.info(f"Revenue recognition table created: {table_id}")
        return table_id
    
    def validate_data_quality(self):
        """Run data quality checks"""
        
        checks = []
        
        # Check 1: No negative revenue
        query = """
        SELECT COUNT(*) as negative_revenue_count
        FROM `revenue_data.revenue_recognition_current`
        WHERE total_recognized_revenue < 0
        """
        result = self.client.query(query).result()
        negative_count = next(iter(result)).negative_revenue_count
        checks.append(("Negative Revenue Check", negative_count == 0, f"Found {negative_count} negative values"))
        
        # Check 2: Revenue doesn't exceed contract value
        query = """
        SELECT COUNT(*) as over_recognized_count
        FROM `revenue_data.revenue_recognition_current`
        WHERE total_recognized_revenue > total_value
        """
        result = self.client.query(query).result()
        over_count = next(iter(result)).over_recognized_count
        checks.append(("Over-recognition Check", over_count == 0, f"Found {over_count} over-recognized contracts"))
        
        # Check 3: All contracts have recognition method
        query = """
        SELECT COUNT(*) as missing_method_count
        FROM `revenue_data.revenue_recognition_current`
        WHERE total_recognized_revenue IS NULL
        """
        result = self.client.query(query).result()
        missing_count = next(iter(result)).missing_method_count
        checks.append(("Recognition Method Check", missing_count == 0, f"Found {missing_count} contracts without recognition"))
        
        # Log results
        for check_name, passed, message in checks:
            if passed:
                self.logger.info(f"✅ {check_name}: PASSED")
            else:
                self.logger.warning(f"❌ {check_name}: FAILED - {message}")
        
        return all(check[1] for check in checks)
    
    def generate_summary_report(self):
        """Generate summary statistics"""
        
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
        summary = next(iter(result))
        
        print("\n" + "="*50)
        print("REVENUE RECOGNITION SUMMARY")
        print("="*50)
        print(f"Total Contracts: {summary.total_contracts}")
        print(f"Total Contract Value: ${summary.total_contract_value:,.2f}")
        print(f"Total Recognized Revenue: ${summary.total_recognized_revenue:,.2f}")
        print(f"Total Remaining Revenue: ${summary.total_remaining_revenue:,.2f}")
        print(f"Average Completion: {summary.avg_completion_percentage}%")
        print(f"Unique Clients: {summary.unique_clients}")
        print(f"Recognition Rate: {(summary.total_recognized_revenue/summary.total_contract_value)*100:.1f}%")
        print("="*50)
        
        return summary
    
    def run_full_pipeline(self):
        """Run the complete ETL pipeline"""
        
        self.logger.info("Starting revenue recognition pipeline...")
        
        try:
            # Step 1: Create revenue recognition table
            self.create_revenue_recognition_table()
            
            # Step 2: Run data quality checks
            if self.validate_data_quality():
                self.logger.info("All data quality checks passed!")
            else:
                self.logger.warning("Some data quality checks failed. Review the logs.")
            
            # Step 3: Generate summary report
            self.generate_summary_report()
            
            self.logger.info("Pipeline completed successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}")
            return False

# Run the pipeline
if __name__ == "__main__":
    pipeline = RevenuePipeline()
    success = pipeline.run_full_pipeline()