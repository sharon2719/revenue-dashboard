import pandas as pd
import random
from datetime import datetime, timedelta
import os

def create_mock_data():
    """Generate realistic mock data for the revenue recognition dashboard"""
    
    # Create data directory if it doesn't exist
    os.makedirs('data/mock_data', exist_ok=True)
    
    # 1. SALESFORCE DATA (Client Contracts)
    print("Generating Salesforce (CRM) data...")
    
    clients = ['TechCorp Inc', 'Global NGO', 'Healthcare Plus', 'EduFoundation', 'GreenEnergy Co']
    contract_types = ['Monthly Retainer', 'Project-based', 'Hourly Services', 'Fixed Price']
    
    salesforce_data = []
    for i in range(20):  # 20 contracts
        start_date = datetime.now() - timedelta(days=random.randint(0, 365))
        end_date = start_date + timedelta(days=random.randint(90, 730))  # 3-24 months
        
        contract = {
            'contract_id': f'CON-{1000 + i}',
            'client_name': random.choice(clients),
            'total_value': random.randint(50000, 500000),
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'payment_terms': random.choice(['Net 30', 'Net 15', 'Monthly', 'Quarterly']),
            'contract_type': random.choice(contract_types),
            'status': random.choice(['Active', 'Pending', 'Completed']),
            'monthly_value': random.randint(5000, 50000)
        }
        salesforce_data.append(contract)
    
    df_salesforce = pd.DataFrame(salesforce_data)
    df_salesforce.to_csv('data/mock_data/salesforce_data.csv', index=False)
    print(f"✓ Created salesforce_data.csv with {len(salesforce_data)} contracts")
    
    # 2. HARVEST DATA (Time Tracking)
    print("Generating Harvest (Time Tracking) data...")
    
    employees = ['John Smith', 'Sarah Johnson', 'Mike Wilson', 'Lisa Brown', 'David Lee']
    task_types = ['Consulting', 'Development', 'Analysis', 'Meeting', 'Documentation']
    
    harvest_data = []
    for i in range(200):  # 200 time entries
        entry_date = datetime.now() - timedelta(days=random.randint(0, 180))
        
        entry = {
            'entry_id': f'TIME-{2000 + i}',
            'project_id': f'PROJ-{random.randint(1, 15)}',
            'employee': random.choice(employees),
            'hours': round(random.uniform(0.5, 8.0), 2),
            'hourly_rate': random.choice([75, 100, 125, 150, 175, 200]),
            'date': entry_date.strftime('%Y-%m-%d'),
            'task_type': random.choice(task_types),
            'billable': random.choice([True, False, True, True])  # 75% billable
        }
        harvest_data.append(entry)
    
    df_harvest = pd.DataFrame(harvest_data)
    df_harvest.to_csv('data/mock_data/harvest_data.csv', index=False)
    print(f"✓ Created harvest_data.csv with {len(harvest_data)} time entries")
    
    # 3. PROJECTS DATA (Deliverables & Milestones)
    print("Generating Projects data...")
    
    project_phases = ['Discovery', 'Planning', 'Implementation', 'Testing', 'Deployment']
    
    projects_data = []
    for i in range(15):  # 15 projects
        project = {
            'project_id': f'PROJ-{i + 1}',
            'contract_id': f'CON-{random.randint(1000, 1019)}',
            'project_name': f'Project {chr(65 + i)}',
            'phase': random.choice(project_phases),
            'completion_percentage': random.randint(10, 100),
            'deliverable_type': random.choice(['Software', 'Report', 'Training', 'System']),
            'milestone_date': (datetime.now() + timedelta(days=random.randint(-30, 90))).strftime('%Y-%m-%d'),
            'budget_allocated': random.randint(10000, 100000),
            'actual_spent': random.randint(5000, 80000)
        }
        projects_data.append(project)
    
    df_projects = pd.DataFrame(projects_data)
    df_projects.to_csv('data/mock_data/projects_data.csv', index=False)
    print(f"✓ Created projects_data.csv with {len(projects_data)} projects")
    
    # Display sample data
    print("\n" + "="*50)
    print("SAMPLE DATA PREVIEW:")
    print("="*50)
    
    print("\nSalesforce Data (First 3 rows):")
    print(df_salesforce.head(3).to_string())
    
    print("\nHarvest Data (First 3 rows):")
    print(df_harvest.head(3).to_string())
    
    print("\nProjects Data (First 3 rows):")
    print(df_projects.head(3).to_string())
    
    print("\n" + "="*50)
    print("DATA GENERATION COMPLETE!")
    print("Files created in data/mock_data/:")
    print("- salesforce_data.csv")
    print("- harvest_data.csv") 
    print("- projects_data.csv")
    print("="*50)

if __name__ == "__main__":
    create_mock_data()