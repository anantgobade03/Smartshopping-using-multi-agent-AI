# # fast_recommendations.py
# import json
# import sqlite3
# from time import time
# from typing import Dict, List

# import pandas as pd
# from tqdm import tqdm  # Progress bar library

# class FastRecommendationEngine:
#     def __init__(self, db_name: str = 'ecommerce.db') -> None:
#         self.db_name = db_name
#         self.conn = sqlite3.connect(db_name)
        
#         # Pre-load all necessary data
#         self._load_data()
    
#     def _load_data(self) -> None:
#         """Load all required data into memory"""
#         # Load all customers at once
#         self.customers = pd.read_sql("SELECT * FROM customers", self.conn)
        
#         # Load all products at once
#         self.products = pd.read_sql("SELECT * FROM products", self.conn)
        
#         # Create fast lookup dictionaries
#         self.products_by_category = self.products.groupby('Category')
#         self.product_dict = self.products.set_index('Product_ID').to_dict('index')
    
#     def _analyze_preferences_fast(self, customer_data: Dict) -> Dict:
#         """Simplified preference analysis without LLM"""
#         # These are simplified heuristics - adjust based on your business rules
#         return {
#             'preferred_categories': list(set(
#                 eval(customer_data['Browsing_History']) + 
#                 eval(customer_data['Purchase_History'])
#             ))[:3],  # Top 3 categories
#             'price_range': (
#                 'low' if customer_data['Avg_Order_Value'] < 2000 else
#                 'high' if customer_data['Avg_Order_Value'] > 5000 else 
#                 'medium'
#             )
#         }
    
#     def _score_product_fast(self, product: Dict, preferences: Dict) -> float:
#         """Optimized scoring function"""
#         score = 0.0
        
#         # Category match (40% weight)
#         if product['Category'] in preferences['preferred_categories']:
#             score += 0.4
        
#         # Price range match (30% weight)
#         price_range = (
#             'low' if product['Price'] < 1000 else
#             'high' if product['Price'] > 5000 else
#             'medium'
#         )
#         if price_range == preferences['price_range']:
#             score += 0.3
        
#         # Product rating (20% weight)
#         score += product['Product_Rating'] * 0.2
        
#         # Sentiment score (10% weight)
#         score += product['Customer_Review_Sentiment_Score'] * 0.1
        
#         return score
    
#     def get_recommendations_fast(self, customer_id: str, n: int = 5) -> List[str]:
#         """Optimized recommendation generation"""
#         customer_data = self.customers[self.customers['Customer_ID'] == customer_id].iloc[0].to_dict()
#         preferences = self._analyze_preferences_fast(customer_data)
        
#         # Get relevant products
#         candidate_products = pd.concat([
#             self.products_by_category.get_group(cat) 
#             for cat in preferences['preferred_categories']
#             if cat in self.products_by_category.groups
#         ])
        
#         # Score and sort
#         candidate_products['score'] = candidate_products.apply(
#             lambda row: self._score_product_fast(row.to_dict(), preferences),
#             axis=1
#         )
        
#         # Return top N product IDs
#         return candidate_products.sort_values('score', ascending=False)['Product_ID'].head(n).tolist()
    
#     def generate_all_recommendations(self, output_file: str = "fast_recommendations.json") -> None:
#         """Batch process all customers"""
#         start_time = time()
#         results = {}
        
#         print("Optimized batch processing started...")
#         for _, row in tqdm(self.customers.iterrows(), total=len(self.customers)):
#             try:
#                 results[row['Customer_ID']] = self.get_recommendations_fast(row['Customer_ID'])
#             except Exception as e:
#                 print(f"\nError processing {row['Customer_ID']}: {str(e)}")
#                 continue
        
#         # Save results
#         with open(output_file, 'w') as f:
#             json.dump(results, f, indent=2)
        
#         print(f"\nProcessed {len(results)} customers in {time()-start_time:.2f} seconds")
#         print(f"Results saved to {output_file}")
    
#     def close(self) -> None:
#         """Close database connection"""
#         self.conn.close()

# if __name__ == "__main__":
#     engine = FastRecommendationEngine()
#     try:
#         engine.generate_all_recommendations()
#     finally:
#         engine.close()


# fast_recommendations.py (Fixed Version)
import json
import sqlite3
from time import time
from typing import Dict, List, Optional
import pandas as pd
from tqdm import tqdm

class FastRecommendationEngine:
    def __init__(self, db_name: str = 'ecommerce.db') -> None:
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self._load_data()
    
    def _load_data(self) -> None:
        """Load and preprocess all data"""
        self.customers = pd.read_sql("SELECT * FROM customers", self.conn)
        self.products = pd.read_sql("SELECT * FROM products", self.conn)
        
        # Get all valid categories
        self.valid_categories = set(self.products['Category'].unique())
        
        # Pre-group products by category
        self.products_by_category = {
            cat: group for cat, group in self.products.groupby('Category')
        }
    
    def _get_valid_preferences(self, customer_data: Dict) -> Dict:
        """Get preferences with only valid categories"""
        try:
            # Combine browsing and purchase history
            all_categories = list(set(
                eval(customer_data['Browsing_History']) + 
                eval(customer_data['Purchase_History'])
            ))
            
            # Filter to only categories that exist in products
            valid_categories = [
                cat for cat in all_categories 
                if cat in self.valid_categories
            ][:3]  # Use top 3 valid categories
            
            return {
                'preferred_categories': valid_categories or list(self.valid_categories)[:3],
                'price_range': (
                    'low' if customer_data['Avg_Order_Value'] < 2000 else
                    'high' if customer_data['Avg_Order_Value'] > 5000 else 
                    'medium'
                )
            }
        except:
            # Fallback if error occurs
            return {
                'preferred_categories': list(self.valid_categories)[:3],
                'price_range': 'medium'
            }
    
    def _score_product(self, product: Dict, preferences: Dict) -> float:
        """Optimized scoring function"""
        score = 0.0
        if product['Category'] in preferences['preferred_categories']:
            score += 0.4
        
        price_range = (
            'low' if product['Price'] < 1000 else
            'high' if product['Price'] > 5000 else
            'medium'
        )
        if price_range == preferences['price_range']:
            score += 0.3
        
        score += product['Product_Rating'] * 0.2
        score += product['Customer_Review_Sentiment_Score'] * 0.1
        return score
    
    def get_recommendations(self, customer_id: str, n: int = 5) -> Optional[List[str]]:
        """Safe recommendation generation"""
        try:
            customer_data = self.customers[
                self.customers['Customer_ID'] == customer_id
            ].iloc[0].to_dict()
            
            preferences = self._get_valid_preferences(customer_data)
            
            # Get products from valid categories
            product_groups = [
                self.products_by_category[cat]
                for cat in preferences['preferred_categories']
                if cat in self.products_by_category
            ]
            
            if not product_groups:
                return None
                
            candidates = pd.concat(product_groups)
            candidates['score'] = candidates.apply(
                lambda row: self._score_product(row.to_dict(), preferences),
                axis=1
            )
            
            return candidates.sort_values('score', ascending=False)['Product_ID'].head(n).tolist()
        except Exception as e:
            print(f"Debug: Error processing {customer_id} - {str(e)}")
            return None
    
    def generate_all_recommendations(self, output_file: str = "recommendations.json") -> None:
        """Batch process with error handling"""
        results = {}
        print("Processing recommendations...")
        
        for _, row in tqdm(self.customers.iterrows(), total=len(self.customers)):
            recs = self.get_recommendations(row['Customer_ID'])
            if recs:  # Only store if recommendations exist
                results[row['Customer_ID']] = recs
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nSuccess! Processed {len(results)}/{len(self.customers)} customers")
        print(f"Results saved to {output_file}")

if __name__ == "__main__":
    engine = FastRecommendationEngine()
    try:
        engine.generate_all_recommendations()
    finally:
        engine.close()