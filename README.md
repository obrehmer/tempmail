# TempMail – Disposable Email Address Service

👉 **Check it out at [https://tempmail.olifani.eu/](https://tempmail.olifani.eu/)!**

TempMail is a disposable, temporary email inbox service designed for spam protection and anonymous sign-ups. The entire setup is fully automated using Ansible and deploys the application on an Ubuntu 24 server.

---

## Features

- Temporary email addresses valid for **5 minutes** by default  
- Replying to emails is supported, but only as a direct response to incoming messages.
- Manual **"Reload" button** to instantly generate a new email alias, invalidating the old one  
- Expired aliases are automatically **blacklisted in Postfix** to prevent reuse  
- **No outgoing mail** — receive-only service  
- Real-time inbox updates via **WebSocket**  
- Retro frontend with user-friendly UI, including:  
  - **Copy to Clipboard** button for email addresses  
  - **Reload** button to generate new aliases instantly  
- Stats view protected with **HTTP Basic Auth**  
- Self-hosted with minimal footprint and simple setup  
- Ansible-managed configuration for Apache and Postfix, including:  
  - **Anonymized logging** for enhanced privacy  
  - Apache logs redirected to `/dev/null` for minimal data retention  
- ModSecurity 2 is enabled as a Web Application Firewall (WAF) to secure the service against common web attacks.


---

## Requirements

- Ubuntu 24.04 LTS server  
- DNS A record pointing to your server  
- MX record configured to receive emails on the chosen domain  
- Recommended: Cloudflare for DNS management and SSL termination  
- Ansible installed locally for deployment  
- Public IP and domain name properly configured  

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


## Security Considerations

Emails and aliases expire after 5 minutes — no long-term storage

All aliases are randomized and stored in user sessions only

HTTPS recommended via Cloudflare or Let's Encrypt for secure communication

Backend files and directories are write-protected from public users

Logging for Apache and Postfix is anonymized and minimized to protect privacy
