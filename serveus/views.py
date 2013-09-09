import os
import datetime
import zipfile
import base64
import hashlib
import time
import glob
import sqlite3
import xml.etree.ElementTree as ET
from functools import wraps
from flask import render_template, flash, redirect, request, url_for, make_response, abort
from flask.ext.login import login_user, current_user, LoginManager, logout_user, login_required
from flask.ext.wtf import Required
from serveus import app
from forms import LoginForm, RecoveryForm, ChangePassForm
from werkzeug import secure_filename
from datetime import date
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from misc import Pagination

from models import db, User, UserType, Case, Key, Image, Database, Region

login_manager = LoginManager()
login_manager.init_app(app)

malariaList = ['Any Malaria Species','Falciparum','Vivax','Ovale','Malariae','No Malaria']
admin = UserType.query.filter(UserType.name == 'Administrator').first()
doctor = UserType.query.filter(UserType.name == 'Doctor').first()
microscopist = UserType.query.filter(UserType.name == 'Microscopist').first()

"""Allows only UserTypes in list parameter."""
def allowed(types=[]):
    def decorator(function):
        @wraps(function)
        def returned(*args, **kwargs):
            if current_user.usertype in types:
                return function(*args, **kwargs)
            else:
                abort(401)
        return returned
    return decorator

@app.route('/')
@app.route('/index/')
def index():
    return render_template("index.html",login_form = LoginForm(), recovery_form = RecoveryForm())
    
@app.route('/profilepage/', methods = ['GET', 'POST'])
@login_required
def profilepage():
    changepass_form = ChangePassForm()
    
    if changepass_form.validate_on_submit():
        old_pass = changepass_form.oldpassword.data
        new_pass = changepass_form.newpassword.data
        changepass_form.oldpassword.data = changepass_form.newpassword.data = ""
        if old_pass == current_user.password:
            current_user.password = new_pass
            db.session.commit()
            message = 'Password successfuly changed.'
            return render_template("profilepage.html", user = current_user, changepass_form = changepass_form, message = message)
            
        error = 'Old password mismatch.'
        return render_template("profilepage.html", user = current_user, changepass_form = changepass_form, error = error)

    return render_template("profilepage.html", user = current_user, changepass_form = changepass_form)

@app.route('/dashboard/')
@login_required
def dashboard():
    casenum=[]
    casenum2=[]
    regionList= Region.query.all()

    for i in regionList:
        print i
        a=Case.query.filter(Case.region==i)
        a= [i for i in a] 
        casenum.append(len(a))
    cases=zip(regionList,casenum)
    print 'cases:', len(cases), cases
    for i in malariaList[1:]:
        a=Case.query.filter(Case.human_diagnosis == i)
        a= [i for i in a] 
        print len(a)
        casenum2.append(len(a))
    cases2=zip(malariaList[1:],casenum2)
    total = len(Case.query.all())
    return render_template("dashboard.html", user = current_user, cases=cases, cases2=cases2, malariaList = malariaList[1:], regionList = regionList[1:], date=datetime.datetime.now().strftime('%B %d, %Y'), casenum=casenum, total=total)

@app.route('/records/')
@login_required
def records():
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
    
    if request.args:
        malariaSelected = request.args.get('malaria_selection')
        regionSelected = request.args.get('region_selection')
        malariaIndex = malariaList.index(malariaSelected)
        regionIndex = Region.query.all().index(regionSelected)
        
        date_start = request.args.get('date_start')
        date_end = request.args.get('date_end')
        sort_by = request.args.get('sort_by')
        order = request.args.get('order')
        
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
    
    return render_template("records.html", caseList = caseList, pagination = pagination, malariaList = malariaList, regionList=Region.query.all(), malariaIndex = malariaIndex, regionIndex = regionIndex, date_start = date_start, date_end = date_end, sort_by = sort_by, order = order, user = current_user)

    
@app.route('/map/')
@login_required
def maps():
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    zoom = request.args.get('zoom')
    date_start = request.args.get('date_start')
    date_end = request.args.get('date_end')

    if not (lat and lng and zoom and date_start and date_end):
        return redirect('/map/?lat=10.422988&lng=120.629883&zoom=7&date_start=Last 30 Days&date_end=Today')
    dt=datetime.date.today()-datetime.timedelta(days=30)
    dte=datetime.date.today()
    if date_start != 'Last 30 Days' :
            a=request.args.get('date_start')
            b=a.split('/')
            dt=datetime.date(int(b[2]),int(b[0]),int(b[1]))
    if date_end != 'Today' :
            a=request.args.get('date_end')
            b=a.split('/')
            dte=datetime.date(int(b[2]),int(b[0]),int(b[1]))
    cl1 = Case.query.filter(Case.human_diagnosis == "Falciparum",Case.date>=dt,Case.date<=dte)
    cl2= []
    for i in cl1:
        cl2.append(str(i.lat)+','+str(i.lng))
    # Falciparum, vivax, malariae, ovale, no malaria
    list1 = cl2
    cl2= []
    cl1 = Case.query.filter(Case.human_diagnosis == "Vivax",Case.date>=dt,Case.date<=dte)
    for i in cl1:
        cl2.append(str(i.lat)+','+str(i.lng))
    list2 = cl2
    cl2= []
    cl1 = Case.query.filter(Case.human_diagnosis == "Malariae",Case.date>=dt,Case.date<=dte)
    for i in cl1:
        cl2.append(str(i.lat)+','+str(i.lng))
    list3 = cl2
    cl2= []
    cl1 = Case.query.filter(Case.human_diagnosis == "Ovale",Case.date>=dt,Case.date<=dte)
    for i in cl1:
        cl2.append(str(i.lat)+','+str(i.lng))
    list4 = cl2
    cl2= []
    cl1 = Case.query.filter(Case.human_diagnosis == "No Malaria",Case.date>=dt,Case.date<=dte)
    for i in cl1:
        cl2.append(str(i.lat)+','+str(i.lng))
    list5 = cl2
    return render_template("map.html", lat = lat, lng = lng, zoom = zoom, list1 = list1, list2 = list2, list3 = list3, list4 = list4, list5 = list5, date_start = date_start, date_end = date_end, user = current_user)

@app.route('/case/<int:id>/',  methods = ['GET', 'POST'])
def case(id):
    case = Case.query.get(id)
    images = []
    for img in case.images:
        images.append('pic/' + str(img.id))
    images = sorted(images)
    if request.method == 'POST':
        reportString = 'Patient ID: ' + str(case.id) + '<br>' + 'Date: ' + case.date.strftime('%B %d, %Y') + '<br>' + 'Age: ' + str(case.age) + '<br>' + 'Address: ' + case.address + '<br>' + 'Diagnosis: ' + case.human_diagnosis + '<br>' + 'Images: '
        if request.form:
            for i in range (0, len(images)):
                if str('checkbox_' + str(i)) in request.form:
                    reportString += str(images[i]) + ' '
        
        return reportString
    return render_template("case.html", case = case, user = current_user, images=images)

@app.route('/logout/')
def logout():
    logout_user()
    return redirect("index")
    
@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)

@app.route('/recovery/',  methods = ['GET', 'POST'])
def recovery():
    form = LoginForm()
    error = False
    if form.validate_on_submit():
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
   
@app.route('/login/',  methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    error = False
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username,password=password).first()
        if user:
            login_user(user)
            return redirect("/dashboard")
        else:
            error = True
            error_message = "Invalid username or password!"
            return render_template("index.html",login_form = LoginForm(), recovery_form = RecoveryForm(), error_message = error_message)
    else:
        error = True
    return redirect("/index")

"""Returns a CSV file of the cases stored."""
@app.route('/csv/', methods = ['GET'])
@allowed([admin, doctor])
def csv():
    x = ['date,age,address,human diagnosis,latitude,longitude,malaria type,region']
    for case in Case.query.all():
        y = [case.date, case.age, case.address, case.human_diagnosis, case.lat, case.lng, case.maltype, case.region]
        y = map(str, y)
        x.append(','.join(y))
    csv = '\n'.join(x)
    response = make_response(csv)
    response.headers["Content-Disposition"] = "attachment; filename=malaria.csv"
    return response

# API

UPLOAD_FOLDER = os.path.join(os.getcwd().replace('\\','/'), 'upload/')
REMOVE_TEMP = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
upload_cache = {}

"""Decrypts the encrypted archive, stores the data if authenticated, and returns OK if successful."""
@app.route('/api/send/', methods=['GET','POST'])
def upload_file():
    if request.method == 'POST':
        # get file from form
        f = request.files['file']
        # if form is not empty
        if f:
            # temporarily save uploaded archive in folder with same name as archive filename
            filename = secure_filename(f.filename)
            folder = (app.config['UPLOAD_FOLDER'] + filename).replace('.zip', '')
            os.makedirs(folder)
            f.save(os.path.join(folder, filename))

            # extract uploaded archive to folder and delete original archive
            with open(os.path.join(folder, filename), 'r') as f:
                z = zipfile.ZipFile(f)
                z.extractall(folder)
            if REMOVE_TEMP:
                os.remove(f.name)

            # get encrypted AES key (128-bit SHA-1 of plaintext password) from XML file and decrypt using RSA private key
            with open(os.path.join(folder, 'accountData.xml'), 'r') as f:
                g = f.read()

            root = ET.fromstring(g)
            username = root.find('user').text
            enc_aes_key = root.find('pass').text.replace('\n','')
            enc_aes_key = base64.b64decode(enc_aes_key)
            private_key = RSA.importKey(Key.query.first().private_key)
            aes_key = private_key.decrypt(enc_aes_key)

            # decrypt image archive using decrypted AES key
            with open(os.path.join(folder, 'cipherZipFile.zip'), 'r') as f:
                enc_img_zip = f.read()
                cipher = AES.new(aes_key, AES.MODE_ECB, 'dummy_parameter')
                msg = cipher.decrypt(enc_img_zip)

            # store decrypted image archive on disk
            with open(os.path.join(folder, 'decrypted.zip'), 'w') as f:
                f.write(msg)
            if REMOVE_TEMP:
                os.remove(os.path.join(folder, 'cipherZipFile.zip'))

            # extract decrypted image archive and store in database
            with open(os.path.join(folder, 'decrypted.zip'), 'r') as f:
                z = zipfile.ZipFile(f)
                z.extractall(folder)
            if REMOVE_TEMP:
                os.remove(f.name)

            # make case using XML data
            tree = ET.parse(os.path.join(folder, 'textData.xml'))
            root = tree.getroot()
            mapping = {}
            for child in root:
                mapping[child.tag] = child.text
            month, day, year = map(int, mapping['date-created'].split('/'))
            hours, minutes, seconds = map(int, mapping['time-created'].split(':'))
            latitude = float(mapping['latitude'])
            longitude = float(mapping['longitude'])
            species = mapping['species'].replace('Plasmodium ', '').capitalize()
            age = mapping['age']
            address = mapping['address']
            region = Region.query.filter(Region.name == mapping['region']).first()

            dt = datetime.datetime(year, month, day, hours, minutes, seconds)
            case = Case(date=dt,age=age,address=address,region=region,human_diagnosis=species,lat=latitude,lng=longitude)

            user = User.query.filter(User.username == username).first()
            hex_aes_key = ''.join(x.encode('hex') for x in aes_key)
            if hex_aes_key == user.password[:32]:
                db.session.add(case)
                db.session.commit()

                # store images in database
                for img_file in glob.glob(os.path.join(folder, "*.jpg")):
                    img = Image(img_file, case)
                    db.session.add(img)
                    db.session.commit()

                return 'OK'
            else:
                # {'username': (tries, case, folder)
                upload_cache[user] = (0, case, folder)
                return 'RETYPE 0'


    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''

"""Handles retyping of passwords from app."""
@app.route('/api/retype/', methods=['GET','POST'])
def retype():
    if request.method == 'POST':
        username, aes_key = request.form['message'].split('\n')
        hex_aes_key = ''.join(x.encode('hex') for x in aes_key)

        user = User.query.filter(User.username == username).first()
        if hex_aes_key == user.password[:32]:
            entry = upload_cache[username]
            if not entry:
                return 'RETYPE 5'
            tries = entry[0]
            case = entry[1]
            folder = entry[2]

            db.session.add(case)
            db.session.commit()

            # store images in database
            for img_file in glob.glob(os.path.join(folder, "*.jpg")):
                img = Image(img_file, case)
                db.session.add(img)
                db.session.commit()

            return 'OK'
        else:
            if tries != 4:
                entry[username] = (tries + 1, case, folder)
            else:
                entry.pop(username)
            return "RETYPE %s" % tries


"""Returns the RSA public key."""
@app.route('/api/key/', methods=['GET'])
def update_key():
    key = Key.query.first()
    public_key = key.public_key
    return public_key

"""Returns a Base-64 string of the credentials database, or "OK" otherwise."""
@app.route('/api/db/', methods=['GET','POST'])
def update_db():
    if request.method == 'GET':
        return '''
        <!doctype html>
        <title>Get database date</title>
        <h1>Get database date</h1>
        <form action="" method=post>
          <p><input type=text name=message>
             <input type=submit value=Send>
        </form>
        '''
    elif request.method == 'POST':
        date_string = request.form['message']
        # if sent date < modified date
        if Database.need_update(date_string):
            conn = sqlite3.connect('updated.db')
            c = conn.cursor()
            c.execute("DELETE FROM user")
            for user in User.query.all():
                username = user.username
                password = user.password
                c.execute("INSERT INTO user VALUES(NULL, '%s', '%s')" % (username, password))
            conn.commit()
            conn.close()
            with open('updated.db', 'r') as f:
                g = f.read()
            return base64.b64encode(g)
        else:
            return 'OK'

    """
    temp = []
    for entry in User.query.all():
        username = entry.username
        password = entry.password
        temp.append(username + ',' + password)
    return '\n'.join(temp)
    """

"""Returns the APK if the version string sent differs from the current, or "OK" otherwise."""
@app.route('/api/apk/', methods=['GET','POST'])
def update_apk():
    if request.method == 'POST':
        # assume server always has latest version
        if request.form['message'] != '1.0':
            return redirect(url_for('static', filename='Malaria-debug-unaligned.apk'))
        else:
            return 'OK'

"""Returns the JPG requested."""
@app.route('/pic/<int:picture_id>/', methods=['GET'])
def fetch_image(picture_id):
    x = Image.query.get(picture_id)
    response = make_response(x.im)
    response.headers['Content-Type'] = 'image/jpeg'
    return response
