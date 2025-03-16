from flask import Flask, request, jsonify, make_response, render_template, redirect, url_for, flash
import jwt
import datetime
from functools import wraps
import bcrypt

app = Flask(__name__)

try:
    FLAG = open("./flag.txt", "r").read()
except:
    FLAG = "[**Sample_FLAG**]"

app.config['SECRET_KEY'] = open("./secret.txt", "r").read()

users = {
    "guest": bcrypt.hashpw(b"guest", bcrypt.gensalt()).decode("utf-8"),
    "admin": bcrypt.hashpw(b"strong_admin_password", bcrypt.gensalt()).decode("utf-8")
}

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('Authorization')

        if not token:
            return jsonify({'message': 'You\'re not admin!!'}), 403
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = data['user_id']
            level = data['level']
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expired!'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 403

        return f(current_user, level, *args, **kwargs)

    return decorated_function

@app.route("/")
def index():
    token = request.cookies.get('Authorization')
    level = None

    if token:
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            level = data.get('level')
        except jwt.InvalidTokenError:
            pass

    return render_template("index.html", level=level)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")

    username = request.form.get('username')
    password = request.form.get('password')

    if username in users and bcrypt.checkpw(password.encode(), users[username].encode()):
        level = "admin" if username == "admin" else "guest"
    else:
        flash('Invalid credentials!', 'danger')
        return redirect(url_for('login'))

    token = jwt.encode({
        'user_id': username,
        'level': level,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, app.config['SECRET_KEY'], algorithm="HS256")

    resp = make_response(redirect(url_for('index')))
    resp.set_cookie('Authorization', token)

    flash(f'Login success! Logged in as {level}.', 'success')

    return resp

@app.route("/flag", methods=['GET'])
@token_required
def flag(current_user, level):
    if level == 'admin':
        return render_template("flag.html", flag=FLAG)
    return jsonify({'message': f'Hello, {current_user}! You are not admin!!!!'}), 403

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=3234)
