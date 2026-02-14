# MicroMatch

MicroMatch is a micro-internship marketplace connecting students with short-term professional opportunities.

MicroMatch is a full-stack web application built with React and FastAPI, featuring secure JWT authentication, role-based access control, and containerized PostgreSQL infrastructure.

The project follows agile sprint methodology and emphasizes scalable architecture and secure backend practices.

## Tech Stack

### Frontend
* React
* Vite
* Axios
* React Router

### Backend
* FastAPI
* SQLAlchemy
* PostgreSQL
* Passlib (bcrypt)
* Python-JOSE (JWT)

### DevOps
* Docker
* Docker Compose

## Project Structure
```bash
MicroMatch/
│
├── backend/
│   └── app/
│       ├── core/
│       │   ├── auth.py
│       │   └── dependencies.py
│       ├── routers/
│       │   └── auth.py
│       ├── schemas/
│       │   └── user.py
│       ├── utils/
│       │   └── security.py
│       ├── database.py
│       ├── models.py
│       └── main.py
│
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package-lock.json
│   ├── package.json
│   └── README.md
│
├── README.md
└── docker-compose.yml
```

## Authentication System
**Implemented in Sprint 1:**
* User registration
* Secure password hashing (bcrypt)
* OAuth2 password login flow
* JWT token generation
* Token expiration handling
* Protected routes
* Role-Based Access Control (RBAC)

### Security Highlights
* Passwords are never stored in plain text
* JWT tokens include user ID and role
* Proper 401 vs 403 status handling
* Database-level uniqueness constraints

## Running the Application
**1. Clone the Repository**
```bash
git clone https://github.com/chazdj/MicroMatch.git
cd MicroMatch
```
**2. Start Database with Docker** 
```bash
docker-compose up -d
```
**3. Set Up Backend Environment**
```bash
cd backend
python -m venv venv
source venv/Scripts/activate #Windows
pip install -r requirements.txt
```
**4. Run Backend**
```bash
uvicorn app.main:app --reload
```

Backend runs at:

http://127.0.0.1:8000


Swagger API Docs available at:

http://127.0.0.1:8000/docs

**5. Run Frontend**
```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:

http://localhost:5173

## Authentication Flow

1. User registers
2. User logs in
3. JWT token returned
4. Token stored client-side
5. Protected routes require valid token
6. Role determines authorization level

## Sprint Progress

Sprint 1 Completed:

* Backend architecture
* Database integration
* Secure authentication
* Role-based access control
* Frontend scaffold setup

Next Sprint:

* Frontend auth UI
* Protected route logic
* User profile system
* Matching feature

## Author

Chastidy Joanem  
M.S. Software Engineering  
B.S. Computer Science