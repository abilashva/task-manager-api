"""Request/response models with validation."""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Status(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=1000)
    priority: Priority = Priority.medium
    status: Status = Status.todo
    due_date: Optional[date] = None


class TaskUpdate(BaseModel):
    """All fields optional: only the ones sent are changed."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=1000)
    priority: Optional[Priority] = None
    status: Optional[Status] = None
    due_date: Optional[date] = None


class Task(BaseModel):
    id: int
    title: str
    description: str
    priority: Priority
    status: Status
    due_date: Optional[date] = None
    created_at: str
