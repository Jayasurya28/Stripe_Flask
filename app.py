import stripe
import os
import json
from flask import Flask, render_template, request, jsonify
from twilio.rest import Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Stripe API Key
stripe.api_key = os.getenv("STRIPE_API_KEY")

# Twilio Credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
CUSTOMER_PHONE_NUMBER = os.getenv("CUSTOMER_PHONE_NUMBER")

def send_sms(body_text):
    """Helper function to send SMS with proper error handling"""
    try:
        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = twilio_client.messages.create(
            from_=TWILIO_PHONE_NUMBER,
            to=CUSTOMER_PHONE_NUMBER,
            body=body_text
        )
        print(f"✅ SMS sent successfully! Message SID: {message.sid}")
        return True, message.sid
    except Exception as e:
        print(f"❌ Error sending SMS: {str(e)}")
        return False, str(e)

@app.route("/verify-twilio")
def verify_twilio():
    """Endpoint to verify Twilio credentials and phone numbers"""
    try:
        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        account = twilio_client.api.accounts(TWILIO_ACCOUNT_SID).fetch()
        return jsonify({
            "status": "success",
            "account_status": account.status,
            "twilio_phone": TWILIO_PHONE_NUMBER,
            "customer_phone": CUSTOMER_PHONE_NUMBER
        })
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 400

@app.route("/")
def home():
    return render_template("index.html", key=os.getenv("STRIPE_PUBLIC_KEY"))

@app.route("/pay", methods=["POST"])
def pay():
    """Creates a Stripe checkout session"""
    success_url = "http://localhost:5000/success"
    cancel_url = "http://localhost:5000/cancel"

    try:
        print("\n=== Creating Payment Session ===")
        
        # Generate a unique order ID
        order_id = "ORD" + os.urandom(4).hex()
        print(f"Generated Order ID: {order_id}")
        print(f"Customer Phone: {CUSTOMER_PHONE_NUMBER}")
        
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "Premium Package",
                        "description": "Access to all premium features"
                    },
                    "unit_amount": 5000,  # $50.00
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                "customer_phone": CUSTOMER_PHONE_NUMBER,
                "order_id": order_id
            }
        )
        
        print(f"✅ Session created successfully! Session ID: {session.id}")
        return jsonify({"id": session.id})
    except Exception as e:
        print(f"❌ Error creating session: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.route("/webhook", methods=["POST"])
def webhook():
    """Handles Stripe Webhook events"""
    print("\n=== Webhook Request Received ===")
    print("Headers:", dict(request.headers))
    payload = request.get_data(as_text=True)
    print("Raw Payload:", payload)
    sig_header = request.headers.get("Stripe-Signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    
    print(f"Webhook Secret from env: {webhook_secret}")
    print(f"Signature from Stripe: {sig_header}")

    try:
        # Validate Stripe webhook signature
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        print(f"\n✅ Webhook verified: {event['type']}")
        
        # Handle successful payment events
        if event["type"] == "checkout.session.completed":
            print("\n=== Processing Checkout Completion ===")
            session = event["data"]["object"]
            order_id = session.get("metadata", {}).get("order_id")
            print(f"Order ID from metadata: {order_id}")
            
            # Send success SMS with order ID in requested format
            message = f"Your order no: #{order_id} is confirmed and payment done successful"
            print(f"Attempting to send SMS: {message}")
            
            success, result = send_sms(message)
            if success:
                print(f"✅ SMS sent successfully! SID: {result}")
            else:
                print(f"❌ Failed to send SMS: {result}")

        else:
            print(f"Received event type: {event['type']} - not processing")

        return jsonify({"status": "success"}), 200

    except stripe.error.SignatureVerificationError as e:
        print(f"❌ Webhook signature verification failed: {str(e)}")
        return jsonify({"error": "Invalid signature"}), 400
        
    except Exception as e:
        print(f"❌ Webhook error: {str(e)}")
        print(f"Error type: {type(e)}")
        print(f"Error details: {e.__dict__ if hasattr(e, '__dict__') else 'No additional details'}")
        return jsonify({"error": str(e)}), 400

@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/cancel")
def cancel():
    return render_template("cancel.html")

@app.route("/test-sms")
def test_sms():
    success, result = send_sms("This is a test SMS from your Flask application")
    if success:
        return jsonify({"status": "success", "message_sid": result})
    else:
        return jsonify({"error": result}), 400

@app.route("/test-webhook", methods=["POST"])
def test_webhook():
    """Test endpoint for webhook verification"""
    print("\n=== Test Webhook Received ===")
    print("Headers:", dict(request.headers))
    print("Payload:", request.get_data(as_text=True))
    
    # Try to send a test SMS
    success, result = send_sms("Test webhook received - checking webhook configuration")
    if success:
        print("✅ Test webhook SMS sent")
    else:
        print(f"❌ Test webhook SMS failed: {result}")
    
    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)
