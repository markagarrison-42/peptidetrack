from app import application
from extensions import db
from models import User
from werkzeug.security import generate_password_hash

with application.app_context():
    db.create_all()
    if User.query.filter_by(role='practitioner').count() > 0:
        print('Practitioner already exists')
    else:
        user = User(
            username='madfella',
            email='mark.a.garrison@gmail.com',
            password_hash=generate_password_hash('qeskAk-wixfow-hajko3'),
            role='practitioner',
        )
        db.session.add(user)
        db.session.commit()
        print('Practitioner created:', user.username, user.role)
