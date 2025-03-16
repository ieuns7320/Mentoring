from flask import Flask, request, render_template, jsonify
import jwt
import base64
import json
import datetime

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    decoded_data = None
    encoded_token = None
    error = None

    if request.method == "POST":
        action = request.form.get("action")

        if action == "decode":
            jwt_token = request.form.get("jwt_token")
            secret_key = request.form.get("secret_key")

            try:
                header, payload, signature = jwt_token.split(".")
                decoded_header = base64.urlsafe_b64decode(header + "==").decode("utf-8")
                decoded_payload = base64.urlsafe_b64decode(payload + "==").decode("utf-8")

                decoded_data = {
                    "header": json.loads(decoded_header),
                    "payload": json.loads(decoded_payload),
                    "signature": signature
                }

                if secret_key:
                    try:
                        jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
                        decoded_data["signature_valid"] = True
                    except jwt.InvalidSignatureError:
                        decoded_data["signature_valid"] = False
                    except jwt.ExpiredSignatureError:
                        decoded_data["signature_valid"] = "Expired"

            except Exception as e:
                error = str(e)

        elif action == "encode":
            header = request.form.get("header")
            payload = request.form.get("payload")
            secret_key = request.form.get("secret_key")
            exp_time = request.form.get("exp_time")

            try:
                header_json = json.loads(header)
                payload_json = json.loads(payload)

                if exp_time:
                    payload_json["exp"] = datetime.datetime.utcnow() + datetime.timedelta(seconds=int(exp_time))

                encoded_token = jwt.encode(payload_json, secret_key, algorithm="HS256", headers=header_json)

            except Exception as e:
                error = str(e)

    return render_template("index.html", decoded_data=decoded_data, encoded_token=encoded_token, error=error)

@app.route("/base64", methods=["GET", "POST"])
def base64_decode():
    decoded_text = None
    error = None

    if request.method == "POST":
        encoded_text = request.form.get("encoded_text")

        try:
            decoded_text = base64.b64decode(encoded_text).decode("utf-8")
        except Exception as e:
            error = str(e)

    return render_template("base64.html", decoded_text=decoded_text, error=error)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9999)
