# ✈️ Airport & Management System

![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-6.0-092E20?style=flat&logo=django&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)
![Postgres](https://img.shields.io/badge/PostgreSQL-15-316192?style=flat&logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/redis-%23DD0031.svg?style=flat&logo=redis&logoColor=white)
![Celery](https://img.shields.io/badge/celery-%2337814A.svg?style=flat&logo=celery&logoColor=white)
![Pytest](https://img.shields.io/badge/pytest-%23ffffff.svg?style=flat&logo=pytest&logoColor=2f96e4)

**Backend system for managing airport logistics, flights, tickets, and passenger transport.**

The project is developed based on **Django 6.0**. The system ensures a full ticket booking cycle, including online payment, AI assistant support, and real-time status updates.

---

## 🛠 Tech Stack

### 🔹 Core & Backend
* **Python 3.13** — programming language.
* **Django 6.0** — main framework.
* **Django REST Framework (DRF)** — REST API.
* **PostgreSQL 15** — database.

### 🔹 Real-time & AI
* **Django Channels (Uvicorn)** — WebSockets for chats and notifications.
* **Google Gemini (GenAI)** — AI assistant for users.

### 🔹 Task Queue & Caching
* **Celery** — distributed task queue (background processes, emails).
* **Redis** — message broker and caching backend.

### 🔹 Quality Assurance (Testing)
* **Pytest** — framework for unit and integration testing.
  
### 🔹 Integrations & Tools
* **Stripe** — payment system.
* **Docker & Docker Compose** — containerization.
* **DRF Spectacular** — documentation (Swagger).
* **Django Silk** — SQL query monitoring.
* **Simple JWT** — JWT token auth

---

## 🚀 How to Run the Project (Docker)

To run, you need [Docker Desktop](https://www.docker.com/products/docker-desktop).

### 1. Clone the repository
```bash
git clone "https://github.com/Vladyslav3012/DRF.git"
```
Navigate to the working directory
```bash
cd DRF
```
### 2. Configure variables (.env)
Create a .env file in the project root and add your settings:
```bash
# Django Core
SECRET_KEY=your_secret_key_change_me

# Database
DATABASE_NAME=Airport
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
DATABASE_HOST=db
DATABASE_PORT=5432

#JWT auth
ACCESS_TOKEN_LIFETIME=30
REFRESH_TOKEN_LIFETIME=1
AUTH_HEADER_TYPES = JWT

# Integrations (API Keys)
STRIPE_PUBLIC_KEY="change me"
STRIPE_SECRET_KEY="change me"
STRIPE_WEBHOOK_SECRET="change me"
GEMINI_SECRET_KEY="change me"
SECRET_TOKEN_TO_WEBHOOK="change me"
NGROK_AUTHTOKEN='change me'

# Celery & Redis
EMAIL_HOST_USER='youemail@gmail.com'
EMAIL_HOST_PASSWORD='secretpasswordchangeme'

CELERY_BROKER_URL=''
CELERY_RESULT_BACKEND=''
```
In Stripe, create a webhook with an additional path parameter, which will be your SECRET_TOKEN_TO_WEBHOOK.

### 3. Start containers
```bash
docker-compose up --build
```
### 4. Create administrator
Open a new terminal and run the command:

```bash
docker-compose exec web python manage.py createsuperuser
```
## 🔗 Available Links
| Service | URL |
| :--- | :--- |
| **Swagger UI (Docs)** | `<you-ngrok-address>/api/docs/` |
| **Admin-Panel** | `<you-ngrok-address>/admin/` |
| **Silk (Monitoring)** | `<you-ngrok-address>/silk/` |
| **Chat with AI** | `<you-ngrok-address>/api/v1/gemini/chat` |
### If you don't have an ngrok address, you can use localhost:8000

## ⚠️ Troubleshooting (Windows)
If you see error:
```bash
exec ./entrypoint.sh: no such file or directory
```
This is a line ending format issue (CRLF). 
Open entrypoint.sh in VS Code. 
Change CRLF to LF in the bottom right corner.
Save the file and restart the container.
