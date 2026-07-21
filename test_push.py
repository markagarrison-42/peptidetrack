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
    
    subs = PushSubscription.query.all()
    print(f'Found {len(subs)} subscriptions')
    for sub in subs:
        print(f'Sending to user {sub.user_id}...')
        result = send_push(sub, 'Test', 'This is a test notification from PeptideTrack', '/')
        print(f'Result: {result}')
