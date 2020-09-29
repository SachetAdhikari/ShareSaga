from appp import app
class Config():
    app.config['SECRET_KEY']= '138a79505fa3993f6a50dce42f55bd7de4b7ecb1'
    app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///site.db'
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = '#' #os.environ.get('EMAIL_USER')
    app.config['MAIL_PASSWORD'] = '#' #os.environ.get('EMAIL_PASS')