from flask import Flask, render_template, request, redirect, session, jsonify
import mysql.connector
import random
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ================= DATABASE =================
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Vsjaymali@21",
    database="smart_ai_career_guide"
)
cursor = db.cursor(dictionary=True)

# ================= OTP STORAGE =================
otp_storage = {}

# ================= EMAIL FUNCTION =================
def send_email_otp(receiver_email, otp):
    try:
        sender_email = "shraddhajaymali.2112@gmail.com"
        app_password = "iighjjblnkvfdfdm"  # no spaces

        msg = MIMEText(f"Your OTP is {otp}")
        msg["Subject"] = "Smart AI Career Guide OTP"
        msg["From"] = sender_email
        msg["To"] = receiver_email

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()

        print("✅ OTP SENT SUCCESSFULLY")

    except Exception as e:
        print("❌ EMAIL ERROR:", e)

# ================= HOME =================
@app.route("/")
def home():
    return render_template("index.html")

# ================= SEND OTP =================
@app.route("/send-otp", methods=["POST"])
def send_otp():
    data = request.get_json()
    email = data.get("email")

    otp = str(random.randint(100000, 999999))
    otp_storage[email] = otp

    print("OTP:", otp)  # Debug

    send_email_otp(email, otp)  # Send email

    return jsonify({"message": "OTP sent successfully!"})

# ================= REGISTER =================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        mobile = request.form["mobile"]
        dob = request.form["dob"]
        user_otp = request.form["otp"]

        # calculate age 
        dob_date = datetime.strptime(dob, "%Y-%m-%d")
        today = datetime.today()
        age = today.year - dob_date.year - (
            (today.month, today.day) < (dob_date.month, dob_date.day))


        # OTP Verification
        if otp_storage.get(email) != user_otp:
            return "Invalid OTP"

        # Check existing user
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        if cursor.fetchone():
            return render_template("register.html", error="Email already registered")

        # Insert user
        cursor.execute(
    "INSERT INTO users (name, email, password, dob, age, mobile, verified) VALUES (%s,%s,%s,%s,%s,%s,%s)",
    (name, email, password, dob, age, mobile, 1)
)
        db.commit()

        return render_template("register.html", success=True)

    return render_template("register.html")

# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )
        user = cursor.fetchone()

        if user:
            session["user_id"] = user["user_id"]
            session["name"] = user["name"]
            return redirect("/dashboard")

        return "Invalid Credentials"

    return render_template("login.html")

# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    return render_template("dashboard.html", name=session["name"])

# ================= PSYCHOMETRIC TEST =================
@app.route("/psychometric-test")
def psychometric_test():
    if "user_id" not in session:
        return redirect("/login")

    return render_template("psychometric_test.html")

# ================= SUBMIT PSYCHOMETRIC =================
@app.route("/submit-psychometric", methods=["POST"])
def submit_psychometric():
    q1 = int(request.form["q1"])
    q2 = int(request.form["q2"])
    q3 = int(request.form["q3"])

    session["psychometric"] = {
        "technical": q1,
        "social": q2,
        "business": q3
    }

    return redirect("/career-test")

# ================= CAREER TEST =================
@app.route("/career-test")
def career_test():
    if "user_id" not in session:
        return redirect("/login")

    return render_template("career_test.html")

# ================= SUBMIT CAREER =================
@app.route("/submit-career", methods=["POST"])
def submit_career():
    interests = request.form.getlist("interest")

    math = int(request.form["math"])
    science = int(request.form["science"])

    score = 0

    if "tech" in interests:
        score += 30
    if math > 70:
        score += 20
    if science > 70:
        score += 20

    psych = session.get("psychometric", {})
    final_score = score + psych.get("technical", 0)

    if final_score > 80:
        result = "Engineering / Software Developer"
    elif final_score > 50:
        result = "Business / Management"
    else:
        result = "Creative Field"

    return render_template("result.html", result=result)

# ================= RESULT =================
@app.route("/result")
def result():
    if "user_id" not in session:
        return redirect("/login")

    return render_template("result.html")

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)

# Psychometric Test Questions:
@app.route("/submit-psychometric", methods=["POST"])
def submit_psychometric():

    if "user_id" not in session:
        return redirect("/login")

    data = request.get_json()
    answers = data["answers"]

    tech = social = creative = business = 0

    for ans in answers:
        if ans["type"] == "technical":
            tech += ans["score"]
        elif ans["type"] == "social":
            social += ans["score"]
        elif ans["type"] == "creative":
            creative += ans["score"]
        elif ans["type"] == "business":
            business += ans["score"]

    cursor.execute("""
        INSERT INTO psychometric_data 
        (user_id, technical_score, social_score, creative_score, business_score)
        VALUES (%s,%s,%s,%s,%s)
    """, (session["user_id"], tech, social, creative, business))

    db.commit()

    return {"message": "Saved"}

@app.route("/submit-career", methods=["POST"])
def submit_career():

    interests = request.form.getlist("interest")

    math = int(request.form["math"])
    science = int(request.form["science"])

    score = 0

    if "tech" in interests:
        score += 30
    if math > 70:
        score += 20
    if science > 70:
        score += 20

    # Combine psychometric
    psych = session.get("psychometric", {})
    final_score = score + psych.get("technical", 0)

    if final_score > 80:
        result = "Engineering / Software Developer"
    elif final_score > 50:
        result = "Business / Management"
    else:
        result = "Creative Field"

    return render_template("result.html", result=result)