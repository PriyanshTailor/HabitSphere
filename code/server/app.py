from flask import Flask, request, redirect, session, jsonify, send_from_directory
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import joblib
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

load_dotenv()

app = Flask(__name__, static_folder='../client', static_url_path='')
app.secret_key = 'your_secret_key'

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'habitsphere'
app.config['SESSION_PERMANENT'] = False
mysql = MySQL(app)

# Upload configuration
UPLOAD_FOLDER = os.path.join('..', 'client', 'images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Load ML models and encoders
model_dir = os.path.join("..", "model", "habit_suggest_model")
habit_model = habit_symbol_model = habit_image_model = None

try:
    habit_model = joblib.load(os.path.join(model_dir, "habit_model.pkl"))
    habit_symbol_model = joblib.load(os.path.join(model_dir, "habit_symbol_model.pkl"))
    habit_image_model = joblib.load(os.path.join(model_dir, "habit_image_model.pkl"))
    target_encoder = joblib.load(os.path.join(model_dir, "habit_encoder.pkl"))
    symbol_encoder = joblib.load(os.path.join(model_dir, "habit_symbol_encoder.pkl"))
    image_encoder = joblib.load(os.path.join(model_dir, "habit_image_encoder.pkl"))

    label_encoders = {}
    encoder_columns = [
        "age_group", "gender", "personality_type", "mood", "goal",
        "time_of_day", "habit_type", "difficulty", "habit_category"
    ]
    for col in encoder_columns:
        label_encoders[col] = joblib.load(os.path.join(model_dir, f"{col}_encoder.pkl"))
except Exception as e:
    print("Model loading error:", e)

@app.route('/')
def home():
    return redirect('/login.html')

@app.route('/<path:path>')
def serve_static_file(path):
    return app.send_static_file(path)

@app.route('/signup', methods=['POST'])
def signup_post():
    fullname = request.form['fullname']
    email = request.form['email']
    password = request.form['password']
    confirm = request.form['confirm_password']

    if password != confirm:
        return redirect('/signup.html?msg=Passwords+do+not+match')

    hashed_password = generate_password_hash(password)
    cur = mysql.connection.cursor()
    try:
        cur.execute("INSERT INTO users (fullname, email, password) VALUES (%s, %s, %s)",
                    (fullname, email, hashed_password))
        mysql.connection.commit()
        return redirect('/login.html?msg=Signup+successful')
    except Exception as e:
        print("Signup Error:", e)
        mysql.connection.rollback()
        return redirect('/signup.html?msg=User+already+exists')
    finally:
        cur.close()

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form['email']
    password = request.form['password']

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, fullname, email, password FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()

    if user and check_password_hash(user[3], password):
        session['user_id'] = user[0]
        session['fullname'] = user[1]
        session['email'] = user[2]
        session['login_success'] = True
        return redirect('/index.html')
    else:
        return redirect('/login.html?msg=Invalid+credentials')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login.html?msg=Logged+out+successfully')

@app.route('/get_user_info')
def get_user_info():
    if 'user_id' not in session:
        return jsonify({'fullname': '', 'email': '', 'member_since': '', 'profile_pic_url': ''})

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT fullname, email, created_at, profile_pic_url FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()

    if user:
        fullname, email, created_at, profile_pic_url = user
        member_since = created_at.strftime("%d %b %Y, %I:%M %p") if created_at else ''
        if not profile_pic_url:
            profile_pic_url = '/images/defaultuser.jpg'
        return jsonify({
            'fullname': fullname,
            'email': email,
            'member_since': member_since,
            'profile_pic_url': profile_pic_url
        })
    else:
        return jsonify({'fullname': '', 'email': '', 'member_since': '', 'profile_pic_url': ''})

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401

    user_id = session['user_id']
    fullname = request.form.get('fullname')
    email = request.form.get('email')
    password = request.form.get('password')
    file = request.files.get('profile_pic_file')

    cur = mysql.connection.cursor()
    try:
        if fullname:
            cur.execute("UPDATE users SET fullname = %s WHERE id = %s", (fullname, user_id))
            session['fullname'] = fullname

        if email:
            cur.execute("UPDATE users SET email = %s WHERE id = %s", (email, user_id))
            session['email'] = email

        if password:
            hashed_password = generate_password_hash(password)
            cur.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, user_id))

        if file and allowed_file(file.filename):
            filename = secure_filename(f"user_{user_id}_" + file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            pic_url = f"/images/{filename}"
            cur.execute("UPDATE users SET profile_pic_url = %s WHERE id = %s", (pic_url, user_id))

        mysql.connection.commit()
        return jsonify({'success': True})
    except Exception as e:
        print("Update Profile Error:", e)
        mysql.connection.rollback()
        return jsonify({'success': False, 'message': 'Profile update failed'}), 500
    finally:
        cur.close()

@app.route('/suggest_habit', methods=['POST'])
def suggest_habit():
    if habit_model is None or habit_symbol_model is None or habit_image_model is None:
        return jsonify({'habit': 'Model not available'}), 500

    try:
        data = request.get_json()
        df = pd.DataFrame([data])
        for col in df.columns:
            df[col] = label_encoders[col].transform(df[col].astype(str))

        habit_pred = habit_model.predict(df)
        habit = target_encoder.inverse_transform(habit_pred)[0]

        symbol_pred = habit_symbol_model.predict(df)
        symbol = symbol_encoder.inverse_transform(symbol_pred)[0]

        image_pred = habit_image_model.predict(df)
        image_file = image_encoder.inverse_transform(image_pred)[0]

        return jsonify({
            'habit': habit,
            'symbol': symbol,
            'image_file': image_file
        })
    except Exception as e:
        print("Prediction Error:", e)
        return jsonify({'habit': 'Error', 'symbol': '', 'image_file': ''}), 500

@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/add_habit', methods=['POST'])
def add_habit():
    if 'user_id' not in session:
        return redirect('/login.html?msg=Please+login+first')

    habit = request.form.get('habit')
    icon = request.form.get('habit_icon', '📝')
    time = request.form.get('habit_time', 'Anytime')
    user_id = session['user_id']

    cur = mysql.connection.cursor()
    try:
        cur.execute(
            "INSERT INTO user_habits (user_id, habit, icon, preferred_time, status) VALUES (%s, %s, %s, %s, %s)",
            (user_id, habit, icon, time, 'Pending')
        )
        mysql.connection.commit()
        return redirect('/index.html')
    except Exception as e:
        print("Add Habit Error:", e)
        mysql.connection.rollback()
        return redirect('/create_habit.html?msg=Failed+to+add')
    finally:
        cur.close()

@app.route('/get_user_habits')
def get_user_habits():
    if 'user_id' not in session:
        return jsonify([])

    user_id = session['user_id']
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, habit, icon, preferred_time, scheduled_day, status FROM user_habits WHERE user_id = %s AND status = 'Pending'", (user_id,))
    habits = cur.fetchall()
    cur.close()

    habit_list = []
    for h in habits:
        habit_list.append({
            'id': h[0],
            'habit': h[1],
            'icon': h[2],
            'time': str(h[3]) if h[3] else '',
            'day': str(h[4]) if h[4] else '',
            'status': h[5]
        })
    return jsonify(habit_list)

@app.route('/update_habit_status', methods=['POST'])
def update_habit_status():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    habit_id = data.get('id')
    status = data.get('status', 'Done')

    cur = mysql.connection.cursor()
    try:
        if status == "Done":
            cur.execute("UPDATE user_habits SET status = %s, done_at = NOW() WHERE id = %s AND user_id = %s",
                        (status, habit_id, session['user_id']))
        else:
            cur.execute("UPDATE user_habits SET status = %s WHERE id = %s AND user_id = %s",
                        (status, habit_id, session['user_id']))
        mysql.connection.commit()
        return jsonify({'message': 'Status updated'})
    except Exception as e:
        print("Update Status Error:", e)
        mysql.connection.rollback()
        return jsonify({'error': 'Failed to update status'}), 500
    finally:
        cur.close()

@app.route('/get_dashboard_stats')
def get_dashboard_stats():
    if 'user_id' not in session:
        return jsonify({'streak': 0, 'success_ratio': 0})

    cur = mysql.connection.cursor()
    user_id = session['user_id']

    cur.execute("""
        SELECT COUNT(*) FROM user_habits 
        WHERE user_id = %s AND status = 'Done'
    """, (user_id,))
    done_count = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM user_habits 
        WHERE user_id = %s AND status = 'Skipped'
    """, (user_id,))
    skipped_count = cur.fetchone()[0]

    total = done_count + skipped_count
    success_ratio = round((done_count / total) * 100) if total > 0 else 0

    cur.execute("""
        SELECT DISTINCT DATE(done_at) FROM user_habits
        WHERE user_id = %s AND status = 'Done'
        ORDER BY DATE(done_at) DESC
    """, (user_id,))
    rows = cur.fetchall()

    streak = 0
    today = datetime.today().date()
    for row in rows:
        day = row[0]
        if day == today or day == today - timedelta(days=streak):
            streak += 1
        else:
            break

    cur.close()
    return jsonify({'streak': streak, 'success_ratio': success_ratio})

@app.before_request
def before_request():
    if mysql.connection:
        cursor = mysql.connection.cursor()
        cursor.execute("SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;")
        cursor.close()
        
@app.route('/get_insights')
def get_insights():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    cur = mysql.connection.cursor()

    # 1) Streak: get max consecutive days with habits done
    cur.execute("""
        SELECT DATE(done_at) as day
        FROM user_habits
        WHERE user_id = %s AND status = 'Done'
        GROUP BY day
        ORDER BY day DESC
    """, (user_id,))
    days = [row[0] for row in cur.fetchall()]
    streak = 0
    if days:
        streak = 1
        prev = days[0]
        for day in days[1:]:
            if (prev - day).days == 1:
                streak += 1
                prev = day
            else:
                break

    # 2) Most completed habit
    cur.execute("""
        SELECT habit, 
               COUNT(*) AS total,
               SUM(status = 'Done') AS done_count
        FROM user_habits
        WHERE user_id = %s
        GROUP BY habit
        ORDER BY done_count DESC
        LIMIT 1
    """, (user_id,))
    most_completed = cur.fetchone()
    if most_completed and most_completed[1] > 0:
        most_completed_name = most_completed[0]
        percent_done = int(most_completed[2] / most_completed[1] * 100)
    else:
        most_completed_name = "-"
        percent_done = 0

    # 3) Most missed habit
    cur.execute("""
        SELECT habit, 
               COUNT(*) AS total,
               SUM(status = 'Skipped') AS skipped_count
        FROM user_habits
        WHERE user_id = %s
        GROUP BY habit
        ORDER BY skipped_count DESC
        LIMIT 1
    """, (user_id,))
    most_missed = cur.fetchone()
    if most_missed and most_missed[1] > 0:
        most_missed_name = most_missed[0]
        percent_skipped = int(most_missed[2] / most_missed[1] * 100)
    else:
        most_missed_name = "-"
        percent_skipped = 0

    # 4) Weekly done count
    cur.execute("""
        SELECT DATE(done_at) as day, COUNT(*) 
        FROM user_habits
        WHERE user_id = %s AND status = 'Done'
          AND done_at >= CURDATE() - INTERVAL 6 DAY
        GROUP BY day
        ORDER BY day
    """, (user_id,))
    weekly = cur.fetchall()
    weekly_data = []
    for i in range(7):
        day = (pd.Timestamp.now() - pd.Timedelta(days=6-i)).date()
        count = next((c for d, c in weekly if d == day), 0)
        weekly_data.append({'date': str(day), 'count': count})

    # 5) Success vs Skipped ratio
    cur.execute("""
        SELECT 
          SUM(status = 'Done') as done_count,
          SUM(status = 'Skipped') as skipped_count
        FROM user_habits
        WHERE user_id = %s
    """, (user_id,))
    done_count, skipped_count = cur.fetchone()
    done_count = done_count or 0
    skipped_count = skipped_count or 0
    total = done_count + skipped_count
    success_percent = int(done_count / total * 100) if total > 0 else 0

    cur.close()

    return jsonify({
        'streak': streak,
        'most_completed': {'habit': most_completed_name, 'percent': percent_done},
        'most_missed': {'habit': most_missed_name, 'percent': percent_skipped},
        'weekly': weekly_data,
        'success_percent': success_percent
    })

@app.route('/schedule_habit', methods=['POST'])
def schedule_habit():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    habit = data.get('name')
    time = data.get('time', 'Anytime')
    icon = data.get('icon', '✨')
    day = data.get('day')
    user_id = session['user_id']

    cur = mysql.connection.cursor()
    try:
        cur.execute(
            "INSERT INTO user_habits (user_id, habit, icon, preferred_time, scheduled_day, status) VALUES (%s, %s, %s, %s, %s, %s)",
            (user_id, habit, icon, time, day, 'Scheduled')
        )
        mysql.connection.commit()
        return jsonify({'message': 'Habit scheduled'})
    except Exception as e:
        print("Schedule Habit Error:", e)
        mysql.connection.rollback()
        return jsonify({'error': 'Failed to schedule habit'}), 500
    finally:
        cur.close()

if __name__ == '__main__':
    app.run(debug=True)
