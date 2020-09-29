import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from authlib.integrations.flask_client import OAuth
from appp.config import Config


app=Flask(__name__)
app.config.from_object(Config)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db= SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt= Bcrypt(app)
oauth= OAuth(app)
login_manager= LoginManager(app)
login_manager.login_view= 'login'
login_manager.login_message_category = 'info'

mail = Mail(app)


G = oauth.register(
    name='google',
    client_id=os.environ.get('CLIENT_ID'),
    client_secret=os.environ.get('CLIENT_SECRET'),
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'},
)

from appp import routes
