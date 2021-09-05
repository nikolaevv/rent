import datetime
import bcrypt
import secrets

from sqlalchemy.orm import Session
from .utils import save_file
from .config import CHAT_FOLDER_NAME, CONTRACTS_FOLDER_NAME
from . import models, schemas

def get_messages(db: Session, business_id: int):
    return db.query(models.Message).filter(models.Message.business_id == business_id).all()

def send_message(db: Session, business_id, role, text = None, file = None):
    timestamp = datetime.datetime.now()
    filename = save_file(CHAT_FOLDER_NAME, file)

    db_message = models.Message(business_id=business_id, role=role, timestamp=timestamp, text=text, filename=filename)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def authenticate(db: Session, login, password):
    suitable_users = db.query(models.User).filter(models.User.login == login)

    if suitable_users.count() > 0:
        suitable_user = suitable_users.first()
        is_correct_password = bcrypt.checkpw(password.encode('utf-8'), suitable_user.password_hash.encode('utf-8'))
        if is_correct_password:
            access_token = secrets.token_hex(nbytes=64)
            suitable_user.access_token = access_token
            db.commit()
            return {'correct': True, 'access_token': access_token}
    
    return {'correct': False}
 
def get_users(db: Session):
    return db.query(models.User).all()

def get_businesses(db: Session):
    return db.query(models.Business).all()

def get_business_by_id(db: Session, business_id: int):
    businesses = db.query(models.Business).filter(models.Business.id == business_id)
    if businesses.count() > 0:
        return businesses.first()

def get_agreement_path(db: Session, business_id: int):
    business = get_business_by_id(db, business_id)
    if business:
        if business.agreement:
            return 'files/{}/{}'.format(CONTRACTS_FOLDER_NAME, business.agreement)

def break_agreement(db: Session, business_id: int):
    business = get_business_by_id(db, business_id)
    if business:
        if business.is_agreement_active and business.debt > 0 and business.termination_time:
            business.is_agreement_active = False
            db.commit()
            return {"success": True}

    return {"success": False}

def create_payment(db: Session, business_id, summ, tinkoff_id):
    timestamp = datetime.datetime.now()
    business = get_business_by_id(db, business_id)
    

    if business:
        db_payment = models.Payment(business_id=business.id, tinkoff_id=tinkoff_id, summ=summ, timestamp=timestamp)
        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)
        return db_payment

def get_payment_by_id(db: Session, tinkoff_id: int):
    payments = db.query(models.Payment).filter(models.Payment.tinkoff_id == tinkoff_id)
    if payments.count() > 0:
        return payments.first()

def get_payments_by_id(db: Session, business_id: int):
    payments = db.query(models.Payment).filter(models.Payment.business_id == business_id)
    return payments

def authorize_payment(db: Session, tinkoff_id: int):
    payment = get_payment_by_id(db, tinkoff_id)
    payment.status = 'AUTHORIZED'
    db.commit()
    return payment

def add_autopayment_data(db: Session, business_id: id, rebill_id: int, card_id: int):
    business = get_business_by_id(db, business_id)
    business.rebill_id = rebill_id
    business.card_id = card_id
    business.autopayment = True
    db.commit()

def increment_locked_summ(db: Session, business_id: id, summ: int):
    business = get_business_by_id(db, business_id)
    business.locked_summ += summ
    db.commit()

def get_active_payment(db: Session, business_id: id):
    payments = db.query(models.Payment).filter(models.Payment.business_id == business_id).filter(models.Payment.status == 'AUTHORIZED')
    if payments.count() > 0:
        return payments.first()

def request_withdraw(db: Session, business_id: id, summ: int, acceptable_share: float):
    business = get_business_by_id(db, business_id)
    locked_summ = business.locked_summ
    if summ <= locked_summ * acceptable_share:
        locked_summ = business.locked_summ - summ
        business.locked_summ = 0
        db.commit()

        return {
            'payment': get_active_payment(db, business_id),
            'recent_summ': locked_summ
        }

    return False

def update_business_wallet_address(db: Session, business_id: id, wallet_address: str, private_key: str):
    business = get_business_by_id(db, business_id)
    business.wallet_address = wallet_address
    business.private_key = private_key
    db.commit()

def get_all_payments(db: Session):
    return db.query(models.Payment).all()