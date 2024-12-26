import requests
import logging
import os
# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")
logger = logging.getLogger(__name__)

# Configuration for webhook URL
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "http://resume_ranker:5001/webhook")

def send_webhook_notification(jd_id):
    """
    Send a webhook notification to the Resume Ranker service.

    Args:
        jd_id (str): The ID of the processed JD.

    Returns:
        dict: The response from the webhook service.
    """
    payload = {
        "jd_id": jd_id  # Only send the jd_id
    }

    try:
        logger.info(f"Sending webhook notification to {WEBHOOK_URL} for JD {jd_id}")
        response = requests.post(WEBHOOK_URL, json=payload, timeout=5)
        response.raise_for_status()
        logger.info(f"Webhook notification successful for JD {jd_id}: {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send webhook notification for JD {jd_id}: {e}")
        return {"error": str(e)}