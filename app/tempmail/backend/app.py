from flask import Flask, render_template, session, redirect, url_for, send_from_directory, abort, request, flash
from flask_socketio import SocketIO

import os
import json
import time
import random
import string
import pwd
import requests
import re
import hashlib
import smtplib

from datetime import datetime, timedelta, timezone
from pathlib import Path
from email.message import EmailMessage

GA_CONFIG_PATH = "/var/tempmail/misc/config_ga4.json"

try:
    with open(GA_CONFIG_PATH) as f:
        ga4_config = json.load(f)
        GA_MEASUREMENT_ID = ga4_config.get("measurement_id")
        GA_API_SECRET = ga4_config.get("api_secret")
except Exception as e:
    print(f"Fehler beim Laden der GA4-Konfiguration: {e}")
    GA_MEASUREMENT_ID = None
    GA_API_SECRET = None

app = Flask(__name__)
socketio = SocketIO(app)

with open("/var/tempmail/misc/app.secret.json") as f:
    secret_data = json.load(f)
    app.secret_key = secret_data["secret_key"]

EMAIL_DIR = "/var/tempmail/mails"
TIMER_DURATION = 300
ALIAS_LIFETIME = timedelta(minutes=5)
TARGET_USER = "www-data"
STATS_FILE = "/var/tempmail/misc/stats.json"
ACTIVE_ALIASES_FILE = "/var/tempmail/misc/active_aliases.json"


def send_ga4_pageview(request, client_id):

    url = f"https://www.google-analytics.com/mp/collect?measurement_id={GA_MEASUREMENT_ID}&api_secret={GA_API_SECRET}"
    
    payload = {
        "client_id": client_id,
        "events": [
            {
                "name": "page_view",
                "params": {
                    "page_location": request.base_url,
                    "page_title": "Inbox",
                    "engagement_time_msec": "100"
                }
            }
        ]
    }

    try:
        response = requests.post(url, json=payload, timeout=1)
        response.raise_for_status()
        print("✅ GA4 page_view sent")
    except Exception as e:
        print(f"❌ GA4 error: {e}")

def send_ga4_emailview(request, client_id):

    url = f"https://www.google-analytics.com/mp/collect?measurement_id={GA_MEASUREMENT_ID}&api_secret={GA_API_SECRET}"
    
    payload = {
        "client_id": client_id,
        "events": [
            {
                "name": "email_view",
                "params": {
                    "page_location": request.base_url,
                    "page_title": "View Email",
                    "engagement_time_msec": "100"
                }
            }
        ]
    }

    try:
        response = requests.post(url, json=payload, timeout=1)
        response.raise_for_status()
        print("✅ GA4 email_view sent")
    except Exception as e:
        print(f"❌ GA4 error: {e}")



def send_ga4_forward_email(request, client_id):

    url = f"https://www.google-analytics.com/mp/collect?measurement_id={GA_MEASUREMENT_ID}&api_secret={GA_API_SECRET}"
    
    payload = {
        "client_id": client_id,
        "events": [
            {
                "name": "forward_email",
                "params": {
                    "page_location": request.base_url,
                    "page_title": "Forward Email",
                    "engagement_time_msec": "100"
                }
            }
        ]
    }

    try:
        response = requests.post(url, json=payload, timeout=1)
        response.raise_for_status()
        print("✅ GA4 email forward")
    except Exception as e:
        print(f"❌ GA4 error: {e}")

def send_ga4_reply_email(request, client_id):

    url = f"https://www.google-analytics.com/mp/collect?measurement_id={GA_MEASUREMENT_ID}&api_secret={GA_API_SECRET}"
    
    payload = {
        "client_id": client_id,
        "events": [
            {
                "name": "reply_email",
                "params": {
                    "page_location": request.base_url,
                    "page_title": "Reply Email",
                    "engagement_time_msec": "100"
                }
            }
        ]
    }

    try:
        response = requests.post(url, json=payload, timeout=1)
        response.raise_for_status()
        print("✅ GA4 email reply")
    except Exception as e:
        print(f"❌ GA4 error: {e}")

def send_ga4_create_new_email(request, client_id):

    url = f"https://www.google-analytics.com/mp/collect?measurement_id={GA_MEASUREMENT_ID}&api_secret={GA_API_SECRET}"
    
    payload = {
        "client_id": client_id,
        "events": [
            {
                "name": "create_new_email",
                "params": {
                    "page_location": request.base_url,
                    "page_title": "Create Alias",
                    "engagement_time_msec": "100"
                }
            }
        ]
    }

    try:
        response = requests.post(url, json=payload, timeout=1)
        response.raise_for_status()
        print("✅ GA4 create new email")
    except Exception as e:
        print(f"❌ GA4 error: {e}")


def add_active_alias(email_id):
    try:
        with open(ACTIVE_ALIASES_FILE, "r") as f:
            active_aliases = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        active_aliases = {}

    active_aliases[email_id] = datetime.now(timezone.utc).isoformat()

    with open(ACTIVE_ALIASES_FILE, "w") as f:
        json.dump(active_aliases, f)

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
        print(f"error while creating stats.json: {e}")

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
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    stats = {}

    try:
        with open(STATS_FILE, "r") as f:
            stats = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        stats = {}

    stats[today] = stats.get(today, 0) + 1

    with open(STATS_FILE, "w") as f:
        json.dump(stats, f)

def reset_email_session():
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
    add_active_alias(session['email_id'])

@app.route('/new-alias')
def new_alias():
    reset_email_session()
    if 'email_id' not in session or check_alias_expiration():
        reset_email_session()

    if 'client_id' not in session:
        raw = f"{request.remote_addr}-{time.time()}"
        session['client_id'] = hashlib.sha256(raw.encode()).hexdigest()[:16]

    if GA_MEASUREMENT_ID and GA_API_SECRET:
        send_ga4_create_new_email(request, session['client_id'])

 
    return redirect(url_for('index'))

@app.route('/index.html')
def index():
    if 'email_id' not in session or check_alias_expiration():
        reset_email_session()

    if 'client_id' not in session:
        raw = f"{request.remote_addr}-{time.time()}"
        session['client_id'] = hashlib.sha256(raw.encode()).hexdigest()[:16]

    if GA_MEASUREMENT_ID and GA_API_SECRET:
        send_ga4_pageview(request, session['client_id'])

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

@app.route('/email/<email_id>/<filename>')
def view_email(email_id, filename):
    if 'email_id' not in session or check_alias_expiration():
        reset_email_session()

    if 'client_id' not in session:
        raw = f"{request.remote_addr}-{time.time()}"
        session['client_id'] = hashlib.sha256(raw.encode()).hexdigest()[:16]

    if GA_MEASUREMENT_ID and GA_API_SECRET:
        send_ga4_emailview(request, session['client_id'])



    inbox_dir = os.path.join(EMAIL_DIR, email_id)
    file_path = os.path.join(inbox_dir, filename)

    if not os.path.exists(file_path):
        abort(404)

    mail = {}
    try:
        with open(file_path) as f:
            mail = json.load(f)
    except Exception as e:
        print(f"Fehler beim Laden der Mail-Datei: {e}")
        mail = {}

    # Sicherstellen, dass alle erwarteten Felder vorhanden sind
    mail.setdefault("from", "Unknown sender")
    mail.setdefault("to", f"{email_id}@inboxcl.xyz")
    mail.setdefault("subject", "(No subject)")
    mail.setdefault("date", "Unknown date")
    mail.setdefault("body", "[No content]")

    is_welcome = (mail.get("subject") == "Welcome to tempmail.olifani.eu")

    return render_template("email_view.html",
                           mail=mail,
                           alias=email_id,
                           filename=filename,
                           is_welcome=is_welcome)

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

@app.route('/ads.txt')
def ads():
    return send_from_directory('static/meta', 'ads.txt')

@app.route('/why-temp-email.html')
def why_temp_email():
    if 'email_id' not in session or check_alias_expiration():
        reset_email_session()

    if 'client_id' not in session:
        raw = f"{request.remote_addr}-{time.time()}"
        session['client_id'] = hashlib.sha256(raw.encode()).hexdigest()[:16]

    if GA_MEASUREMENT_ID and GA_API_SECRET:
        send_ga4_pageview(request, session['client_id'])



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

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('403.html'), 403

@app.route("/forbidden")
def forbidden_error_page():
    return render_template("403.html"), 403

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

@app.route("/temporary-email.html")
def temporary_email():
    if 'email_id' not in session or check_alias_expiration():
        reset_email_session()

    if 'client_id' not in session:
        raw = f"{request.remote_addr}-{time.time()}"
        session['client_id'] = hashlib.sha256(raw.encode()).hexdigest()[:16]

    if GA_MEASUREMENT_ID and GA_API_SECRET:
        send_ga4_pageview(request, session['client_id'])



    return render_template("temporary-email.html")


@app.route('/send-reply', methods=['POST'])
def send_reply():
    if 'email_id' not in session or check_alias_expiration():
        reset_email_session()

    if 'client_id' not in session:
        raw = f"{request.remote_addr}-{time.time()}"
        session['client_id'] = hashlib.sha256(raw.encode()).hexdigest()[:16]

    if GA_MEASUREMENT_ID and GA_API_SECRET:
        send_ga4_reply_email(request, session['client_id'])


    reply_to = request.form.get('reply_to')
    alias = request.form.get('alias')
    subject = request.form.get('subject')
    body = request.form.get('body')
    filename = request.form.get('filename')

    if not reply_to or not alias or not subject or not filename:
        flash("Missing required fields.", "error")
        if filename:
            return redirect(url_for('view_email', email_id=alias, filename=filename))
        else:
            return redirect(url_for('index'))

    try:

        inbox_dir = os.path.join(EMAIL_DIR, alias)
        original_path = os.path.join(inbox_dir, filename)

        original_body = ""
        if os.path.exists(original_path):
            with open(original_path, 'r') as f:
                try:
                    original = json.load(f)
                    original_body = original.get("body", "")
                except Exception as e:
                    original_body = "[Fehler beim Laden der ursprünglichen Nachricht]"

        quoted_original = "\n".join(["> " + line for line in original_body.splitlines()])

        full_body = f"{body}\n\n--- Original message ---\n{quoted_original}"

        msg = EmailMessage()
        msg['From'] = f"{alias}@inboxcl.xyz"
        msg['To'] = reply_to
        msg['Subject'] = subject
        msg.set_content(full_body)

        with smtplib.SMTP('localhost') as smtp:
            smtp.send_message(msg)

        print(f"✅ Reply sent to {reply_to} with subject '{subject}'")

        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Mail verschickt</title>
            <script>
                // Lade index.html im Hintergrund automatisch
                setTimeout(function() {
                    window.location.href = "/index.html";
                }, 2000);

                function closeWindow() {
                    window.close(); // Funktioniert nur bei per JS geöffnetem Fenster
                }
            </script>
            <style>
                body {
                    font-family: sans-serif;
                    text-align: center;
                    padding-top: 50px;
                }
                button {
                    padding: 10px 20px;
                    font-size: 16px;
                    border: none;
                    background: #3498db;
                    color: white;
                    border-radius: 6px;
                    cursor: pointer;
                }
            </style>
        </head>
        <body>
            <h2>Mail wurde erfolgreich verschickt!</h2>
            <button onclick="closeWindow()">Schließen</button>
        </body>
        </html>
        '''

    except Exception as e:
        print(f"❌ Fehler beim Senden: {e}")
        flash(f"Fehler beim Senden: {str(e)}", "error")
        return redirect(url_for('view_email', email_id=alias, filename=filename))


def sanitize_header(value):
    # Entfernt potenziell gefährliche Zeichen in Headern
    return re.sub(r'[\r\n]+', '', value.strip())

@app.route('/forward/<mail_id>', methods=['POST'])
def forward_mail(mail_id):
    if 'email_id' not in session or check_alias_expiration():
        reset_email_session()

    if 'client_id' not in session:
        raw = f"{request.remote_addr}-{time.time()}"
        session['client_id'] = hashlib.sha256(raw.encode()).hexdigest()[:16]

    if GA_MEASUREMENT_ID and GA_API_SECRET:
        send_ga4_forward_email(request, session['client_id'])


    target_email = request.form.get('target_email')

    if not target_email:
        flash("No destination email provided.", "error")
        return redirect(url_for('index'))

    # Einfache E-Mail-Formatprüfung
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", target_email):
        flash("Invalid email address format.", "error")
        return redirect(url_for('index'))

    inbox_dir = os.path.join(EMAIL_DIR, mail_id)
    mail_file = None

    if os.path.exists(inbox_dir):
        files = sorted(os.listdir(inbox_dir), reverse=True)
        if files:
            mail_file = os.path.join(inbox_dir, files[0])

    if not mail_file or not os.path.exists(mail_file):
        flash("No email to forward.", "error")
        return redirect(url_for('index'))

    try:
        with open(mail_file, 'r') as f:
            mail = json.load(f)

        msg = EmailMessage()
        msg['From'] = sanitize_header(f"{mail_id}@inboxcl.xyz")
        msg['To'] = sanitize_header(target_email)
        msg['Subject'] = sanitize_header("[FWD] " + mail.get("subject", "(No subject)"))

        if mail.get("body", "").startswith("<"):
            msg.set_content("HTML message forwarded, open in HTML view.")
            msg.add_alternative(mail["body"], subtype='html')
        else:
            msg.set_content(mail["body"])

        with smtplib.SMTP('localhost') as smtp:
            smtp.send_message(msg)

        for fname in os.listdir(inbox_dir):
            os.remove(os.path.join(inbox_dir, fname))
        session.clear()

        return '''
        <!DOCTYPE html>
        <html>
        <head><meta charset="UTF-8"><title>Forwarded</title>
        <script>
        setTimeout(function(){ window.location.href = "/index.html"; }, 2000);
        </script></head>
        <body style="font-family: sans-serif; text-align: center; padding: 2em;">
        <h2>Mail forwarded successfully.</h2>
        <p>This temporary address has been deleted.</p>
        </body></html>
        '''

    except Exception as e:
        print(f"❌ Fehler beim Weiterleiten: {e}")
        flash(f"Forwarding failed: {str(e)}", "error")
        return redirect(url_for('index'))

@app.route('/faq')
def faq():
    if 'email_id' not in session or check_alias_expiration():
        reset_email_session()

    if 'client_id' not in session:
        raw = f"{request.remote_addr}-{time.time()}"
        session['client_id'] = hashlib.sha256(raw.encode()).hexdigest()[:16]

    if GA_MEASUREMENT_ID and GA_API_SECRET:
        send_ga4_pageview(request, session['client_id'])



    return render_template('faq.html')


if __name__ == '__main__':
    ensure_stats_file()
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
