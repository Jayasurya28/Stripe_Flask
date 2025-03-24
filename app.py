import stripe
from flask import Flask, render_template, request, jsonify
import os

app = Flask(__name__)
from dotenv import load_dotenv
load_dotenv()
# Replace with your Stripe test keys
stripe.api_key = os.getenv("STRIPE_API_KEY")

@app.route("/")
def home():
    return render_template("index.html", key=os.getenv("STRIPE_PUBLIC_KEY"))

@app.route("/pay", methods=["POST"])
def pay():
    if os.getenv("DEPLOYMENT_ENV") == "production":
        success_url = "https://your-production-website.com/success"
        cancel_url = "https://your-production-website.com/cancel"
    else:
        success_url = "http://localhost:5000/success"
        cancel_url = "http://localhost:5000/cancel"
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": "Test Product"},
                    "unit_amount": 5000,  # $50.00
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
        )
        return jsonify({"id": session.id})
    except Exception as e:
        return str(e), 400

@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/cancel")
def cancel():
    return render_template("cancel.html")

if __name__ == "__main__":
    app.run(debug=True)
