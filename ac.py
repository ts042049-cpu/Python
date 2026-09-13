import os
from getpass import getpass

import requests

# 1. Yahan apna SmartThings Personal Access Token dalein
API_TOKEN = os.getenv("SMARTTHINGS_API_TOKEN") or getpass(
    "Enter your SmartThings Personal Access Token: "
)

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def get_devices():
    """SmartThings account se connected saare devices fetch karta hai."""
    if not API_TOKEN:
        raise RuntimeError("SMARTTHINGS_API_TOKEN environment variable is not set")

    url = "https://api.smartthings.com/v1/devices"
    response = requests.get(url, headers=HEADERS, timeout=15)
    if response.status_code == 200:
        return response.json().get("items", [])
    else:
        print(f"Error fetching devices: {response.status_code} - {response.text}")
        return []

def set_ac_temperature(device_id, target_temp_celsius):
    """AC ka cooling setpoint temperature change karta hai."""
    if not API_TOKEN:
        raise RuntimeError("SMARTTHINGS_API_TOKEN environment variable is not set")

    url = f"https://api.smartthings.com/v1/devices/{device_id}/commands"
    
    payload = {
        "commands": [
            {
                "component": "main",
                "capability": "thermostatCoolingSetpoint",
                "command": "setCoolingSetpoint",
                "arguments": [target_temp_celsius]
            }
        ]
    }
    
    response = requests.post(url, headers=HEADERS, json=payload, timeout=15)
    if response.status_code in (200, 202):
        print(f"Temperature successfully set to {target_temp_celsius}°C!")
    else:
        print(f"Failed to set temperature: {response.status_code} - {response.text}")

# --- Execution ---
if __name__ == "__main__":
    # Pehle AC ka Device ID find karein
    devices = get_devices()
    print("--- Connected Devices ---")
    for d in devices:
        print(f"Name: {d.get('label') or d.get('name')} | Device ID: {d.get('deviceId')}")
    
    # 2. Console se apna AC Device ID copy karke yahan paste karein
    TARGET_DEVICE_ID = os.getenv("SMARTTHINGS_AC_DEVICE_ID") or input(
        "Enter your AC device ID: "
    ).strip()
    
    # 3. New temperature (in °C)
    NEW_TEMPERATURE = 24
    
    if TARGET_DEVICE_ID:
        set_ac_temperature(TARGET_DEVICE_ID, NEW_TEMPERATURE)