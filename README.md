# MicroMatch

MicroMatch is a full-stack micro-internship marketplace that connects students with short-term, skill-based professional opportunities. Built with React and FastAPI, the platform supports the complete micro-internship lifecycle — from account creation and project discovery through application management, deliverable submission, project completion, and post-project feedback.

The project follows Agile sprint methodology across four sprints, emphasizing scalable architecture, secure backend practices, intelligent matching, and a polished user experience.

---

## Features

### Core Platform
- **User Authentication** — Registration and JWT-based login for students, organizations, and admins
- **Role-Based Access Control (RBAC)** — Students, organizations, and admins have fully separated permissions enforced at every endpoint
- **Student Profiles** — University, major, graduation year, skills, bio, portfolio links, and auto-awarded achievement badges
- **Organization Profiles** — Company name, industry, website, and description
- **Project Management** — Organizations can create, manage, and close projects
- **Project Discovery** — Students can browse and filter projects by required skills

### Application Workflow
- **Apply to Projects** — Students submit applications with cover notes
- **Application Review** — Organizations accept or reject applications
- **Application Tracking** — Students track real-time application status

### Project Completion Lifecycle
- **Deliverable Submission** — Accepted students submit links or content as project deliverables
- **Deliverable Review** — Organizations review and approve submitted deliverables
- **Project Completion** — Organizations mark projects complete, triggering badge awards and notifications
- **Feedback System** — Post-completion ratings and comments for both parties

### Messaging
- **Project-Scoped Messaging** — Accepted students and their organization can exchange messages within a project
- **Messages Hub** — Dedicated `/messages` page with left sidebar listing all active project conversations
- **Real-Time Polling** — Auto-refresh every 5 seconds keeps conversations current
- **Message Notifications** — Each sent message triggers a bell notification for the recipient

### Notifications
- **Event-Driven Notifications** — Bell icon in navbar shows unread count; triggered by application decisions, deliverable reviews, project completion, and new messages
- **Mark as Read** — Individual notifications can be dismissed

### Analytics Dashboard
- **Student Analytics** — Applications submitted, accepted, completed projects, and average feedback rating displayed as stat cards and a bar chart on the home dashboard
- **Organization Analytics** — Total projects posted, active projects, completed projects, and unique applicants
- **Role-Separated Views** — Each role sees only their own metrics; cross-role access returns 403

### Smart Matching & Recommendations
- **Matching Score Engine** — Five-factor weighted algorithm scoring projects against student skills, graduation year, interests, and activity
- **Personalized Recommendations** — Students see ranked project cards with score breakdowns on their home dashboard
- **Quick Apply CTAs** — One-click apply directly from recommendation cards

### Profile Enhancements
- **Skills Chips** — Comma-separated skills rendered as visual chips on the profile
- **Portfolio Links** — Clickable portfolio URLs visible on the public profile
- **Star Ratings** — Average feedback rating displayed as stars
- **Auto-Awarded Badges** — System awards achievement badges based on real activity milestones (First Project, 3 Projects, 10 Projects, Top Rated, Rising Star)
- **Computed Fields** — Completed project count and average rating calculated live from the database

### Admin & Operations
- **Admin Moderation** — Admin users can view and manage platform content
- **System Logging Middleware** — Every request is logged with user identity, method, path, status code, and timestamp
- **Admin Log View** — Admins can query and filter system logs from the frontend

---

## Tech Stack

### Frontend
- React (Vite)
- React Router
- Axios
- Tailwind CSS


### Backend
- FastAPI
- SQLAlchemy (ORM)
- PostgreSQL
- Passlib (bcrypt)
- Python-JOSE (JWT)
- Pydantic V2

### DevOps
* Docker
* Docker Compose

### Testing
- pytest
- pytest-cov
- SQLite (test database)

---

## Project Structure

```bash
MicroMatch/
├── backend/
│   ├── app/
│   │   ├── core/               # Authentication, dependencies, RBAC
│   │   ├── middleware/         # Logging middleware
│   │   ├── routers/            # API routes
│   │   │   ├── auth.py
│   │   │   ├── projects.py
│   │   │   ├── applications.py
│   │   │   ├── deliverables.py
│   │   │   ├── feedback.py
│   │   │   ├── messages.py
│   │   │   ├── notifications.py
│   │   │   ├── analytics.py
│   │   │   ├── recommendations.py
│   │   │   ├── student_profile.py
│   │   │   └── organization_profile.py
│   │   ├── schemas/            # Pydantic request/response models
│   │   ├── utils/              # Password hashing, notifications, badges
│   │   │   ├── security.py
│   │   │   ├── notifications.py
│   │   │   └── badges.py
│   │   ├── database.py
│   │   ├── main.py
│   │   └── models.py           # SQLAlchemy models
│   ├── tests/                  # 243 unit + integration + E2E tests
│   ├── requirements.txt
│   └── test.db
├── frontend/
│   └── src/
│       ├── api/                # Axios API clients per feature
│       ├── components/         # Reusable UI components
│       ├── context/            # AuthContext
│       └── pages/              # Route-level page components
├── docker-compose.yml
└── README.md
```

---

## API Endpoints
 
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/register` | Register new user | Public |
| POST | `/auth/login` | Login, receive JWT | Public |
| GET | `/projects` | Browse all open projects | JWT |
| POST | `/projects` | Create a project | Org |
| PATCH | `/projects/{id}/status` | Update project status | Org |
| POST | `/applications` | Apply to a project | Student |
| GET | `/applications/me` | Get my applications | Student |
| PATCH | `/applications/{id}/status` | Accept/reject application | Org |
| POST | `/applications/{id}/deliverables` | Submit deliverable | Student |
| GET | `/applications/{id}/deliverables` | Review deliverables | Org |
| POST | `/feedback` | Submit post-completion feedback | JWT |
| POST | `/projects/{id}/messages` | Send a message | Participant |
| GET | `/projects/{id}/messages` | Get conversation history | Participant |
| GET | `/notifications` | Get user notifications | JWT |
| PUT | `/notifications/{id}/read` | Mark notification read | JWT |
| GET | `/analytics/student` | Student productivity metrics | Student |
| GET | `/analytics/organization` | Organization metrics | Org |
| GET | `/recommendations` | Personalized project ranking | Student |
| GET/POST/PUT | `/student/profile` | Student profile CRUD | Student |
| PUT | `/student/profile/enhance` | Save portfolio links | Student |
| GET | `/student/profile/{id}` | View any student's public profile | JWT |
| GET/POST/PUT | `/organization/profile` | Organization profile CRUD | Org |
| GET | `/admin/logs` | System request logs | Admin |
 
---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/chazdj/MicroMatch.git
cd MicroMatch
```
 
### 2. Setup Backend Environment
```bash
cd backend
python -m venv venv
source venv/Scripts/activate   # Windows
# source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt
```
 
### 3. Setup Frontend Environment
```bash
cd ../frontend
npm install
```
 
### 4. Start PostgreSQL using Docker
```bash
docker-compose up -d
```
 
### 5. Apply Database Schema
```bash
# Tables are created automatically on first run via Base.metadata.create_all()
# For the profile enhancement columns, run this once against your PostgreSQL instance:
psql -U <db_user> -d <db_name> -c "ALTER TABLE student_profiles ADD COLUMN IF NOT EXISTS portfolio_links TEXT, ADD COLUMN IF NOT EXISTS badges TEXT;"
```
 
---

## Running the Application

### Backend
```bash
cd backend
uvicorn app.main:app --reload
```
API will run on `http://127.0.0.1:8000`
Interactive docs: `http://127.0.0.1:8000/docs`

### Frontend
```bash
cd frontend
npm start
```
Frontend will run on `http://localhost:3000`

---

## Testing & Coverage

### Run all tests
```bash
cd backend
pytest -v
```

### Run with coverage report
```bash
coverage run -m pytest tests/
coverage report -m
coverage report -m > coverage_summary.txt
```

### Test Suite Overview
 
| Suite | Tests | Coverage |
|-------|-------|----------|
| Authentication | ✓ | ≥ 95% |
| Projects | ✓ | ≥ 95% |
| Applications | ✓ | ≥ 95% |
| Deliverables | ✓ | ≥ 95% |
| Feedback | ✓ | ≥ 95% |
| Notifications | ✓ | ≥ 95% |
| Recommendations | ✓ | ≥ 95% |
| Messages | ✓ | ≥ 95% |
| Analytics | ✓ | ≥ 95% |
| Profile Enhancements | ✓ | ≥ 90% |
| Badges | ✓ | 100% |
| **Total** | **251 tests** | **≥ 96%** |
 
---

## Usage
 
### Students
1. Register → Login → Complete profile (skills, bio, portfolio links)
2. View personalized project recommendations on the Home dashboard
3. Browse and search all open projects
4. Apply to projects → Track application status
5. Once accepted: submit deliverables, message your organization
6. After project completion: leave feedback and earn achievement badges
7. View your analytics (applications, completed projects, average rating) on the dashboard

### Organizations
1. Register → Login → Complete organization profile
2. Create and manage project listings
3. Review incoming applications → Accept or reject
4. Review deliverables submitted by accepted students
5. Mark projects complete → Student is notified and badges are awarded
6. Message accepted students from the Messages hub
7. View analytics (projects posted, active, completed, unique applicants)

### Admins
1. Login → Access admin-only routes
2. View and filter system logs
3. Moderate platform content

---

## Achievement Badges
 
Badges are awarded automatically by the system based on verified activity — students cannot manually set them.
 
| Badge | Criteria |
|-------|----------|
| 🏁 First Project | Complete 1 project |
| 📂 3 Projects | Complete 3 projects |
| 🏆 10 Projects | Complete 10 projects |
| ⭐ Top Rated | Average feedback rating ≥ 4.5 |
| 🌟 Rising Star | 3+ completions and average rating ≥ 4.0 |
 
---

## Author
 
**Chastidy Joanem**  
M.S. Software Engineering | B.S. Computer Science  
SWENG 894 Capstone