import json
import os
from datetime import datetime, timedelta

ACTIVE_ALIASES_FILE = "/var/tempmail/misc/active_aliases.json"
REJECT_RECIPIENTS_FILE = "/etc/postfix/reject_recipients"
ALIAS_LIFETIME = timedelta(minutes=5)

def update_reject_recipients():
    try:
        with open(ACTIVE_ALIASES_FILE, "r") as f:
            active_aliases = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        active_aliases = {}

    updated_aliases = {}
    new_rejections = []

    for alias, created_at_str in active_aliases.items():
        created_at = datetime.fromisoformat(created_at_str)
        if datetime.utcnow() - created_at > ALIAS_LIFETIME:
            new_rejections.append(f"{alias}@inboxcl.xyz REJECT")
        else:
            updated_aliases[alias] = created_at_str

    if new_rejections:
        try:
            with open(REJECT_RECIPIENTS_FILE, "a") as f:
                for line in new_rejections:
                    f.write(line + "\n")
            os.system(f"postmap {REJECT_RECIPIENTS_FILE}")
            os.system("systemctl reload postfix")
        except Exception as e:
            print(f"Error updating reject_recipients: {e}")

    with open(ACTIVE_ALIASES_FILE, "w") as f:
        json.dump(updated_aliases, f)

if __name__ == "__main__":
    update_reject_recipients()

