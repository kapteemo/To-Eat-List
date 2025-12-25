from flask import Flask, g, render_template, request, redirect, session, flash, url_for, jsonify
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "to_eat.db"

app = Flask(__name__)
app.secret_key = "change-me-to-a-secure-random-value"


def get_db():
    if "db" not in g:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        g.db = conn
    return g.db


def user_owns_list(list_id, user_id=None):
    db = get_db()
    if user_id is None:
        user_id = session.get("user_id")
    cur = db.execute("SELECT id FROM food_lists WHERE id = ? AND user_id = ?", (list_id, user_id))
    return cur.fetchone() is not None


def item_belongs_to_user(item_id, user_id=None):
    db = get_db()
    if user_id is None:
        user_id = session.get("user_id")
    cur = db.execute(
        "SELECT fi.id FROM food_items fi JOIN food_lists fl ON fi.list_id = fl.id WHERE fi.id = ? AND fl.user_id = ?",
        (item_id, user_id)
    )
    return cur.fetchone() is not None


@app.teardown_appcontext
def close_db(exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        if not username or not password:
            flash("Username and password required.")
            return redirect(url_for("register"))

        if password != confirm:
            flash("Passwords do not match.")
            return redirect(url_for("register"))

        db = get_db()
        cur = db.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cur.fetchone() is not None:
            flash("Username already taken.")
            return redirect(url_for("register"))

        pw_hash = generate_password_hash(password)
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, pw_hash))
        db.commit()
        flash("Registration successful. Please log in.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        db = get_db()
        cur = db.execute("SELECT id, username, hash FROM users WHERE username = ?", (username,))
        user = cur.fetchone()
        if user is None or not check_password_hash(user["hash"], password):
            flash("Invalid username or password.")
            return redirect(url_for("login"))

        session.clear()
        session["user_id"] = user["id"]
        flash("Welcome back!")
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    user_id = session["user_id"]
    # fetch username for personalized greeting
    user = db.execute("SELECT username FROM users WHERE id = ?", (user_id,)).fetchone()
    username = user["username"] if user else ""
    cur = db.execute("SELECT id, list_name, created_at FROM food_lists WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
    lists = cur.fetchall()
    return render_template("dashboard.html", lists=lists, username=username)


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        name = request.form.get("list_name", "").strip()
        if not name:
            flash("List name cannot be empty.")
            return redirect(url_for("create"))
        db = get_db()
        cur = db.execute("INSERT INTO food_lists (user_id, list_name) VALUES (?, ?)", (session["user_id"], name))
        db.commit()
        list_id = cur.lastrowid
        return redirect(url_for("editor", list_id=list_id))
    return render_template("create.html")


@app.route("/edit/<int:list_id>")
@login_required
def editor(list_id):
    db = get_db()
    lst = db.execute("SELECT id, list_name FROM food_lists WHERE id = ? AND user_id = ?", (list_id, session["user_id"]))
    row = lst.fetchone()
    if row is None:
        flash("List not found or access denied.")
        return redirect(url_for("dashboard"))
    items = db.execute("SELECT id, food_name, is_checked FROM food_items WHERE list_id = ?", (list_id,)).fetchall()
    # Render page; items will be loaded via JS
    return render_template("editor.html", list=row)


@app.route('/api/list_items/<int:list_id>')
@login_required
def api_list_items(list_id):
    if not user_owns_list(list_id):
        return jsonify({"error": "access denied"}), 403
    db = get_db()
    cur = db.execute("SELECT id, food_name, is_checked FROM food_items WHERE list_id = ? ORDER BY id", (list_id,))
    items = [{"id": r["id"], "food_name": r["food_name"], "is_checked": r["is_checked"]} for r in cur.fetchall()]
    return jsonify(items)


@app.route('/api/add_item', methods=["POST"])
@login_required
def api_add_item():
    data = request.get_json() or {}
    list_id = data.get("list_id")
    food_name = (data.get("food_name") or "").strip()
    if list_id is None:
        return jsonify({"error": "list_id required"}), 400
    try:
        list_id = int(list_id)
    except Exception:
        return jsonify({"error": "invalid list_id"}), 400
    if not user_owns_list(list_id):
        return jsonify({"error": "access denied"}), 403
    if not food_name:
        return jsonify({"error": "food_name required"}), 400
    db = get_db()
    cur = db.execute("INSERT INTO food_items (list_id, food_name) VALUES (?, ?)", (list_id, food_name))
    db.commit()
    return jsonify({"id": cur.lastrowid, "food_name": food_name, "is_checked": 0})


@app.route('/api/toggle_item', methods=["POST"])
@login_required
def api_toggle_item():
    data = request.get_json() or {}
    item_id = data.get("id")
    is_checked = int(bool(data.get("is_checked")))
    if not item_belongs_to_user(item_id):
        return jsonify({"error": "access denied"}), 403
    db = get_db()
    db.execute("UPDATE food_items SET is_checked = ? WHERE id = ?", (is_checked, item_id))
    db.commit()
    return jsonify({"ok": True})


@app.route('/api/delete_item', methods=["POST"])
@login_required
def api_delete_item():
    data = request.get_json() or {}
    item_id = data.get("id")
    if not item_belongs_to_user(item_id):
        return jsonify({"error": "access denied"}), 403
    db = get_db()
    db.execute("DELETE FROM food_items WHERE id = ?", (item_id,))
    db.commit()
    return jsonify({"ok": True})


@app.route('/api/edit_list', methods=["POST"])
@login_required
def api_edit_list():
    data = request.get_json() or {}
    list_id = data.get("list_id") or data.get("id")
    name = (data.get("name") or data.get("list_name") or "").strip()
    if not name:
        return jsonify({"error": "list_name required"}), 400
    if not user_owns_list(list_id):
        return jsonify({"error": "access denied"}), 403
    db = get_db()
    db.execute("UPDATE food_lists SET list_name = ? WHERE id = ?", (name, list_id))
    db.commit()
    return jsonify({"ok": True})


@app.route('/api/delete_list', methods=["POST"])
@login_required
def api_delete_list():
    data = request.get_json() or {}
    list_id = data.get("list_id") or data.get("id")
    if not user_owns_list(list_id):
        return jsonify({"error": "access denied"}), 403
    db = get_db()
    db.execute("DELETE FROM food_lists WHERE id = ?", (list_id,))
    db.commit()
    return jsonify({"ok": True})


@app.route('/api/edit_item', methods=["POST"])
@login_required
def api_edit_item():
    data = request.get_json() or {}
    item_id = data.get("id")
    food_name = (data.get("food_name") or "").strip()
    if not food_name:
        return jsonify({"error": "food_name required"}), 400
    if not item_belongs_to_user(item_id):
        return jsonify({"error": "access denied"}), 403
    db = get_db()
    db.execute("UPDATE food_items SET food_name = ? WHERE id = ?", (food_name, item_id))
    db.commit()
    return jsonify({"ok": True})


@app.route("/mylists")
@login_required
def mylists():
    # mirror /my_lists but with route spec from blueprint
    db = get_db()
    user_id = session["user_id"]
    cur = db.execute("SELECT id, list_name FROM food_lists WHERE user_id = ?", (user_id,))
    lists = cur.fetchall()
    expanded = []
    for lst in lists:
        items = db.execute("SELECT id, food_name, is_checked FROM food_items WHERE list_id = ?", (lst["id"],)).fetchall()
        expanded.append({"list": lst, "items": items})
    return render_template("my_lists.html", expanded=expanded)


@app.route("/random")
@login_required
def random_food():
    return redirect(url_for('random_pick'))


@app.route('/random_pick')
@login_required
def random_pick():
    db = get_db()
    row = db.execute("SELECT food_name FROM global_random_foods ORDER BY RANDOM() LIMIT 1").fetchone()
    if not row:
        flash("No global foods available.")
        return redirect(url_for("dashboard"))
    food = row["food_name"]
    # fetch user's lists for "Add to List" integration
    user_id = session.get("user_id")
    lists = db.execute("SELECT id, list_name FROM food_lists WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
    return render_template("random.html", food=food, lists=lists)


@app.route("/create_list", methods=["GET", "POST"])
@login_required
def create_list():
    if request.method == "POST":
        name = request.form.get("list_name", "").strip()
        if not name:
            flash("List name cannot be empty.")
            return redirect(url_for("create_list"))
        db = get_db()
        db.execute("INSERT INTO food_lists (user_id, list_name) VALUES (?, ?)", (session["user_id"], name))
        db.commit()
        flash("List created.")
        return redirect(url_for("dashboard"))
    return render_template("create_list.html")


@app.route("/my_lists")
@login_required
def my_lists():
    db = get_db()
    user_id = session["user_id"]
    cur = db.execute("SELECT id, list_name FROM food_lists WHERE user_id = ?", (user_id,))
    lists = cur.fetchall()
    expanded = []
    for lst in lists:
        items = db.execute("SELECT id, food_name, is_checked FROM food_items WHERE list_id = ?", (lst["id"],)).fetchall()
        expanded.append({"list": lst, "items": items})
    return render_template("my_lists.html", expanded=expanded)


if __name__ == "__main__":
    app.run(debug=True)
