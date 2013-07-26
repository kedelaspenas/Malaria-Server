from flask import render_template, flash, redirect
from flask.ext.login import login_user, current_user
from flask.ext.wtf import Required
from serveus import app
from forms import LoginForm
from flask.ext.login import UserMixin
from yourapplication import db
from yourapplication import User


class UserClass(UserMixin):
    def __init__(self, username, password, id):
        self.username = username
        self.password = password
        self.id = id
    
    def __repr__(self):
        return self.username
        
@app.route('/')
@app.route('/index')
def index():
    form=LoginForm()
    return render_template("index.html",form=form)

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

@app.route('/records')
def records():

    # Dummy object that will we replaced by SQL queried 
    
    class Record:
        date = "06/07/2013"
        patient_id = 101
        location = "Bicol Region"
        diagnosis = "Vivax"
        '''
        def __init__(self, date, patient_id, location, diagnosis):
            self.date = date
            self.patient_id = patient_id
            self.location = location
            self.diagnosis = diagnosis
        '''
    list = [Record(), Record(), Record(), Record(), Record()]
        
    return render_template("records.html", list = list)

@app.route('/map')
def map():
    return render_template("map.html")

@app.route('/case')
def case():

    # Dummy object that will we replaced by SQL queried data
    class Case:
        patient_id = 101
        date = "06/07/2013"
        name = "Raigor Stonehoof"
        age = 49
        address = "41 Real Street, Some Subdivision, Bicol Region"
        human_diagnosis = "Vivax"
        computer_diagnosis = "Falciparum, Vivax"
        images = ["1.png", "2.png", "3.png", "4.png"]

    return render_template("case.html", case = Case())

@app.route('/logout')
def logout():
    return redirect("index.html")


@app.route('/login',  methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    error = False
    userlist = [('kirong','1234'),('noel','123')]
    userlist2 = User.query.all()
    if form.validate_on_submit():
        #flash('Login Data: Username: ' + form.username.data + ' Password: ' + form.password.data)
        #return redirect('/index')
        
        username = form.username.data
        password = form.password.data
        x = username, password
        
        if User.query.filter_by(username=username,password=password).first():
            return redirect("/dashboard")
        else:
            return redirect("/index")
        '''for i in User.query.all():
            y = i.username, i.password
            if(x==y):
                return redirect("/dashboard")
            return redirect("/index")
            '''
        '''if x in userlist:
            user = UserClass(username, password, 1)
            login_user(user)
            return redirect("/dashboard")
        else:
            return redirect("/index")'''
    else:
        error = True
        
    return 'ghjgj'
    #render_template('login.html.old', title = 'Sign In', form = form, error = error)