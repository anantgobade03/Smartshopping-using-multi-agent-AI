# system_orchestrator.py
import sys
from pathlib import Path
from typing import Dict, Optional

sys.path.append(str(Path(__file__).parent))

from agents.customer_agent import CustomerAgent
from agents.product_agent import ProductAgent
from agents.recommendation_agent import RecommendationAgent
from utils.data_loader import DataHandler

class EcommerceRecommendationSystem:
    def __init__(self, db_name='ecommerce.db'):
        self.data_handler = DataHandler(db_name)
        self.product_agent = ProductAgent(self.data_handler)
    
    def get_recommendations(self, customer_id: str, n_recommendations: int = 5) -> Optional[Dict]:
        """Main method to get recommendations for a customer"""
        customer_agent = CustomerAgent(customer_id, self.data_handler)
        if not customer_agent.profile:
            print(f"Customer {customer_id} not found")
            return None
            
        recommendation_agent = RecommendationAgent(customer_agent, self.product_agent)
        recommendations = recommendation_agent.generate_recommendations(n_recommendations)
        
        return {
            'customer_id': customer_id,
            'recommendations': recommendations,
            'customer_preferences': customer_agent.get_preferences()
        }
    
    def close(self):
        """Clean up resources"""
        self.data_handler.close()

if __name__ == "__main__":
    system = EcommerceRecommendationSystem()
    
    try:
        # First check available customers
        # print("Available customers:", system.data_handler.get_all_customer_ids()[:5])
        print("Available customers: All customers avaliable")
        
        # Get recommendations for first available customer
        customer_id = input("Enter customer ID (or press enter for first customer): ").strip()
        if not customer_id:
            customer_id = system.data_handler.get_all_customer_ids()[0]
            print(f"Using customer ID: {customer_id}")
        
        recs = system.get_recommendations(customer_id)
        
        if recs:
            # In system_orchestrator.py, change the output code to:
            print("\nTop Recommendations:")
            for idx, rec in enumerate(recs['recommendations'], 1):
                print(f"{idx}. {rec['Product_ID']} - {rec['Category']} | Price: ₹{rec['Price']} | Rating: {rec['Product_Rating']}")
        else:
            print("No recommendations generated")
        
    finally:
        system.close()