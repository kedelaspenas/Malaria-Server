from flask import render_template, flash, redirect, request
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
def defaultMap():
    return map(10.422988,120.629883, 7)

@app.route('/map/<float:lat>/<float:lng>/<int:zoom>')
def map(lat, lng, zoom):
    list1 = ['11.5,120','10.1,119']
    list2 = ['10.5,122']
    list3 = ['9,118']
    list4 = ['11.5,122.5']
    return render_template("map.html", lat = lat, lng = lng, zoom = zoom, list1 = list1, list2 = list2, list3 = list3, list4 = list4)

@app.route('/case',  methods = ['GET', 'POST'])
def case():

    # Dummy object that will we replaced by SQL queried data
    class Case:
        patient_id = 101
        date = "06/07/2013"
        time = "12:10 pm"
        name = "Raigor Stonehoof"
        age = 49
        address = "41 Real Street, Some Subdivision, Bicol Region"
        human_diagnosis = "Vivax"
        computer_diagnosis = "Falciparum, Vivax"
        lat = 11.5
        lng = 122.5
        images = ["1.png", "2.png", "3.png", "4.png"]
    
    case = Case()
    
    if request.method == 'POST':
        reportString = 'Patient ID: ' + str(case.patient_id) + '<br>' + 'Date: ' + case.date + '<br>' + 'Age: ' + str(case.age) + '<br>' + 'Address: ' + case.address + '<br>' + 'Diagnosis: ' + case.human_diagnosis + '<br>' + 'Images: '
        if request.form:
            for i in range (0, len(case.images)):
                if str('checkbox_' + str(i)) in request.form:
                    reportString += str(case.images[i]) + ' '
        
        return reportString
    return render_template("case.html", case = case)

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
        
    return redirect("/index")

# test view for experimentation    
@app.route('/test',  methods = ['GET', 'POST'])
def test():
    if request.method == 'POST':
        if request.form and 'checker1' in request.form and 'checker2' in request.form:
            return request.form['checker1'] + ' ' + request.form['checker2']
        else:
            return 'off'
        
    return '<html><head><title></title></head><body><form action="" method="post"><input type="checkbox" name="checker1"><input type="checkbox" name="checker2"><input type="submit" value="Submit"></form> </body></html> ' + str(range(0,10))
