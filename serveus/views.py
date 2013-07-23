from flask import render_template, flash, redirect
from serveus import app
from forms import LoginForm

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

@app.route('/records')
def records():

    # Dummy object that will we replaced by SQL queried data
    class Record:
        date = "06/07/2013"
        patient_id = 101
        location = "ARMM (Autonomous Region in Muslim Mindanao)"
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
    if form.validate_on_submit():
        flash('Login Data: Username: ' + form.username.data + ' Password: ' + form.password.data)
        return redirect('/index')
        
    error = False
    return render_template('login.html', title = 'Sign In', form = form, error = error)