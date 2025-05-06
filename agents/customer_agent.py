# # agents/customer_agent.py
# from dataclasses import dataclass
# from typing import Dict, List, Optional
# import ollama
# import json
# from utils.data_loader import DataHandler

# @dataclass
# class CustomerProfile:
#     customer_id: str
#     age: int
#     gender: str
#     location: str
#     browsing_history: List[str]
#     purchase_history: List[str]
#     customer_segment: str
#     avg_order_value: float
#     holiday: str
#     season: str

# class CustomerAgent:
#     def __init__(self, customer_id: str, data_handler: DataHandler):
#         self.customer_id = customer_id
#         self.data_handler = data_handler
#         self.profile = self._load_profile()
#         self.preferences = self._analyze_preferences() if self.profile else None
        
#     def _load_profile(self) -> Optional[CustomerProfile]:
#         """Load customer profile from database"""
#         raw_data = self.data_handler.get_customer_data(self.customer_id)
#         if not raw_data:
#             return None
            
#         # Safely parse JSON-like strings
#         def parse_history(history_str):
#             try:
#                 return eval(history_str)
#             except:
#                 return []
        
#         return CustomerProfile(
#             customer_id=raw_data['Customer_ID'],
#             age=raw_data['Age'],
#             gender=raw_data['Gender'],
#             location=raw_data['Location'],
#             browsing_history=parse_history(raw_data['Browsing_History']),
#             purchase_history=parse_history(raw_data['Purchase_History']),
#             customer_segment=raw_data['Customer_Segment'],
#             avg_order_value=raw_data['Avg_Order_Value'],
#             holiday=raw_data['Holiday'],
#             season=raw_data['Season']
#         )
    
#     # ... rest of the file ...
    
#     def _analyze_preferences(self) -> Dict:
#         """Analyze customer preferences using LLM"""
#         prompt = f"""
#         Analyze the following customer profile and determine their preferences:
#         - Age: {self.profile.age}
#         - Gender: {self.profile.gender}
#         - Location: {self.profile.location}
#         - Browsing History: {self.profile.browsing_history}
#         - Purchase History: {self.profile.purchase_history}
#         - Customer Segment: {self.profile.customer_segment}
#         - Average Order Value: {self.profile.avg_order_value}
#         - Current Season: {self.profile.season}
        
#         Return a JSON object with the customer's likely preferences including:
#         - preferred_categories
#         - price_range (low, medium, high)
#         - brand_preferences
#         - style_preferences
#         - seasonal_preferences
#         """
        
#         response = ollama.chat(
#             model='gemma:2b',
#             messages=[{'role': 'user', 'content': prompt}],
#             format='json'
#         )
        
#         return eval(response['message']['content'])
    
#     def get_preferences(self) -> Dict:
#         """Get analyzed customer preferences"""
#         return self.preferences
    
#     def update_profile(self, new_interaction: Dict):
#         """Update customer profile with new interaction data"""
#         # Update browsing history
#         if 'browsed_items' in new_interaction:
#             self.profile.browsing_history.extend(new_interaction['browsed_items'])
        
#         # Update purchase history
#         if 'purchased_items' in new_interaction:
#             self.profile.purchase_history.extend(new_interaction['purchased_items'])
        
#         # Update other fields as needed
#         # Then save back to database
#         self._save_profile()
    
#     def _save_profile(self):
#         """Save updated profile back to database"""
#         # Implementation would update SQLite database
#         pass

# agents/customer_agent.py
from dataclasses import dataclass
from typing import Dict, List, Optional
import ollama
import json
from utils.data_loader import DataHandler

@dataclass
class CustomerProfile:
    customer_id: str
    age: int
    gender: str
    location: str
    browsing_history: List[str]
    purchase_history: List[str]
    customer_segment: str
    avg_order_value: float
    holiday: str
    season: str

class CustomerAgent:
    def __init__(self, customer_id: str, data_handler: DataHandler):
        self.customer_id = customer_id
        self.data_handler = data_handler
        self.profile = self._load_profile()
        self.preferences = self._analyze_preferences() if self.profile else None
        
    def _load_profile(self) -> Optional[CustomerProfile]:
        """Load customer profile from database"""
        raw_data = self.data_handler.get_customer_data(self.customer_id)
        if not raw_data:
            return None
            
        # Safely parse JSON-like strings
        def parse_history(history_str):
            try:
                return eval(history_str)
            except:
                return []
        
        return CustomerProfile(
            customer_id=raw_data['Customer_ID'],
            age=raw_data['Age'],
            gender=raw_data['Gender'],
            location=raw_data['Location'],
            browsing_history=parse_history(raw_data['Browsing_History']),
            purchase_history=parse_history(raw_data['Purchase_History']),
            customer_segment=raw_data['Customer_Segment'],
            avg_order_value=raw_data['Avg_Order_Value'],
            holiday=raw_data['Holiday'],
            season=raw_data['Season']
        )
    
    # ... rest of the file ...
    
    # def _analyze_preferences(self) -> Dict:
    #     """Analyze customer preferences using LLM"""
    #     prompt = f"""
    #     Analyze the following customer profile and determine their preferences:
    #     - Age: {self.profile.age}
    #     - Gender: {self.profile.gender}
    #     - Location: {self.profile.location}
    #     - Browsing History: {self.profile.browsing_history}
    #     - Purchase History: {self.profile.purchase_history}
    #     - Customer Segment: {self.profile.customer_segment}
    #     - Average Order Value: {self.profile.avg_order_value}
    #     - Current Season: {self.profile.season}
        
    #     Return a JSON object with the customer's likely preferences including:
    #     - preferred_categories
    #     - price_range (low, medium, high)
    #     - brand_preferences
    #     - style_preferences
    #     - seasonal_preferences
    #     """
        
    #     response = ollama.chat(
    #         model='gemma:2b',
    #         messages=[{'role': 'user', 'content': prompt}],
    #         format='json'
    #     )
        
    #     return eval(response['message']['content'])

    def _analyze_preferences(self) -> Dict:
        """Analyze customer preferences using LLM with robust JSON parsing"""
        prompt = f"""
        Analyze the following customer profile and return preferences as valid JSON:
        - Age: {self.profile.age}
        - Gender: {self.profile.gender}
        - Location: {self.profile.location}
        - Browsing History: {self.profile.browsing_history}
        - Purchase History: {self.profile.purchase_history}
        - Customer Segment: {self.profile.customer_segment}
        - Average Order Value: {self.profile.avg_order_value}
        - Current Season: {self.profile.season}
        
        Return format (must be valid JSON):
        {{
            "preferred_categories": ["list", "of", "categories"],
            "price_range": "low/medium/high",
            "brand_preferences": ["list", "of", "brands"],
            "style_preferences": ["list", "of", "styles"],
            "seasonal_preferences": ["list", "of", "seasons"]
        }}
        """
        
        response = ollama.chat(
            model='gemma:2b',
            messages=[{'role': 'user', 'content': prompt}],
            format='json'  # Explicitly request JSON format
        )
        
        # Safer JSON parsing with error handling
        try:
            import json
            from json import JSONDecodeError
            
            # First try standard JSON parsing
            return json.loads(response['message']['content'])
        except JSONDecodeError:
            # Fallback: replace problematic values before eval
            fixed_content = (
                response['message']['content']
                .replace(': true', ': True')
                .replace(': false', ': False')
            )
            return eval(fixed_content)
    
    def get_preferences(self) -> Dict:
        """Get analyzed customer preferences"""
        return self.preferences
    
    def update_profile(self, new_interaction: Dict):
        """Update customer profile with new interaction data"""
        # Update browsing history
        if 'browsed_items' in new_interaction:
            self.profile.browsing_history.extend(new_interaction['browsed_items'])
        
        # Update purchase history
        if 'purchased_items' in new_interaction:
            self.profile.purchase_history.extend(new_interaction['purchased_items'])
        
        # Update other fields as needed
        # Then save back to database
        self._save_profile()
    
    def _save_profile(self):
        """Save updated profile back to database"""
        # Implementation would update SQLite database
        pass