import os
import threading

from posthog import Posthog

posthog = Posthog(
  project_api_key='phc_DPuhaEbPkRMYteIVSLoi0b4ZVqZ3afLq8M6klC0QCX9',
  host='https://us.i.posthog.com'
)

# It's crucial to allow users to opt-out.
# An environment variable is a standard way to do this.
TELEMETRY_ENABLED = os.environ.get("A1FACTS_TELEMETRY_DISABLED") != "1"



def send_telemetry_ping(event_string: str, properties: dict={}):
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
    telemetry_thread = threading.Thread(target=send_telemetry_ping, args=(event_string, properties))
    telemetry_thread.start()