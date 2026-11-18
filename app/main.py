"""Task Manager REST API."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Response, status

from .database import get_conn, init_db
from .schemas import Priority, Status, Task, TaskCreate, TaskUpdate


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Task Manager API", version="1.0.0", lifespan=lifespan)


def _row_to_task(row) -> Task:
    return Task(**dict(row))


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> Task:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO tasks (title, description, priority, status, due_date) VALUES (?, ?, ?, ?, ?)",
            (
                payload.title,
                payload.description,
                payload.priority.value,
                payload.status.value,
                payload.due_date.isoformat() if payload.due_date else None,
            ),
        )
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (cur.lastrowid,)).fetchone()
    return _row_to_task(row)


@app.get("/tasks", response_model=list[Task])
def list_tasks(
    status: Optional[Status] = None,
    priority: Optional[Priority] = None,
    search: Optional[str] = Query(default=None, description="match in title"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[Task]:
    query, params = "SELECT * FROM tasks WHERE 1=1", []
    if status:
        query += " AND status = ?"
        params.append(status.value)
    if priority:
        query += " AND priority = ?"
        params.append(priority.value)
    if search:
        query += " AND title LIKE ?"
        params.append(f"%{search}%")
    query += " ORDER BY id LIMIT ? OFFSET ?"
    params += [limit, offset]
    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()
    return [_row_to_task(r) for r in rows]


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int) -> Task:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return _row_to_task(row)


@app.patch("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, payload: TaskUpdate) -> Task:
    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise HTTPException(status_code=400, detail="No fields to update")

    values = []
    for key, value in changes.items():
        if hasattr(value, "value"):  # enums
            value = value.value
        elif hasattr(value, "isoformat"):  # dates
            value = value.isoformat()
        values.append(value)

    assignments = ", ".join(f"{key} = ?" for key in changes)  # keys come from the schema, not the user
    with get_conn() as conn:
        cur = conn.execute(f"UPDATE tasks SET {assignments} WHERE id = ?", (*values, task_id))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Task not found")
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return _row_to_task(row)


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int) -> Response:
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
