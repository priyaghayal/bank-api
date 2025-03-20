from fastapi.testclient import TestClient
from main import app, Base, engine
import pytest

# Setup test client
client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Reset database before each test"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield

# Test cases
def test_create_customer():
    response = client.post("/customers/", json={"name": "John Doe"})
    assert response.status_code == 200
    assert response.json()["name"] == "John Doe"

def test_transfer_funds():
    customer_1 = client.post("/customers/", json={"name": "Charlie"}).json()
    customer_2 = client.post("/customers/", json={"name": "Dave"}).json()
    account_1 = client.post(f"/customers/{customer_1['id']}/accounts/", json={"initial_deposit": 200.0}).json()
    account_2 = client.post(f"/customers/{customer_2['id']}/accounts/", json={"initial_deposit": 50.0}).json()
    
    transfer_data = {"from_account": account_1["account_id"], "to_account": account_2["account_id"], "amount": 100.0}
    response = client.post("/transfers/", json=transfer_data)
    
    assert response.status_code == 200
    assert response.json()["message"] == "Transfer successful"
