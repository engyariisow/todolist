import os
from flask import Flask, render_template, request, redirect, url_for
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://fmftgvrdbtpqocmfcqmm.supabase.co")
SUPABASE_KEY = os.environ.get(
    "SUPABASE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZtZnRndnJkYnRwcW9jbWZjcW1tIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODU1OTQ5MjIsImV4cCI6MjEwMTE3MDkyMn0.bKwVeTVH848A-4zpankK9g3lnIPeXrDF3vAK0HXE9hM",
)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.route("/")
def index():
    todos = (
        supabase.table("todos")
        .select("*")
        .order("done", desc=False)
        .order("id", desc=True)
        .execute()
        .data
    )
    return render_template("index.html", todos=todos)


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title", "").strip()
    if title:
        supabase.table("todos").insert({"title": title}).execute()
    return redirect(url_for("index"))


@app.route("/complete/<int:task_id>", methods=["POST"])
def complete(task_id):
    rows = (
        supabase.table("todos").select("done").eq("id", task_id).execute().data
    )
    if rows:
        supabase.table("todos").update(
            {"done": not rows[0]["done"]}
        ).eq("id", task_id).execute()
    return redirect(url_for("index"))


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete(task_id):
    supabase.table("todos").delete().eq("id", task_id).execute()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True,
    )
