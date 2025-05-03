#!/usr/bin/env python3
import os
import sys
import email
import json
import time
from pathlib import Path
import pwd
import grp

EMAIL_STORAGE_BASE = "/var/www/tempmail/backend/emails"
TARGET_USER = "www-data"
LOG_FILE = "/var/log/receive_mail.log"

def log(msg):
    try:
        with open(LOG_FILE, "a") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception as e:
        print(f"Logfehler: {e}", file=sys.stderr)

def sanitize(s):
    return ''.join(c for c in s if c.isalnum() or c in ('@', '.', '-', '_'))

def extract_email_id(to_address):
    # z. B. aus xyz123@olifani.eu -> xyz123
    return to_address.split('@')[0]

def set_ownership(path, user):
    try:
        pw_record = pwd.getpwnam(user)
        uid = pw_record.pw_uid
        gid = pw_record.pw_gid
        os.chown(path, uid, gid)
    except Exception as e:
        log(f"Berechtigungsfehler für {path}: {e}")

def main():
    raw_email = sys.stdin.read()
    msg = email.message_from_string(raw_email)

    to_address = msg['To']
    from_address = msg['From']
    subject = msg['Subject'] or "(kein Betreff)"
    email_id = extract_email_id(to_address)

    # E-Mail Body extrahieren (nur Textteil)
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                body = part.get_payload(decode=True).decode(errors="replace")
                break
    else:
        body = msg.get_payload(decode=True).decode(errors="replace")

    # Zielverzeichnis
    inbox_dir = Path(EMAIL_STORAGE_BASE) / email_id
    inbox_dir.mkdir(parents=True, exist_ok=True)
    set_ownership(inbox_dir, TARGET_USER)

    # Zeitstempel
    timestamp = int(time.time())
    filename = inbox_dir / f"{timestamp}.json"

    with open(filename, "w") as f:
        json.dump({
            "from": from_address,
            "to": to_address,
            "subject": subject,
            "body": body.strip()
        }, f, ensure_ascii=False, indent=2)

    set_ownership(filename, TARGET_USER)
    log(f"E-Mail für {to_address} gespeichert unter {filename}")

if __name__ == "__main__":
    main()

