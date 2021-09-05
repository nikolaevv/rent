from .crud import get_businesses, get_active_payment
from .tinkoff import init_auto_payment, charge_auto_payment, cancel_payment
import datetime
from app import models
from app.database import SessionLocal, engine

db = SessionLocal()

businesses = get_businesses(db)

def get_acceptable_share():
    return 0.85

for business in businesses:
    if business.autopayment:
        summ = business.locked_summ

        active_payment = get_active_payment(db)

        if (datetime.datetime.now() - active_payment.timestamp).days >= 6:

            cancel_payment(id)

            if get_acceptable_share() < 0.3:
                summ *= 3
            
            payment_id = init_auto_payment(summ, business.id)
            charge_auto_payment(payment_id, rebill_id)