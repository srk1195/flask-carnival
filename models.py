import itsdangerous

from myapp import db,app
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer



class Student(db.Model, UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(25),nullable=False,unique=True)
    email = db.Column(db.String(30),nullable=False,unique=True)
    password = db.Column(db.String(100),nullable=False)
    gender = db.Column(db.String(5))
    birthday = db.Column(db.Date)
    phone = db.Column(db.BigInteger(),nullable=False,unique=True)
    image_file = db.Column(db.String(64),nullable=False,default='default.jpg')
    events = db.relationship('Event',secondary='student_events',backref='student',lazy='dynamic')


    def __repr__(self):
        return '<User %r>' % self.username

    def get_reset_token(self,expires_after_secs=1800):
        s = Serializer(app.config['SECRET_KEY'],expires_after_secs)
        return s.dumps({'user_id':self.id}).decode('utf-8')

    @staticmethod
    def get_verify_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except itsdangerous.SignatureExpired:
            return None
        return Student.query.get(user_id)

class Event(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(15),nullable=False,unique=True)
    des1 = db.Column(db.String(300),nullable=False)
    des2 = db.Column(db.String(300))
    event_place = db.Column(db.String(20))
    event_date = db.Column(db.Date)
    event_time = db.Column(db.String(10),nullable=False,default='10:00')
    image_file = db.Column(db.String(64),default='rahul.jpg')
    likes = db.Column(db.Integer,default=0)


    def __repr__(self):
        return '<Event %r>' % self.title


db.Table('student_events',
        db.Column('student_id',db.Integer,db.ForeignKey('student.id')),
        db.Column('event_id',db.Integer,db.ForeignKey('event.id')),
        db.Column('liked_by_id',db.Boolean)
        )

