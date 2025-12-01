import requests
import os

def send_slack_message(message):
    webhook = os.getenv("SLACK_WEBHOOK_URL")
    if not webhook:
        raise ValueError("SLACK_WEBHOOK_URL not set.")
    
    payload = {"text": message}
    requests.post(webhook, json=payload)
