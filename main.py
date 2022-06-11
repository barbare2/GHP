from flask import Flask, redirect, url_for, render_template, request, session, app, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import exists
from jinja2 import Environment, FileSystemLoader
import requests
from flask_admin import Admin
from flask_admin.contrib. sqla import ModelView
from bs4 import BeautifulSoup
from flask_paginate import Pagination, get_page_args




#app config
app = Flask(__name__)
app.config['SECRET_KEY'] = 'user'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite'
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




#parsing
ammount_of_pages = 1
img_urls = []
clinic_names = []
categ = []
clinic_addresses = []
clinic_ranks = []
categories = dict({})
keycounter = 0

while ammount_of_pages < 3:
    url = 'https://tsamali.ge/clinics/' + str(ammount_of_pages)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    s = soup.find('div', class_='doctor_items')
    sub_soup = s.find_all('div', class_='doctor_item_inside')

    for each in sub_soup:
        img_url = each.find('div', class_='doctor_item_l').a.attrs.get('style').split('(')[1].split(')')[0]
        img_urls.append(img_url)
        name = each.find('div', class_='doctor_item_r').a.text
        clinic_names.append(name)
        address = each.find('div', class_='doctor_clinic_location').text
        clinic_addresses.append(address)
        rank = each.find('div', class_='item_rank_text').text
        clinic_ranks.append(rank)
        c = each.find( 'div', class_='item_time3' )
        kategoriebi = c.ul.text.strip()
        cat_list = kategoriebi.split('\n')[0:3]

        categories[keycounter] = cat_list
        keycounter += 1
    ammount_of_pages+=1




#paging
USERS = list(range(len(categories)))
def get_users(offset=0, per_page=10):
    return USERS[offset: offset+per_page]




# admin page view
class MyView(ModelView):
    def is_accessible (self):
        return 'admin' in session

admin = Admin(app)
admin.add_view(MyView(Users, db.session))




# app routes
@app.route('/')
def home():
    return render_template('index.html', img_urls=img_urls)


@app.route('/book_visit')
def book_visit():
    page,per_page,offset = get_page_args(page_parameter="page", per_page_parameter="per_page")
    total = len(USERS)
    pagination_users = get_users(offset=offset, per_page=per_page)
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')
    return render_template('book_visit.html',
                           USERS=pagination_users,
                           page=page,
                           per_page=per_page,
                           pagination=pagination,
                           img_urls=img_urls,
                           clinic_names= clinic_names,
                           clinic_addresses=clinic_addresses,
                           clinic_ranks= clinic_ranks,
                           categories=categories,
                           categ= categ)


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
            user = Users(name=Name, email=Email, password=Password)
            db.session.add(user)
            db.session.commit()
            flash("რეგისტრაცია წარმატებით დასრულდა!", 'info')

    return render_template('registration.html')


@app.route('/authorization',  methods=['POST', 'GET'])
def authorization():
    if request.method == 'POST':
        acc_email = request.form['registered_acc_email']
        acc_passsword = request.form['registered_acc_password']
        if acc_email == 'kotejaparidze9@gmail.com' and acc_passsword == 'barbare2':
            session['admin'] = acc_email
        if db.session.query(Users.id).filter_by(email=acc_email).first() is not None:
            ID = db.session.query( Users.id ).filter_by( email=acc_email ).first()[0]
            if db.session.query( Users.password ).filter_by( id=ID ).first()[0] == acc_passsword:
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
        name = request.form['name']
        mail = request.form['email']
        docname = request.form['doctor']
        date = request.form['date']
        time = request.form['time']
        if name=='' or mail=='' or docname=='' or date=='' or time=='':
            flash("აუცილებლად შეავსეთ ყველა ველი", 'error')
        else:
            flash("თქვენ წარმატებით დაჯავშნეთ!", 'info')

    return render_template('booking_details.html')


@app.route('/logout')
def log_out():
    if 'active_user' in session:
        session.pop( 'active_user')
    if 'admin' in session:
        session.pop('admin')
    return render_template('index.html')


@app.route('/access')
def access():
    return render_template('access.html')


if __name__ == "__main__":
    app.run(debug=True)
