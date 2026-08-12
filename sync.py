import requests

# Target endpoint on your projector
url = "http://10.209.0.54/program/serial/network/com/open"

# Standard headers often expected by controller interfaces
headers = {
    "User-Agent": "Epson-Controller-Sync/1.0",
    "Content-Type": "application/x-www-form-urlencoded",
}

try:
    print(f"Sending sync request to {url}...")
    
    # Sending a POST request (change to requests.get if your endpoint expects GET)
    response = requests.post(url, headers=headers, timeout=5)
    
    # Raise an exception if the status code indicates an error (4xx or 5xx)
    response.raise_for_status()

    print(f"Success! Server responded with status code: {response.status_code}")
    print("Response payload:")
    print(response.text)

except requests.exceptions.Timeout:
    print("Error: The connection to the projector timed out. Check the IP address and network connectivity.")
except requests.exceptions.ConnectionError:
    print("Error: Could not connect to the projector. Is it turned on and connected to the same subnet?")
except requests.exceptions.HTTPError as err:
    print(f"HTTP Error occurred: {err}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
