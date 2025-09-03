import os
import threading

from posthog import Posthog
import requests

def get_ip_address():
    """
    Gets the public IP address of the current machine.
    
    Returns:
        str: The public IP address, or 'unknown' if unable to retrieve.
    """
    try:
        response = requests.get('https://api.ipify.org', timeout=5)
        if response.status_code == 200:
            return response.text.strip()
    except Exception:
        # Fail silently if there's a network error
        pass
    return 'unknown'


posthog = Posthog(
  project_api_key='phc_DPuhaEbPkRMYteIVSLoi0b4ZVqZ3afLq8M6klC0QCX9',
  host='https://us.i.posthog.com'
)

# It's crucial to allow users to opt-out.
# An environment variable is a standard way to do this.
TELEMETRY_ENABLED = os.environ.get("A1FACTS_TELEMETRY_DISABLED") != "1"



def send_telemetry_ping(event_string: str, properties: dict):
    """
    Sends a non-blocking request to the telemetry endpoint.
    """
    if TELEMETRY_ENABLED:
        try:
            posthog.capture(event_string, properties=properties)
        except Exception:
            # Fail silently if there's a network error or the service is down.
            pass

def nonblocking_send_telemetry_ping(event_string: str="a1facts_run", properties: dict={}):
    properties["ip_address"] = get_ip_address()
    telemetry_thread = threading.Thread(target=send_telemetry_ping, args=(event_string, properties))
    telemetry_thread.start()