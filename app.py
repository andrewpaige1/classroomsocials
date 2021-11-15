from os import name
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy 
from datetime import datetime
import bcrypt
from sqlalchemy.orm import backref
from os import environ


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL').replace("://", "ql://", 1)
"sqlite:///sqlite3.db"
#"sqlite:///database.db"
#environ.get('DATABASE_URL').replace("://", "ql://", 1)
app.secret_key = environ.get('SECRET_KEY')
db = SQLAlchemy(app)


students = db.Table("students", 
    db.Column('user_id', db.Integer, db.ForeignKey("user.id")),
    db.Column('course_id', db.Integer, db.ForeignKey("course.id"))
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.now)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    email = db.Column(db.String(300))
    password = db.Column(db.LargeBinary)
    courses = db.relationship("Course", secondary=students, backref=db.backref("students", lazy="dynamic"))
    instagram = db.Column(db.String(120))
    snapchat = db.Column(db.String(120))
    twitter = db.Column(db.String(120))
    linkedIn = db.Column(db.String(120))
    bio = db.Column(db.String(120))

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))

@app.route('/')
def index():
    if 'email' in session:
   #     user = User.query.filter_by(email=session["email"]).first()#find the first user that matches name
        return redirect(url_for("courses"))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'email' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':#handle form
        email = request.form['email']#get username from form
        existing_user = User.query.filter_by(email=email).first()#find the first user that matches name
        if existing_user:#check if user exists
            #hash the password and compare it to the one stored in the db
            existing_pass = existing_user.password
            if bcrypt.checkpw(request.form['pass'].encode('utf-8'), existing_pass):
                #create session
                session['email'] = request.form['email']
                return redirect(url_for('index'))
            else:
                print('wrong username or password')
        else:
            print('wrong username or password')
    return render_template("login.html")

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.before_request
def make_session_permanent():
    session.permanent = True

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        #find existing user
        email = request.form['email']
        if "my.brookdalecc.edu" not in email:
            return render_template("register.html", message="Sorry we don't support that email currently")
        existing_user = User.query.filter_by(email=request.form['email']).first()
        #if there's no previous users let them sign up
        if existing_user is None:
            #hashed password
            hashpass = bcrypt.hashpw(request.form['pass'].encode('utf-8'), bcrypt.gensalt())
            #creates a new user in table
            #i think its saying INSERT USER in USERS
            #tbh it's been a year since i looked at sql
            user = User(first_name=request.form['firstName'], 
            last_name=request.form["lastName"], email=email, password=hashpass, instagram="", snapchat="", twitter="", linkedIn="", bio="")
            #this prepares the user to be added to the table
            db.session.add(user)
            #commit new user to table
            db.session.commit()
            session['email'] = email
            print('user added')
            return redirect(url_for('index'))
        else:
            print('user exists')
    return render_template("register.html")


@app.route("/profile")
def profile():
    if 'email' in session:   
        user = User.query.filter_by(email=session['email']).first()         
        return render_template("profile.html", user=user)
    return redirect(url_for("index"))

@app.route("/editProfile/<id>", methods=['POST'])
def edit_profile(id):
    if 'email' in session:            
        user = User.query.get(id)
        user.instagram = request.form['instagram']
        user.snapchat = request.form['snapchat']
        user.twitter = request.form['twitter']
        user.linkedIn = request.form['linkedIn']
        user.bio = request.form['bio']
        db.session.commit()
        return redirect(url_for('profile'))
    return redirect(url_for("index"))


@app.route("/courses", methods=['GET', 'POST'])
def courses():
    if 'email' in session:
        if request.method == "POST":
            user = User.query.filter_by(email=session["email"]).first()
            course_name = request.form['courseName'].lower()
            if len(course_name) < 4:
                return render_template("courses.html", users=user, message="Please enter a valid class name")
            dash_count = 0
            for letter in course_name:
                if letter == "-":
                    dash_count = dash_count + 1
            if dash_count != 2:
                return render_template("courses.html", users=user, message="Please enter a valid class name")
            course = Course.query.filter_by(name=course_name).first()
                   
            #user_courses = User.query.filter_by(email=session["email"]).first()
            if course is None:
                course = Course(name=course_name)
                db.session.add(course)
                course.students.append(user)
                #commit new user to table
                db.session.commit()
            else:
                for students in course.students:
                    if students.email == session['email']:
                        return render_template("courses.html", users=user, message="You already entered this course!")  
                course = Course.query.filter_by(name=course_name).first()
                course.students.append(user)
                db.session.commit()
            return render_template("courses.html", users=user)
        user = User.query.filter_by(email=session["email"]).first()
        return render_template("courses.html", users=user)
    return redirect(url_for('index'))
@app.route("/events")
def events():
    return render_template("events.html")

@app.route("/connect")
def connect():
    return render_template("connect.html")



@app.route("/course/<course_name>")
def view_course(course_name):
    if 'email' in session:
        course = Course.query.filter_by(name=course_name).first()
        return render_template("view_course.html", course_students=course.students)
    return redirect(url_for("index"))
if __name__ == '__main__':
  app.run()