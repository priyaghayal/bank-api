from pydantic import BaseModel

# Customer Schema
class CustomerCreate(BaseModel):
    name: str

# Account Schema
class AccountCreate(BaseModel):
    initial_deposit: float

# Transfer Schema
class Transfer(BaseModel):
    from_account: int
    to_account: int
    amount: float
