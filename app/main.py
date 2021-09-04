from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Form, File, UploadFile, Header, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from . import models, schemas, crud
from .tinkoff import init_first_payment, cancel_payment, perform_auto_payment, charge_auto_payment
from .database import SessionLocal, engine
from .reports import create_all_payments_report

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

def authorize(token: str, db: Session = Depends(get_db), role: str = 'ALL', id: int = None) -> bool:
    if token:
        access_token = token.split('Bearer ')[-1]
        suitable_users = db.query(models.User).filter(models.User.access_token == access_token)
        if suitable_users.count() > 0:
            suitable_user = suitable_users.first()
            if (role == 'ALL' or suitable_user.role.value == role) or (suitable_user.business_id == id):
                return suitable_user

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

@app.post("/api/user/auth", response_model={})
def authenticate(auth_item: schemas.AuthItem, db: Session = Depends(get_db)):
    return crud.authenticate(db, auth_item.login, auth_item.password)

@app.get("/api/user", response_model=Optional[schemas.User])
def get_users(authorization: str = Header(None), db: Session = Depends(get_db)):
    requestor = authorize(authorization, db, 'ALL')
    return requestor

@app.get("/api/businesses/{id}/messages", response_model=List[schemas.Message])
def get_messages(id, db: Session = Depends(get_db)):
    messages = crud.get_messages(db, id)
    return messages

@app.post("/api/businesses/{id}/messages", response_model={})
def send_message(id, data: schemas.MessageSend, authorization: str = Header(None), db: Session = Depends(get_db)):
    requestor = authorize(authorization, db)
    messages = crud.send_message(db, id, requestor.role, data.text)
    return {}

@app.get("/api/businesses/", response_model=List[schemas.Business])
def get_businesses(authorization: str = Header(None), db: Session = Depends(get_db)):
    requestor = authorize(authorization, db, 'ALL')
    all_businesses = crud.get_businesses(db)
    return all_businesses

@app.get("/api/businesses/report")
def get_payments_report(authorization: str = Header(None), db: Session = Depends(get_db)):
    return {}


@app.get("/api/businesses/{id}", response_model=schemas.Business)
def get_business(id, authorization: str = Header(None), db: Session = Depends(get_db)):
    requestor = authorize(authorization, db, 'ALL', id)
    business = crud.get_business_by_id(db, id)
    return business

@app.get("/api/businesses/{id}/agreement")
async def get_business_agreement(id, authorization: str = Header(None), db: Session = Depends(get_db)):
    agreement_path = crud.get_agreement_path(db, id)
    if agreement_path:
        return FileResponse(agreement_path)

@app.post("/api/businesses/{id}/agreement/break", response_model={})
def break_business_agreement(id, authorization: str = Header(None), db: Session = Depends(get_db)):
    requestor = authorize(authorization, db, 'AIRPORT')
    result = crud.break_agreement(db, id)
    # + Отправка на почту уведомления
    return result

@app.get("/api/businesses/{id}/payments")
def get_business_payments(id, authorization: str = Header(None), db: Session = Depends(get_db)):
    payments = crud.get_payments_by_id(db, id)
    create_all_payments_report(payments)
    return FileResponse('files/reports/report.xlsx')

@app.post("/api/businesses/{id}/payments/init", response_model=schemas.InitPaymentResponse)
def create_payment(id, data: schemas.InitPaymentItem, authorization: str = Header(None), db: Session = Depends(get_db)):
    requestor = authorize(authorization, db, 'BUSINESS', id)
    result = init_first_payment(data.summ, id)
    print(result)
    crud.update_autopayment(db, id, data.summ, result['id'])
    #crud.create_payment(db, id, data.summ, result['id'])
    return result

@app.get("/api/payments", response_model=List[schemas.Payment])
def get_all_payments(authorization: str = Header(None), db: Session = Depends(get_db)):
    all_payments = crud.get_all_payments(db)
    return all_payments

@app.post("/api/businesses/{id}/payments/confirm", response_model={})
def confirm_payment(id, data: schemas.ConfirmPaymentItem, db: Session = Depends(get_db)):
    print(data)
    # 1. set payment to authorized
    payment = crud.authorize_payment(db, data.PaymentId)    
    # 2. add card_id & rebill_id & autopayment
    crud.add_autopayment_data(db, id, data.RebillId, data.CardId)
    # 3. Increment locked_summ
    crud.increment_locked_summ(db, id, payment.summ)
    return {}

def get_acceptable_share():
    return 0.85

@app.get("/api/businesses/{id}/payments/withdraw", response_model={})
def withdraw_summ(id, authorization: str = Header(None), db: Session = Depends(get_db)):
    requestor = authorize(authorization, db, 'ALL', id)
    business = crud.get_business_by_id(db, id)

    if business.autopayment:
        acceptable_share = get_acceptable_share()
        # how much % business can withdraw
        return {"result": business.locked_summ * acceptable_share}

@app.post("/api/businesses/{id}/payments/withdraw", response_model={})
def withdraw_payment(id, data: schemas.WithdrawRequest, authorization: str = Header(None), db: Session = Depends(get_db)):
    requestor = authorize(authorization, db, 'BUSINESS', id)
    business = crud.get_business_by_id(db, id)

    if business.autopayment:
        acceptable_share = get_acceptable_share()
        # how much % business can withdraw

        result = crud.request_withdraw(db, id, data.summ, acceptable_share)

        if result and result['payment']:
            cancel_payment(result['payment'].tinkoff_id)

            payment = init_first_payment(result['recent_summ'], id)
            crud.create_payment(db, id, result['recent_summ'], payment['id'])
            charge_auto_payment(payment['id'], business.rebill_id)
            return {'success': True}

    return {'success': False}

@app.put("/api/businesses/{id}/payments/walletAddress", response_model={})
def update_wallet_adress(id, data: schemas.UpdateWalletAdress, authorization: str = Header(None), db: Session = Depends(get_db)):
    requestor = authorize(authorization, db, 'BUSINESS', id)
    print('1111', data.wallet_adress)
    crud.update_business_wallet_address(db, id, data.wallet_adress)
    return {}

@app.post("/api/businesses/{id}/payments/remind", response_model={})
def remind_about_payment(id, authorization: str = Header(None), db: Session = Depends(get_db)):
    # send to email notification and call
    pass