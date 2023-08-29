from flask import Flask, render_template, request
from datetime import date
import requests
from textblob import TextBlob
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

api_key = os.environ.get("DROPBOX_API_KEY")

def convert_to_pdf(content):
    # Placeholder for actual PDF conversion
    return content

def send_to_dropbox_sign(contract_content, api_key):

    # Set up the API endpoint and headers
    url = "https://api.dropboxsign.com/send_contract"  # This URL is a placeholder, replace with the actual endpoint
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Format the data to be sent to Dropbox Sign
    data = {
        "contract_content": contract_content,
        # Add any other required fields here based on the Dropbox Sign API documentation
    }
    
    # Make the API call
    response = requests.post(url, headers=headers, json=data)
    
    # Handle the response
    if response.status_code == 200:
        # Handle success case (e.g., extract any necessary information from the response)
        return "Contract sent to Dropbox Sign successfully!"
    else:
        # Handle error cases
        return f"Failed to send contract to Dropbox Sign. Error: {response.text}"

    # Your implementation of sending contract to Dropbox using their API
    return "Contract sent to Dropbox successfully!"  # Placeholder response

def suggest_clause_improvement(clause, sentiment):

    def suggest_clause_improvement(clause, sentiment):
        # For the sake of simplicity, we'll use a few predefined suggestions.
        suggestions = {
            "negative": [
                "Consider rephrasing to sound more collaborative.",
                "This clause might sound confrontational. Think about a more neutral tone.",
                "How about addressing this point in a more positive manner?"
            ],
            "neutral": [
                "This clause is quite neutral. Make sure it's clear and specific.",
                "Consider adding more specific details to this clause.",
                "Is there a way to make this point clearer?"
            ],
            "positive": []
        }
        
        # Based on the sentiment, pick a suggestion
        if sentiment > 0.5:
            sentiment_category = "positive"
        elif sentiment < -0.5:
            sentiment_category = "negative"
        else:
            sentiment_category = "neutral"
        
        # Return a suggestion from the appropriate category
        return suggestions[sentiment_category][0] if suggestions[sentiment_category] else None

        
        if analysis.sentiment.polarity > 0:
            return "Positive tone detected in the custom clause."
        elif analysis.sentiment.polarity == 0:
            return "Neutral tone detected in the custom clause."
        else:
            return "Negative tone detected in the custom clause."

@app.route('/')
def index():
    return render_template('select_contract.html')

@app.route('/generate_contract', methods=['POST'])
def generate_contract():
    contract_type = request.form['contract_type']
    if contract_type == "rental":
        return render_template('rental_form.html')
    elif contract_type == "nda":
        return render_template('nda_form.html')
    elif contract_type == "employment":
        return render_template('employment_form.html')

def analyze_sentiment(clause):
    analysis = TextBlob(clause)
    if analysis.sentiment.polarity > 0:
        return "Positive tone detected in the custom clause."
    elif analysis.sentiment.polarity == 0:
        return "Neutral tone detected in the custom clause."
    else:
        return "Negative tone detected in the custom clause."



@app.route('/finalize_contract', methods=['POST'])
def finalize_contract():
    contract_type = request.form.get('contract_type', '')
    custom_clause = request.form.get('custom_clause', '')
    sentiment_feedback = analyze_sentiment(custom_clause)

    if contract_type == "rental":
        landlord_name = request.form.get('landlord_name', '')
        tenant_name = request.form.get('tenant_name', '')
        property_address = request.form.get('property_address', '')
        rent_amount = request.form.get('rent_amount', '')
        duration = request.form.get('duration', '')
        
        with open('contract_templates/rental.txt', 'r') as file:
            contract = file.read()
            contract = contract.replace('[LANDLORD_NAME]', landlord_name)
            contract = contract.replace('[TENANT_NAME]', tenant_name)
            contract = contract.replace('[PROPERTY_ADDRESS]', property_address)
            contract = contract.replace('[RENT_AMOUNT]', rent_amount)
            contract = contract.replace('[DURATION]', duration)
            contract = contract.replace('[DATE]', str(date.today()))

    elif contract_type == "nda":
        party_one = request.form.get('party_one', '')
        party_two = request.form.get('party_two', '')

        with open('contract_templates/nda.txt', 'r') as file:
            contract = file.read()
            contract = contract.replace('[PARTY_ONE]', party_one)
            contract = contract.replace('[PARTY_TWO]', party_two)
            contract = contract.replace('[DATE]', str(date.today()))

    elif contract_type == "employment":
        employer_name = request.form.get('employer_name', '')
        employee_name = request.form.get('employee_name', '')
        position = request.form.get('position', '')
        salary = request.form.get('salary', '')
        duration = request.form.get('duration', '')

        with open('contract_templates/employment.txt', 'r') as file:
            contract = file.read()
            contract = contract.replace('[EMPLOYER_NAME]', employer_name)
            contract = contract.replace('[EMPLOYEE_NAME]', employee_name)
            contract = contract.replace('[POSITION]', position)
            contract = contract.replace('[SALARY]', salary)
            contract = contract.replace('[DURATION]', duration)
            contract = contract.replace('[DATE]', str(date.today()))


    feedback = analyze_sentiment(custom_clause)
    
        

    contract += f"\n\nCustom Clause: {custom_clause}\nFeedback: {sentiment_feedback}"
    return f"""
    <pre>{contract}</pre>
    <form action="/send_to_dropbox" method="post">
        <input type="hidden" name="contract_content" value="{contract}">
        <input type="submit" value="Send to Dropbox Sign">
    </form>
    """

@app.route('/send_to_dropbox', methods=['POST'])
def send_to_dropbox():
    contract_content = request.form['contract_content']
    message = send_to_dropbox_sign(contract_content, api_key)
    return message

if __name__ == '__main__':
    app.run(debug=True)