from flask import Flask, render_template, session, redirect, url_for, send_from_directory, abort
from flask_socketio import SocketIO
import os, json, uuid
import time, random, string
from datetime import datetime, timedelta
from pathlib import Path
import pwd

app = Flask(__name__)
app.secret_key = 'super-secret-key'
socketio = SocketIO(app)

EMAIL_DIR = "/var/tempmail/mails"
TIMER_DURATION = 300  # 2 Minuten in Sekunden
ALIAS_LIFETIME = timedelta(minutes=5)
TARGET_USER = "www-data"
STATS_FILE = "/var/tempmail/misc/stats.json"

def ensure_stats_file():
    initial_data = {}
    try:
        os.makedirs(os.path.dirname(STATS_FILE), exist_ok=True)
        if not os.path.exists(STATS_FILE):
            with open(STATS_FILE, 'w') as f:
                json.dump(initial_data, f)
            pw_record = pwd.getpwnam(TARGET_USER)
            os.chown(STATS_FILE, pw_record.pw_uid, pw_record.pw_gid)
    except Exception as e:
        print(f"Fehler beim Erstellen von stats.json: {e}")

def generate_email():
    return ''.join(random.choices(string.ascii_lowercase, k=5))

def check_alias_expiration():
    if 'email_created_at' in session:
        created_at = datetime.fromtimestamp(session['email_created_at'])
        if datetime.now() - created_at > ALIAS_LIFETIME:
            return True
    return False

def create_welcome_email(email_id):
    inbox_dir = Path(EMAIL_DIR) / email_id
    inbox_dir.mkdir(parents=True, exist_ok=True)
    try:
        pw_record = pwd.getpwnam(TARGET_USER)
        uid = pw_record.pw_uid
        gid = pw_record.pw_gid
        os.chown(inbox_dir, uid, gid)
    except Exception:
        pass

    filename = inbox_dir / f"{int(time.time())}_welcome.json"
    welcome_email = {
        "from": "noreply@olifani.eu",
        "to": f"{email_id}@inboxcl.xyz",
        "subject": "Welcome to tempmail.olifani.eu",
        "body": "This is your new temporary inbox. You can receive emails here for the next 5 minutes."
    }

    with open(filename, "w") as f:
        json.dump(welcome_email, f, indent=2)

    try:
        os.chown(filename, uid, gid)
    except Exception:
        pass

def log_address_creation():
    today = datetime.utcnow().strftime("%Y-%m-%d")
    stats = {}

    try:
        with open(STATS_FILE, "r") as f:
            stats = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        stats = {}

    stats[today] = stats.get(today, 0) + 1

    with open(STATS_FILE, "w") as f:
        json.dump(stats, f)

@app.route('/email/<email_id>/<filename>')
def view_email(email_id, filename):
    inbox_dir = os.path.join(EMAIL_DIR, email_id)
    file_path = os.path.join(inbox_dir, filename)

    if not os.path.exists(file_path):
        abort(404)

    with open(file_path) as f:
        mail = json.load(f)

    return render_template('email_view.html', mail=mail)

@app.route('/index.html')
def index():
    if 'email_id' not in session or check_alias_expiration():
        if 'email_id' in session:
            inbox_dir = os.path.join(EMAIL_DIR, session['email_id'])
            if os.path.exists(inbox_dir):
                for fname in os.listdir(inbox_dir):
                    os.remove(os.path.join(inbox_dir, fname))
        session.clear()
        session['email_id'] = generate_email()
        session['email_created_at'] = time.time()
        log_address_creation()
        create_welcome_email(session['email_id'])

    email_id = session['email_id']
    inbox_dir = os.path.join(EMAIL_DIR, email_id)
    emails = []

    if os.path.exists(inbox_dir):
        for fname in sorted(os.listdir(inbox_dir), reverse=True):
            fpath = os.path.join(inbox_dir, fname)
            with open(fpath) as f:
                mail = json.load(f)
                mail['filename'] = fname
                emails.append(mail)

    remaining_time = ALIAS_LIFETIME - (datetime.now() - datetime.fromtimestamp(session['email_created_at']))
    remaining_minutes, remaining_seconds = divmod(int(remaining_time.total_seconds()), 60)

    if remaining_minutes < 0:
        remaining_minutes = 0
        remaining_seconds = 0

    session['remaining_time'] = remaining_time.total_seconds()

    return render_template("index.html",
                           email=f"{email_id}@inboxcl.xyz",
                           emails=emails,
                           email_id=email_id,
                           remaining_minutes=remaining_minutes,
                           remaining_seconds=remaining_seconds)

@app.route('/delete_emails/<email_id>')
def delete_emails(email_id):
    inbox_dir = os.path.join(EMAIL_DIR, email_id)
    if os.path.exists(inbox_dir):
        for fname in os.listdir(inbox_dir):
            os.remove(os.path.join(inbox_dir, fname))
    return redirect(url_for('index'))

@app.route('/sitemap-side.xml')
def sitemap():
    return send_from_directory('static/meta', 'sitemap.xml')

@app.route('/robots.txt')
def robots():
    return send_from_directory('static/meta', 'robots.txt')

@app.route('/why-temp-email.html')
def why_temp_email():
    return render_template('why-temp-email.html')

@app.route("/stats")
def stats():
    try:
        with open(STATS_FILE, "r") as f:
            stats = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        stats = {}

    return render_template("stats.html", stats=stats)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    ensure_stats_file()
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)

