import sys
print("Script started", file=sys.stderr)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

# for a2
import sqlite3

def get_db():
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row # lets you access columns by name
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # create table if missing
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL
        )
    """)

    # check count
    cursor.execute("SELECT COUNT(*) FROM tasks") # send request
    count = cursor.fetchone()[0] # read response + [0] pull that specific request

    # seed if empty
    if count == 0:
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Buy milk", 0))
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Write README", 0))
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Walk dog", 1))
    
    conn.commit()
    conn.close()

init_db() # called before startup + routes

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
def get_tasks():
    conn = get_db() # get connection
    cursor = conn.cursor() # make cursor (does the querying)
    cursor.execute("SELECT * FROM tasks") # run sql
    rows = cursor.fetchall() # get all rows
    conn.close() # close connection
    return [dict(row) for row in rows] # covert and return

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    # validate (keep this same as before)
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="title is required");
    # connect & cursor
    conn = get_db()
    cursor = conn.cursor()

    # insert and use ? as placeholders, pass values separately
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
    (task.title, 0) # 0 = false/not done yet
    )
    # save to disk
    conn.commit()
    # get the id SQLite gave
    new_id = cursor.lastrowid
    # close 
    conn.close()
    # return new task
    return {"id": new_id, "title": task.title, "done":False}

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskCreate):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="title is required")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (task.title, 0, task_id) # title, done, id
    )

    conn.commit()

    # check if anything was updated
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    conn.close()
    return {"id": task_id, "title": task.title, "done": 0}

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    conn.commit()

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    conn.close()
    return # 204 means empty response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)