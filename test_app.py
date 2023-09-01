from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import date
import requests
from textblob import TextBlob
import os
from dotenv import load_dotenv
import base64

load_dotenv()

app = Flask(__name__)

api_key = os.environ.get("DROPBOX_API_KEY")


def convert_to_pdf(content):
    # Placeholder for actual PDF conversion
    return content


def send_to_dropbox_sign(contract_content, api_key):
    url = "https://api.hellosign.com/v3/signature_request/send"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{api_key}:'.encode()).decode()}"
    }

    # Prepare data for multi-part form upload
    data = {
        "test_mode": "1",
        "title": "Test Contract",
        "subject": "Please sign this contract",
        "message": "This is a test contract. Please sign it.",
        "signers[0][name]": "Vishesh Tripathi",
        "signers[0][email_address]": "vishesht27@gmail.com",
    }

    # Attach the file
    files = {
        "file[0]": (
            "contract.txt",
            contract_content,
        )  # Assuming contract_content is plain text. Adjust as needed.
    }

    response = requests.post(url, headers=headers, data=data, files=files)

    if response.status_code != 200:
        raise Exception(
            f"Failed to send contract to Dropbox Sign. Error: {response.json()}"
        )

    return "Contract sent successfully to Dropbox Sign!"


def suggest_clause_improvement(clause):
    """
    This function takes in a clause and returns a suggestion based on its sentiment.
    For the sake of this mockup, we'll just return a hardcoded string.
    In a real-world scenario, you'd use an NLP model or API here.
    """
    # Mock sentiment analysis
    sentiment = "neutral"  # This can be changed to "positive" or "negative" based on the sentiment of the clause.

    if sentiment == "positive":
        return "Positive tone detected in the custom clause."
    elif sentiment == "negative":
        return "Negative tone detected in the custom clause."
    else:
        return "Neutral tone detected in the custom clause."


@app.route("/")
def index():
    return render_template("select_contract.html")


@app.route("/select_contract", methods=["GET"])
def select_contract():
    return render_template("select_contract.html")


@app.route("/generate_contract", methods=["POST"])
def generate_contract():
    contract_type = request.form["contract_type"]
    if contract_type == "rental":
        return render_template("rental_form.html")
    elif contract_type == "nda":
        return render_template("nda_form.html")
    elif contract_type == "employment":
        return render_template("employment_form.html")


def analyze_sentiment(clause):
    analysis = TextBlob(clause)
    if analysis.sentiment.polarity > 0:
        return "Positive tone detected in the custom clause."
    elif analysis.sentiment.polarity == 0:
        return "Neutral tone detected in the custom clause."
    else:
        return "Negative tone detected in the custom clause."


@app.route("/finalize_contract", methods=["POST"])
def finalize_contract():
    contract_type = request.form.get("contract_type", "")
    custom_clause = request.form.get("custom_clause", "")
    sentiment_feedback = analyze_sentiment(custom_clause)

    if contract_type == "rental":
        landlord_name = request.form.get("landlord_name", "")
        tenant_name = request.form.get("tenant_name", "")
        property_address = request.form.get("property_address", "")
        rent_amount = request.form.get("rent_amount", "")
        duration = request.form.get("duration", "")

        with open("contract_templates/rental.txt", "r") as file:
            contract = file.read()
            contract = contract.replace("[LANDLORD_NAME]", landlord_name)
            contract = contract.replace("[TENANT_NAME]", tenant_name)
            contract = contract.replace("[PROPERTY_ADDRESS]", property_address)
            contract = contract.replace("[RENT_AMOUNT]", rent_amount)
            contract = contract.replace("[DURATION]", duration)

    elif contract_type == "nda":
        party_one = request.form.get("disclosing_party", "")
        party_two = request.form.get("receiving_party", "")
        duration = request.form.get("duration", "")

        with open("contract_templates/nda.txt", "r") as file:
            contract = file.read()
            contract = contract.replace("[PARTY_ONE_NAME]", party_one)
            contract = contract.replace("[PARTY_TWO_NAME]", party_two)
            contract = contract.replace("[DURATION]", duration)

    elif contract_type == "employment":
        employer_name = request.form.get("employer_name", "")
        employee_name = request.form.get("employee_name", "")
        position = request.form.get("Position", "")
        salary = request.form.get("salary", "")
        duration = request.form.get("duration", "")

        with open("contract_templates/employment.txt", "r") as file:
            contract = file.read()
            contract = contract.replace("[EMPLOYER_NAME]", employer_name)
            contract = contract.replace("[EMPLOYEE_NAME]", employee_name)
            contract = contract.replace("[POSITION]", position)
            contract = contract.replace("[SALARY]", salary)
            contract = contract.replace("[DURATION]", duration)
            contract = contract.replace("[DATE]", str(date.today()))

    feedback = analyze_sentiment(custom_clause)

    contract += f"\n\nCustom Clause: {custom_clause}\nFeedback: {sentiment_feedback}"
    return f"""
    <pre>{contract}</pre>
    <form action="/send_to_dropbox" method="post">
        <input type="hidden" name="contract_content" value="{contract}">
        <input type="submit" value="Send to Dropbox Sign">
    </form>
    """


@app.route("/send_to_dropbox", methods=["POST"])
def send_to_dropbox():
    contract_content = request.form["contract_content"]
    message = send_to_dropbox_sign(contract_content, api_key)
    return message


if __name__ == "__main__":
    app.run(debug=True)