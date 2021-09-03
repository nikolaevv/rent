from datetime import datetime, date
from typing import Optional
from .choices import Role, Terminal, PaymentStatus
from pydantic import BaseModel

class Business(BaseModel):
    id: int
    title: str
    terminal: Optional[Terminal]
    stage: Optional[int]
    account_numbers: Optional[str]
    square: Optional[float]
    autopayment: bool
    TIN: str
    rent_rate: Optional[float]
    is_agreement_active: bool
    debt: float
    agreement: Optional[str]
    payment_time: Optional[datetime]
    termination_time: Optional[datetime]
    signing_date: Optional[date]
    email: Optional[str]
    phone: Optional[str]
    card_id: Optional[int]
    wallet_address: Optional[str]
    rebill_id: Optional[int]
    locked_summ: Optional[float]

    class Config:
        orm_mode = True

class Message(BaseModel):
    id: int
    business_id: int
    timestamp: datetime
    text: Optional[str]
    filename: Optional[str]
    role: Role

    class Config:
        orm_mode = True

class User(BaseModel):
    id: int
    business_id: Optional[int]
    login: str
    password_hash: str
    access_token: Optional[str]
    role: Role

    class Config:
        orm_mode = True

class Payment(BaseModel):
    id: int
    business_id: int
    summ: float
    status: PaymentStatus
    timestamp: datetime

    class Config:
        orm_mode = True

class MessageItem(BaseModel):
    text: str
    file: str

class InitPaymentItem(BaseModel):
    summ: float

class InitPaymentResponse(BaseModel):
    id: int
    url: str

class UpdateWalletAdress(BaseModel):
    wallet_adress: str

class ConfirmPaymentItem(BaseModel):
    TerminalKey: str
    PaymentId: int
    Status: str
    Success: bool
    CardId: int
    RebillId: int

class WithdrawRequest(BaseModel):
    summ: float

class AuthItem(BaseModel):
    login: str
    password: str