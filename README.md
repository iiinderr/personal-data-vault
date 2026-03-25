# 🔐 Personal Data Vault

A **privacy-first backend API** built with FastAPI that securely stores sensitive user data using encryption, authentication, and access control.

## 🚀 What is this project?

This project is a **secure data vault system** where users can:

* Store encrypted notes
* Save password hints securely
* Manage document metadata
* Authenticate using JWT
* Access data based on roles (RBAC)

👉 This is a **backend-only project**, tested via Swagger UI (`/docs`).

---

## 🧠 Why this project?

Most apps store sensitive data insecurely.
This project focuses on:

* **Security-first design**
* **Encryption at rest**
* **Proper authentication & authorization**
* **Audit logging (real-world feature)**

---

## 🛠️ Tech Stack

* FastAPI
* SQLAlchemy
* SQLite
* JWT (PyJWT)
* bcrypt
* cryptography (Fernet)
* Pytest

---

## ▶️ Run Locally

```bash
git clone <your-repo-url>
cd personal-data-vault
pip install -r requirements.txt
uvicorn main:app --reload
```

Open:

```
http://127.0.0.1:8000/docs
```
---

## 📡 API Endpoints

### 🔑 Auth

| Method | Endpoint               | Description      |
| ------ | ---------------------- | ---------------- |
| POST   | /api/v1/users/register | Register user    |
| POST   | /api/v1/users/login    | Login (get JWT)  |
| GET    | /api/v1/users/me       | Get current user |

---

### 📝 Notes

| Method | Endpoint           | Description        |
| ------ | ------------------ | ------------------ |
| POST   | /api/v1/notes/     | Create note        |
| GET    | /api/v1/notes/     | List notes         |
| GET    | /api/v1/notes/{id} | Get decrypted note |
| DELETE | /api/v1/notes/{id} | Delete note        |

---

### 📄 Documents

| Method | Endpoint           | Description           |
| ------ | ------------------ | --------------------- |
| POST   | /api/v1/documents/ | Add document metadata |
| GET    | /api/v1/documents/ | List documents        |

---

### 🔐 Password Hints

| Method | Endpoint           | Description        |
| ------ | ------------------ | ------------------ |
| POST   | /api/v1/hints/     | Create hint        |
| GET    | /api/v1/hints/     | List hints         |
| GET    | /api/v1/hints/{id} | Get decrypted hint |

---

### 👑 Admin

| Method | Endpoint                      | Description |
| ------ | ----------------------------- | ----------- |
| GET    | /api/v1/admin/audit-logs      | View logs   |
| GET    | /api/v1/admin/users           | List users  |
| PATCH  | /api/v1/admin/users/{id}/role | Change role |
