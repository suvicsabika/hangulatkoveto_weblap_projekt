from flask import Flask, render_template, url_for, redirect, request, jsonify
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from datetime import datetime, date
from flask_cors import CORS

app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = "ezmostegynagyontitkoskulcs"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/Asus/Documents/emotiontracker/datas.db'
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
mail = Mail(app)
CORS(app)

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = "hangulatkoveto.weblap@gmail.com"
app.config['MAIL_PASSWORD'] = "mjorhfmuppsiqoxh"
app.config['MAIL_DEFAULT_SENDER'] = 'Hangulatkövető weblap TEAM'
s = URLSafeTimedSerializer('ezmostegynagyontitkoskulcs')

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

class Calendar(UserMixin, db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    person_id = db.Column(db.Integer(), db.ForeignKey("user.id"))
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    day = db.Column(db.Integer)
    status = db.Column(db.Integer)

class LoginForm(FlaskForm):
    username = StringField('Felhasználónév', validators=[InputRequired(), Length(min = 4, max = 15)])
    password = PasswordField('Jelszó', validators=[InputRequired(), Length(min = 8, max = 80)])
    remember = BooleanField('Emlékezz rám')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email('Invalid email address'), Length(max=50)])
    username = StringField('Felhasználónév', validators=[InputRequired(), Length(min = 4, max = 15)])
    password = PasswordField('Jelszó', validators=[InputRequired(), Length(min = 8, max = 80)])
    password2 = PasswordField('Jelszó újra', validators=[InputRequired(), Length(min = 8, max = 80)])

class EmailForgot(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email('Invalid email address'), Length(max=50)])

class PasswordForgot(FlaskForm):
    password = PasswordField('Jelszó', validators=[InputRequired(), Length(min = 8, max = 80)])
    password2 = PasswordField('Jelszó újra', validators=[InputRequired(), Length(min = 8, max = 80)])

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    error = None

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('main'))

        error = 'Hiba! Helytelen adatok vagy nincs fiókja?'
        
    return render_template('login.html', form=form, error=error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        if (form.password.data != form.password2.data):
            hiba_uzenet = "A két jelszó nem egyezik, próbálja meg újra."
            return render_template('register.html', form = form, error = hiba_uzenet)
        
        duplicate_email = db.session.query(User).filter(User.email == form.email.data).first()
        if (duplicate_email):
            hiba_uzenet = "Az e-mail cím már létezik az adatbázisban, elfelejtette jelszavát?"
            return render_template('register.html', form = form, error = hiba_uzenet)

        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password )
        db.session.add(new_user)
        db.session.commit()
        
        login_user(new_user)
        return redirect(url_for('main'))

    return render_template('register.html', form = form)

@app.route('/main')
@login_required
def main():
    current_year = datetime.now().strftime('%Y')
    current_month = datetime.now().strftime('%m')
    if (current_month[0] == "0"):
        current_month = current_month.split('0')[1]
    
    today = datetime.now().strftime('%d')
    if (today[0] == "0"):
        today = today.split('0')[1]
    
    todays_data = db.session.query(Calendar).filter(Calendar.person_id == current_user.id, Calendar.year == int(current_year), Calendar.month == int(current_month) - 1, Calendar.day == int(today)).first()
    if (todays_data):
        bruno_kepek = ["bruno_atlagos.png", "bruno_boldog.png", "bruno_faradt.png", "bruno_duhos.png",  "bruno_izgatott.png", "bruno_szerelmes.png", "bruno_szomoru.png", "bruno_unott.png", "bruno_visszahuzodo.png"]
        
        return render_template('main.html', name=current_user.username, kep = "static/Bruno_egylufi/" + bruno_kepek[todays_data.status])

    return render_template('main.html', name=current_user.username, kep = "/static/Bruno.png")

@app.route('/osszefoglalo')
@login_required
def osszefoglalo():
    current_year = datetime.now().strftime('%Y')
    current_month = datetime.now().strftime('%m')
    if (current_month[0] == "0"):
        current_month = current_month.split('0')[1]
    
    current_months_calendars = db.session.query(Calendar).filter(Calendar.person_id == current_user.id, Calendar.year == int(current_year), Calendar.month == int(current_month) - 1).all()
    if (current_months_calendars):
        current_months_status = [month.status for month in current_months_calendars]
        current_month_data = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        for erzes in current_months_status:
            if erzes == 0:
                current_month_data[0] += 1
            if erzes == 1:
                current_month_data[1] += 1
            if erzes == 2:
                current_month_data[2] += 1
            if erzes == 3:
                current_month_data[3] += 1
            if erzes == 4:
                current_month_data[4] += 1
            if erzes == 5:
                current_month_data[5] += 1
            if erzes == 6:
                current_month_data[6] += 1
            if erzes == 7:
                current_month_data[7] += 1
            if erzes == 8:
                current_month_data[8] += 1
        return render_template('osszefoglalo.html', name = current_user.username, values = current_month_data)

    return render_template('osszefoglalo.html', name = current_user.username, values = 0) 

@app.route('/fiok', methods=["GET", "POST"])
@login_required
def fiok():
    form = PasswordForgot()
    form2 = EmailForgot()

    if form.validate_on_submit():
        if (form.password.data != form.password2.data):
            hiba_uzenet = "A két jelszó nem egyezik, próbálja meg újra."
            return render_template('register.html', form = form, error = hiba_uzenet)

        hashed_password = generate_password_hash(form.password.data, method='sha256')
        db.session.query(User).filter(User.id == current_user.id).update({'password': hashed_password})
        db.session.commit()
        uzenet = "Sikeresen megváltoztatta jelszavát."
        return render_template('fiok.html', form = form, form2 = form2, name=current_user.username, okjelszo = uzenet)

    if form2.validate_on_submit():
        db.session.query(User).filter(User.id == current_user.id).update({'email': form2.email.data})
        db.session.commit()
        uzenet = "Sikeresen megváltoztatta e-mail címét."
        return render_template('fiok.html', form = form, form2 = form2, name=current_user.username, okjelszo = uzenet)

    return render_template('fiok.html', form = form, form2 = form2, name=current_user.username)

@app.route('/reset', methods=['GET', 'POST'])
def reset():
    form = EmailForgot()

    if form.validate_on_submit():
        letezik_e = db.session.query(User).filter(User.email == form.email.data).first()
        if (not letezik_e):
            hiba = "Ez az e-mail cím nem létezik adatbázisunkban, regisztráljon be egy fiókért."
            return render_template('reset.html', form=form, error = hiba)
        email = request.form['email']
        token = s.dumps(email, salt='email-confirm')

        msg = Message('Jelszó helyreállító üzenet', sender='hangulatkoveto.weblap@gmail.com', recipients=[email])
        link = url_for('confirm_email', token=token, _external=True)
        email_uzenet = """Kedves {}!
        
Ezt az üzenetet azért kapja, mert jelszó helyreáálítást kért weblapunktól.
A következő link 1 óra hosszáig él, itt új jelszót tud adni fiókjához:
{}
        
További kellemes hetet,
Hangulatkövető weblap - Szkriptnyelvek projektmunka"""

        msg.body = email_uzenet.format(letezik_e.username, link)
        mail.send(msg)
        uzenet = "Jelszó helyreállító e-mail elküldve a megadott e-amil címre."
        
        return render_template('reset.html', form = form, ok = uzenet)

    return render_template('reset.html', form = form)

@app.route('/confirm_email/<token>', methods = ['GET', 'POST'])
def confirm_email(token):
    form = PasswordForgot()
    form2 = LoginForm()
    email = ""
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except SignatureExpired:
            error = "A token lejárt, próbálja újra."
            return render_template('password_reset.html', form = form, error = error)

    if form.validate_on_submit():
        if (form.password.data != form.password2.data):
            error = "A két jelszó nem egyezik, próbálja újra."
            return render_template('password_reset.html', form = form, error = error)

        hashed_password = generate_password_hash(form.password.data, method='sha256')
        db.session.query(User).filter(User.email == email).update({'password': hashed_password})
        db.session.commit()
        uzenet = "Sikeresen helyreállította jelszavát, most már bejelentkezhet."
        
        return render_template('login.html', form = form2, ok = uzenet)

    return render_template('password_reset.html', form = form)

@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/erzes', methods=['POST'])
@login_required
def erzes():
    data = request.get_json()
    current_id = current_user.id
    selected_day = Calendar(person_id=current_id, year=int(data['year']), month=int(data['month']), day=int(data['day']), status=int(data['status']))
    duplicate = db.session.query(Calendar).filter(Calendar.person_id == current_id, Calendar.year == selected_day.year, Calendar.month == selected_day.month, Calendar.day == selected_day.day).first()
    if (duplicate):
        db.session.delete(duplicate)
    db.session.add(selected_day)
    db.session.commit()

    return "Adatbázisba feltöltve."

@app.route('/erzeski', methods=['GET'])
@login_required
def erzeski():
    database_of_user = Calendar.query.filter(Calendar.person_id == current_user.id).all()
    json_user_data = [{'year':row.year,'month':row.month, "day":row.day, "status":row.status} for row in database_of_user if row.person_id == current_user.id]
    
    return jsonify(json_user_data)

if __name__ == '__main__':
    app.run(debug = True)