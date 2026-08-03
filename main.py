import sys
print("Script started", file=sys.stderr)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Depends
from repository import TaskRepository, PostgresRepository
import os

repo = PostgresRepository(os.getenv("DATABASE_URL"))

def get_repo():
    return repo

@app.exception_handler(RequestValidationError)
def validation_error_handler(request, exc):
    return JSONResponse(status_code=400, content={"error": "invalid request body"})

class TaskCreate(BaseModel):
    title: str

@app.get("/")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks(repo: TaskRepository = Depends(get_repo)):
    return repo.get_all()

@app.get("/tasks/{task_id}")
def get_task(task_id: int, repo: TaskRepository = Depends(get_repo)):
    task = repo.get_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task

@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate, repo: TaskRepository = Depends(get_repo)):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="title is required")

    created_task = repo.create(task.title)
    return created_task

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskCreate, repo: TaskRepository = Depends(get_repo)):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="title is required")

    updated_task = repo.update(task_id, task.title)
    if updated_task is None:
        raise HTTPException(status_code=404, detail=f"task {task_id} not found")
    return updated_task

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, repo: TaskRepository = Depends(get_repo)):
    deleted = repo.delete(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"task {task_id} not found")
    return

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)