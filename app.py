from flask import Flask, request, jsonify
from services.whatsapp_service import WhatsAppService
import os
import logging

app = Flask(__name__)
logger = logging.getLogger(__name__)

# Initialize WhatsApp service
whatsapp_service = WhatsAppService(
    access_token=os.getenv("ACCESS_TOKEN"),
    phone_number_id=os.getenv("PHONE_NUMBER_ID"),
    version=os.getenv("VERSION")
)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok"
    })

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """Verify webhook subscription with Meta"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode == 'subscribe' and token == os.getenv("WEBHOOK_TOKEN"):
        logger.info("WEBHOOK_VERIFIED")
        return challenge, 200
    return "Verification failed", 403


@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """Process incoming WhatsApp messages"""
    payload = request.json
    logger.info(f"Incoming payload: {payload}")

    try:
        for entry in payload['entry']:
            for change in entry['changes']:
                value = change['value']
                if 'messages' in value:
                    for message in value['messages']:
                        if message['type'] == 'text':
                            # Extract message details
                            sender_waid = message['from']
                            message_body = message['text']['body']
                            message_id = message['id']

                            logger.info(f"Received message from {sender_waid}: {message_body}")

                            # Process message through agent (placeholder)
                            agent_response = process_message_with_agent(message_body)

                            # Send response via WhatsApp
                            whatsapp_service.send_text_message(
                                recipient_waid=sender_waid,
                                message=agent_response,
                                reply_to_message_id=message_id
                            )
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({'status': 'error'}), 500


def process_message_with_agent(message: str) -> str:
    """Placeholder for agent processing logic"""
    # TODO: Integrate with your actual agent system
    return f"Received your message: '{message}'. This is an automated reply."


@app.route('/send-message', methods=['POST'])
def send_message():
    """API endpoint to send custom messages"""
    data = request.json
    try:
        response = whatsapp_service.send_text_message(
            recipient_waid=data['recipient'],
            message=data['message']
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)