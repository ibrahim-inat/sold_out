"""
SOLD-OUT — tests/payments/test_validators.py
"""

import pytest
import datetime
from apps.payments.validators import luhn_check, detect_card_brand, validate_cvv, validate_expiry

def test_luhn_check_valid_visa():
    assert luhn_check("4111 1111 1111 1111") == True
    assert luhn_check("4111111111111111") == True

def test_luhn_check_invalid():
    assert luhn_check("4111 1111 1111 1112") == False

def test_luhn_check_non_digit():
    assert luhn_check("4111 1111 ABCD 1111") == False

def test_luhn_check_length():
    assert luhn_check("411111111111") == False # 12 digits
    assert luhn_check("41111111111111111111") == False # 20 digits

def test_detect_card_brand_visa():
    assert detect_card_brand("4111111111111") == "VISA"
    assert detect_card_brand("4111111111111111") == "VISA"

def test_detect_card_brand_mastercard():
    assert detect_card_brand("5111111111111111") == "MASTERCARD"
    assert detect_card_brand("5511111111111111") == "MASTERCARD"
    assert detect_card_brand("2221111111111111") == "MASTERCARD"

def test_detect_card_brand_amex():
    assert detect_card_brand("341111111111111") == "AMEX"
    assert detect_card_brand("371111111111111") == "AMEX"

def test_detect_card_brand_troy():
    assert detect_card_brand("9792111111111111") == "TROY"

def test_detect_card_brand_unknown():
    assert detect_card_brand("6011111111111111") == "UNKNOWN"

def test_validate_cvv():
    assert validate_cvv("123", "VISA") == True
    assert validate_cvv("1234", "VISA") == False
    assert validate_cvv("123", "AMEX") == False
    assert validate_cvv("1234", "AMEX") == True
    assert validate_cvv("ABC", "VISA") == False

def test_validate_expiry():
    now = datetime.datetime.now()
    current_year = now.year
    current_month = now.month
    
    # Future
    future_year = current_year + 1
    assert validate_expiry(str(current_month), str(future_year)) == True
    
    # Past year
    past_year = current_year - 1
    assert validate_expiry("12", str(past_year)) == False
    
    # Same year, past month
    if current_month > 1:
        assert validate_expiry(str(current_month - 1), str(current_year)) == False
        
    # Valid YY format
    assert validate_expiry("12", str(future_year)[-2:]) == True
