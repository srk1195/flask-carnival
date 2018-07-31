from myapp import app,mail,bcrypt,db,admin,login_manager,moment,socketio
from flask import render_template,url_for,redirect,flash,request
from flask_login import logout_user,login_user,current_user,login_required
from forms import (StudentRegistrationForm,LoginForm,UpdateAccountForm,
                   AddEvent,RequestResetForm,ResetPasswordForm)
from models import Student,Event
from mails import send_email,send_message
from flask_admin.contrib.sqla import ModelView
import  secrets
import  os
import  secrets
from PIL import  Image
from datetime import datetime
from flask_mail import Message
from flask_socketio import send,emit,join_room,leave_room
from random import sample

app.config.from_pyfile('config.cfg')

@login_manager.user_loader
def load_user(user_id):
    #  This will load the current user to login and gives the ID of the logged user
    return Student.query.get(int(user_id))


@app.route('/')
@app.route('/home')
@login_required
def home():
    db.create_all()
    page = request.args.get('page',1,type=int)
    events = Event.query.filter().order_by(Event.title).paginate(page=page,per_page=3)
    epoch = datetime(1970, 1, 1, 0, 0, 0)
    return render_template('home.html',title='Home',events=events,
                           current_time = datetime.utcnow(),epoch=epoch,sidebar=True)

@app.route('/about')
def about():
    return render_template('about.html',title='About',sidebar=True)

@app.route('/register',methods=['GET','POST'])
def register():
    if current_user.is_authenticated:
        redirect(url_for('home'))
    form = StudentRegistrationForm()
    if form.validate_on_submit():
        StudentObj = Student()
        StudentObj.username = form.username.data
        StudentObj.email = form.email.data
        #  generating a hashed password
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        StudentObj.password = hashed_pass
        StudentObj.phone = form.phone.data
        StudentObj.birthday = form.birthday.data
        StudentObj.gender = form.gender.data
        try:
            db.session.add(StudentObj)
            db.session.commit()
            send_email(StudentObj.email,'New User Registration','/mail/new_user',name=StudentObj.username)
            send_message('Hey,'+StudentObj.username+'Thanks for registering with us..This year on '+str(StudentObj.birthday)+'lets rock!',str(StudentObj.phone))
        except Exception as e:
            print(e + StudentObj.id)
            pass
        flash('You have successfully registered', 'success')
        return redirect(url_for('home'))
    return render_template('register.html',title='Register',form=form,sidebar=True)


@app.route('/login',methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        flash('You already Logged in bro','warning')
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        student = Student.query.filter_by(username=form.username.data).first()
        #  Decrypting password
        if student and bcrypt.check_password_hash(student.password,form.password.data):
            flash('You have successfully logged in Mr.' + student.username, 'success')
            # send_email('sai@topikt.com', 'Fresh Registration', 'mail/new_user')
            #  to = str(student.phone)
            #  send_message('You are logged in bro for',to,'Carnival')
            login_user(student)
            return redirect(url_for('home'))
        else:
            flash('Credentials are wrong','danger')
    return render_template('login.html',title='Login',form=form,sidebar=True)


@app.route('/logout')
@login_required
def logout():
    flash('You have been Successfully Logged out '+current_user.username, 'danger')
    logout_user()
    return  redirect(url_for('login'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    #  getting the file extension name
    _, f_ext = os.path.splitext(form_picture.filename)
    #  random name + extension of the file
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path,'static/images',picture_fn)
    print(picture_path + "\n" + picture_fn)
    output_size = (125,125)
    i = Image.open(form_picture)
    # i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn

@app.route('/account',methods=['GET',"POST"])
@login_required
def account():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    form = UpdateAccountForm()
    # e1 = Event.query.filter(Event.title=='alpha').first()
    # print(e1.student)
    s1 = Student.query.filter(Student.username==current_user.username).first()
    events= s1.events.all()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
            db.session.commit()
        current_user.username = form.username.data
        current_user.phone = form.phone.data
        current_user.birthday = form.birthday.data
        current_user.gender = form.gender.data
        db.session.commit()
        flash('Your account has Updated','info')
        return redirect(url_for('account'))

    elif request.method=='GET':
        s1 = Student.query.filter(Student.username==current_user.username).first()
        form.username.data = s1.username
        form.phone.data = s1.phone
        form.birthday.data = s1.birthday
        form.gender.data = s1.gender

    rands = sample(range(1,6),3)
    event_count = s1.events.count()
    rands.append(event_count)
    image_file = url_for('static', filename='images/' + current_user.image_file)
    return render_template('account.html',events=events,title='Account',form=form,image_file=image_file,sidebar=True,make=rands)

# Custom Filters
@app.template_filter('reverse')
def reverse_filter(s):
    return s[::-1]

@app.route('/addevent',methods=['GET','POST'])
@login_required
def addevent():
    if current_user.username != "admin":
        return render_template('404.html',title='Unauthorized access')

    form = AddEvent()
    if form.validate_on_submit():
        e1 = Event()
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            e1.image_file = picture_file
        e1.title = form.title.data
        e1.des1 = form.des1.data
        e1.des2 = form.des2.data
        e1.event_place =form.event_place.data
        e1.event_date = form.event_date.data
        e1.event_time = form.event_time.data
        db.session.add(e1)
        db.session.commit()
        flash('Event Added','info')
        return redirect(url_for('addevent'))
    return render_template('addevent.html',form=form,sidebar=False)


@app.route('/event/<int:event_id>')
@login_required
def event(event_id):
    e1 = Event.query.get_or_404(event_id)
    s1 = Student.query.get_or_404(current_user.id)
    if s1 in e1.student:
        flash('You have already registered to the event!','danger')
        return redirect(url_for('account'))
    else:
        e1.student.append(s1)
        db.session.commit()
        flash('Your registration has been done successfully','success')
        try:
            send_message('You have been registered for the event '+ e1.title +' -carnival' ,str(current_user.phone))
            send_email(current_user.email,'Event Registration Details','/mail/event_registered',event_name=e1.title,name=current_user.username)
        except Exception as e:
            pass
        
        #  send_email(current_user.email,'Registration','mail/new_user')
        #  send_message('You have been registered for event',str(current_user.phone))
        return redirect(url_for('account'))
    return render_template(url_for('account'))


@app.route('/event_delete/<int:event_id>')
@login_required
def event_delete(event_id):
    e1 = Event.query.get_or_404(event_id)
    s1 = Student.query.get_or_404(current_user.id)
    if s1 in e1.student:
        e1.student.remove(s1)
        db.session.commit()
        flash('You have Un-registered for the event','success')
        return  redirect(url_for('account'))
    else:
        flash('Sorry,You are not even registered','warning')
        return  redirect(url_for('account'))
    return render_template(url_for('account'))



def send_reset_email(student):
    token = student.get_reset_token()
    msg = Message('Password Reset Request',
                  recipients=[student.email])
    msg.body = f''' To reset the password use the below link:
{url_for('reset_token',token=token,_external=True)}

IGNORE if not requested'''
    msg.send(msg)

@app.route('/reset_password',methods=['GET','POST'])
def reset_request():
    if current_user.is_authenticated:
        return  redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        student = Student.query.filter(Student.email==form.email.data).first()
        token = student.get_reset_token()
        token_message = f'''
{url_for('reset_token',token=token,_external=True)} '''
        #  sending a mail for successful request for password
        try:
            send_email(student.email,'Reset Request Password Form','/mail/reset_password',token_message=token_message)
        except Exception as e:
            print(e)
            pass
        
        flash('An Email Has been sent to your ID '+ student.email,'success')
        return redirect(url_for('login'))
    return render_template('reset_request.html',title='Reset password',form=form)

@app.route('/reset_password/<token>',methods=['GET','POST'])
def reset_token(token):
    student = Student.get_verify_token(token)
    if student is None:
        flash('Invalid or expired tokens','danger')
        return  redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        student.password = hashed_pass
        db.session.commit()
        flash('Your password has been updated','success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset password', form=form)

@socketio.on('message')
def handleMessage(msg):
    print('Message - '+ msg)
    msg=current_user.username.upper()+" : "+msg
    send(msg,broadcast=True)

@socketio.on('connect')
def connect_handler():
    if current_user.is_authenticated:
        emit('my response',
             {'message': '{0} has joined'.format(current_user.username)},
             broadcast=True)
    else:
        return False  # not allowed here

#  Admin Views
class myModelView(ModelView):
    def is_accessible(self):
        # if admin_check():
        if current_user.username == "admin":
            return current_user.is_authenticated
        else:
            return not current_user.is_authenticated
            # return not current_user.is_authenticated


    def inaccessible_callback(self, name, **kwargs):
        flash('You cannot access my back','warning')
        return redirect(url_for('login'))


admin.add_view(myModelView(Event,db.session))
admin.add_view(myModelView(Student,db.session))

