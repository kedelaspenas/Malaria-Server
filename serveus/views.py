import os
import datetime
from flask import render_template, flash, redirect, request, url_for
from flask.ext.login import login_user, current_user, LoginManager, logout_user, login_required
from flask.ext.wtf import Required
from serveus import app
from forms import LoginForm
from werkzeug import secure_filename
from datetime import date
from misc import Pagination

from models import db, User, UserType, Case

login_manager = LoginManager()
login_manager.init_app(app)

@app.route('/')
@app.route('/index/')
def index():
    form=LoginForm()
    return render_template("index.html",form=form)

@app.route('/dashboard/')
@login_required
def dashboard():
	cases = Case.query.all()
	return render_template("dashboard.html", user = current_user, cases=cases, date=datetime.datetime.now().strftime('%B %d, %Y'))

@app.route('/records/')
@login_required
def records2():
    print request.args.get('page')
    if not request.args.get('page'):
        page = 1
    else:
        page = int(request.args.get('page'))
    # Malaria Case Filters
    print request.args.get('malaria_selection')
    print request.args.get('region_selection')
    print request.args.get('date_start')
    print request.args.get('date_end')
    # Table sorter
    print request.args.get('sort_by') # date, location, diagnosis
    print request.args.get('order') # asc, desc
    if request.args:
        print 'Arguments present'
    else:
        print 'No arguments given'
    malariaList = ['Any Malaria Species','Falciparum','Vivax','Ovale','Malariae','Knowlesi','No Malaria']
    regionList = ['The Philippines','NCR (National Capital Region)','CAR (Cordillera Administrative Region)','Region I (Ilocos Region)','Region II (Cagayan Valley)','Region III (Central Luzon)','Region IV-A (CALABARZON)','Region IV-B (MIMAROPA)','Region V (Bicol Region)','Region VI (Western Visayas)','Region VII (Central Visayas)','Region VIII (Eastern Visayas)','Region IX (Zamboanga Peninsula)','Region X (Northern Mindanao)','Region XI (Davao Region)','Region XII (Soccsksargen)','Region XIII (Caraga)','ARMM (Autonomous Region in Muslim Mindanao)']
    if request.args:
        #print request.form['malaria_selection']
        #print request.form['region_selection']
        #print request.form['date_start']
        #print request.form['date_end']
        malariaSelected = request.args.get('malaria_selection')
        regionSelected = request.args.get('region_selection')
        malariaIndex = malariaList.index(malariaSelected)
        regionIndex = regionList.index(regionSelected)
        
        date_start = request.args.get('date_start')
        date_end = request.args.get('date_end')
        sort_by = request.args.get('sort_by')
        order = request.args.get('order')
        # here
        caseList=''
        if date_start != 'The Beginning' :
            a=request.args.get('date_start')
            b=a.split('/')
            dt=datetime.date(int(b[2]),int(b[0]),int(b[1]))
            a=request.args.get('date_end')
            b=a.split('/')
            dte=datetime.date(int(b[2]),int(b[0]),int(b[1]))
        else :
            dt=datetime.date(1000,1,1)
            dte=datetime.date(9000,12,31)
        #print sort_by
        #print order
        sortby=''
        if sort_by== 'date':
            sortby='date'
        elif sort_by== 'location':
            sortby='address'
        elif sort_by== 'diagnosis':
            sortby='human_diagnosis'
        else:
            sortby='id'
        param= "\"case\"."+sortby+" "+order
        print param
        if regionIndex == 0 and malariaIndex == 0:
                caseList= Case.query.filter(Case.date>=dt,Case.date<=dte).order_by(param)
                #print param
          
        elif regionIndex == 0:
                caseList = Case.query.filter(Case.human_diagnosis == malariaSelected,Case.date>=dt,Case.date<=dte).order_by(param)       
        elif malariaIndex == 0:      
                caseList = Case.query.filter(Case.address.contains(regionSelected),Case.date>=dt,Case.date<=dte).order_by(param)
        else:
            caseList = Case.query.filter(Case.address.contains(regionSelected),Case.human_diagnosis == malariaSelected,Case.date>=dt,Case.date<=dte).order_by(param)
    else:
        # Default values
        malariaIndex = 0
        regionIndex = 0
        date_start = "The Beginning"
        date_end = "This Day"
        sort_by = "date"
        order = "desc"
        caseList = Case.query.order_by(Case.date.desc())

    # Pagination
    caseList = [i for i in caseList]
    pagination = Pagination(page, Pagination.PER_PAGE, len(caseList))
    caseList = caseList[(page-1)*Pagination.PER_PAGE : ((page-1)*Pagination.PER_PAGE) + Pagination.PER_PAGE]
    
    return render_template("records.html", caseList = caseList, pagination = pagination, malariaList = malariaList, regionList = regionList, malariaIndex = malariaIndex, regionIndex = regionIndex, date_start = date_start, date_end = date_end, sort_by = sort_by, order = order, user = current_user)

'''   
@app.route('/records/')
@login_required
def records():
    # Malaria Case Filters
    print request.args.get('malaria_selection')
    print request.args.get('region_selection')
    print request.args.get('date_start')
    print request.args.get('date_end')
    # Table sorter
    print request.args.get('sort_by') # date, location, diagnosis
    print request.args.get('order') # asc, desc
    if request.args:
        print 'Arguments present'
    else:
        print 'No arguments given'
    malariaList = ['Any Malaria Species','Falciparum','Vivax','Ovale','Malariae','Knowlesi','No Malaria']
    regionList = ['The Philippines','NCR (National Capital Region)','CAR (Cordillera Administrative Region)','Region I (Ilocos Region)','Region II (Cagayan Valley)','Region III (Central Luzon)','Region IV-A (CALABARZON)','Region IV-B (MIMAROPA)','Region V (Bicol Region)','Region VI (Western Visayas)','Region VII (Central Visayas)','Region VIII (Eastern Visayas)','Region IX (Zamboanga Peninsula)','Region X (Northern Mindanao)','Region XI (Davao Region)','Region XII (Soccsksargen)','Region XIII (Caraga)','ARMM (Autonomous Region in Muslim Mindanao)']
    if request.args:
        #print request.form['malaria_selection']
        #print request.form['region_selection']
        #print request.form['date_start']
        #print request.form['date_end']
        malariaSelected = request.args.get('malaria_selection')
        regionSelected = request.args.get('region_selection')
        malariaIndex = malariaList.index(malariaSelected)
        regionIndex = regionList.index(regionSelected)
        
        date_start = request.args.get('date_start')
        date_end = request.args.get('date_end')
        sort_by = request.args.get('sort_by')
        order = request.args.get('order')
        # here
        caseList=''
        if date_start != 'The Beginning' :
            a=request.args.get('date_start')
            b=a.split('/')
            dt=datetime.date(int(b[2]),int(b[0]),int(b[1]))
            a=request.args.get('date_end')
            b=a.split('/')
            dte=datetime.date(int(b[2]),int(b[0]),int(b[1]))
        else :
            dt=datetime.date(1000,1,1)
            dte=datetime.date(9000,12,31)
      #  print b
        if regionIndex ==0 and malariaIndex == 0:
            caseList= Case.query.filter(Case.date>=dt,Case.date<=dte).order_by(Case.date)
        elif regionIndex == 0:
            caseList = Case.query.filter(Case.human_diagnosis == malariaSelected,Case.date>=dt,Case.date<=dte).order_by(Case.date)
        elif malariaIndex == 0:
            caseList = Case.query.filter(Case.address.contains(regionSelected),Case.date>=dt,Case.date<=dte).order_by(Case.date)
        else:
            caseList = Case.query.filter(Case.address.contains(regionSelected),Case.human_diagnosis == malariaSelected,Case.date>=dt,Case.date<=dte).order_by(Case.date)
    else:
        malariaIndex = 0
        regionIndex = 0
        date_start = "The Beginning"
        date_end = "This Day"
        sort_by = "date"
        order = "desc"
        caseList = Case.query.order_by(Case.date.desc())
        
    return render_template("records.html", list = caseList, malariaList = malariaList, regionList = regionList, malariaIndex = malariaIndex, regionIndex = regionIndex, date_start = date_start, date_end = date_end, sort_by = sort_by, order = order, user = current_user)
'''
@app.route('/map/')
def maps():
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    zoom = request.args.get('zoom')
    print str(lat)
    print str(lng)
    print str(zoom)
    if not (lat and lng and zoom):
        return redirect('/map/?lat=10.422988&lng=120.629883&zoom=7')
    # Falciparum, vivax, malariae, ovale, no malaria
    list1 = ['11.5,120','10.1,119']
    list2 = ['10.5,122']
    list3 = ['9,118']
    list4 = ['11.5,122.5']
    list5 = ['10.4,119','9.5,118']
    return render_template("map.html", lat = lat, lng = lng, zoom = zoom, list1 = list1, list2 = list2, list3 = list3, list4 = list4, list5 = list5, user = current_user)

@app.route('/case/<int:id>/',  methods = ['GET', 'POST'])
def case(id):
    case = Case.query.get(id)
    case.images = [str(i % 4 + 1) + '.png' for i in xrange(50)]
    if request.method == 'POST':
        reportString = 'Patient ID: ' + str(case.id) + '<br>' + 'Date: ' + case.date.strftime('%B %d, %Y') + '<br>' + 'Age: ' + str(case.age) + '<br>' + 'Address: ' + case.address + '<br>' + 'Diagnosis: ' + case.human_diagnosis + '<br>' + 'Images: '
        if request.form:
            for i in range (0, len(case.images)):
                if str('checkbox_' + str(i)) in request.form:
                    reportString += str(case.images[i]) + ' '
        
        return reportString
    return render_template("case.html", case = case, user = current_user)

@app.route('/logout/')
def logout():
    logout_user()
    return redirect("index")
    
@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)
    
@app.route('/login/',  methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    error = False
    if form.validate_on_submit():
        #flash('Login Data: Username: ' + form.username.data + ' Password: ' + form.password.data)
        #return redirect('/index')
        
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username,password=password).first()
        if user:
            login_user(user)
            return redirect("/dashboard")
        else:
            return redirect("/index")
    else:
        error = True
        
    return redirect("/index")

# test view for experimentation    
@app.route('/test/',  methods = ['GET', 'POST'])
def test():
    if request.method == 'POST':
        if request.form and 'checker1' in request.form and 'checker2' in request.form:
            return request.form['checker1'] + ' ' + request.form['checker2']
        else:
            return 'off'
        
    return '<html><head><title></title></head><body><form action="" method="post"><input type="checkbox" name="checker1"><input type="checkbox" name="checker2"><input type="submit" value="Submit"></form> </body></html> ' + str(range(0,10))


# API

UPLOAD_FOLDER = os.getcwd().replace('\\','/') + '/files/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/api/send/', methods=['POST'])
def upload_file():
	if request.method == 'POST':
		file = request.files['file']
		if file:
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			return 'win'
		else:
			return 'fail'

@app.route('/api/text/', methods=['POST'])
def upload_file2():
	if request.method == 'POST':
		print request.form['message']
		return 'got the message: %s' % request.form['message']

@app.route('/api/key/', methods=['POST'])
def update_key():
	# if identifier is correct
	if request.method == 'POST':
		return os.urandom(256)

@app.route('/api/db/', methods=['POST'])
def update_db():
	# if sent date < modified date
	# return 'no change'
	return redirect(url_for('static', filename='db.db'))

@app.route('/api/apk/', methods=['POST'])
def update_apk():
	# if sent version < current version
	# return 'no change'
	return redirect(url_for('static', filename='apk.apk'))
