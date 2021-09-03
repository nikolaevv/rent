import datetime

from app import models
from app.database import SessionLocal, engine

db = SessionLocal()

models.Base.metadata.create_all(bind=engine)

db_record = models.Business(
    email="starlei165@gmail.com",
    phone="1111",
    debt=10000,
    is_agreement_active=True,
    termination_time=datetime.datetime.now(),
    TIN="111111111111111",
    title="Macdonalds",
    agreement="Вадим's Resume.pdf"
)

db.add(db_record)

db_record = models.User(
    login="starlei165@gmail.com",
    password_hash="$2a$10$hCyWcJ302enjX4tEFd/m.uiLGLhFSMHe.X6EEjIR4pWoIYhZtwGi2",
    access_token="111111111111111",
    business_id=1,
    role="BUSINESS",
)

db.add(db_record)

db_record = models.User(
    login="arabic165@gmail.com",
    password_hash="$2a$10$hCyWcJ302enjX4tEFd/m.uiLGLhFSMHe.X6EEjIR4pWoIYhZtwGi2",
    access_token="111111111111111",
    role="AIRPORT",
)

db.add(db_record)

db_record = models.Message(
    timestamp=datetime.datetime.now(),
    text="Лови уведомление о расторжении контракта",
    business_id=1,
    filename="s4x76309uj387jff.pdf",
    role="AIRPORT",
)

db.add(db_record)

db.commit()
db.close()