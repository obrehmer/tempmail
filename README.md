# tempmail.olifani.eu

**tempmail.olifani.eu** ist ein temporärer E-Mail-Dienst zur anonymen Registrierung und zum Schutz vor Spam. Die E-Mail-Adressen sind kurzlebig und werden nach wenigen Minuten automatisch gelöscht.

## 🚀 Features

- Temporäre, zufällig generierte E-Mail-Adressen
- Empfang von E-Mails in Echtzeit (via Socket.IO)
- Automatische Löschung nach Ablaufzeit
- Willkommensnachricht in jedem neuen Postfach
- Passwortgeschützte Statistik-Seite
- Eigene Fehlerseiten (404 & 500)

## 🔒 Sicherheit

- Zugriff auf `/stats` durch `.htpasswd` geschützt
- Sitzungsspeicherung auf Basis von Flask-Session
- Keine E-Mail-Versendung – nur Empfang möglich

## ⚙️ Installation (via Ansible)

Das Projekt beinhaltet ein Ansible-Playbook (`install.yml`), das folgende Aufgaben übernimmt:

- Apache-Konfiguration inkl. Fehlerseiten
- Setup von `.htpasswd`
- Deployment der Webanwendung
- Automatischer Neustart von Apache bei Änderungen

## 🧪 Entwicklung & Tests

Start der App lokal:

```bash
python3 app.py

