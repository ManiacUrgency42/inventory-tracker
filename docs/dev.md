---
layout: default
title: Developer Guide
permalink: /dev/
---

# Developer & Maintainer Guide

---

## Architecture

```mermaid
graph TD
    subgraph Input
        A1[USB Barcode Scanner]
        A2[Manual keyboard entry]
    end

    subgraph Pi ["Raspberry Pi (self-hosted)"]
        B[FastAPI app\nuvicorn on port 8080]
        C[PostgreSQL\ninventory DB]
        D[cloudflared\nCloudflare Tunnel daemon]
    end

    subgraph Cloud
        E[Cloudflare Edge]
        F[inventory.yourdomain.com]
    end

    G[(Neon\nweekly backup)]

    A1 & A2 -->|barcode + Enter| B
    B <-->|SQL queries| C
    B --> D
    D --> E --> F
    C -->|pg_dump every Sunday 2am| G
```

---

## File Structure

```
inventory-tracker/
├── app.py              # All route logic
├── database.py         # PostgreSQL connection + schema init
├── seed.py             # Populate sample data (run once)
├── requirements.txt
├── .env                # DATABASE_URL (not committed)
├── .env.example        # Template for .env
├── .gitignore
├── docs/
│   ├── user.md         # User guide  → /docs/user
│   ├── dev.md          # This file   → /docs/dev
│   └── data.md         # Data ref    → /docs/data
└── templates/
    ├── index.html      # Scanner input page
    ├── item.html       # Item display / not-found
    ├── admin.html      # Admin panel
    ├── admin_edit.html # Edit item form
    ├── docs_index.html # Docs landing page
    └── docs_page.html  # Shared docs wrapper
```

---

## Routes

| Method | Path                  | Description                        |
|--------|-----------------------|------------------------------------|
| GET    | `/`                   | Scanner input page                 |
| POST   | `/scan`               | Receive barcode, redirect to item  |
| GET    | `/item/{barcode}`     | Display item info                  |
| GET    | `/admin`              | List all items, search             |
| POST   | `/admin/add`          | Insert new item                    |
| GET    | `/admin/edit/{id}`    | Edit form for an item              |
| POST   | `/admin/edit/{id}`    | Update item                        |
| POST   | `/admin/delete/{id}`  | Delete item                        |
| GET    | `/docs`               | Docs landing page                  |
| GET    | `/docs/{section}`     | user / dev / data                  |

---

## Dependencies

| Package          | Purpose                          |
|------------------|----------------------------------|
| fastapi          | Web framework + routing          |
| uvicorn          | ASGI server                      |
| jinja2           | HTML templating                  |
| python-multipart | Parsing HTML form POST bodies    |
| markdown         | Rendering `.md` files to HTML    |
| psycopg2-binary  | PostgreSQL driver                |
| python-dotenv    | Load `.env` for local dev        |

---

## Raspberry Pi Setup

### 1. Flash the OS

Use Raspberry Pi Imager on your Mac. Flash **Raspberry Pi OS Lite (64-bit)**. In settings before writing:
- Hostname: `inventory`
- Enable SSH
- Set username/password
- Configure WiFi

Insert SD card into Pi and power on. SSH in from your Mac:

```bash
ssh pi@inventory.local
```

### 2. Install PostgreSQL

```bash
sudo apt update && sudo apt install -y postgresql postgresql-contrib
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

Create the DB and user:

```bash
sudo -u postgres psql <<EOF
CREATE USER inventory WITH PASSWORD 'yourpassword';
CREATE DATABASE inventory OWNER inventory;
EOF
```

### 3. Clone and run the app

```bash
sudo apt install -y python3-pip python3-venv git
git clone https://<PAT>@github.com/maniacurgency42/inventory-tracker.git
cd inventory-tracker
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
echo "DATABASE_URL=postgresql://inventory:yourpassword@localhost:5432/inventory" > .env
python seed.py
```

### 4. Run as a systemd service (always on)

```bash
sudo nano /etc/systemd/system/inventory.service
```

```ini
[Unit]
Description=Inventory Tracker
After=network.target postgresql.service

[Service]
User=pi
WorkingDirectory=/home/pi/inventory-tracker
EnvironmentFile=/home/pi/inventory-tracker/.env
ExecStart=/home/pi/inventory-tracker/.venv/bin/uvicorn app:app --host "::" --port 8080
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable inventory
sudo systemctl start inventory
```

### 5. Cloudflare Tunnel (global access)

```bash
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64.deb -o cloudflared.deb
sudo dpkg -i cloudflared.deb

cloudflared tunnel login        # opens a browser link — authenticate on your Mac
cloudflared tunnel create inventory
cloudflared tunnel route dns inventory inventory.yourdomain.com
sudo cloudflared service install
```

App is now live at `https://inventory.yourdomain.com`.

### 6. Weekly backup cron

```bash
mkdir -p /home/pi/backups
crontab -e
```

Add:

```
0 2 * * 0  pg_dump postgresql://inventory:yourpassword@localhost:5432/inventory > /home/pi/backups/inventory-$(date +\%Y\%m\%d).sql
```

Runs every Sunday at 2am. Copy dumps to Neon or cloud storage for off-Pi backup.

---

## Deploying Updates

When you push changes to GitHub, pull them on the Pi and restart:

```bash
ssh pi@inventory.local
cd inventory-tracker
git pull
sudo systemctl restart inventory
```

---

## Local Development (Mac)

For dev on your Mac, point `DATABASE_URL` at a local Postgres instance or a Neon dev branch:

```bash
cp .env.example .env
# edit .env with your local DB URL
source .venv/bin/activate
uvicorn app:app --host "::" --port 8080 --reload
```

---

## Adding a New Field

1. Add the column in `database.py` inside `init_db()`
2. Add the field to the `INSERT` and `UPDATE` queries in `app.py`
3. Add the input to `templates/admin.html` and `templates/admin_edit.html`
4. Add the field to `templates/item.html` for display

For the existing Pi database, run the migration over SSH:

```bash
sudo -u postgres psql inventory -c "ALTER TABLE items ADD COLUMN new_field TEXT;"
```
