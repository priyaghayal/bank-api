# Banking API

This is a simple banking API built using FastAPI. It allows creating customers, managing accounts, and transferring funds.

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/priyaghayal/bank-api.git
   cd banking-api
   ```

2. Create a virtual environment and activate it:
    ```sh
    python -m venv .venv
    source .venv/bin/activate  # On macOS/Linux
    .venv\Scripts\activate  # On Windows
    ```

3. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

## Running the Project
Start the FastAPI server:

    
```sh
uvicorn main:app --reload
```


## API Documentation
Once the server is running, you can access the API documentation at:

- Swagger UI: http://127.0.0.1:8000/docs
- Redoc: http://127.0.0.1:8000/redoc

## Running Tests
To run the test cases, use:

```sh
pytest -v
```
