import stripe
from flask import Flask, render_template, request, jsonify
import os
from twilio.rest import Client
import json

app = Flask(__name__)
from dotenv import load_dotenv
load_dotenv()
# Replace with your Stripe test keys
stripe.api_key = os.getenv("STRIPE_API_KEY")

# Initialize Twilio client
twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

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

@app.route("/webhook", methods=["POST"])
def webhook():
    print("\n=== Webhook Request Received ===")
    print("Headers:", dict(request.headers))
    payload = request.get_data(as_text=True)
    print("🔴 Raw Payload:", payload)
    
    sig_header = request.headers.get("Stripe-Signature")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    print("\n=== Webhook Configuration ===")
    print(f"🔑 Webhook secret: {webhook_secret}")
    print(f"📝 Signature header: {sig_header}")

    try:
        # First try to parse the payload as JSON to check if it's valid
        try:
            json_payload = json.loads(payload)
            print("\n=== Parsed JSON Payload ===")
            print(json.dumps(json_payload, indent=2))
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON payload: {e}")
            return jsonify({"error": "Invalid JSON payload"}), 400

        # Then try to verify the Stripe signature
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
            print("\n=== Stripe Event ===")
            print(f"🔔 Event type: {event['type']}")
            print(f"📅 Created: {event['created']}")
            print(f"🆔 Event ID: {event['id']}")
        except stripe.error.SignatureVerificationError as e:
            print(f"\n❌ Signature verification failed: {e}")
            return jsonify({"error": "Webhook signature verification failed"}), 400

        # Handle the event
        if event["type"] == "payment_intent.succeeded":
            print("\n=== Processing Payment Success ===")
            try:
                print("📱 Attempting to send SMS...")
                print(f"From: {os.getenv('TWILIO_PHONE_NUMBER')}")
                print(f"To: {os.getenv('CUSTOMER_PHONE_NUMBER')}")
                
                message = twilio_client.messages.create(
                    from_=os.getenv("TWILIO_PHONE_NUMBER"),
                    to=os.getenv("CUSTOMER_PHONE_NUMBER"),
                    body="Your order no :#223rftvd is confirmed and payment done successfull"
                )
                print(f"✅ SMS sent successfully! Message SID: {message.sid}")
            except Exception as e:
                print(f"❌ Error sending SMS: {str(e)}")
                print(f"Error type: {type(e)}")
                print(f"Error details: {e.__dict__}")
        elif event["type"] == "checkout.session.completed":
            print("\n=== Processing Checkout Completion ===")
            try:
                print("📱 Attempting to send SMS...")
                print(f"From: {os.getenv('TWILIO_PHONE_NUMBER')}")
                print(f"To: {os.getenv('CUSTOMER_PHONE_NUMBER')}")
                
                message = twilio_client.messages.create(
                    from_=os.getenv("TWILIO_PHONE_NUMBER"),
                    to=os.getenv("CUSTOMER_PHONE_NUMBER"),
                    body="Your order no :#223rftvd is confirmed and payment done successfull"
                )
                print(f"✅ SMS sent successfully! Message SID: {message.sid}")
            except Exception as e:
                print(f"❌ Error sending SMS: {str(e)}")
                print(f"Error type: {type(e)}")
                print(f"Error details: {e.__dict__}")
        else:
            print(f"\n⚠️ Unhandled event type: {event['type']}")

        print("\n=== Webhook Processing Complete ===")
        return jsonify({"status": "success"}), 200

    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        print(f"Error type: {type(e)}")
        print(f"Error details: {e.__dict__}")
        return jsonify({"error": str(e)}), 400

@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/cancel")
def cancel():
    return render_template("cancel.html")

@app.route("/test-sms")
def test_sms():
    try:
        print("📱 Testing SMS sending...")
        print(f"From: {os.getenv('TWILIO_PHONE_NUMBER')}")
        print(f"To: {os.getenv('CUSTOMER_PHONE_NUMBER')}")
        
        message = twilio_client.messages.create(
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=os.getenv("CUSTOMER_PHONE_NUMBER"),
            body="This is a test SMS from your Flask application"
        )
        print(f"✅ Test SMS sent successfully! Message SID: {message.sid}")
        return jsonify({"status": "success", "message_sid": message.sid})
    except Exception as e:
        print(f"❌ Error sending test SMS: {str(e)}")
        print(f"Error type: {type(e)}")
        print(f"Error details: {e.__dict__}")
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(port=5000, debug=True)
