from flask import Flask, render_template, request, jsonify
from system_orchestrator import EcommerceRecommendationSystem
import time
import random
import ollama

app = Flask(__name__)

# Predefined patience quotes
PATIENCE_QUOTES = [
    "Good things come to those who wait...",
    "Great recommendations take time to brew...",
    "Patience is the key to perfect suggestions...",
    "We're curating the best options just for you...",
    "Your personalized picks are being prepared with care..."
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_recommendations', methods=['POST'])
def get_recommendations():
    customer_id = request.form['customer_id']
    
    # Return immediately with loading state
    return jsonify({
        'status': 'loading',
        'quote': random.choice(PATIENCE_QUOTES)
    })

@app.route('/generate_recommendations', methods=['POST'])
def generate_recommendations():
    customer_id = request.form['customer_id']
    system = EcommerceRecommendationSystem()
    
    try:
        recs = system.get_recommendations(customer_id)
        system.close()
        
        if recs:
            return jsonify({
                'status': 'success',
                'recommendations': recs['recommendations']
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'No recommendations found'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        })
    

    
    # Add new endpoint to generate explanation
@app.route('/generate_explanation', methods=['POST'])
def generate_explanation():
    try:
        # Get JSON data instead of form data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        customer_id = data.get('customer_id')
        recommendations = data.get('recommendations')
        
        if not customer_id or not recommendations:
            return jsonify({'error': 'Missing required fields'}), 400

        system = EcommerceRecommendationSystem()
        customer_data = system.data_handler.get_customer_data(customer_id)
        system.close()

        if not customer_data:
            return jsonify({'error': 'Customer not found'}), 404

        prompt = f"""
Generate a concise 5-10 line explanation for why these products were recommended for customer {customer_id}.
Focus on key patterns and value propositions. Use this format:

<b>Recommendation Insights for {customer_id}:</b><br>
1. [Main reason connecting all products]<br>
2. [Key product category/feature match]<br> 
3. [Price range alignment]<br>
4. [Unique benefit highlight]<br>
5. [Final value summary]<br>

Customer Profile:
- Age: {customer_data['Age']}
- Gender: {customer_data['Gender']}
- Purchase History: {eval(customer_data['Purchase_History'])}

Products: {[f"{r['Product_ID']} ({r['Category']})" for r in recommendations]}
"""
        
        response = ollama.chat(
            model='gemma:2b',
            messages=[{'role': 'user', 'content': prompt}],
            options={'temperature': 0.7}
        )
        
        return jsonify({
            'explanation': response['message']['content']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)