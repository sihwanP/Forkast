# Forkast Deployment Guide (AWS Lightsail)

This guide helps you deploy the Forkast Django application to your AWS Lightsail instance.

## Prerequisites
- SSH Access to your Lightsail instance (`13.125.161.160`)
- Key file: `C:/jobproject/Key/Multi_bitnami_Key.pem`

## 1. Transfer Project Files
You need to copy the `c:\dev\Forkast` directory to your server.
Use `scp` or FileZilla.

```bash
# Example SCP command (run from your local machine)
scp -i "C:/jobproject/Key/Multi_bitnami_Key.pem" -r c:/dev/Forkast bitnami@13.125.161.160:/home/bitnami/
```

## 2. Server Setup (On Remote Server)
SSH into your server:
```bash
ssh -i "C:/jobproject/Key/Multi_bitnami_Key.pem" bitnami@13.125.161.160
```

Once inside:

### Install Python Dependencies
```bash
cd /home/bitnami/Forkast
python3 -m venv venv
source venv/bin/activate
pip install django
```

### Run Migrations
```bash
python manage.py makemigrations platform_ui
python manage.py migrate
```

### Collect Static Files (Optional for dev, required for proper prod)
```bash
python manage.py collectstatic
```

### Create Superuser (Admin)
```bash
python manage.py createsuperuser
```

## 3. Run Server (Local Testing)
For testing locally on Windows:
```powershell
# If 'python' doesn't work, try 'py'
py manage.py runserver
```
Then visit: `http://127.0.0.1:8000`

## 4. Run Server (AWS Lightsail)
On your Lightsail instance:
```bash
python3 manage.py runserver 0.0.0.0:8000
```
Then visit: `http://13.125.161.160:8000`

## 4. Production
For production, configure Apache/Nginx to serve the app.
