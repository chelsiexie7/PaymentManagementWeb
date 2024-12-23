import shutil
import os
from fastapi import UploadFile, File
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client.payment_management

def upload_evidence(file: UploadFile = File(...)):
    # 确保 evidence 目录存在
    os.makedirs("evidence", exist_ok=True)

    # 保存文件到 evidence 目录
    file_location = f"evidence/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 返回文件路径
    return {"file_location": file_location}

# 下载文件
def download_evidence(file_id: str):
    file = db.files.find_one({"_id": file_id})
    if file:
        return {"file_location": file['file_location']}
    return {"error": "File not found"}
