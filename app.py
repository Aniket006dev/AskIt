from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

def init_db():
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS trainers (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS questions (id INTEGER PRIMARY KEY, student_id INTEGER, question TEXT, answer TEXT)")
    conn.commit()
    conn.close()

@app.route("/")
def home():
    conn = sqlite3.connect("data.db")
    cur = conn.cursor()
    cur.execute("SELECT q.question, q.answer, s.username FROM questions q JOIN students s ON q.student_id=s.id WHERE q.answer IS NOT NULL")
    qa = cur.fetchall()
    conn.close()
    return render_template("home.html", qa=qa)

@app.route("/student_register", methods=["GET","POST"])
def student_register():
    if request.method=="POST":
        username=request.form["username"]
        password=generate_password_hash(request.form["password"])
        conn=sqlite3.connect("data.db")
        cur=conn.cursor()
        cur.execute("INSERT INTO students (username,password) VALUES (?,?)",(username,password))
        conn.commit()
        conn.close()
        return redirect(url_for("student_login"))
    return render_template("student_register.html")

@app.route("/student_login", methods=["GET","POST"])
def student_login():
    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"]
        conn=sqlite3.connect("data.db")
        cur=conn.cursor()
        cur.execute("SELECT * FROM students WHERE username=?",(username,))
        user=cur.fetchone()
        conn.close()
        if user and check_password_hash(user[2],password):
            session["student"]=user[0]
            return redirect(url_for("ask"))
        return "Invalid"
    return render_template("student_login.html")

@app.route("/ask", methods=["GET","POST"])
def ask():
    if "student" not in session:
        return redirect(url_for("student_login"))
    if request.method=="POST":
        q=request.form["question"]
        sid=session["student"]
        conn=sqlite3.connect("data.db")
        cur=conn.cursor()
        cur.execute("INSERT INTO questions (student_id,question,answer) VALUES (?,?,NULL)",(sid,q))
        conn.commit()
        conn.close()
        return render_template("home.html")
    return render_template("ask.html")

# app.route("/")

@app.route("/trainer_register", methods=["GET","POST"])
def trainer_register():
    if request.method=="POST":
        username=request.form["username"]
        password=generate_password_hash(request.form["password"])
        conn=sqlite3.connect("data.db")
        cur=conn.cursor()
        cur.execute("INSERT INTO trainers (username,password) VALUES (?,?)",(username,password))
        conn.commit()
        conn.close()
        return redirect(url_for("trainer_login"))
    return render_template("trainer_register.html")

@app.route("/trainer_login", methods=["GET","POST"])
def trainer_login():
    if request.method=="POST":
        username=request.form["username"]
        password=request.form["password"]
        conn=sqlite3.connect("data.db")
        cur=conn.cursor()
        cur.execute("SELECT * FROM trainers WHERE username=?",(username,))
        user=cur.fetchone()
        conn.close()
        if user and check_password_hash(user[2],password):
            session["trainer"]=user[0]
            return redirect(url_for("dashboard"))
        return "Invalid"
    return render_template("trainer_login.html")

@app.route("/dashboard", methods=["GET","POST"])
def dashboard():
    if "trainer" not in session:
        return redirect(url_for("trainer_login"))
    conn=sqlite3.connect("data.db")
    cur=conn.cursor()
    cur.execute("SELECT q.id,q.question,q.answer,s.username FROM questions q JOIN students s ON q.student_id=s.id")
    qs=cur.fetchall()
    conn.close()
    return render_template("dashboard.html",qs=qs)

@app.route("/answer/<int:qid>", methods=["POST"])
def answer(qid):
    if "trainer" not in session:
        return redirect(url_for("trainer_login"))
    ans=request.form["answer"]
    conn=sqlite3.connect("data.db")
    cur=conn.cursor()
    cur.execute("UPDATE questions SET answer=? WHERE id=?",(ans,qid))
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__=="__main__":
    init_db()
    app.run(debug=True)
