import os
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, Float, ForeignKey, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from dotenv import load_dotenv
from database import get_db, Base, engine
from models import Customer, Account, Transaction
from schemas import CustomerCreate, AccountCreate, Transfer
from utils import ERROR_MESSAGES

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Initialize FastAPI app
app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

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
        raise HTTPException(status_code=404, detail=ERROR_MESSAGES["customer_not_found"])
    return customer

@app.post("/customers/{customer_id}/accounts/")
def create_account(customer_id: int, account: AccountCreate, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail=ERROR_MESSAGES["customer_not_found"])
    
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
        raise HTTPException(status_code=404, detail=ERROR_MESSAGES["account_not_found"])
    if from_acc.balance < transfer.amount:
        raise HTTPException(status_code=400, detail=ERROR_MESSAGES["insufficient_funds"])
    
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
        raise HTTPException(status_code=404, detail=ERROR_MESSAGES["account_not_found"])
    return {"account_id": account.id, "balance": account.balance}

@app.get("/accounts/{account_id}/transactions/")
def get_transactions(account_id: int, db: Session = Depends(get_db)):
    transactions = db.query(Transaction).filter((Transaction.from_account == account_id) | (Transaction.to_account == account_id)).all()
    return transactions
