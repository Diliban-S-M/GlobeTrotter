from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "globetrotter_secret"

def get_db():
    return sqlite3.connect("database.db")

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        ).fetchone()

        if user and check_password_hash(user[3], password):
            session["user_id"] = user[0]
            return redirect("/dashboard")

        return "Invalid login"

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")

    db = get_db()
    trips = db.execute(
        "SELECT * FROM trips WHERE user_id=?",
        (session["user_id"],)
    ).fetchall()

    return render_template("dashboard.html", trips=trips)

@app.route("/create-trip", methods=["GET", "POST"])
def create_trip():
    if request.method == "POST":
        name = request.form["name"]
        start = request.form["start"]
        end = request.form["end"]

        if start > end:
            return "Invalid date range"

        db = get_db()
        db.execute(
            "INSERT INTO trips (user_id, name, start_date, end_date) VALUES (?,?,?,?)",
            (session["user_id"], name, start, end)
        )
        db.commit()

        return redirect("/dashboard")

    return render_template("create_trip.html")

@app.route("/itinerary/<int:trip_id>")
def itinerary(trip_id):
    db = get_db()

    stops = db.execute(
        "SELECT * FROM stops WHERE trip_id=? ORDER BY position",
        (trip_id,)
    ).fetchall()

    activities = db.execute(
        "SELECT * FROM activities"
    ).fetchall()

    total = db.execute(
        """
        SELECT SUM(cost) FROM activities
        WHERE stop_id IN (
            SELECT id FROM stops WHERE trip_id=?
        )
        """,
        (trip_id,)
    ).fetchone()[0] or 0

    return render_template(
        "itinerary.html",
        stops=stops,
        activities=activities,
        total=total
    )


@app.route("/add-stop/<int:trip_id>", methods=["POST"])
def add_stop(trip_id):
    city = request.form["city"]
    start = request.form["start"]
    end = request.form["end"]

    if start > end:
        return "Invalid date range"

    db = get_db()
    pos = db.execute(
        "SELECT COUNT(*) FROM stops WHERE trip_id=?",
        (trip_id,)
    ).fetchone()[0]

    db.execute(
        "INSERT INTO stops (trip_id, city, start_date, end_date, position) VALUES (?,?,?,?,?)",
        (trip_id, city, start, end, pos + 1)
    )
    db.commit()

    return redirect(f"/itinerary/{trip_id}")


@app.route("/share/<int:trip_id>")
def share(trip_id):
    db = get_db()
    trip = db.execute(
        "SELECT * FROM trips WHERE id=?",
        (trip_id,)
    ).fetchone()

    stops = db.execute(
        "SELECT * FROM stops WHERE trip_id=?",
        (trip_id,)
    ).fetchall()

    return render_template("share.html", trip=trip, stops=stops)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/add-activity/<int:stop_id>", methods=["POST"])
def add_activity(stop_id):
    name = request.form["name"]
    cost = int(request.form["cost"])

    db = get_db()
    db.execute(
        "INSERT INTO activities (stop_id, name, cost) VALUES (?,?,?)",
        (stop_id, name, cost)
    )
    db.commit()

    trip_id = db.execute(
        "SELECT trip_id FROM stops WHERE id=?",
        (stop_id,)
    ).fetchone()[0]

    return redirect(f"/itinerary/{trip_id}")


if __name__ == "__main__":
    app.run(debug=True)
