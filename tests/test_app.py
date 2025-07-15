import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, Base, TodoItem, get_db

# Set up test database
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create test database tables
Base.metadata.create_all(bind=engine)

# Test client
client = TestClient(app)

def test_create_todo():
    todo_data = {"title": "Test Todo", "description": "This is a test todo"}
    response = client.post("/todos", json=todo_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == todo_data["title"]
    assert data["description"] == todo_data["description"]

def test_read_todos():
    response = client.get("/todos")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0

def test_update_todo():
    todo_data = {"title": "Test Todo", "description": "This is a test todo"}
    response = client.post("/todos", json=todo_data)
    todo_id = response.json()["id"]

    update_data = {"title": "Updated Todo", "completed": True}
    response = client.put(f"/todos/{todo_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["completed"] == update_data["completed"]

def test_delete_todo():
    todo_data = {"title": "Test Todo", "description": "This is a test todo"}
    response = client.post("/todos", json=todo_data)
    todo_id = response.json()["id"]

    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 200

    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 404