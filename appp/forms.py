from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from appp.models import Users, Post, BatchChoices

class RegistrationForm(FlaskForm):
    batch= SelectField('Batch',choices=[(g.batch,g.batch) for g in BatchChoices.query.order_by('batch')],validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(),Length(min=8, max=16)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    vregno = StringField('VIT Registration No',
                        validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg','jpeg', 'png'])])
    submit = SubmitField('Update')


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

class CommentForm(FlaskForm):
    content = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Post')


class ContributeResourcesForm(FlaskForm):
    topic = StringField('Topic',
                        validators=[DataRequired()])
    files = FileField('', validators=[FileAllowed(['pdf'])])
    submit = SubmitField('Contribute')
    update = SubmitField('Update')


class AddCourseForm(FlaskForm):
    course = StringField('Course',validators=[DataRequired()])
    batch = batch= SelectField('Batch',choices=[(g.batch,g.batch) for g in BatchChoices.query.order_by('batch')],validators=[DataRequired()])
    fname= StringField('Faculty Name',validators=[DataRequired()])
    fpic= FileField('Upload Faculty Photo', validators=[FileAllowed(['jpg','jpeg', 'png'])])
    submit = SubmitField('Add')

class DeleteCourseForm(FlaskForm):
    coursee = StringField('Course',validators=[DataRequired()])
    batch = batch= SelectField('Batch',choices=[(g.batch,g.batch) for g in BatchChoices.query.order_by('batch')],validators=[DataRequired()])
    submit = SubmitField('Delete')

class AddBatchForm(FlaskForm):
    available_batch=StringField('Batch',validators=[DataRequired()])
    submit = SubmitField('Add Batch')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with this email. You must register first!')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

