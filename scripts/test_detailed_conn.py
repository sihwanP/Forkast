import requests
import logging
import http.client as http_client

# Enable verbose logging for requests
http_client.HTTPConnection.debuglevel = 1
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

print("--- STARTING VERBOSE CONNECTIVITY TEST ---")
try:
    print("1. Testing Classic Google...")
    response = requests.get('https://www.google.com', timeout=10)
    print(f"   [SUCCESS] Status: {response.status_code}")
except Exception as e:
    print(f"   [FAILURE] Error: {e}")

try:
    print("\n2. Testing Generative AI Endpoint (Discovery)...")
    # This URL is used by the library internally for discovery
    response = requests.get('https://generativelanguage.googleapis.com/$discovery/rest?version=v1beta', timeout=10)
    print(f"   [SUCCESS] Status: {response.status_code}")
    print(f"   [HEADERS] {response.headers}")
except Exception as e:
    print(f"   [FAILURE] Error: {e}")
print("--- END TEST ---")
