from typing import Dict
import ollama
from utils.data_loader import DataHandler

class FeedbackAgent:
    def __init__(self, data_handler):
        self.data_handler = data_handler
    
    def process_feedback(self, customer_id: str, product_id: str, feedback: Dict):
        """Process customer feedback and update models"""
        # Analyze feedback sentiment
        sentiment = self._analyze_feedback_sentiment(feedback['comments'])
        
        # Update product ratings/sentiment in database
        self._update_product_sentiment(product_id, sentiment)
        
        # Generate insights for improvement
        insights = self._generate_insights(customer_id, product_id, feedback)
        
        return insights
    
    def _analyze_feedback_sentiment(self, text: str) -> float:
        """Analyze sentiment of feedback text"""
        prompt = f"""
        Analyze the sentiment of this customer feedback on a scale from -1 (very negative) to 1 (very positive):
        
        Feedback: "{text}"
        
        Return only a single float number representing the sentiment score.
        """
        
        response = ollama.chat(
            model='gemma:2b',
            messages=[{'role': 'user', 'content': prompt}]
        )
        
        try:
            return float(response['message']['content'])
        except:
            return 0.0
    
    def _update_product_sentiment(self, product_id: str, sentiment: float):
        """Update product sentiment in database"""
        # Implementation would update SQLite database
        pass
    
    def _generate_insights(self, customer_id: str, product_id: str, feedback: Dict) -> str:
        """Generate actionable insights from feedback"""
        prompt = f"""
        Based on this customer feedback, provide insights for improving recommendations:
        
        Customer ID: {customer_id}
        Product ID: {product_id}
        Rating: {feedback.get('rating', 'N/A')}
        Comments: {feedback.get('comments', 'None')}
        Sentiment Score: {feedback.get('sentiment', 'N/A')}
        
        Provide 2-3 actionable suggestions to improve future recommendations for this customer.
        """
        
        response = ollama.chat(
            model='gemma:2b',
            messages=[{'role': 'user', 'content': prompt}]
        )
        
        return response['message']['content']