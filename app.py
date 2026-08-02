import os
from flask import Flask, jsonify, render_template, request
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://fmftgvrdbtpqocmfcqmm.supabase.co")
SUPABASE_KEY = os.environ.get(
    "SUPABASE_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZtZnRndnJkYnRwcW9jbWZjcW1tIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODU1OTQ5MjIsImV4cCI6MjEwMTE3MDkyMn0.bKwVeTVH848A-4zpankK9g3lnIPeXrDF3vAK0HXE9hM",
)

app = Flask(__name__)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/todos")
def api_todos():
    todos = (
        supabase.table("todos")
        .select("*")
        .order("done", desc=False)
        .order("created_at", desc=True)
        .execute()
        .data
    )
    return jsonify(todos)


@app.route("/api/sync", methods=["POST"])
def api_sync():
    payload = request.get_json(silent=True) or {}
    table = supabase.table("todos")
    for op in payload.get("ops") or []:
        if not isinstance(op, dict) or not op.get("id"):
            continue
        op_id = op["id"]
        kind = op.get("op")
        if kind == "insert":
            title = str(op.get("title", "")).strip()
            if not title:
                continue
            table.upsert(
                {
                    "id": op_id,
                    "title": title,
                    "done": bool(op.get("done", False)),
                }
            ).execute()
        elif kind == "update":
            fields = {k: op[k] for k in ("title", "done") if k in op}
            if fields:
                table.update(fields).eq("id", op_id).execute()
        elif kind == "delete":
            table.delete().eq("id", op_id).execute()
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True,
    )
