from myapp import db, bcrypt, mail
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField,RadioField,IntegerField,DateField,TextAreaField
from wtforms.validators import data_required, Email, Length, EqualTo,ValidationError
from datetime import datetime
from models import Student,Event
from flask_wtf.file import FileField, FileAllowed, FileRequired


#  Registration Form for Students

class StudentRegistrationForm(FlaskForm):
    username = StringField('Username', validators=[data_required(), Length(min=2, max=25)])
    email = StringField('Email Address', validators=[data_required(), Email()])
    password = PasswordField('Password', validators=[data_required(), Length(min=2, max=40)])
    confirm_password = PasswordField('Confirm password', validators=[data_required(),
                                                                       EqualTo('password'), Length(min=2, max=40)])
    gender = RadioField('Gender',choices=[('Male','Men'),('Female','Women')],default='')
    birthday = DateField('Birthday',default=datetime.utcnow())
    phone =  IntegerField('Phone',validators=[data_required()])
    submit = SubmitField('Sign Up')

    def validate_username(self,username):
        student = Student.query.filter_by(username=username.data).first()
        if student:
            raise ValidationError('The Username is taken')

    def validate_email(self,email):
        student = Student.query.filter_by(email=email.data).first()
        if student:
            raise ValidationError('The email is taken')

    def validate_phone(self,phone):
        student = Student.query.filter_by(phone=phone.data).first()
        if student:
            raise ValidationError('The phone number is already existing')

class LoginForm(FlaskForm):
    username = StringField('Username',validators=[data_required()])
    password = StringField('Password',validators=[data_required()])
    submit = SubmitField('Login')

    # def check_username(self,username):
    #     student = Student.query.filter_by(username=username.data).first()
    #     if student:
    #         raise ValidationError('Please enter a valid username')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[data_required()])
    phone = IntegerField('Phone', validators=[data_required()])
    birthday = DateField('Birthday', default=datetime.utcnow())
    gender = RadioField('Gender', choices=[('Male', 'Men'), ('Female', 'Women')], default='')
    picture = FileField('Change photo', validators=
                            [FileAllowed(['jpg', 'png', 'jpeg'], 'Images Only')])
    submit = SubmitField('Update')

class AddEvent(FlaskForm):
    title = StringField('Title',validators=[data_required()])
    des1 = TextAreaField('Main Description')
    des2 = TextAreaField('Secondary Description')
    event_date = DateField('Event Date',default=datetime.utcnow())
    event_time = StringField('Event time')
    event_place = StringField('Event place')
    picture = FileField('Add photo',validators=
                            [FileAllowed(['jpg', 'png', 'jpeg'], 'Images Only')])
    submit = SubmitField('Append')

    def validate_title(self,title):
        event = Event.query.filter_by(title=title.data).first()
        if event:
            raise ValidationError('The event title is taken already')

class RequestResetForm(FlaskForm):
    email = StringField('Email Address', validators=[data_required(), Email()])
    submit = SubmitField('Request Password')

    def validate_email(self,email):
        student = Student.query.filter_by(email=email.data).first()
        if student is None:
            raise ValidationError('There is no account.Register First')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[data_required(), Length(min=2, max=40)])
    confirm_password = PasswordField('Confirm password', validators=[data_required(),
                                        EqualTo('password'), Length(min=2, max=40)])
    submit = SubmitField('Reset password')