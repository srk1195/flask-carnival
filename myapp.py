from flask import  Flask
from flask_sqlalchemy import  SQLAlchemy
from flask_mail import  Mail
from flask_login import  LoginManager
from flask_bcrypt import  Bcrypt
from flask_admin import Admin, BaseView, expose
from flask_moment import  Moment
from flask_socketio import  SocketIO


app = Flask(__name__)

# Mail settings
app.config['MAIL_SERVER']='smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
#  config file
app.config.from_pyfile('config.cfg')
#  db and bcrypt
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
#  mail instantiation
mail = Mail(app)
admin = Admin(app)
socketio = SocketIO(app)
moment = Moment(app)
#  Login Manager stuff
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = ''
login_manager.login_message_category = 'info'
# login_manager.login_message = "Oh Mother Fucker !! login to access this page"

from routes import  *
db.create_all()
from errors import *
