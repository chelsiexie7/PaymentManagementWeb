from fastapi import FastAPI, UploadFile, File
from .crud import get_payments, create_payment, update_payment, delete_payment
from .models import Payment
from .utils import upload_evidence, download_evidence
from fastapi import Query
from fastapi.encoders import jsonable_encoder

app = FastAPI()

@app.get("/payments/")
def get_payments_route(name: str = Query(None)):
    payments = get_payments(name=name)
    return jsonable_encoder(payments)

@app.post("/payments/")
def create_payment_route(payment: Payment):
    return create_payment(payment)

@app.put("/payments/{payment_id}")
def update_payment_route(payment_id: str, payment: Payment):
    return update_payment(payment_id, payment)

@app.delete("/payments/{payment_id}")
def delete_payment_route(payment_id: str):
    return delete_payment(payment_id)

@app.post("/upload_evidence/")
def upload_evidence_route(file: UploadFile = File(...)):
    return upload_evidence(file)

@app.get("/download_evidence/{file_id}")
def download_evidence_route(file_id: str):
    return download_evidence(file_id)
