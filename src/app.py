import os
from typing import List
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database models
class TodoItem(Base):
    __tablename__ = "todo_items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Pydantic models
class TodoItemBase(BaseModel):
    title: str
    description: str | None = None

class TodoItemCreate(TodoItemBase):
    pass

class TodoItemUpdate(TodoItemBase):
    completed: bool | None = None

class TodoItemInDB(TodoItemBase):
    id: int
    completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# FastAPI app
app = FastAPI()

# CRUD operations
@app.post("/todos", response_model=TodoItemInDB)
def create_todo(todo_item: TodoItemCreate, db: SessionLocal = Depends(get_db)):
    db_todo = TodoItem(title=todo_item.title, description=todo_item.description)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.get("/todos", response_model=List[TodoItemInDB])
def read_todos(db: SessionLocal = Depends(get_db)):
    todos = db.query(TodoItem).all()
    return todos

@app.get("/todos/{todo_id}", response_model=TodoItemInDB)
def read_todo(todo_id: int, db: SessionLocal = Depends(get_db)):
    todo = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo item not found")
    return todo

@app.put("/todos/{todo_id}", response_model=TodoItemInDB)
def update_todo(todo_id: int, todo_item: TodoItemUpdate, db: SessionLocal = Depends(get_db)):
    db_todo = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo item not found")
    update_data = todo_item.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_todo, key, value)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.delete("/todos/{todo_id}", response_model=TodoItemInDB)
def delete_todo(todo_id: int, db: SessionLocal = Depends(get_db)):
    db_todo = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo item not found")
    db.delete(db_todo)
    db.commit()
    return db_todo