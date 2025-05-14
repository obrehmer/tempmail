# Changelog

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

## [v1.1.1] - 2025-05-12
### Changed
- **Postfix `main.cf`**:
  - Set `mydestination` to `$myhostname, localhost.localdomain, localhost` to ensure correct local delivery.
  - Configured `virtual_alias_maps` to use `regexp:/etc/postfix/virtual` for regex-based alias routing.

- **Postfix `master.cf`**:
  - Hardened SMTP service with:
    - Maximum simultaneous connections per client limited (`smtpd_client_connection_count_limit=10`).
    - Connection rate per client throttled (`smtpd_client_connection_rate_limit=30`).
    - Error delay introduced (`smtpd_error_sleep_time=1s`) to discourage abuse.

### Security
- Improved mail server security through stricter client limits and dynamic email alias blocking.


## [v1.2.0] - 2025-05-13
### Added
- Added ads.txt and route in app.py
- ads.txt is necessary for registration with Google Adsense 

## [v1.3.0] - 2025-05-13

### Added
- ✨ New "Copy to Clipboard" feature for temporary email addresses.
  - A "📋 Copy" button was added below the displayed email.
  - Clicking the button copies the email address to the clipboard.
  - A success indicator (✅ Copied) briefly replaces the button label after clicking.
  - Fully styled to match the existing retro-mac theme.

### Changed
- Minor adjustments in HTML to support the feature, including assigning a proper ID to the email display element.

## [v1.3.1] - 2025-05-14
### Added
- Ansible role/tasks to enable anonymous Postfix logging.
- Suppresses logging of sender, recipient, and full mail details.
- Configures `header_checks` to discard headers from being logged.
- Optional integration with `rsyslog` to mute Postfix log entries completely.

### Changed
- Postfix configuration updated for enhanced privacy.
- `install.yaml` updated to include new logging configuration steps.

### Notes
- This change is intended for privacy-focused deployments (e.g. disposable or anonymous email services).
- See [GitHub Repo](https://github.com/obrehmer/tempmail) for implementation details.

## [v1.4.0] - 2025-05-14

### Added
- Ansible tasks to fully anonymize logging for Apache and Postfix.
- New configuration to redirect Apache `access.log` and `error.log` to `/dev/null`.
- Postfix logging stripped of sender, recipient, and message details for privacy.

### Changed
- Default behavior of logging now aligns with strict data minimization principles.
- Apache and Postfix configurations are now automatically managed via Ansible.

### Notes
- This update is especially useful for privacy-focused or temporary services (e.g., tempmail).
- Make sure to reload Apache and Postfix after applying the new configuration.

