from flask import Flask
from flask_cors import CORS
from flask_security import  Security
from config import DevelopmentConfig
from werkzeug.security import generate_password_hash
from application.models import db, Admin
from application.sec import datastore
from flask_mail import Mail

mail = Mail()
    
def create_app():
    app = Flask(__name__)
    CORS(app) 
    app.config.from_object(DevelopmentConfig)
    app.security = Security(app, datastore)
    from application.views import api, cache
    db.init_app(app)
    cache.init_app(app)
    mail.init_app(app) 
    
    app.register_blueprint(api)

    with app.app_context():
        db.create_all()

        # Create roles if they don't exist
        datastore.find_or_create_role(name='admin', description='This is admin!')
        datastore.find_or_create_role(name='influencer', description='This is influencer!')
        datastore.find_or_create_role(name='sponsor', description='This is sponsor!')
        db.session.commit()

        # Create an admin user if not already present
        if not datastore.find_user(email="admin@gmail.com"):
            admin = Admin(
                email='admin@gmail.com',
                password=generate_password_hash('admin'),
                name="admin",
                user_id=1
            )
            datastore.create_user(
                name="admin",
                email="admin@gmail.com",
                password=generate_password_hash("admin"),
                roles=['admin'],
                fs_uniquifier = "1st"
                
            )
            db.session.add(admin)
            db.session.commit()
    return app

app = create_app()



if __name__ == '__main__':
    app.run(debug=True)