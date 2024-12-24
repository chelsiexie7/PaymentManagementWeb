from .models import Payment
from pymongo import MongoClient
import pandas as pd
from datetime import datetime
from bson.objectid import ObjectId
import math

client = MongoClient("mongodb://localhost:27017/")
db = client.payment_management

# store csv data into the mongodb database
def import_csv_to_db(file_path: str):
    df = pd.read_csv(file_path)
    
    #format the data
    df['payee_added_date_utc'] = pd.to_datetime(df['payee_added_date_utc'])
    df['payee_due_date'] = pd.to_datetime(df['payee_due_date'])
    df['total_due'] = df.apply(calculate_total_due, axis=1)

    # inert the data into MongoDB
    for _, row in df.iterrows():
        db.payments.insert_one(row.to_dict())

def calculate_total_due(row):
    discount = row['discount_percent'] if pd.notna(row['discount_percent']) else 0
    tax = row['tax_percent'] if pd.notna(row['tax_percent']) else 0
    due_amount = row['due_amount']
    
    total_due = due_amount * (1 - discount / 100) * (1 + tax / 100)
    return round(total_due, 2)

from datetime import datetime

def get_payments(name: str = None):
    query = {}
    if name:
        query["payee_first_name"] = {"$regex": name, "$options": "i"}  

    payments_cursor = db.payments.find(query)
    updated_payments = []
    for payment in payments_cursor:
        payment["_id"] = str(payment["_id"])


        if isinstance(payment['payee_due_date'], str):
            due_date = datetime.strptime(payment['payee_due_date'], "%Y-%m-%d").date()
        elif isinstance(payment['payee_due_date'], datetime):
            due_date = payment['payee_due_date'].date()
        else:
            raise ValueError("Invalid date format in 'payee_due_date'")

        if due_date == datetime.today().date():
            payment['payee_payment_status'] = 'due_now'
        elif due_date < datetime.today().date():
            payment['payee_payment_status'] = 'overdue'

        db.payments.update_one({'_id': ObjectId(payment['_id'])}, {'$set': {'payee_payment_status': payment['payee_payment_status']}})

        # subsititute NaN to None
        for key, value in payment.items():
            if isinstance(value, float) and math.isnan(value):
                payment[key] = None

        updated_payments.append(payment)

    return updated_payments


# post function
def create_payment(payment: Payment):
    payment_data = payment.dict()
    db.payments.insert_one(payment_data)
    return {"id": str(payment_data["_id"])}

# update function
def update_payment(payment_id: str, payment: Payment):
    update_data = payment.dict(exclude_unset=True)
    db.payments.update_one({"_id": payment_id}, {"$set": update_data})
    return {"status": "success"}

# delete function
def delete_payment(payment_id: str):
    db.payments.delete_one({"_id": payment_id})
    return {"status": "success"}

import_csv_to_db('app/payment_information.csv')

