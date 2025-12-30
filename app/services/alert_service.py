import requests

N8N_WEBHOOK_URL = "http://localhost:5678/webhook/confirmed-match"


def trigger_n8n_alert(payload):
    try:
        response = requests.post(
            N8N_WEBHOOK_URL,
            json=payload,
            timeout=5
        )
        return response.status_code == 200
    except Exception:
        return False
