from flask_security import SQLAlchemyUserDatastore
from application.models import db, User, Role

datastore = SQLAlchemyUserDatastore(db, User, Role)