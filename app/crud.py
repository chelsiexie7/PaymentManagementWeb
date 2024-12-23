from .models import Payment
from pymongo import MongoClient
import pandas as pd
from datetime import datetime
from bson.objectid import ObjectId
import math

# 连接MongoDB数据库
client = MongoClient("mongodb://localhost:27017/")
db = client.payment_management

# 将CSV文件数据插入到数据库
def import_csv_to_db(file_path: str):
    df = pd.read_csv(file_path)
    
    # 确保字段符合规定
    df['payee_added_date_utc'] = pd.to_datetime(df['payee_added_date_utc'])
    df['payee_due_date'] = pd.to_datetime(df['payee_due_date'])
    df['total_due'] = df.apply(calculate_total_due, axis=1)

    # 将数据插入到MongoDB
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
    # 创建 MongoDB 查询条件
    query = {}
    if name:
        query["payee_first_name"] = {"$regex": name, "$options": "i"}  # 模糊匹配名字，忽略大小写

    payments_cursor = db.payments.find(query)
    updated_payments = []
    for payment in payments_cursor:
        # 转换 _id 为字符串
        payment["_id"] = str(payment["_id"])

        # 检查并转换 payee_due_date 的格式
        if isinstance(payment['payee_due_date'], str):
            due_date = datetime.strptime(payment['payee_due_date'], "%Y-%m-%d").date()
        elif isinstance(payment['payee_due_date'], datetime):
            due_date = payment['payee_due_date'].date()
        else:
            raise ValueError("Invalid date format in 'payee_due_date'")

        # 检查并更新支付状态
        if due_date == datetime.today().date():
            payment['payee_payment_status'] = 'due_now'
        elif due_date < datetime.today().date():
            payment['payee_payment_status'] = 'overdue'

        # 更新数据库中的记录
        db.payments.update_one({'_id': ObjectId(payment['_id'])}, {'$set': {'payee_payment_status': payment['payee_payment_status']}})

        # 替换 NaN 值为 None
        for key, value in payment.items():
            if isinstance(value, float) and math.isnan(value):
                payment[key] = None

        updated_payments.append(payment)

    return updated_payments


# 创建支付记录
def create_payment(payment: Payment):
    payment_data = payment.dict()
    db.payments.insert_one(payment_data)
    return {"id": str(payment_data["_id"])}

# 更新支付记录
def update_payment(payment_id: str, payment: Payment):
    update_data = payment.dict(exclude_unset=True)
    db.payments.update_one({"_id": payment_id}, {"$set": update_data})
    return {"status": "success"}

# 删除支付记录
def delete_payment(payment_id: str):
    db.payments.delete_one({"_id": payment_id})
    return {"status": "success"}

import_csv_to_db('app/payment_information.csv')

