"""
SOLD-OUT — apps.payments.validators

Credit card validators (PCI-DSS simulated).
"""

import datetime
import re

def luhn_check(number: str) -> bool:
    """Standart Luhn (modulus 10) algoritması ile kart numarasını doğrular."""
    # Boşluk ve tireleri temizle
    number = re.sub(r'[\s\-]', '', number)
    
    if not number.isdigit():
        return False
        
    if not (13 <= len(number) <= 19):
        return False

    total = 0
    reverse_digits = number[::-1]
    
    for i, char in enumerate(reverse_digits):
        n = int(char)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
        
    return total % 10 == 0


def detect_card_brand(number: str) -> str:
    """Kart numarasına göre marka tespiti yapar."""
    number = re.sub(r'[\s\-]', '', number)
    
    if not number.isdigit():
        return "UNKNOWN"

    # TROY: Türkiye'nin ödeme yöntemi, 9792 ile başlar, 16 hane
    if number.startswith("9792") and len(number) == 16:
        return "TROY"
        
    # VISA: 4 ile başlar, 13, 16 veya 19 hane
    if number.startswith("4") and len(number) in [13, 16, 19]:
        return "VISA"
        
    # MASTERCARD: 51-55 veya 2221-2720 ile başlar, 16 hane
    if len(number) == 16:
        prefix_2 = int(number[:2])
        prefix_4 = int(number[:4])
        if (51 <= prefix_2 <= 55) or (2221 <= prefix_4 <= 2720):
            return "MASTERCARD"
            
    # AMEX: 34 veya 37 ile başlar, 15 hane
    if (number.startswith("34") or number.startswith("37")) and len(number) == 15:
        return "AMEX"
        
    return "UNKNOWN"


def validate_cvv(cvv: str, brand: str) -> bool:
    """Markaya göre CVV geçerliliğini kontrol eder."""
    if not cvv.isdigit():
        return False
        
    if brand == "AMEX":
        return len(cvv) == 4
    else:
        return len(cvv) == 3


def validate_expiry(month: str, year: str) -> bool:
    """Son kullanma tarihinin geçip geçmediğini kontrol eder."""
    if not (month.isdigit() and year.isdigit()):
        return False
        
    m = int(month)
    y = int(year)
    
    if not (1 <= m <= 12):
        return False
        
    # Eğer 2 haneliyse, 2000 ekle
    if y < 100:
        y += 2000
        
    now = datetime.datetime.now()
    current_year = now.year
    current_month = now.month
    
    if y < current_year:
        return False
        
    if y == current_year and m < current_month:
        return False
        
    return True
