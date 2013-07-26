from flask import render_template, flash, redirect, request
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
    list = ['11.5,120','10.1,119','10.5,122','9,118','11.5,122.5']
    return render_template("map.html", list = list)

@app.route('/case',  methods = ['GET', 'POST'])
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
    
    case = Case()
    
    if request.method == 'POST':
        return str(case.patient_id) + '\n' + case.date + '\n' + case.name + '\n' + str(case.age) + '\n' + case.address + '\n' + case.human_diagnosis
    return render_template("case.html", case = case)

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

# test view for experimentation    
@app.route('/test',  methods = ['GET', 'POST'])
def test():
    if request.method == 'POST':
        if request.form and 'checker1' in request.form and 'checker2' in request.form:
            return request.form['checker1'] + ' ' + request.form['checker2']
        else:
            return 'off'
        
    return '<html><head><title></title></head><body><form action="" method="post"><input type="checkbox" name="checker1"><input type="checkbox" name="checker2"><input type="submit" value="Submit"></form> </body></html> '
