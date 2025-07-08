import unittest
from google.cloud import bigquery
import pandas as pd

class TestRevenueRecognition(unittest.TestCase):
    
    def setUp(self):
        self.client = bigquery.Client()
        self.dataset_id = 'revenue_data'
    
    def test_revenue_not_negative(self):
        """Test that no revenue values are negative"""
        query = """
        SELECT COUNT(*) as negative_count
        FROM `revenue_data.revenue_recognition_current`
        WHERE total_recognized_revenue < 0
        """
        result = self.client.query(query).result()
        negative_count = next(iter(result)).negative_count
        self.assertEqual(negative_count, 0, "Found negative revenue values")
    
    def test_revenue_not_exceeding_contract_value(self):
        """Test that recognized revenue doesn't exceed contract value"""
        query = """
        SELECT COUNT(*) as over_recognized_count
        FROM `revenue_data.revenue_recognition_current`
        WHERE total_recognized_revenue > total_value
        """
        result = self.client.query(query).result()
        over_count = next(iter(result)).over_recognized_count
        self.assertEqual(over_count, 0, "Found over-recognized contracts")
    
    def test_all_contracts_have_recognition_method(self):
        """Test that all contracts have a recognition method applied"""
        query = """
        SELECT COUNT(*) as missing_method_count
        FROM `revenue_data.revenue_recognition_current`
        WHERE total_recognized_revenue IS NULL
        """
        result = self.client.query(query).result()
        missing_count = next(iter(result)).missing_method_count
        self.assertEqual(missing_count, 0, "Found contracts without recognition method")

if __name__ == '__main__':
    unittest.main()