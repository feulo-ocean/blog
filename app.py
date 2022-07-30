from flask import Flask, render_template, redirect, url_for, request, flash
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user, logout_user, login_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.exc import IntegrityError
import os

app = Flask("hello")
db_url = os.environ.get("DATABASE_URL") or "sqlite:///app.db"
app.config["SQLALCHEMY_DATABASE_URI"] =  db_url.replace("postgres", "postgresql") 
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "pudim"

db = SQLAlchemy(app)
login = LoginManager(app)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(70), nullable=False)
    body = db.Column(db.String(500))
    created = db.Column(db.DateTime, nullable=False, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True, index=True) 
    email = db.Column(db.String(64), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    posts = db.relationship('Post', backref='author')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


db.create_all()

@app.route("/")
def index():
    posts = Post.query.order_by(-Post.created).all()
    return render_template("index.html", posts=posts)

@app.route('/register', methods=["GET","POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        try:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            flash("Username or E-mail already exists!")
        else:
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash("Incorrect Username or Password")
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('index'))
    return render_template("login.html")

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/create', methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        title = request.form['title']
        body = request.form['body']
        try:
            post = Post(title=title, body=body, author=current_user)
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('index'))
        except IntegrityError:
            flash("Error on create Post, try again later")
    return render_template('create.html')