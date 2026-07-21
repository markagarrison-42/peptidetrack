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
    from pywebpush import webpush, WebPushException
    import json

    subs = PushSubscription.query.all()
    print(f'Found {len(subs)} subscriptions')

    vapid_private = os.environ.get('VAPID_PRIVATE_KEY', '')
    vapid_email   = os.environ.get('VAPID_EMAIL', '')
    print(f'VAPID private key length: {len(vapid_private)}')
    print(f'VAPID email: {vapid_email}')

    for sub in subs:
        print(f'\nSending to endpoint: {sub.endpoint[:60]}')
        try:
            webpush(
                subscription_info={
                    'endpoint': sub.endpoint,
                    'keys': {
                        'p256dh': sub.p256dh,
                        'auth':   sub.auth,
                    },
                },
                data=json.dumps({'title': 'Test', 'body': 'Test notification', 'url': '/'}),
                vapid_private_key=vapid_private,
                vapid_claims={'sub': vapid_email},
            )
            print('SUCCESS')
        except WebPushException as e:
            print(f'WebPushException: {e}')
            if e.response:
                print(f'Response status: {e.response.status_code}')
                print(f'Response body: {e.response.text[:200]}')
        except Exception as e:
            print(f'Exception: {type(e).__name__}: {e}')
