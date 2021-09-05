from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.types import DateTime, Text, Enum, Date
from sqlalchemy.orm import relationship
from .database import Base
from .choices import Role, Terminal, PaymentStatus

class Business(Base):
    __tablename__ = "business"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255))
    terminal = Column(Enum(Terminal), nullable=True)
    stage = Column(Integer, nullable=True)
    account_numbers = Column(Text, nullable=True)
    square = Column(Float, nullable=True)
    autopayment = Column(Boolean, default = False)
    TIN = Column(Text)
    rent_rate = Column(Float, nullable=True)
    is_agreement_active = Column(Boolean, default=False)
    debt = Column(Float, default=0)
    agreement = Column(String(255), nullable=True)
    payment_time = Column(DateTime, nullable=True)
    termination_time = Column(DateTime, nullable=True)
    signing_date = Column(Date, nullable=True)
    email = Column(Text)
    phone = Column(String(255))
    locked_summ = Column(Float, default=0.0)
    rebill_id = Column(Integer, nullable=True)
    card_id = Column(Integer, nullable=True)

    wallet_address = Column(Text, nullable=True)
    private_key = Column(Text, nullable=True)

    messages = relationship("Message")
    users = relationship("User")
    payments = relationship("Payment")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(255))
    business_id = Column(Integer, ForeignKey('business.id'), nullable=True)
    password_hash = Column(Text)
    access_token = Column(Text)
    role = Column(Enum(Role))

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey('business.id'))
    timestamp = Column(DateTime)
    text = Column(Text, index=True, nullable=True)
    filename = Column(String(255), index=True, nullable=True)
    role = Column(Enum(Role))

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    summ = Column(Float)
    tinkoff_id = Column(Text)
    business_id = Column(Integer, ForeignKey('business.id'))
    status = Column(Enum(PaymentStatus), default="PROCEED")
    timestamp = Column(DateTime)