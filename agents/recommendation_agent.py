# agents/recommendation_agent.py
from typing import Dict, List
import ollama
import numpy as np
import pandas as pd
from .customer_agent import CustomerAgent
from .product_agent import ProductAgent

class RecommendationAgent:
    def __init__(self, customer_agent: CustomerAgent, product_agent: ProductAgent):
        self.customer_agent = customer_agent
        self.product_agent = product_agent
    
    def generate_recommendations(self, n_recommendations: int = 5) -> List[Dict]:
        """Generate personalized product recommendations"""
        preferences = self.customer_agent.get_preferences()
        
        # Updated query with correct column names
        query = f"""
        SELECT * FROM products 
        WHERE Category IN ({','.join([f"'{cat}'" for cat in preferences['preferred_categories']])})
        ORDER BY Product_Rating DESC
        LIMIT 100
        """
        
        candidate_products = pd.read_sql(query, self.customer_agent.data_handler.conn)
        
        # Score products based on customer preferences
        candidate_products['score'] = candidate_products.apply(
            lambda row: self._score_product(row, preferences),
            axis=1
        )
        
        # Get top recommendations
        recommendations = candidate_products.sort_values('score', ascending=False).head(n_recommendations)
        
        # Generate explanations for recommendations
        recommendations['explanation'] = recommendations.apply(
            lambda row: self._generate_explanation(row.to_dict(), preferences),
            axis=1
        )
        
        return recommendations.to_dict('records')

    def generate_recommendations(self, n_recommendations: int = 5) -> List[Dict]:
        """Generate personalized product recommendations without explanations"""
        preferences = self.customer_agent.get_preferences()
        
        query = f"""
        SELECT * FROM products 
        WHERE Category IN ({','.join([f"'{cat}'" for cat in preferences['preferred_categories']])})
        ORDER BY Product_Rating DESC
        LIMIT 100
        """
        
        candidate_products = pd.read_sql(query, self.customer_agent.data_handler.conn)
        
        # Score products based on customer preferences
        candidate_products['score'] = candidate_products.apply(
            lambda row: self._score_product(row, preferences),
            axis=1
        )
        
        # Get top recommendations without explanations
        recommendations = candidate_products.sort_values('score', ascending=False)\
                                          .head(n_recommendations)
        
        return recommendations.to_dict('records')

    
    def _score_product(self, product: Dict, preferences: Dict) -> float:
        """Score a product based on customer preferences"""
        score = 0
        
        # Updated column names to match your schema
        if product['Category'] in preferences['preferred_categories']:
            score += 0.3
        
        price_range = self._get_price_range(product['Price'])
        if price_range == preferences['price_range']:
            score += 0.2
        
        if product['Brand'] in preferences.get('brand_preferences', []):
            score += 0.2
        
        score += product['Product_Rating'] * 0.1
        score += product['Customer_Review_Sentiment_Score'] * 0.1
        
        purchased_items = self.customer_agent.profile.purchase_history
        if product['Category'] in purchased_items:
            score += 0.1
        
        return score
    
    def _get_price_range(self, price: float) -> str:
        """Categorize price into range"""
        if price < 1000:
            return 'low'
        elif price < 5000:
            return 'medium'
        else:
            return 'high'
    
    def _generate_explanation(self, product: Dict, preferences: Dict) -> str:
        """Generate natural language explanation for recommendation"""
        prompt = f"""
        Explain why this product would be a good recommendation for this customer:
        
        Customer Preferences:
        {preferences}
        
        Product Details:
        {product}
        
        Provide a concise 1-2 sentence explanation.
        """
        
        response = ollama.chat(
            model='gemma:2b',
            messages=[{'role': 'user', 'content': prompt}]
        )
        
        return response['message']['content']