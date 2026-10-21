from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

VALID_PRIORITIES = {"Low", "Medium", "High"}
DEFAULT_PRIORITY = "Medium"

tasks = [
    {"id": 1, "title": "Project-1 Report"},
    {"id": 2, "title": "Project-2 MMFs"},
]
next_id = 3


def normalize_task(task):
    """Return a task with a valid default priority."""
    normalized_task = dict(task)
    priority = normalized_task.get("priority")
    if priority not in VALID_PRIORITIES:
        priority = DEFAULT_PRIORITY
    normalized_task["priority"] = priority
    return normalized_task


def get_priority(data):
    """Return the requested priority or the default priority."""
    priority = data.get("priority", DEFAULT_PRIORITY)
    if priority not in VALID_PRIORITIES:
        return None
    return priority


@app.route("/")
def index():
    """Render the task tracker page."""
    return render_template("index.html")


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    """Return all tasks, including backward-compatible priorities."""
    return jsonify([normalize_task(task) for task in tasks])


@app.route("/api/tasks", methods=["POST"])
def add_task():
    """Create a task with a validated priority."""
    global next_id
    data = request.get_json(silent=True) or {}

    if not data.get("title"):
        return jsonify({"error": "Title is required"}), 400

    priority = get_priority(data)
    if priority is None:
        return jsonify({
            "error": "Priority must be Low, Medium, or High"
        }), 400

    new_task = {
        "id": next_id,
        "title": data["title"],
        "priority": priority,
    }
    tasks.append(new_task)
    next_id += 1

    return jsonify(new_task), 201


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    """Update a task and default an omitted priority to Medium."""
    data = request.get_json(silent=True) or {}
    task = next((item for item in tasks if item["id"] == task_id), None)

    if task is None:
        return jsonify({"error": "Task not found"}), 404

    if "title" in data and not data["title"]:
        return jsonify({"error": "Title is required"}), 400

    priority = get_priority(data)
    if priority is None:
        return jsonify({
            "error": "Priority must be Low, Medium, or High"
        }), 400

    if "title" in data:
        task["title"] = data["title"]
    task["priority"] = priority

    return jsonify(normalize_task(task))


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    """Delete a task by its identifier."""
    global tasks
    tasks = [task for task in tasks if task["id"] != task_id]
    return jsonify({"result": "success"}), 200


if __name__ == "__main__":
    app.run(debug=True, port=5000)
