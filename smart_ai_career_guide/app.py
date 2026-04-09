from flask import Flask, render_template, request, redirect, session, jsonify
import mysql.connector
from mysql.connector import Error
import random
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv
import asyncio
# from emergent_sdk.chat import LlmChat, UserMessage

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'supersecretkey-change-this')

# ================= DATABASE CONNECTION =================
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'Vsjaymali@21'),
            database=os.getenv('DB_NAME', 'smart_ai_career_guide')
        )
        return connection
    except Error as e:
        print(f"❌ Database Error: {e}")
        return None

# ================= CAREER DATABASE LOADER =================
def load_careers():
    with open('careers_database.json', 'r') as f:
        data = json.load(f)
    return data['careers']

# ================= OTP STORAGE =================
otp_storage = {}

# ================= EMAIL FUNCTION =================
def send_email_otp(receiver_email, otp):
    try:
        sender_email = os.getenv('SMTP_EMAIL')
        app_password = os.getenv('SMTP_PASSWORD')
        
        msg = MIMEText(f"Your OTP for Smart AI Career Guide is: {otp}\n\nValid for 10 minutes.")
        msg["Subject"] = "Smart AI Career Guide - Email Verification"
        msg["From"] = sender_email
        msg["To"] = receiver_email
        
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        
        print("✅ OTP SENT SUCCESSFULLY")
        return True
    except Exception as e:
        print(f"❌ EMAIL ERROR: {e}")
        return False

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
    
    otp_storage[email] = {
        'otp': otp,
        'timestamp': datetime.now()
    }
    
    print(f"OTP for {email}: {otp}")  # Debug
    send_email_otp(email, otp)
    
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
        
        # Calculate age
        dob_date = datetime.strptime(dob, "%Y-%m-%d")
        today = datetime.today()
        age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
        
        # OTP Verification
        if email not in otp_storage:
            return render_template("register.html", error="OTP expired or not sent")
        
        stored_data = otp_storage[email]
        if stored_data['otp'] != user_otp:
            return render_template("register.html", error="Invalid OTP")
        
        # Check if OTP is expired (10 minutes)
        if datetime.now() - stored_data['timestamp'] > timedelta(minutes=10):
            del otp_storage[email]
            return render_template("register.html", error="OTP expired")
        
        db = get_db_connection()
        if not db:
            return render_template("register.html", error="Database connection error")
        
        cursor = db.cursor(dictionary=True)
        
        # Check existing user
        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        if cursor.fetchone():
            cursor.close()
            db.close()
            return render_template("register.html", error="Email already registered")
        
        # Insert user
        cursor.execute(
            "INSERT INTO users (name, email, password, dob, age, mobile, verified) VALUES (%s,%s,%s,%s,%s,%s,%s)",
            (name, email, password, dob, age, mobile, 1)
        )
        db.commit()
        cursor.close()
        db.close()
        
        # Clear OTP
        del otp_storage[email]
        
        return render_template("register.html", success=True)
    
    return render_template("register.html")

# ================= LOGIN =================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        
        db = get_db_connection()
        if not db:
            return "Database connection error"
        
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM users WHERE email=%s AND password=%s",
            (email, password)
        )
        user = cursor.fetchone()
        cursor.close()
        db.close()
        
        if user:
            session["user_id"] = user["user_id"]
            session["name"] = user["name"]
            session["email"] = user["email"]
            return redirect("/dashboard")
        
        return render_template("login.html", error="Invalid credentials")
    
    return render_template("login.html")

# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")
    
    user_id = session["user_id"]
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    # Check if tests completed
    cursor.execute("SELECT * FROM psychometric_data WHERE user_id=%s ORDER BY test_date DESC LIMIT 1", (user_id,))
    psych_completed = cursor.fetchone() is not None
    
    cursor.execute("SELECT * FROM career_test_data WHERE user_id=%s ORDER BY test_date DESC LIMIT 1", (user_id,))
    career_completed = cursor.fetchone() is not None
    
    cursor.execute("SELECT * FROM career_results WHERE user_id=%s ORDER BY result_date DESC LIMIT 1", (user_id,))
    result = cursor.fetchone()
    
    cursor.close()
    db.close()
    
    return render_template("dashboard.html", 
                         name=session["name"],
                         psych_completed=psych_completed,
                         career_completed=career_completed,
                         result=result)

# ================= PSYCHOMETRIC TEST =================
@app.route("/psychometric-test")
def psychometric_test():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("psychometric_test.html")

# ================= SUBMIT PSYCHOMETRIC =================
@app.route("/submit-psychometric", methods=["POST"])
def submit_psychometric():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
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
    
    db = get_db_connection()
    cursor = db.cursor()
    
    # Delete old psychometric data for this user
    cursor.execute("DELETE FROM psychometric_data WHERE user_id=%s", (session["user_id"],))
    
    cursor.execute("""
        INSERT INTO psychometric_data
        (user_id, technical_score, social_score, creative_score, business_score)
        VALUES (%s,%s,%s,%s,%s)
    """, (session["user_id"], tech, social, creative, business))
    
    db.commit()
    cursor.close()
    db.close()
    
    return jsonify({"message": "Psychometric test completed!"})

# ================= CAREER TEST =================
@app.route("/career-test")
def career_test():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("career_test.html")

# ================= SUBMIT CAREER TEST =================
@app.route("/submit-career", methods=["POST"])
def submit_career():
    if "user_id" not in session:
        return redirect("/login")
    
    top_subjects = request.form.get("top_subjects", "")
    weak_subjects = request.form.get("weak_subjects", "")
    interests = request.form.get("interest", "")
    skills = request.form.get("skills", "")
    relocation = request.form.get("relocation", "No")
    
    db = get_db_connection()
    cursor = db.cursor()
    
    # Delete old career test data
    cursor.execute("DELETE FROM career_test_data WHERE user_id=%s", (session["user_id"],))
    
    # Insert new data
    cursor.execute("""
        INSERT INTO career_test_data
        (user_id, top_subjects, weak_subjects, interests, skills, relocation)
        VALUES (%s,%s,%s,%s,%s,%s)
    """, (session["user_id"], top_subjects, weak_subjects, interests, skills, relocation))
    
    db.commit()
    cursor.close()
    db.close()
    
    # Trigger career prediction
    return redirect("/generate-result")

# ================= CAREER PREDICTION ENGINE =================
def calculate_career_match(career, psychometric, career_test, user_subjects):
    """
    Calculate career match score with weighted algorithm
    - Academic Performance: 40%
    - Psychometric Scores: 30%
    - Interests & Skills: 30%
    """
    
    # 1. Academic Score (40%)
    academic_score = 0
    subject_list = [s.strip().lower() for s in user_subjects.split(',')]
    
    # Check if required subjects match
    required_match = sum(1 for subj in career['required_subjects'] 
                        if any(subj.lower() in s for s in subject_list))
    
    if len(career['required_subjects']) > 0:
        academic_score = (required_match / len(career['required_subjects'])) * 100
    else:
        academic_score = 50  # Neutral score
    
    # Apply minimum score requirements (if applicable)
    if 'min_math_score' in career:
        # Assume average performance if we don't have actual scores
        academic_score *= 0.9  # Slight reduction for not having exact scores
    
    academic_weight = academic_score * 0.40
    
    # 2. Psychometric Score (30%)
    psych_match = 0
    psych_total = 0
    
    for key, required_score in career['personality_fit'].items():
        user_score = psychometric.get(f"{key}_score", 0)
        # Normalize to 0-100 scale (assuming max score is 125 for 25 questions * 5 points)
        normalized_user = (user_score / 125) * 100
        
        # Calculate how close the user is to the required personality
        difference = abs(normalized_user - required_score)
        match_percentage = max(0, 100 - difference)
        
        psych_match += match_percentage
        psych_total += 1
    
    psychometric_score = (psych_match / psych_total) if psych_total > 0 else 50
    psychometric_weight = psychometric_score * 0.30
    
    # 3. Interest & Skills Score (30%)
    interest_score = 0
    
    # Check interest match
    user_interest = career_test.get('interests', '').lower()
    career_interests = [i.lower() for i in career.get('interests', [])]
    
    interest_match = any(ci in user_interest for ci in career_interests)
    if interest_match:
        interest_score += 70
    else:
        interest_score += 30
    
    # Check skills match
    user_skills = career_test.get('skills', '').lower()
    career_skills = [s.lower() for s in career.get('skills', [])]
    
    skill_matches = sum(1 for cs in career_skills if cs in user_skills)
    if len(career_skills) > 0:
        interest_score += (skill_matches / len(career_skills)) * 30
    
    interest_weight = interest_score * 0.30
    
    # Total weighted score
    total_score = academic_weight + psychometric_weight + interest_weight
    
    # Apply elimination rules
    if 'min_math_score' in career and 'Math' not in user_subjects:
        total_score *= 0.7  # Penalty for missing critical subject
    
    return {
        'total_score': round(total_score, 2),
        'academic_score': round(academic_score, 2),
        'psychometric_score': round(psychometric_score, 2),
        'interest_score': round(interest_score, 2),
        'confidence': round(min(total_score, 99), 2)  # Cap at 99%
    }

@app.route("/generate-result")
def generate_result():
    if "user_id" not in session:
        return redirect("/login")
    
    user_id = session["user_id"]
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    # Get psychometric data
    cursor.execute("SELECT * FROM psychometric_data WHERE user_id=%s ORDER BY test_date DESC LIMIT 1", (user_id,))
    psychometric = cursor.fetchone()
    
    # Get career test data
    cursor.execute("SELECT * FROM career_test_data WHERE user_id=%s ORDER BY test_date DESC LIMIT 1", (user_id,))
    career_test = cursor.fetchone()
    
    if not psychometric or not career_test:
        cursor.close()
        db.close()
        return redirect("/dashboard")
    
    # Load careers and calculate matches
    careers = load_careers()
    career_matches = []
    
    for career in careers:
        match_data = calculate_career_match(
            career, 
            psychometric, 
            career_test,
            career_test['top_subjects']
        )
        
        career_matches.append({
            'career': career,
            'scores': match_data
        })
    
    # Sort by total score
    career_matches.sort(key=lambda x: x['scores']['total_score'], reverse=True)
    
    # Get top 3
    top_3 = career_matches[:3]
    
    # Save to database
    cursor.execute("DELETE FROM career_results WHERE user_id=%s", (user_id,))
    
    cursor.execute("""
        INSERT INTO career_results
        (user_id, primary_career, primary_confidence, primary_score,
         secondary_career, secondary_confidence, secondary_score,
         alternative_career, alternative_confidence, alternative_score,
         academic_score, psychometric_score, interest_score)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        user_id,
        top_3[0]['career']['name'], top_3[0]['scores']['confidence'], top_3[0]['scores']['total_score'],
        top_3[1]['career']['name'], top_3[1]['scores']['confidence'], top_3[1]['scores']['total_score'],
        top_3[2]['career']['name'], top_3[2]['scores']['confidence'], top_3[2]['scores']['total_score'],
        top_3[0]['scores']['academic_score'],
        top_3[0]['scores']['psychometric_score'],
        top_3[0]['scores']['interest_score']
    ))
    
    db.commit()
    cursor.close()
    db.close()
    
    return redirect("/result")

# ================= RESULT PAGE =================
@app.route("/result")
def result():
    if "user_id" not in session:
        return redirect("/login")
    
    user_id = session["user_id"]
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM career_results WHERE user_id=%s ORDER BY result_date DESC LIMIT 1", (user_id,))
    result_data = cursor.fetchone()
    
    cursor.close()
    db.close()
    
    if not result_data:
        return redirect("/dashboard")
    
    # Load career details
    careers = load_careers()
    career_details = {}
    
    for career in careers:
        if career['name'] == result_data['primary_career']:
            career_details['primary'] = career
        if career['name'] == result_data['secondary_career']:
            career_details['secondary'] = career
        if career['name'] == result_data['alternative_career']:
            career_details['alternative'] = career
    
    return render_template("result.html", result=result_data, careers=career_details)

# ================= AI CHATBOT =================
@app.route("/chatbot")
def chatbot_page():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("chatbot.html")

@app.route("/api/chat", methods=["POST"])
async def chat_api():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    data = request.get_json()
    user_message = data.get("message", "")
    
    if not user_message:
        return jsonify({"error": "No message provided"}), 400
    
    user_id = session["user_id"]
    session_id = f"user_{user_id}_session"
    
    # Initialize chatbot
    chat = LlmChat(
        api_key=os.getenv('EMERGENT_LLM_KEY'),
        session_id=session_id,
        system_message="""You are a helpful career guidance counselor for the Smart AI Career Guide platform. 
        Help users navigate the platform, answer career-related questions, and provide guidance on:
        - Taking psychometric tests
        - Understanding career test results
        - Exploring different career paths
        - Skills needed for various careers
        - Educational requirements
        
        Be friendly, supportive, and encouraging. Keep responses concise and actionable."""
    ).with_model("gemini", "gemini-3-flash-preview")
    
    # Create user message
    message = UserMessage(text=user_message)
    
    try:
        # Get AI response
        response = await chat.send_message(message)
        
        # Save to database
        db = get_db_connection()
        cursor = db.cursor()
        
        cursor.execute("""
            INSERT INTO chat_history (user_id, session_id, role, message)
            VALUES (%s, %s, %s, %s)
        """, (user_id, session_id, 'user', user_message))
        
        cursor.execute("""
            INSERT INTO chat_history (user_id, session_id, role, message)
            VALUES (%s, %s, %s, %s)
        """, (user_id, session_id, 'assistant', response))
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({"response": response})
    
    except Exception as e:
        print(f"Chatbot error: {e}")
        return jsonify({"error": "Failed to get response"}), 500

# ================= CAREER ADVISOR BOOKING =================
@app.route("/career-advisor")
def career_advisor():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("career_advisor.html")

@app.route("/submit-advisor-booking", methods=["POST"])
def submit_advisor_booking():
    if "user_id" not in session:
        return jsonify({"error": "Not logged in"}), 401
    
    name = request.form.get("name")
    email = request.form.get("email")
    phone = request.form.get("phone")
    preferred_date = request.form.get("preferred_date")
    preferred_time = request.form.get("preferred_time")
    message = request.form.get("message", "")
    
    db = get_db_connection()
    cursor = db.cursor()
    
    cursor.execute("""
        INSERT INTO advisor_bookings
        (user_id, name, email, phone, preferred_date, preferred_time, message, status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
     """, (session["user_id"], name, email, phone, preferred_date, preferred_time, message, "Pending"))
    
    db.commit()
    cursor.close()
    db.close()
    
    return render_template("career_advisor.html", success=True)

# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
from flask import Flask, render_template, request, redirect, session, jsonify
