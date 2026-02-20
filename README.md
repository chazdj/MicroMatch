# MicroMatch

MicroMatch is a micro-internship marketplace connecting students with short-term professional opportunities.

It is a full-stack web application built with React and FastAPI, featuring secure JWT authentication, role-based access control, and containerized PostgreSQL infrastructure. The project follows agile sprint methodology and emphasizes scalable architecture and secure backend practices.

## Features

* **User Authentication:** Registration and login for students, organizations, and admins using JWT.
* **Role-Based Access Control (RBAC):** Students, organizations, and admins have different permissions.
* **Project Management:** Organizations can create and manage projects.
* **Project Discovery:** Students can view and filter projects by required skills.
* **Frontend Integration:** React frontend connected to FastAPI backend.
* **End-to-End Workflow:** Full registration → profile creation → project posting → student project browsing.

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
├── backend/
│   ├── app/
│   │   ├── core/                # Authentication and dependencies
│   │   ├── routers/             # API routes (auth, projects, profiles)
│   │   ├── schemas/             # Pydantic models
│   │   ├── utils/               # Password hashing & utilities
│   │   ├── database.py          # Database setup
│   │   ├── main.py              # FastAPI app
│   │   └── models.py            # SQLAlchemy models
│   ├── tests/                   # Unit and integration tests
│   ├── requirements.txt
│   └── test.db                  # SQLite test database
├── frontend/                     # React frontend
├── docker-compose.yml            # Backend & DB setup
├── .gitignore
└── README.md
```

## Installation

**1. Clone the Repository**
```bash
git clone https://github.com/chazdj/MicroMatch.git
cd MicroMatch
```
**2. Setup Backend Environment**
```bash
cd backend
python -m venv venv
source venv/Scripts/activate #Windows
pip install -r requirements.txt
```

**3. Setup Frontend Environment**
```bash
cd ../frontend
npm install
```

**4. Start PostgreSQL using Docker**
```bash
docker-compose up -d
```

## Running the Application

### Backend
```bash
cd backend
uvicorn app.main:app --reload
```
API will run on `http://127.0.0.1:8000`

### Frontend
```bash
cd frontend
npm start
```
Frontend will run on `http://localhost:3000`

**Login / Registration:**
* `/login` → User login page
* `/register` → User registration page
* `/` → Home/dashboard (protected route)

## Testing & Coverage

### Run tests:
```bash
cd backend
pytest
```

### Run tests with coverage:
```bash
coverage run -m pytest tests/
coverage report -m > coverage_summary.txt
```

### Coverage Categories
* Models
* API Endpoints
* RBAC Logic
* Search & Pagination Logic
* Overall Backend Coverage

The results are saved to `coverage_summary.txt`.

## Usage
* **Students:** Register → Login → Browse available projects → View project details

* **Organizations:** Register → Login → Create projects → View posted projects

* **Admin: **Access admin-only endpoints and manage users/projects

## Author

Chastidy Joanem  
M.S. Software Engineering  
B.S. Computer Science