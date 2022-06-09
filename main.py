from flask import Flask, redirect, url_for, render_template, request, session, app, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import exists
from jinja2 import Environment, FileSystemLoader
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config['SECRET_KEY'] = 'user'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

# b1 = Users(name='barbare', email='barbich222@gmail.com', password='giji2')
# db.session.add(b1)
# db.session.commit()



page = 1
img_urls = []
clinic_names = []
categ = []
clinic_addresses = []
clinic_ranks = []
categories = dict({})
keycounter = 0

while page < 3:
    url = 'https://tsamali.ge/clinics/' + str(page)
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


    page+=1


@app.route('/')
def home():
    return render_template('index.html', img_urls=img_urls)

@app.route('/aboutus')
def about_us():
    return render_template('aboutus.html')

@app.route('/bookvisit')
def book_visit():
    return render_template('bookvisit.html', img_urls=img_urls, clinic_names= clinic_names, clinic_addresses=clinic_addresses, clinic_ranks= clinic_ranks, categories=categories, categ= categ )

@app.route('/clinicinfo')
def clinicinfo():
    return render_template('clinic-full-info.html')

@app.route('/diagnostic')
def diagnostic():
    return render_template('diagnostic.html')

@app.route('/physical')
def physical():
    return render_template('physical.html')

@app.route('/registration',  methods=['POST', 'GET'])
def registration():
    if request.method == 'POST':
        Name = request.form['name']
        Email = request.form['email']
        Password = request.form['password']
        if not Name.isalpha():
            flash("შეიყვანეთ მხოლოდ სახელი და გვარი", 'error')
        else:
            user = Users(name=Name, email=Email, password=Password)
            db.session.add(user)
            db.session.commit()
            flash("რეგისტრაცია წარმატებით დასრულდა!", 'info')

    return render_template('registration.html')

@app.route('/authorization')
def authorization():
    # if request.method == 'POST':
    #     acc_email = request.form['registered_acc_email']
    #     acc_passsword = request.form['registered_acc_password']
    #     if db.session.query(Users.email).filter_by(email=acc_email) and db.session.query(Users.password).filter_by(password=acc_passsword):
    #         return render_template('aboutus.html')
    #     else:
    #         return render_template('bookvisit.html')

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
        elif not name.isalpha() or docname.isalpha():
            flash("სახელის გრაფა არ უნდა შეიცავდეს რიცხვებს", 'error')
        else:
            flash("თქვენ წარმატებით დაჯავშნეთ!", 'info')

    return render_template('booking_details.html')

@app.route('/success_registration')
def success_registration():
    return render_template('success.registration.html')

if __name__ == "__main__":
    app.run(debug=True)

#
#
#
# #
# # import sqlite3
# # conn = sqlite3.connect('users.sqlite')
# #
# # cursor = conn.cursor()
# # cursor.execute("""CREATE TABLE Users (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
# #                    name varchar(100),
# #                     email varchar(50),
# #                     password varchar(10))""")
