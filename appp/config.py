import os
class Config():
    SECRET_KEY='secretKey12345' #for development purpose only
    SQLALCHEMY_DATABASE_URI='sqlite:///site.db' #for development purpose only
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'example@gmail.com' #enter gmail id
    MAIL_PASSWORD = 'yourPassword' #enter gmail password
