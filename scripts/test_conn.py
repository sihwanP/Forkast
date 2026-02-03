import requests
try:
    print("Testing connectivity to google.com...")
    response = requests.get('https://www.google.com', timeout=5)
    print(f"Status Code: {response.status_code}")
except Exception as e:
    print(f"Connectivity Error: {e}")
