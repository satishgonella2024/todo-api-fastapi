import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from src.models import Base, TodoItem

# Create an in-memory SQLite database for testing
engine = create_engine('sqlite:///:memory:', echo=True)
Session = sessionmaker(bind=engine)

# Create the tables
Base.metadata.create_all(engine)

def test_create_todo_item():
    session = Session()
    todo = TodoItem(title='Test Todo', description='This is a test todo item')
    session.add(todo)
    session.commit()
    assert todo.id is not None
    assert todo.completed is False
    assert todo.created_at is not None
    assert todo.updated_at is not None

def test_update_todo_item():
    session = Session()
    todo = TodoItem(title='Test Todo', description='This is a test todo item')
    session.add(todo)
    session.commit()
    
    todo.completed = True
    session.commit()
    
    updated_todo = session.query(TodoItem).get(todo.id)
    assert updated_todo.completed is True
    assert updated_todo.updated_at > updated_todo.created_at

def test_delete_todo_item():
    session = Session()
    todo = TodoItem(title='Test Todo', description='This is a test todo item')
    session.add(todo)
    session.commit()
    
    session.delete(todo)
    session.commit()
    
    deleted_todo = session.query(TodoItem).get(todo.id)
    assert deleted_todo is None