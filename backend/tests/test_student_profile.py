# import pytest
# from app.models import User, StudentProfile
# from app.utils.security import hash_password
# from app.core.auth import create_access_token

# @pytest.fixture
# def student_user(db_session):
#     user = User(email="student@example.com", hashed_password=hash_password("password123"), role="student")
#     db_session.add(user)
#     db_session.commit()
#     db_session.refresh(user)
#     return user

# @pytest.fixture
# def student_token(student_user):
#     return create_access_token({"user_id": student_user.id, "role": student_user.role})

# def test_create_student_profile(client, student_token):
#     headers = {"Authorization": f"Bearer {student_token}"}
#     payload = {"university":"PSU","major":"CS","graduation_year":2026,"skills":"Python,SQL","bio":"Love coding"}
#     response = client.post("/student/profile", json=payload, headers=headers)
#     assert response.status_code == 201
#     data = response.json()
#     assert data["university"] == "PSU"

# def test_get_student_profile(client, student_token):
#     headers = {"Authorization": f"Bearer {student_token}"}
#     response = client.get("/student/profile", headers=headers)
#     assert response.status_code == 200
#     data = response.json()
#     assert "university" in data

# def test_update_student_profile(client, student_token):
#     headers = {"Authorization": f"Bearer {student_token}"}
#     payload = {"bio": "Updated bio"}
#     response = client.put("/student/profile", json=payload, headers=headers)
#     assert response.status_code == 200
#     data = response.json()
#     assert data["bio"] == "Updated bio"

# def test_delete_student_profile(client, student_token):
#     headers = {"Authorization": f"Bearer {student_token}"}
#     response = client.delete("/student/profile", headers=headers)
#     assert response.status_code == 204

# def test_role_restriction(client, db_session):
#     user = User(email="org@example.com", hashed_password=hash_password("password123"), role="organization")
#     db_session.add(user)
#     db_session.commit()
#     db_session.refresh(user)

#     token = create_access_token({"user_id": user.id, "role": user.role})
#     headers = {"Authorization": f"Bearer {token}"}

#     assert client.post("/student/profile", headers=headers, json={"university":"X","major":"Y","graduation_year":2026}).status_code == 403
#     assert client.get("/student/profile", headers=headers).status_code == 403
#     assert client.put("/student/profile", headers=headers, json={"bio":"hack"}).status_code == 403
#     assert client.delete("/student/profile", headers=headers).status_code == 403