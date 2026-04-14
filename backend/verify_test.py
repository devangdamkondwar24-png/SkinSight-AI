import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'services'))
from services.auth_service import auth_service

def test_otp_logic():
    phone = "1234567890"
    print(f"--- Starting OTP Logic Test ---")
    
    # 1. Generate OTP
    otp = auth_service.generate_otp(phone)
    print(f"Generated OTP: {otp}")
    
    # 2. Verify with wrong OTP (1234)
    result_wrong = auth_service.verify_otp(phone, "1234")
    print(f"Verify with '1234': {result_wrong}")
    
    # 3. Generate again and verify with correct OTP
    otp_new = auth_service.generate_otp(phone)
    result_correct = auth_service.verify_otp(phone, otp_new)
    print(f"Verify with correct '{otp_new}': {result_correct}")
    
    if not result_wrong and result_correct:
        print("\n[SUCCESS] Logic is sound. '1234' was rejected correctly.")
    else:
        print("\n[FAILURE] Logic bug found!")

if __name__ == "__main__":
    test_otp_logic()
