import hashlib
import uuid

from flask import Flask, render_template, redirect, request, make_response, url_for
from models.settings import db
from models.topic import Topic
from models.user import User

app = Flask(__name__)
db.create_all()


@app.route("/", methods=["GET"])
def index():
    session_token = request.cookies.get("session_token")
    if session_token:
        user = db.query(User).filter_by(session_token=session_token).first()
        topics = db.query(Topic).all()
        return render_template("index.html", user=user, topics=topics)
    else:
        return redirect(url_for("signup"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    elif request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        password_repeat = request.form.get("password_repeat")

        if password != password_repeat:
            return "Passwords don't match"

        user = User(
            username=username,
            email=email,
            password=hashlib.sha512(password.encode()).hexdigest(),
            session_token=str(uuid.uuid4()),
        )
        db.add(user)
        db.commit()

        response = make_response(redirect(url_for("index")))
        response.set_cookie(
            "session_token", user.session_token, httponly=True, samesite="Strict"
        )

        return response


@app.route("/create-topic", methods=["GET", "POST"])
def create_topic():
    if request.method == "GET":
        return render_template("topic/create.html")
    elif request.method == "POST":
        title = request.form.get("title")
        text = request.form.get("text")
        session_token = request.cookies.get("session_token")
        user = User.get_by_session()

        if not user:
            return redirect(url_for("signup"))

        Topic.create(title=title, text=text, author=user)

        return redirect(url_for("index"))


@app.route("/topic/<topic_id>", methods=["GET"])
def topic_data(topic_id):
    topic = db.query(Topic).get(int(topic_id))
    user = User.get_by_session()

    return render_template("topic/data.html", topic=topic, user=user)


@app.route("/topic/<topic_id>/edit", methods=["GET", "POST"])
def topic_edit(topic_id):
    topic = db.query(Topic).get(int(topic_id))
    if request.method == "GET":
        return render_template("topic/edit.html", topic=topic)
    elif request.method == "POST":
        title = request.form.get("title")
        text = request.form.get("text")

        user = User.get_by_session()

        if not user:
            return redirect(url_for("index"))
        elif topic.author.id != user.id:
            return "Operation not allowed"
        else:
            topic.title = title
            topic.text = text
            db.add(topic)
            db.commit()

            return redirect(url_for("index"))

@app.route("/topic/<topic_id>/delete")
def topic_delete(topic_id):
    topic = db.query(Topic).get(int(topic_id))
    db.delete(topic)
    db.commit()
    return redirect(url_for("index"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = (db.query(User).filter_by
                (
                username=username,
                password=hashlib.sha512(password.encode()).hexdigest()
                ).first()
                )
        if not user:
            return "Invalid credentials!"
        else:
            user.session_token = str(uuid.uuid4())
            db.add(user)
            db.commit()

            response = make_response(redirect(url_for("index")))
            response.set_cookie(
                "session_token", user.session_token, httponly=True, samesite="Strict"
            )
            return response


@app.route("/logout")
def logout():
    session_token = request.cookies.get("session_token")
    response = make_response(redirect(url_for("signup")))
    response.set_cookie("session_token", expires=0)
    # response.delete_cookie("session_token")
    return response
