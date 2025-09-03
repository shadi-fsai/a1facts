import requests
import os
import threading

# It's crucial to allow users to opt-out.
# An environment variable is a standard way to do this.
TELEMETRY_ENABLED = os.environ.get("A1FACTS_TELEMETRY_DISABLED") != "1"

# Your unique URL from Pipedream or another webhook service.
TELEMETRY_URL = "https://eon59vvwyxpjj4c.m.pipedream.net" 

def send_telemetry_ping():
    """
    Sends a non-blocking request to the telemetry endpoint.
    """
    if TELEMETRY_ENABLED:
        try:
            # The timeout prevents the request from hanging indefinitely.
            requests.post(TELEMETRY_URL, timeout=2) 
            # You don't need to send any data; Pipedream logs the IP from the request itself.
        except requests.RequestException:
            # Fail silently if there's a network error or the service is down.
            pass

def nonblocking_send_telemetry_ping():
    telemetry_thread = threading.Thread(target=send_telemetry_ping)
    telemetry_thread.start()

