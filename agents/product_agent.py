from typing import Dict, List
import ollama
import pandas as pd
from utils.data_loader import DataHandler

class ProductAgent:
    def __init__(self, data_handler: DataHandler):
        self.data_handler = data_handler
    
    def get_product_details(self, product_id: str) -> Dict:
        """Get detailed information about a product"""
        return self.data_handler.get_product_data(product_id)
    
    def find_similar_products(self, product_id: str) -> List[Dict]:
        """Find similar products based on product relationships"""
        similar_ids = self.data_handler.get_similar_products(product_id)
        return [self.get_product_details(pid) for pid in similar_ids]
    
    def analyze_product_trends(self, category: str = None) -> Dict:
        """Analyze trends for products or categories using LLM"""
        query = "SELECT * FROM products"
        if category:
            query += f" WHERE category = '{category}'"
        
        products = pd.read_sql(query, self.data_handler.conn)
        
        prompt = f"""
        Analyze the following product data and identify trends:
        {products.head().to_string()}
        
        Provide insights on:
        - Popular categories
        - Price trends
        - Seasonal variations
        - Customer sentiment
        - Emerging trends
        
        Return your analysis in markdown format.
        """
        
        response = ollama.chat(
            model='gemma:2b',
            messages=[{'role': 'user', 'content': prompt}]
        )
        
        return response['message']['content']
    
    def generate_product_description(self, product_id: str) -> str:
        """Generate compelling product description using LLM"""
        product = self.get_product_details(product_id)
        
        prompt = f"""
        Create a compelling product description for marketing purposes based on:
        - Category: {product['category']}
        - Subcategory: {product['subcategory']}
        - Brand: {product['brand']}
        - Price: {product['price']}
        - Average Rating: {product['product_rating']}
        - Sentiment Score: {product['customer_review_sentiment_score']}
        
        Make it engaging and highlight unique selling points.
        """
        
        response = ollama.chat(
            model='gemma:2b',
            messages=[{'role': 'user', 'content': prompt}]
        )
        
        return response['message']['content']
    
    