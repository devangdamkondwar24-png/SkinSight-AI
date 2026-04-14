import os
import requests
from dotenv import load_dotenv

load_dotenv()

def diagnostic_sms():
    api_key = os.environ.get("FAST2SMS_API_KEY")
    phone = "9999999999" # Sample number
    otp = "1234"
    
    print(f"--- Fast2SMS Diagnostic ---")
    print(f"API Key Found: {'Yes' if api_key else 'No'}")
    if api_key:
        print(f"Key length: {len(api_key)}")
    
    url = "https://www.fast2sms.com/dev/bulkV2"
    # Testing alternative route 'v3' (Standard Message)
    payload = {
        "route": "q", # 'q' is for quick/bulk messages
        "message": f"Your SkinSight AI verification code is: {otp}",
        "numbers": phone
    }
    headers = {
        "authorization": api_key,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        print("Sending request to Fast2SMS...")
        response = requests.post(url, data=payload, headers=headers, timeout=15)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"Exception: {str(e)}")

if __name__ == "__main__":
    diagnostic_sms()
