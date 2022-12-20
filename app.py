from cs50 import SQL
from flask import Flask, render_template, request, session, redirect, send_file
from flask_session import Session
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
import os


app = Flask(__name__)

# Ensure templates are auto-reloadedh
app.config["TEMPLATES_AUTO_RELOAD"] = True

# SQLite database
db = SQL("sqlite:///notes.db")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

message = ""


def add_session(name):
    session["user_id"] = db.execute("SELECT * FROM user WHERE name = ?", name)[0]["user_id"]


def generate_title(ID):
    titles = db.execute("SELECT header FROM notes WHERE id = ?", ID)
    if len(titles) == 0:
        title = "New note"
    else:
        titles = [titles[x]["header"] for x in range(len(titles))]
        previous_max = 0
        for item in titles:
            if item[:8] == "New note" and len(item) > 8:
                temp = int(item[10:len(item)-1])
                if temp > previous_max:
                    previous_max = temp
        count = previous_max + 1
        title = "New note (" + str(count) + ")"
    return title


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    message = ""
    if request.method == "GET":
            return render_template("login.html")
    else:
        user_id = session.get("user_id")
        name = request.form.get("nickname")
        names = db.execute("SELECT name FROM user")
        names = [names[x]["name"] for x in range(len(names))]
        password = request.form.get("password")

        if not name:
            message="Must provide username"
        elif not password:
            message="Must provide password"
        elif name not in names or check_password_hash(password, db.execute("SELECT password FROM user WHERE name = ?", name)[0]["password"]):
            message="Incorrect credentials"

        if message != "":
            return render_template("login.html", message=message, name=name, password=password)

        add_session(name)
        return redirect("/")


@app.route("/registration", methods=["GET", "POST"])
def registration():
    message = ""
    if request.method == "GET":
        return render_template("new_account.html", message=message)
    else:
        # user`s data
        names = [name.get("name") for name in db.execute("SELECT name FROM user")]

        name = request.form.get("nickname")
        password = request.form.get("password")
        confirm = request.form.get("confirm_password")
        user_id = session.get("user_id")

        # empty fields
        if not name:
            message="Must provide username"
        elif not password or not confirm:
            message="Must provide password"
        elif name in names:
            message="This name is already taken by another user"
        elif len(password) < 8 or len(password) > 24:
            message="Password lenght should be more than 7 symbols and less than 25"
        elif password != confirm:
            message="Passwords don't match"

        if message != "":
            return render_template("new_account.html", message=message, name=name, password=password, confirm=request.form.get("confirm_password"))

        # add data to DB + session
        db.execute("INSERT INTO user (name, password) VALUES(?, ?)", name, generate_password_hash(password))
        add_session(name)
        return redirect("/")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    for file in os.listdir('downloads/'):
        os.remove('downloads/' + file)
    user_id = session.get("user_id")
    data = db.execute("SELECT header, notes_id FROM notes WHERE id = ?", user_id)
    if len(data) == 0:
        name = db.execute("SELECT name FROM user WHERE user_id = ?", user_id)[0]["name"].split(" ")
        newName = ""

        for x, y in enumerate(name):
            newName += y.capitalize() + (" " if x < len(name) else "")

        return render_template("index.html", message=True, name=newName)
    return render_template("index.html", data=data)


@app.route("/actions", methods=["POST"])
@login_required
def note():
    try:
        if request.form["new"]:
            return render_template("note.html", title_block="new note", action="create", btn="Save new note")
    except:
        user_id = session.get("user_id")
        try:
            if request.form["time"]:
                data = db.execute("SELECT * FROM notes WHERE id = ? ORDER BY time", user_id)
                return render_template("index.html", data=data, message=True if len(data) == 0 else False)
        except:
            try:
                if request.form["alphabetic"]:
                    data = db.execute("SELECT * FROM notes WHERE id = ? ORDER BY header", user_id)
                    return render_template("index.html", data=data, message=True if len(data) == 0 else False)
            except:
                data = db.execute("SELECT * FROM notes WHERE id = ? ORDER BY header DESC", user_id)
                return render_template("index.html", data=data, message=True if len(data) == 0 else False)


@app.route("/create", methods=["POST"])
@login_required
def create():
    text = request.form.get("text")
    if text == '':
        return render_template("note.html", title=request.form.get("title"), message="There is no data. Nothing to save.", title_block="new note", action="create", btn="Save new note")
    title = request.form.get("title")
    user_id = session.get("user_id")
    if title == '':
        title = generate_title(user_id)
    current = datetime.datetime.now()
    time = str(datetime.date.today()) + "-" + str(current.hour) + "-" + str(current.minute) + "-" + str(current.second)
    db.execute("INSERT INTO notes (id, header, text, time) VALUES (?, ?, ?, ?)", user_id, title, text, time)
    return redirect("/")


@app.route("/edit", methods=["POST"])
@login_required
def edit():
    try:
        if request.form["delete"]:
            note_id = request.form["delete"]
            db.execute("DELETE FROM notes WHERE notes_id = ?", note_id)
            return redirect("/")
    except:
        try:
            note_id = request.form["button"]
            data = db.execute("SELECT header, text FROM notes WHERE notes_id = ?", note_id)[0]
            return render_template("note.html", note_id=note_id, title=data["header"], text=data["text"], title_block="edit mode", action="save_edit", btn="Edit note")
        except:
            note_id = request.form["download"]
            data = db.execute("SELECT header, text FROM notes WHERE notes_id = ?", note_id)[0]
            filename = data["header"] + ".txt"
            complete_filename = os.path.join("downloads/", filename)
            with open(complete_filename, "w") as file:
                file.write(data["text"])
            return send_file(complete_filename, as_attachment=True)


@app.route("/save_edit", methods=["POST"])
@login_required
def save_edit():
    title = request.form.get("title")
    user_id = session.get("user_id")
    note_id = request.form["save"]
    if title == '':
        title = generate_title(user_id)
    text = request.form.get("text")
    if text == "":
        return render_template("note.html", note_id=note_id, title=title, text=text, title_block="edit mode", action="save_edit", btn="Edit note", message="There is no text. Nothing to save.")
    db.execute("UPDATE notes SET header = ?, text = ? WHERE notes_id = ?", title, text, note_id)
    return redirect("/")


@app.route("/calendar", methods=["GET"])
@login_required
def birthdays():
    data = dates(db.execute("SELECT * FROM birthdays WHERE id = ?", session.get("user_id")))
    return render_template("calendar.html", data=data, bool_val=True if len(data) != 0 else False)


@app.route("/del date", methods=["POST"])
@login_required
def delete_date():
    db.execute("DELETE FROM birthdays WHERE friends_id = ?", request.form["id"])
    return birthdays()


@app.route("/add_date", methods=["POST"])
@login_required
def add_date():
    user_id = session.get("user_id")
    name = request.form["name"]
    day = request.form["day"]
    month = int(request.form["month"])

    if not name or not day or not month or not day.isdigit() or not str(month).isdigit() or int(day) < 1 or month < 1 or (int(day) > 31 and month in [1, 3, 5, 7, 8, 10, 12]) or (int(day) > 30 and month in [4, 6, 9, 11]) or (int(day) > 28 and month == 2):
        data = dates(db.execute("SELECT * FROM birthdays WHERE id = ?", user_id))
        return render_template("calendar.html", data=data, name=name, day=day, month=str(month), bool_val=True if len(data) != 0 else False)
    db.execute("INSERT INTO birthdays (name, date, id) VALUES (?, ?, ?)", name, str(month) + "/" + day, user_id)
    data = dates(db.execute("SELECT * FROM birthdays WHERE id = ?", user_id))
    return render_template("calendar.html", data=data, bool_val=True if len(data) != 0 else False)

46911
def dates(data):
    for i in range(len(data)):
        item = data[i]["date"].split("/")
        TODAY = datetime.date.today()
        FUTURE = datetime.date(TODAY.year, int(item[0]), int(item[1]))
        today = [int(x) for x in str(TODAY).split("-")]
        future = [int(x) for x in str(FUTURE).split("-")]
        if today == future:
            left = "It`s today"
        else:
            if today[1] > future[1] or (today[1] == future[1] and today[2] > future[2]):
                FUTURE = datetime.date(TODAY.year + 1, int(item[0]), int(item[1]))
            left = str((FUTURE - TODAY).days) + " days left"
        data[i]["left"] = left
    data = sorted(data, key=lambda x: x["left"])
    for i in range(len(data)):
        if data[i]["left"] == "It`s today":
            data.insert(0, data[i])
            data.pop(i+1)
    return data
