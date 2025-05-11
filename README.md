# TempMail – Disposable Email Address Service

TempMail is a disposable, temporary email inbox service for spam protection and anonymous sign-ups. This setup is fully automated via Ansible and deploys the application on an Ubuntu 24 server.

---

## Features

- Temporary email addresses valid for 5 minutes
- No outgoing mail (receive only)
- WebSocket updates for real-time inbox changes
- Retro MacOS-style frontend
- Stats view protected with Basic Auth
- Self-hosted, minimal footprint and simple setup

---

## Requirements

- Ubuntu 24.04 LTS server
- DNS A record pointing to the server
- MX record for receiving emails
- Recommended: Cloudflare for DNS and SSL
- Ansible installed locally
- Public IP and domain name configured

---

## Installation

### 1. Clone this Repository

```bash
git clone https://github.com/obrehmer/tempmail.git
cd tempmail/ansible
```

### 2. Adjust Ansible Variables

Edit all relevant tasks and variables in  install.yml 

```
server_name: tempmail.yourdomain.com
htpasswd_user: youradmin
...

```



### 3. Vault Password Setup

Store your Basic Auth password in vault_htpasswd_password.vault:

```
ansible-vault create vault_htpasswd_password.vault
```

htpasswd_password: your_secure_password

Store your ssh public in authorized_keys.vault



### 4. Run the Ansible Playbook

```
Ansible-playbook -i inventory install.yml --ask-vault-pass
```

### 5. Copy the app

Copy the app from /app to /var/www/tempmail on your server

### 6. Start the Flask Application

After installation, start the service via systemd:

systemctl start tempmail


## DNS Setup

Ensure your domain DNS configuration includes:

    A record pointing tempmail.yourdomain.com to your server's public IP

    MX record pointing inboxcl.xyz (or your chosen domain) to the same IP

Using Cloudflare is recommended for managing DNS and enabling HTTPS.

## Project Structure

/var/www/tempmail/	Deployed Flask application
/var/tempmail/mails/	Temporary inbox mail storage
/var/tempmail/misc/stats.json	Daily address creation statistics
/etc/apache2/sites-available/	Apache virtual host config
/var/www/.htpasswd	Basic Auth credentials for /stats

Stats Protection

The /stats endpoint is protected using Basic Auth. The credentials are defined via Ansible:

    htpasswd_user – in Ansible variables

    htpasswd_password – stored securely in vault_htpasswd_password.vault

This protects the statistics page from unauthorized access.
Custom Error Pages

Custom 404.html and 500.html templates are used to ensure consistent UX even during application errors.
Troubleshooting

    Ensure ports 80, 25, and optionally 443 are open

    Check logs with: journalctl -u tempmail

    Validate Apache configuration: apache2ctl configtest

    If /stats fails, check that /var/tempmail/misc/stats.json exists and is writable

## Security Considerations

    Emails are deleted after 5 minutes — no long-term storage

    All aliases are randomized and stored in the session only

    HTTPS via Cloudflare or Let's Encrypt is recommended

    Backend is write-protected from public users
