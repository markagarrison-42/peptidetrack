#!/usr/bin/env python3
"""
Always-on task for PythonAnywhere.
Checks for due dose reminders every 5 minutes and sends push notifications.
"""
import sys
import os
import time

sys.path.insert(0, '/home/madfella/peptidetrack')

# Load env vars from WSGI file
wsgi_path = '/var/www/protocol_mg42apps_com_wsgi.py'
with open(wsgi_path) as f:
    for line in f:
        line = line.strip()
        if line.startswith("os.environ['"):
            key = line.split("'")[1]
            val = line.split("'")[3]
            os.environ[key] = val

from app import create_app
app = create_app()

print("Dose reminder service started", flush=True)

while True:
    try:
        with app.app_context():
            from routes.push import send_dose_reminders
            sent = send_dose_reminders()
            if sent > 0:
                print(f"Reminders sent: {sent}", flush=True)
    except Exception as e:
        print(f"Error: {e}", flush=True)

    time.sleep(300)  # wait 5 minutes
