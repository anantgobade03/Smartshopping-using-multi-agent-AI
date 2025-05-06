# utils/data_loader.py
import pandas as pd
import sqlite3
from pathlib import Path
import json

class DataHandler:
    def __init__(self, db_name='ecommerce.db'):
        self.db_name = db_name
        self.conn = None
        self._initialize_db()
        
    def _initialize_db(self):
        """Initialize SQLite database and tables"""
        self.conn = sqlite3.connect(self.db_name)
        self.conn.execute("PRAGMA foreign_keys = ON")
        
        # Create tables if they don't exist
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS products (
                Product_ID TEXT PRIMARY KEY,
                Category TEXT,
                Subcategory TEXT,
                Price REAL,
                Brand TEXT,
                Average_Rating_of_Similar_Products REAL,
                Product_Rating REAL,
                Customer_Review_Sentiment_Score REAL,
                Holiday TEXT,
                Season TEXT,
                Geographical_Location TEXT,
                Similar_Product_List TEXT,
                Probability_of_Recommendation REAL
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                Customer_ID TEXT PRIMARY KEY,
                Age INTEGER,
                Gender TEXT,
                Location TEXT,
                Browsing_History TEXT,
                Purchase_History TEXT,
                Customer_Segment TEXT,
                Avg_Order_Value REAL,
                Holiday TEXT,
                Season TEXT
            )
        ''')
        self.conn.commit()
    
    def load_csv_to_db(self, product_csv, customer_csv):
        """Load data from CSV files to SQLite database"""
        try:
            # Load product data
            products = pd.read_csv(product_csv)
            products.columns = products.columns.str.strip()  # Clean column names
            products.to_sql('products', self.conn, if_exists='replace', index=False)
            
            # Load customer data
            customers = pd.read_csv(customer_csv)
            customers.columns = customers.columns.str.strip()  # Clean column names
            customers.to_sql('customers', self.conn, if_exists='replace', index=False)
            
            print(f"Successfully loaded {len(products)} products and {len(customers)} customers")
            print("Product columns:", products.columns.tolist())
            print("Customer columns:", customers.columns.tolist())
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False

    
    def get_customer_data(self, customer_id):
        """Retrieve customer data by ID with error handling"""
        query = f"SELECT * FROM customers WHERE Customer_ID = '{customer_id}'"
        result = pd.read_sql(query, self.conn)
        
        if result.empty:
            print(f"No customer found with ID: {customer_id}")
            print("Available customer IDs:", self.get_all_customer_ids())
            return None
        return result.to_dict('records')[0]
    
    def get_all_customer_ids(self):
        """Get list of all customer IDs for debugging"""
        query = "SELECT Customer_ID FROM customers"
        result = pd.read_sql(query, self.conn)
        return result['Customer_ID'].tolist()
    
    # ... rest of the methods remain the same ...
    
    def get_product_data(self, product_id):
        """Retrieve product data by ID"""
        query = f"SELECT * FROM products WHERE product_id = '{product_id}'"
        return pd.read_sql(query, self.conn).to_dict('records')[0]
    
    def get_similar_products(self, product_id):
        """Get similar products for a given product"""
        query = f"SELECT similar_products FROM products WHERE product_id = '{product_id}'"
        result = pd.read_sql(query, self.conn)
        if not result.empty:
            return eval(result.iloc[0]['similar_products'])
        return []
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

# Example usage
if __name__ == "__main__":
    data_dir = Path("data")
    handler = DataHandler()
    handler.load_csv_to_db(
        product_csv=data_dir/"product_recommendation_data.csv",
        customer_csv=data_dir/"customer_data_collection.csv"
    )
    handler.close()