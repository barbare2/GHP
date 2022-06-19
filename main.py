from flask import Flask, redirect, url_for, render_template, request, session, app, flash
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib. sqla import ModelView
from werkzeug.security import generate_password_hash, check_password_hash





#app config
app = Flask(__name__)
app.config['SECRET_KEY'] = 'user'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite'
app.config['SQLALCHEMY_BINDS'] = {'booking': "sqlite:///booking.sqlite", 'clinic_infos': 'sqlite:///clinic_infos.sqlite'}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False





#AI
wyaro = open('GE_data.csv', 'r', encoding='utf-8_sig')
dict_file = dict({})
dict_ulti = dict({})
for a in dict_file:
    dict_ulti[a] = 0
for i in wyaro:
    ls = i.strip("\n").split(',')
    dict_file[ls[0].strip()] = ls[1:len(ls)]
for a in dict_file:
    dict_ulti[a] = 0




#sql alchemy
db = SQLAlchemy(app)
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)


class booking(db.Model):
    __bind_key__ = 'booking'
    id = db.Column(db.String(100), primary_key=True, nullable=False)
    name = db.Column(db.String(100), unique=True, nullable=False)
    clinic = db.Column(db.String(100), unique=True, nullable=False)
    doctor = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    date = db.Column(db.String(100), unique=True, nullable=False)
    time = db.Column(db.String(100), unique=True, nullable=False)


class clinic_infos(db.Model):
    __bind_key__ = 'clinic_infos'
    ID = db.Column(db.String(100), primary_key=True, nullable=False)
    img_url = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.String(100), unique=True, nullable=False)
    rank = db.Column(db.INT, unique=True, nullable=False)
    categories = db.Column(db.String(200), unique=True, nullable=False)


# admin page view
class MyView(ModelView):
    def is_accessible (self):
        return 'admin' in session

admin = Admin(app)
admin.add_view(MyView(Users, db.session))



# app routes
@app.route('/')
def home():
    return render_template('index.html', clinic_infos=clinic_infos, db=db)


@app.route('/book_visit')
def book_visit():
    return render_template('book_visit.html', clinic_infos=clinic_infos, db=db)


@app.route('/aboutus')
def about_us():
    return render_template('aboutus.html')


@app.route('/clinicinfo')
def clinicinfo():
    return render_template('clinic-full-info.html')


@app.route('/diagnostic')
def diagnostic():
    return render_template('diagnostic.html')


@app.route('/physical', methods = ['POST', 'GET'])
def physical():
    if request.method  == 'POST':
        symptoms = request.form['symptoms'].split(',')

        for a in dict_file:
            dict_ulti[a] = 0

        for each in symptoms:
            for one in dict_file:
                if each in dict_file[one] or " " + each in dict_file[one]:
                    dict_ulti[one] += 1

        list = []
        for every in dict_ulti:
            list.append(dict_ulti[every])
        list2 = []
        for all in dict_ulti:
            if dict_ulti[all] == max(list):
                list2.append(all + '\n')
        daavadebebi = ','.join(list2)
        print(dict_ulti)
        return render_template('physical.html', daavadebebi=daavadebebi)

    else :
        print(request.method == 'POST')
        return render_template('physical.html')


@app.route('/registration',  methods=['POST', 'GET'])
def registration():
    if request.method == 'POST':
        Name = request.form['name']
        Email = request.form['email']
        Password = request.form['password']
        if db.session.query(Users).filter_by(email=Email).first() is not None:
            flash( "მოცემული ელექტრონული ფოსტით ექაუნთი არსებობს!", 'error')
        else:
            hashed_password = generate_password_hash(Password)
            user = Users(name=Name, email=Email, password=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash("რეგისტრაცია წარმატებით დასრულდა!", 'info')

    return render_template('registration.html')


@app.route('/authorization',  methods=['POST', 'GET'])
def authorization():
    if request.method == 'POST':
        acc_email = request.form['registered_acc_email']
        acc_passsword = request.form['registered_acc_password']
        if acc_email == 'kotejaparidze9@gmail.com' and check_password_hash(db.session.query(Users.password).filter_by(email=acc_email).first()[0], 'barbare2'):
            session['admin'] = acc_email
        if db.session.query(Users.id).filter_by(email=acc_email).first() is not None:
            ID = db.session.query( Users.id ).filter_by( email=acc_email ).first()[0]
            if check_password_hash(db.session.query( Users.password ).filter_by( id=ID ).first()[0],acc_passsword):
                session['active_user'] = acc_email
                return redirect( url_for( 'home' ) )

            else:
                flash( "მომხმარებლის პაროლი არასწორია!", 'error' )
        else:
            flash( "მომხმარებლის ელექტრონული ფოსტა არ არის რეგისტრირებული!", 'error' )

    return render_template('authorization.html')




@app.route('/booking_details', methods=['POST', 'GET'])
def booking_details():
    if request.method == 'POST':
        id = request.form['id']
        name = request.form['name']
        clinic = request.form['clinic']
        doctor = request.form['doctor']
        email = request.form['email']
        date = request.form['date']
        time = request.form['time']
        if name=='' or clinic=='' or email=='' or doctor=='' or date=='' or time=='':
            flash("აუცილებლად შეავსეთ ყველა ველი", 'error')
        else:
            b_d = booking(id=int(id), name=name, clinic= clinic, doctor=doctor, email=email, date=str(date), time=str(time))
            db.session.add(b_d)
            db.session.commit()
            flash("თქვენ წარმატებით დაჯავშნეთ!", 'info')

    return render_template('booking_details.html')



@app.route('/logout')
def log_out():
    if 'active_user' in session:
        session.pop( 'active_user')
    if 'admin' in session:
        session.pop('admin')
    return redirect( url_for( 'home' ) )


@app.route('/access')
def access():
    return render_template('access.html')


if __name__ == "__main__":
    app.run(debug=True)
