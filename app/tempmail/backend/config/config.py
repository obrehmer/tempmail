from datetime import timedelta
GA_CONFIG_PATH = "/var/tempmail/misc/config_ga4.json"
APP_SECRET = "/var/tempmail/misc/app.secret.json"
EMAIL_DIR = "/var/tempmail/mails"
ALIAS_LIFETIME = timedelta(minutes=5)
TARGET_USER = "www-data"
STATS_FILE = "/var/tempmail/misc/stats.json"
ACTIVE_ALIASES_FILE = "/var/tempmail/misc/active_aliases.json"

class CookieConfig:
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
