# Changelog

## [v1.1.0] - 2025-05-12

### Added
- 🛡️ Temporary email aliases are now automatically blocked in Postfix after expiration (5 minutes).
- 📦 Introduced `expired_aliases.json` to persist and track expired aliases.
- ⚙️ New cron-compatible cleanup script (`expire_aliases.py`) added to handle:
  - Alias expiration logic.
  - Updating Postfix recipient blocklist.
  - Reloading Postfix configuration.

### Changed
- 🧠 `app.py` now appends each generated alias to a tracking file for future expiration handling.

### Notes
- Requires Postfix to be configured with reject_recipients, added to ansible install.yaml
- Requieres a cronjob to refresh the reject_recipients, also added to ansible install.yaml

## [v1.0.0] - 2025-05-10

### Initial Release

- 🚀 Launch of the minimal temporary email web server.
- 📨 Email aliases are generated on-the-fly via the web interface and expire after 5 minutes.
- 🖥️ Flask-based backend with WebSocket support using Flask-SocketIO.
- 📥 Received emails stored as JSON files under `/var/tempmail/mails/<alias>/`.
- 🧾 Apache reverse proxy configured to serve the frontend and route socket traffic.
- 🔒 Stats page protected with HTTP Basic Auth.
- 🔐 IP whitelisting via iptables for Cloudflare origin traffic.
- 📊 Daily alias creation statistics stored in `stats.json`.
- 🧹 Cron job for daily cleanup of expired email files.
