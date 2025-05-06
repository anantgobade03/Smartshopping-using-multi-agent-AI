# initialize_db.py
from utils.data_loader import DataHandler
from pathlib import Path

def initialize_database():
    data_dir = Path("data")
    handler = DataHandler()
    
    if handler.load_csv_to_db(
        product_csv=data_dir/"product_recommendation_data.csv",
        customer_csv=data_dir/"customer_data_collection.csv"
    ):
        print("Database initialized successfully!")
        print("Sample customer IDs:", handler.get_all_customer_ids()[:5])
    else:
        print("Failed to initialize database")
    
    handler.close()

if __name__ == "__main__":
    initialize_database()