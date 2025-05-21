# Changelog

All notable changes to this project will be documented in this file.

---

## [v1.7.2] - 2025-05-21

### Changed

- Some fixes and optimizations in ansible`s install.yaml
- email view in email_view.html changed to HTML

## [v1.7.0] - 2025-05-20

### Added

- A new function ‘reply mail’ has been added, very rudimentary. You can reply to emails you have entered.

## [v1.6.0] - 2025-05-17

### Added
- ✨ Fully redesigned `index.html`, `email_view.html`, `why-temp-email.html`, and `stats.html` with a modern-retro aesthetic and enhanced usability.
- 📬 Dismissible top banner linking to [ai.olifani.eu](https://ai.olifani.eu), stored in session memory when closed.
- ⏳ Visual progress bar below the email address indicating the remaining validity time (5 minutes).
- 📜 `robots.txt` updated to exclude `/stats.html` from search engine indexing.
- 🧪 `modern-retro.css` applied globally across all views.

### Changed
- 🧼 Moved inline JavaScript from `index.html` to external `timer.js` file.
- 🧭 Improved HTML semantics, accessibility, and SEO meta structure across all pages.
- 🧠 Open Graph and Twitter metadata refined for better social sharing previews.

---

## [v1.5.0] - 2025-05-14

### Added
- "Reload" button on the index page to manually generate a new temporary email address.
- Previous alias immediately invalidated and treated as expired.
- Expired aliases automatically added to `/etc/postfix/reject_recipients` to block reuse.
- Automatic Postfix reload after updating the reject recipients file.

### Changed
- Alias lifetime resets upon manual reload.

### Security
- Improved alias management and mail filtering by blacklisting expired aliases.

---

## [v1.4.0] - 2025-05-14

### Added
- Ansible tasks to fully anonymize Apache and Postfix logs.
- Redirect Apache `access.log` and `error.log` to `/dev/null`.
- Postfix logging now omits sender, recipient, and message details for enhanced privacy.

### Changed
- Logging behavior aligned with strict data minimization principles.
- Apache and Postfix configurations are now automatically managed via Ansible.

### Notes
- Remember to reload Apache and Postfix after applying new configurations.

---

## [v1.3.1] - 2025-05-14

### Added
- Ansible roles/tasks for anonymous Postfix logging.
- Suppression of detailed mail logging (sender, recipient, etc.).
- Configuration of Postfix `header_checks` to discard headers from logs.
- Optional integration with `rsyslog` to mute Postfix log entries completely.

### Changed
- Postfix configuration updated to enhance privacy.
- `install.yaml` updated to include new logging steps.

### Notes
- Intended for privacy-focused or disposable email deployments.
- See [GitHub Repo](https://github.com/obrehmer/tempmail) for implementation details.

---

## [v1.3.0] - 2025-05-13

### Added
- Clipboard copy feature for temporary email addresses:
  - "📋 Copy" button added next to the email display.
  - Clicking the button copies the email address with visual success feedback.
  - Styled to fit the existing retro-mac theme.

### Changed
- Minor HTML adjustments, including adding an ID to the email display element.

---

## [v1.2.0] - 2025-05-13

### Added
- Added `ads.txt` file and route in `app.py`.
- Support for Google Adsense registration.

---

## [v1.1.1] - 2025-05-12

### Changed
- Postfix `main.cf`:
  - Set `mydestination` to `$myhostname, localhost.localdomain, localhost` for correct local delivery.
  - Configured `virtual_alias_maps` with regex map at `/etc/postfix/virtual`.
- Postfix `master.cf`:
  - Hardened SMTP service with:
    - Limits on simultaneous client connections.
    - Rate limiting per client.
    - Introduced error delay to reduce abuse.

### Security
- Improved mail server security via stricter client limits and dynamic alias blocking.

---

## [v1.1.0] - 2025-05-12

### Added
- Automatic Postfix blocking of expired aliases (5-minute expiration).
- Introduced `expired_aliases.json` for tracking expired aliases.
- New cron-compatible cleanup script `expire_aliases.py` to handle expiration and Postfix blocklist updates.

### Changed
- `app.py` appends generated aliases to a tracking file for expiration management.

### Notes
- Requires Postfix configured with `reject_recipients`.
- Cronjob for refreshing reject recipients included in Ansible `install.yaml`.

---

## [v1.0.0] - 2025-05-10

### Initial Release

- 🚀 Minimal temporary email web server launched.
- 📨 On-the-fly generated email aliases expire after 5 minutes.
- 🖥️ Flask backend with WebSocket support (Flask-SocketIO).
- 📥 Received emails stored as JSON under `/var/tempmail/mails/<alias>/`.
- 🧾 Apache reverse proxy setup for frontend and socket routing.
- 🔒 Stats page protected with HTTP Basic Auth.
- 🔐 IP whitelisting via iptables for Cloudflare origin traffic.
- 📊 Daily alias creation stats stored in `stats.json`.
- 🧹 Cron job for daily cleanup of expired email files.

