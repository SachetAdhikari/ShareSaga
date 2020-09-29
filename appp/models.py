from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from appp import db, login_manager,app
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    vregno = db.Column(db.String(9), unique=True, nullable=False)
    batch = db.Column(db.String(100), nullable=False)
    image_file = db.Column(db.String(100), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts= db.relationship('Post',backref='author', lazy=True)
    cse= db.relationship('Resources',backref='author', lazy=True)
    comments= db.relationship('Comment',backref='author', lazy=True)
    
    def get_reset_token(self, expires_sec=900):
        s= Serializer(app.config['SECRET_KEY'],expires_sec)
        return s.dumps({'user_id':self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s= Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Users.query.get(user_id)

    def __repr__(self):
        return f"Users('{self.fullname}','{self.email}','{self.vregno}','{self.image_file}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False)
    comments = db.relationship('Comment',backref='post', lazy=True)

    def __repr__(self):
        return f"Post('{self.title}','{self.date_posted}')"

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'),nullable=False)
    def __repr__(self):
        return f"Comment('{self.content}','{self.date_posted}')"


class Resources(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    batch = db.Column(db.String(100), nullable=False)
    course = db.Column(db.String(100), nullable=False)
    topic = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    resource_file_path = db.Column(db.String(100), nullable=False)
    resource_file_name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),nullable=False)

    def __repr__(self):
        return f"Resource('{self.course}','{self.topic}','{self.date_posted}','{self.user_id}')"


class Courses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course = db.Column(db.String(100), nullable=False)
    batch = db.Column(db.String(100), nullable=False)
    faculty_name=db.Column(db.String(100), nullable=False)
    faculty_pic=db.Column(db.String(100), nullable=False, default='default.jpg')

    def __repr__(self):
        return f"Courses('{self.course}','{self.batch}','{self.faculty_name}','{self.faculty_pic}')"



class BatchChoices(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    batch = db.Column(db.String(100),nullable=False)

    def __repr__(self):
        return f"BatchChoices('{self.batch}')"
