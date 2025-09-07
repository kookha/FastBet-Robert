import os
import firebase_admin
from firebase_admin import credentials, firestore

# تحميل المفتاح (خليه مخزّن عندك باسم serviceAccountKey.json)
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

# إضافة مستخدم جديد
def create_user(user_id, username, syriatel_number, balance=0):
    doc_ref = db.collection("users").document(str(user_id))
    doc_ref.set({
        "username": username,
        "syriatel_number": syriatel_number,
        "balance": balance
    })

# جلب بيانات مستخدم
def get_user(user_id):
    doc_ref = db.collection("users").document(str(user_id))
    doc = doc_ref.get()
    if doc.exists:
        return doc.to_dict()
    return None

# تحديث رصيد مستخدم
def update_balance(user_id, new_balance):
    doc_ref = db.collection("users").document(str(user_id))
    doc_ref.update({"balance": new_balance})
