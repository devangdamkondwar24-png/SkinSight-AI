import random
import time
import os
import requests
from typing import Dict, Optional

class AuthService:
    def __init__(self):
        # We'll expect the API key as an environment variable or set it manually later
        self.api_key = os.environ.get("FAST2SMS_API_KEY")
        # In-memory storage for OTPs: {phone_number: {"otp": str, "expires": float}}
        self.otp_store: Dict[str, Dict] = {}
        self.otp_expiry = 300  # 5 minutes

    def generate_otp(self, phone: str) -> str:
        """Generate a random 4-digit OTP and store it."""
        otp = str(random.randint(100000, 999999))
        expiry = time.time() + self.otp_expiry
        self.otp_store[phone] = {"otp": otp, "expires": expiry}
        return otp

    def send_sms(self, phone: str, otp: str) -> bool:
        """Send OTP via Fast2SMS API."""
        # Try to reload the API key if it wasn't available during init
        if not self.api_key:
            self.api_key = os.environ.get("FAST2SMS_API_KEY")

        if not self.api_key:
            print(f"!!!! NO API KEY FOUND !!!!")
            print(f"[DEVELOPMENT MODE] Printing OTP to console for {phone}: {otp}")
            return True # Mock success in dev mode without key

        url = "https://www.fast2sms.com/dev/bulkV2"
        
        # Route 'otp' is for OTP services
        # variables_values are the dynamic parts of the message
        payload = {
            "route": "otp",
            "variables_values": otp,
            "numbers": phone
        }
        
        headers = {
            "authorization": self.api_key,
            "Content-Type": "application/x-www-form-urlencoded"
        }

        try:
            response = requests.post(url, data=payload, headers=headers, timeout=10)
            result = response.json()
            if response.status_code == 200 and result.get("return"):
                print(f"[OK] OTP sent successfully to {phone}")
                return True
            else:
                print(f"[ERROR] Fast2SMS failed: {result}")
                print(f"[FALLBACK] Printing OTP to console for {phone}: {otp}")
                return True
        except Exception as e:
            print(f"[ERROR] SMS delivery exception: {str(e)}")
            print(f"[FALLBACK] Printing OTP to console for {phone}: {otp}")
            return True

    def verify_otp(self, phone: str, otp_input: str) -> bool:
        """Verify the OTP entered by the user."""
        record = self.otp_store.get(phone)
        print(f"[AUTH] Verifying OTP for {phone}. Input: '{otp_input}', Stored: '{record.get('otp') if record else 'None'}'")
        
        if not record:
            print(f"[AUTH] No record found for phone {phone}")
            return False
        
        # Check expiry
        if time.time() > record["expires"]:
            print(f"[AUTH] OTP expired for {phone}")
            del self.otp_store[phone]
            return False
            
        # Check match
        if record["otp"] == otp_input:
            print(f"[AUTH] OTP Match Success for {phone}")
            del self.otp_store[phone]
            return True
            
        print(f"[AUTH] OTP Mismatch for {phone}")
        return False

# Singleton instance
auth_service = AuthService()
