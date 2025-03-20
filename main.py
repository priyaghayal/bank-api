from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, Float, ForeignKey, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# Database setup
DATABASE_URL = "sqlite:///./bank.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    balance = Column(Float, default=0.0)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    from_account = Column(Integer, ForeignKey("accounts.id"))
    to_account = Column(Integer, ForeignKey("accounts.id"))
    amount = Column(Float)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Schemas
class CustomerCreate(BaseModel):
    name: str

class AccountCreate(BaseModel):
    initial_deposit: float

class Transfer(BaseModel):
    from_account: int
    to_account: int
    amount: float

# FastAPI app
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/customers/")
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    new_customer = Customer(name=customer.name)
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer

@app.get("/customers/{customer_id}")
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@app.post("/customers/{customer_id}/accounts/")
def create_account(customer_id: int, account: AccountCreate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    new_account = Account(customer_id=customer_id, balance=account.initial_deposit)
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    
    return {
        "account_id": new_account.id,
        "customer_id": customer.id,
        "customer_name": customer.name,
        "balance": new_account.balance
    }

@app.post("/transfers/")
def transfer_funds(transfer: Transfer, db: Session = Depends(get_db)):
    from_acc = db.query(Account).filter(Account.id == transfer.from_account).first()
    to_acc = db.query(Account).filter(Account.id == transfer.to_account).first()
    
    if not from_acc or not to_acc:
        raise HTTPException(status_code=404, detail="One or both accounts not found")
    if from_acc.balance < transfer.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")
    
    from_acc.balance -= transfer.amount
    to_acc.balance += transfer.amount
    new_transaction = Transaction(from_account=from_acc.id, to_account=to_acc.id, amount=transfer.amount)
    db.add(new_transaction)
    db.commit()
    return {"message": "Transfer successful"}

@app.get("/accounts/{account_id}/balance/")
def get_balance(account_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"account_id": account.id, "balance": account.balance}

@app.get("/accounts/{account_id}/transactions/")
def get_transactions(account_id: int, db: Session = Depends(get_db)):
    transactions = db.query(Transaction).filter((Transaction.from_account == account_id) | (Transaction.to_account == account_id)).all()
    return transactions
