
import os
import sqlite3

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

# Database path can be changed when deploying to Kubernetes.
DATABASE = os.environ.get("DATABASE_PATH", "todo.db")


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    # Create the parent directory if required.
    directory = os.path.dirname(os.path.abspath(DATABASE))
    os.makedirs(directory, exist_ok=True)

    with get_db() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0
            )
        """)


@app.route("/")
def index():
    with get_db() as connection:
        tasks = connection.execute(
            "SELECT * FROM tasks ORDER BY id DESC"
        ).fetchall()

    return render_template("index.html", tasks=tasks)


@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title", "").strip()

    if title:
        with get_db() as connection:
            connection.execute(
                "INSERT INTO tasks (title) VALUES (?)",
                (title,)
            )

    return redirect(url_for("index"))


@app.route("/complete/<int:task_id>", methods=["POST"])
def complete_task(task_id):
    with get_db() as connection:
        connection.execute(
            "UPDATE tasks SET completed = 1 WHERE id = ?",
            (task_id,)
        )

    return redirect(url_for("index"))


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    with get_db() as connection:
        connection.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,)
        )

    return redirect(url_for("index"))


init_db()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
