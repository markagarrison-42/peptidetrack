import sys, os
sys.path.insert(0, '/home/madfella/peptidetrack')
with open('/var/www/protocol_mg42apps_com_wsgi.py') as f:
    for line in f:
        line = line.strip()
        if line.startswith("os.environ["):
            try: exec(line)
            except: pass

from app import create_app
app = create_app()
with app.app_context():
    from models import PushSubscription
    from routes.push import send_push

    # Send to islagarrison (user_id 17)
    subs = PushSubscription.query.filter_by(user_id=17).all()
    print(f'Subscriptions for islagarrison: {len(subs)}')
    for sub in subs:
        result = send_push(sub, 'PeptideTrack Test', 'Notifications are working!', '/')
        print(f'Result: {result}')
