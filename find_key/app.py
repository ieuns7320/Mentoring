from flask import Flask, request, render_template, redirect, url_for, make_response, session
import time
import sqlite3

app = Flask(__name__)
app.secret_key = 'ieuns'

def init_db():
    conn = sqlite3.connect("users.db")
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS users")
    cur.execute("CREATE TABLE users (username TEXT, password TEXT)")
    cur.execute("INSERT INTO users VALUES ('admin', 'supersecret')")
    cur.execute("INSERT INTO users VALUES ('guest', 'guest123')")
    conn.commit()
    conn.close()

CORRECT_ANSWER_0 = "I'm studying crypto"
CORRECT_ANSWER_1 = "KEY{HTTP RESPONSE}"

users = {
    'admin': 'supersecret',
    'guest': 'guest123'
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/level0", methods=["GET", "POST"])
def level0():
    if request.method == "POST":
        user_answer = request.form.get("answer0", "").strip()
        if user_answer == CORRECT_ANSWER_0:
            session['level0_cleared'] = True
            return redirect(url_for("level1"))
        else:
            return render_template("level0.html", result=False)
    
    return render_template("level0.html")

@app.route("/level1", methods=["GET", "POST"])
def level1():
    if not session.get('level0_cleared'):
        return redirect(url_for("level0"))
    
    if request.method == "POST":
        user_answer = request.form.get("answer1", "").strip()
        if user_answer == CORRECT_ANSWER_1:
            session['level1_cleared'] = True
            return redirect(url_for("level2"))
        else:
            response = make_response(render_template("level1.html", result=False))
            response.headers['X-Flag'] = 'KEY{HTTP RESPONSE}'
            return response
    response = make_response(render_template("level1.html"))
    response.headers['X-Flag'] = 'KEY{HTTP RESPONSE}'
    return response

@app.route("/level2", methods=["GET", "POST"])
def level2():
    if not session.get('level1_cleared'):
        return redirect(url_for("level1"))

    result = None

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        blacklist = ["or", "and", '"', "--", "#", ";"]
        # admin' /*
        if any(bad in username.lower() or bad in password.lower() for bad in blacklist):
            result = "Filtered!"
        else:
            conn = sqlite3.connect("users.db")
            cur = conn.cursor()
            try:
                query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
                cur.execute(query)
                user = cur.fetchone()
                conn.close()

                if user and user[0] == "admin":
                    session["level2_cleared"] = True
                    return redirect(url_for("level3"))
                else:
                    result = "Login Fail..."
            except Exception as e:
                result = "Query Error"

    return render_template("level2.html", result=result)

@app.route("/level3", methods=["GET", "POST"])
def level3():
    if not session.get("level2_cleared"):
        return redirect(url_for("level2"))

    if request.method == "POST":
        session["level3_cleared"] = True
        return redirect(url_for("flag"))

    return render_template("level3.html")

@app.route("/flag")
def flag():
    if not session.get("level3_cleared"):
        return redirect(url_for("level3"))
    return render_template("flag.html")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", debug=True, port="3002")
