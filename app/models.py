from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class Payment(BaseModel):
    payee_first_name: str
    payee_last_name: str
    payee_payment_status: str
    payee_added_date_utc: datetime
    payee_due_date: datetime
    payee_address_line_1: str
    payee_address_line_2: Optional[str]
    payee_city: str
    payee_country: str
    payee_province_or_state: Optional[str]
    payee_postal_code: str
    payee_phone_number: str
    payee_email: str
    currency: str
    discount_percent: Optional[float]
    tax_percent: Optional[float]
    due_amount: float
    total_due: float
