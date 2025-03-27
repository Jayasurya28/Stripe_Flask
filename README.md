# Stripe Payment Integration with Flask and SMS Notifications

A Flask web application that integrates Stripe payments with SMS notifications using Twilio. When a customer completes a payment, they automatically receive an SMS confirmation.

## Features

- 🛍️ Clean, modern payment interface
- 💳 Secure payment processing with Stripe
- 📱 Automated SMS notifications after successful payments
- 🔒 Secure webhook handling
- 🎨 Responsive design

## Prerequisites

- Python 3.x
- Stripe Account
- Twilio Account
- ngrok (for local development)

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
STRIPE_API_KEY=your_stripe_secret_key
STRIPE_PUBLIC_KEY=your_stripe_publishable_key
STRIPE_WEBHOOK_SECRET=your_stripe_webhook_secret
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
CUSTOMER_PHONE_NUMBER=customer_phone_number
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Stripe_Flask_
```

2. Create and activate virtual environment:
```bash
python -m venv env
source env/bin/activate  # For Unix/macOS
env\Scripts\activate     # For Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. In a new terminal, start ngrok:
```bash
ngrok http 5000
```

3. Update Webhook URL in Stripe Dashboard:
   - Go to Stripe Dashboard → Developers → Webhooks
   - Add endpoint: `https://your-ngrok-url/webhook`
   - Add events to listen to:
     - `payment_intent.succeeded`
     - `checkout.session.completed`

## Testing the Payment Flow

1. Visit `http://localhost:5000` in your browser
2. Click "Proceed to Payment"
3. Use test card details:
   - Card number: 4242 4242 4242 4242
   - Any future expiry date
   - Any 3-digit CVC
4. Complete the payment
5. Check your phone for the SMS confirmation

## Project Structure

```
Stripe_Flask_/
├── app.py              # Main Flask application
├── templates/          # HTML templates
│   ├── index.html     # Payment page
│   ├── success.html   # Success page
│   └── cancel.html    # Cancel page
├── .env               # Environment variables
├── requirements.txt   # Python dependencies
└── README.md         # Documentation
```

## Important Notes

- Keep both Flask server and ngrok running for webhook functionality
- Update the webhook URL in Stripe dashboard when ngrok URL changes
- Ensure your phone number is verified in Twilio for SMS notifications
- Use test cards in development, real cards in production

## Security

- Environment variables are stored in `.env` file (not committed to git)
- Webhook signatures are verified for security
- Stripe handles payment information securely
- No sensitive data is stored locally

## Troubleshooting

1. **SMS not received:**
   - Check Twilio credentials
   - Verify phone number in Twilio
   - Check webhook logs in Stripe dashboard

2. **Webhook errors:**
   - Ensure ngrok is running
   - Verify webhook URL in Stripe dashboard
   - Check Flask server logs

3. **Payment errors:**
   - Verify Stripe API keys
   - Check browser console for errors
   - Use test cards for development

## License

[Your License Here]

## Support

For support, please [create an issue](repository-issues-url) or contact [your-email].
