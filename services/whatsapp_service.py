import requests
import logging


class WhatsAppService:
    def __init__(self, access_token: str, phone_number_id: str, version: str = "v19.0"):
        self.base_url = f"https://graph.facebook.com/{version}/{phone_number_id}/messages"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        self.logger = logging.getLogger(__name__)

    def send_text_message(self, recipient_waid: str, message: str,
                          reply_to_message_id: str = None) -> requests.Response:
        """Send text message via WhatsApp API"""
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient_waid,
            "type": "text",
            "text": {"body": message}
        }

        if reply_to_message_id:
            payload["context"] = {"message_id": reply_to_message_id}

        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            self.logger.info(f"Message sent to {recipient_waid}: {response.json()}")
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {str(e)}")
            raise

    def send_template_message(self, recipient_waid: str, template_name: str, language_code: str = "en_US"):
        """Send template message (existing functionality)"""
        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_waid,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code}
            }
        }

        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Template send failed: {str(e)}")
            raise