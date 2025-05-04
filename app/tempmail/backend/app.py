from flask import Flask, render_template, session, redirect, url_for
from flask_socketio import SocketIO
from flask import send_from_directory
import os, json, uuid
import time, random, string
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'super-secret-key'
socketio = SocketIO(app)

# Speicherort für empfangene Mails
EMAIL_DIR = "/var/tempmail/mails"
TIMER_DURATION = 300  # 2 Minuten in Sekunden
ALIAS_LIFETIME = timedelta(minutes=5)

def generate_email():
    return ''.join(random.choices(string.ascii_lowercase, k=5))

def check_alias_expiration():
    # Überprüfen, ob der Alias abgelaufen ist
    if 'email_created_at' in session:
        created_at = datetime.fromtimestamp(session['email_created_at'])
        if datetime.now() - created_at > ALIAS_LIFETIME:
            # Alias ist abgelaufen, neuen Alias generieren
            return True
    return False

@app.route('/email/<email_id>/<filename>')
def view_email(email_id, filename):
    inbox_dir = os.path.join(EMAIL_DIR, email_id)
    file_path = os.path.join(inbox_dir, filename)

    if not os.path.exists(file_path):
        abort(404)

    with open(file_path) as f:
        mail = json.load(f)

    return render_template('email_view.html', mail=mail)

@app.route('/')
def index():
    # Überprüfen, ob der Alias abgelaufen ist
    if 'email_id' not in session or check_alias_expiration():
        # Wenn abgelaufen, E-Mails löschen und Session zurücksetzen
        if 'email_id' in session:
            inbox_dir = os.path.join(EMAIL_DIR, session['email_id'])
            if os.path.exists(inbox_dir):
                for fname in os.listdir(inbox_dir):
                    os.remove(os.path.join(inbox_dir, fname))
        session.clear()
        session['email_id'] = generate_email()
        session['email_created_at'] = time.time()

    email_id = session['email_id']
    inbox_dir = os.path.join(EMAIL_DIR, email_id)
    emails = []

    if os.path.exists(inbox_dir):
        for fname in sorted(os.listdir(inbox_dir), reverse=True):
            fpath = os.path.join(inbox_dir, fname)
            with open(fpath) as f:
                mail = json.load(f)
                mail['filename'] = fname  # ← Das ist entscheidend für den Link
                emails.append(mail)

    # Berechne die verbleibende Zeit
    remaining_time = ALIAS_LIFETIME - (datetime.now() - datetime.fromtimestamp(session['email_created_at']))
    remaining_minutes, remaining_seconds = divmod(int(remaining_time.total_seconds()), 60)

    if remaining_minutes < 0:
        remaining_minutes = 0
        remaining_seconds = 0

    # Verbleibende Zeit in der Session speichern
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
        # Alle E-Mails löschen
        for fname in os.listdir(inbox_dir):
            os.remove(os.path.join(inbox_dir, fname))
    return redirect(url_for('index'))


@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('static/meta', 'sitemap.xml')

@app.route('/robots.txt')
def robots():
    return send_from_directory('static/meta', 'robots.txt')


@app.route('/why-temp-email')
def why_temp_email():
    return render_template('why-temp-email.html')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

