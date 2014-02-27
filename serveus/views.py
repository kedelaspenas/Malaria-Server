import os, math, time, datetime, zipfile, base64, hashlib, glob, sqlite3
import xml.etree.ElementTree as ET
from functools import wraps
from flask import render_template, flash, redirect, request, url_for, make_response, abort, jsonify
from flask.ext.login import login_user, current_user, LoginManager, logout_user, login_required
#from flask.ext.wtf import Required
from flask.ext.wtf import Form
from wtforms import TextField, BooleanField
from wtforms.validators import Required
from serveus import app
from forms import LoginForm, RecoveryForm, ChangePassForm
from werkzeug import secure_filename
from datetime import date
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from misc import Pagination
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from PIL import Image as PILImage
from cStringIO import StringIO
from flask import send_file

from sqlalchemy import distinct
# Default to Pillow and fallback to PIL
try: 
	import Image as PIL
except ImportError:
	import PIL
from flask_mail import Message

from models import db, User, UserType, Case, Key, Image, Database, Chunklist, Chunk, Region, Province, Municipality
from serveus import mail

login_manager = LoginManager()
login_manager.init_app(app)

parasiteList = ['Any Disease', 'Falciparum', 'Vivax', 'Ovale', 'Malariae', 'No Disease']

def get_admin():
	return UserType.query.filter(UserType.name == 'Administrator').first()

def get_doctor():
	return UserType.query.filter(UserType.name == 'Doctor').first()

def get_microscopist():
	return UserType.query.filter(UserType.name == 'Microscopist').first()

"""Allows only UserTypes in list parameter."""
def allowed(types=[]):
	def decorator(function):
		@wraps(function)
		def returned(*args, **kwargs):
			other = [i() for i in types]
			if current_user.usertype in other:
				return function(*args, **kwargs)
			else:
				abort(401)
		return returned
	return decorator

@app.route('/')
@app.route('/index/')
def index():
	if current_user.is_authenticated():
		if current_user.is_microscopist():
			return redirect('/records/')
		else:
			return redirect('/monitoring/')
	return render_template("index.html",login_form = LoginForm(), recovery_form = RecoveryForm())
	
@app.route('/profilepage/', methods = ['GET', 'POST'])
@login_required
def profilepage():
	changepass_form = ChangePassForm()
	# Get old password, compare with form and change password
	if changepass_form.validate_on_submit():
		old_pass = ""
		new_pass = ""
		old_pass = changepass_form.oldpassword.data
		new_pass = changepass_form.newpassword.data
		changepass_form.oldpassword.data = changepass_form.newpassword.data = ""
		if len(new_pass) > 0 and len(old_pass) > 0 and old_pass == current_user.password:
			current_user.password = new_pass
			db.session.commit()
			message = 'Password successfully changed.'
			return render_template("profilepage.html", user = current_user, changepass_form = changepass_form, message = message)
		# Error message if old password mismatches	
		if len(new_pass) <= 0 or len(old_pass) <= 0:
			error = 'Please enter in both fields.'
		else:
			error = 'Old password mismatch.'
		return render_template("profilepage.html", user = current_user, changepass_form = changepass_form, error = error)
		
	return render_template("profilepage.html", user = current_user, changepass_form = changepass_form)

@app.route('/dashboard/')
@login_required
def dashboard():
	return render_template("dashboard.html", user = current_user, date=datetime.datetime.now().strftime('%B %d, %Y'))

@app.route('/ajax/provinces')
def ajax_provinces():
	#region = Region.query.filter(Region.name==request.args.get('region')).first()
	region = Region.query.get(request.args.get('region'))
	provinces = Province.query.filter(Province.region==region)
	return jsonify(data=[i.serialize for i in provinces])

@app.route('/ajax/municipalities')
def ajax_municipalities():
	province = Province.query.get(request.args.get('province'))
	municipalities = Municipality.query.filter(Municipality.province==province)
	return jsonify(data=[i.serialize for i in municipalities])

@app.route('/records/')
@login_required
def records():
	print request.args.get('page')
	if not request.args.get('page'):
		page = 1
	else:
		page = int(request.args.get('page'))

	regionList = ['All Regions'] + Region.query.all()
	
	if request.args:
		parasiteSelected = request.args.get('parasite_selection')
		parasiteIndex = parasiteList.index(parasiteSelected)

		regionIndex = int(request.args.get('region_selection'))
		provinceIndex = int(request.args.get('province_selection'))
		municipalityIndex = int(request.args.get('municipality_selection'))

		region = Region.query.get(regionIndex)
		provinceList = ['All Provinces'] + Province.query.filter(Province.region==region).all()
		province = Region.query.get(provinceIndex)
		municipalityList = ['All Municipalities'] + Municipality.query.filter(Municipality.province==province).all()
		
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
			dte=datetime.date(int(b[2]),int(b[0]),int(b[1])) + datetime.timedelta(days=1)
		else :
			dt=datetime.date(1000,1,1)
			dte=datetime.date(9000,12,31)
			
		sortby=''
		if sort_by== 'date':
			sortby='date'
		elif sort_by== 'parasite':
			sortby='parasite'
		elif sort_by== 'description':
			sortby='description'
		elif sort_by== 'microscopist':
			sortby='microscopist'
		else:
			sortby='id'
		param= "\"case\"."+sortby+" "+order

		# chain queries based on filters (clean branching)
		caseList = Case.query.filter(Case.date>=dt,Case.date<=dte).order_by(param)
		if parasiteIndex != 0:
			caseList = caseList.filter(Case.parasite==parasiteList[parasiteIndex])
		if regionIndex != 0:
			caseList = caseList.filter(Case.region==regionList[regionIndex])
		if provinceIndex != 0:
			caseList = caseList.filter(Case.province==Province.query.get(provinceIndex))
		if municipalityIndex != 0:
			caseList = caseList.filter(Case.municipality==Municipality.query.get(municipalityIndex))
	else:
		# Default values
		provinceList = ['All Provinces']
		municipalityList = ['All Municipalities']
		parasiteIndex = 0
		regionIndex = 0
		provinceIndex = 0
		municipalityIndex = 0
		date_start = "The Beginning"
		date_end = "This Day"
		sort_by = "date"
		order = "desc"
		caseList = Case.query.order_by(Case.date.desc())
	# filter allowed records to view if not admin or validator   
	if current_user.is_microscopist():
		templist=[]
		for i in caseList:
			if(i.user == current_user):
				templist.append(i)
		caseList=templist
	# Pagination
	caseList = [i for i in caseList]
	pagination = Pagination(page, Pagination.PER_PAGE, len(caseList))
	caseList = caseList[(page-1)*Pagination.PER_PAGE : ((page-1)*Pagination.PER_PAGE) + Pagination.PER_PAGE]
	
	return render_template("records.html", caseList = caseList, pagination = pagination, parasiteList = parasiteList, parasiteIndex = parasiteIndex, date_start = date_start, date_end = date_end, sort_by = sort_by, order = order, user = current_user, menu_active='records', regionList = regionList, regionIndex = regionIndex, provinceList = provinceList, provinceIndex = provinceIndex, municipalityList = municipalityList, municipalityIndex = municipalityIndex)

	
@app.route('/map/')
@login_required
def maps():
	# Filter arguments
	lat = request.args.get('lat')
	lng = request.args.get('lng')
	zoom = request.args.get('zoom')
	date_start = request.args.get('date_start')
	date_end = request.args.get('date_end')
	default_view = False
	# Check if filters exist
	if not (zoom and date_start and date_end):
		# Go to default view
		default_view = True
		date_start = 'Last 30 Days'
		date_end = 'Today'
		zoom = 7
		# return redirect('/map/?lat=10.422988&lng=120.629883&zoom=7&date_start=Last 30 Days&date_end=Today')
	# Build marker list for map
	dt=datetime.date.today()-datetime.timedelta(days=30)
	dte=datetime.date.today() + datetime.timedelta(days=1)
	if date_start != 'Last 30 Days' :
			a=request.args.get('date_start')
			b=a.split('/')
			dt=datetime.date(int(b[2]),int(b[0]),int(b[1]))
	if date_end != 'Today' :
			a=request.args.get('date_end')
			b=a.split('/')
			dte=datetime.date(int(b[2]),int(b[0]),int(b[1])) + datetime.timedelta(days=1)
	
	case_list = Case.query.filter(Case.date>=dt,Case.date<=dte)
	case_list = [i for i in case_list]
	sorted_list = {'Any Disease': [], 'Test Data': []}
	for i in case_list:
		#sorted_list[i.parasite].append((str(i.id),str(i.lat)+','+str(i.lng)))
		if i.test:
			sorted_list["Test Data"].append((str(i.id),str(i.lat)+','+str(i.lng)))
		else:
			sorted_list["Any Disease"].append((str(i.id),str(i.lat)+','+str(i.lng)))
	
	if default_view or not(lat and lng):
		# Get centroid of markers of cases
		max_y = max_x = 0
		min_y = min_x = 9999
		for i in case_list:
			if i.lat > max_y:
				max_y = i.lat
			if i.lng > max_x:
				max_x = i.lng
			if i.lat < min_y:
				min_y = i.lat
			if i.lng < min_x:
				min_x = i.lng
		# Center
		lat = (min_y + max_y)/2
		lng = (min_x + max_x)/2
		# Calculate zoom based on resolution
		# TODO: Move to client side javascript if applicable
		try:
			zoom = math.floor(math.log(480 * 360 / (((max_y - min_y)+(max_x - min_x))/2) / 256) / 0.6931471805599453) - 1;
		except Exception, e:
			# Default zoom
			zoom = 7
			lat = 10.422988
			lng = 120.629883
	return render_template("map.html", lat = lat, lng = lng, zoom = zoom, case_list = sorted_list, date_start = date_start, date_end = date_end, user = current_user, menu_active='map')

@app.route('/monitoring/')
@login_required
def monitoring():
	# Build bar list for map
	# Get all unique coordinates

	unique_coor = Case.query.group_by(Case.lat, Case.lng)
	bar_list = []
	for i in unique_coor:
		count = Case.query.filter_by(lat=i.lat, lng=i.lng).count()
		bar_list.append(((i.lat, i.lng), count, i.region))
	week_start = datetime.date.today()-datetime.timedelta(days=7)
	week_start = week_start.strftime('%b. %d , %Y')
	week_end = date.today().strftime('%b. %d , %Y')

	def getGeoCenter(coordinatesList):
		latList = []
		lngList = []
		for a in coordinatesList:
			latList.append(a[0])
			lngList.append(a[1])
		centerlat = sum(latList)/float(len(latList))
		centerlng = sum(lngList)/float(len(lngList))
		return (centerlat,centerlng)

	unique_municipality = Case.query.group_by(Case.municipality_id)
	print unique_municipality
	municipality_list = []
	for j in unique_municipality:
		print str(j.region)
		countM = Case.query.filter_by(municipality = j.municipality).count()
		temp = Case.query.filter_by(municipality = j.municipality)
		coor_list = []
		for k in temp:
			coor_list.append((k.lat,k.lng))
		geoCenter = getGeoCenter(coor_list)
		municipality_list.append((geoCenter,countM,j.municipality))
	print municipality_list

	location = "Philippines"
	cases_this_week = 13
	cases_last_week = 14
	# Default to palawan
	zoom = 6
	lat = 11.3333
	lng = 123.0167
	return render_template("monitoring.html", lat = lat, lng = lng, zoom = zoom, municipality_list = municipality_list,  bar_list = bar_list, week_start = week_start, week_end = week_end, location = location, cases_this_week = cases_this_week, cases_last_week= cases_last_week, user = current_user, menu_active='monitoring')
	
@app.route('/timeline/')
@login_required
def timeline():
	# Filter arguments
	lat = request.args.get('lat')
	lng = request.args.get('lng')
	zoom = request.args.get('zoom')
	bound_start = date_start = request.args.get('date_start')
	bound_end = date_end = request.args.get('date_end')
	print str(bound_start)
	default_view = False
	# Check if filters exist
	if not (zoom and date_start and date_end):
		# Go to default view
		default_view = True
		date_start = datetime.date.today()-datetime.timedelta(days=30)
		date_end = datetime.date.today()
		zoom = 7
		case_list = Case.query.all()
		bound_end = None
		bound_start = None
		# return redirect('/map/?lat=10.422988&lng=120.629883&zoom=7&date_start=Last 30 Days&date_end=Today')
	# Build marker list for map
	else:
		a=request.args.get('date_start')
		b=a.split('/')
		print b
		dt=datetime.date(int(b[2]),int(b[0]),int(b[1]))

		a=request.args.get('date_end')
		b=a.split('/')
		dte=datetime.date(int(b[2]),int(b[0]),int(b[1])) + datetime.timedelta(days=1)
		
		bound_start = dt
		bound_end = dte
		
		print str(bound_start)
		
		case_list = Case.query.filter(Case.date>=dt,Case.date<=dte)

	case_list = [i for i in case_list]
	
	min_date = case_list[0].date
	max_date = case_list[0].date
	
	sorted_list = {'Any Disease': [], 'Test Data': []}
	for i in case_list:
		#sorted_list[i.parasite].append((str(i.lat)+','+str(i.lng),i.date))
		if i.test:
			sorted_list["Test Data"].append((str(i.lat)+','+str(i.lng),i.date))
		else:
			sorted_list["Any Disease"].append((str(i.lat)+','+str(i.lng),i.date))
		
		if i.date > max_date:
			max_date = i.date
		if i.date < min_date:
			min_date = i.date
	
	'''
	date_start = str(min_date.year) + '-' + str(min_date.month) + '-' + str(min_date.day)
	date_end = str(max_date.year) + '-' + str(max_date.month) + '-' + str(max_date.day)
	'''
	
	date_start = min_date
	date_end = max_date
	
	if default_view:
		bound_end = max_date + datetime.timedelta(days=1)
		bound_start = min_date - datetime.timedelta(days=1)
	
	
	
	if default_view or not(lat and lng):
		# Get centroid of markers of cases
		max_y = max_x = 0
		min_y = min_x = 9999
		for i in case_list:
			if i.lat > max_y:
				max_y = i.lat
			if i.lng > max_x:
				max_x = i.lng
			if i.lat < min_y:
				min_y = i.lat
			if i.lng < min_x:
				min_x = i.lng
		# Center
		lat = (min_y + max_y)/2
		lng = (min_x + max_x)/2
		# Calculate zoom based on resolution
		# TODO: Move to client side javascript if applicable
		try:
			zoom = math.floor(math.log(480 * 360 / (((max_y - min_y)+(max_x - min_x))/2) / 256) / 0.6931471805599453);
		except Exception, e:
			# Default zoom
			zoom = 7
			lat = 10.422988
			lng = 120.629883
	return render_template("timeline.html", lat = lat, lng = lng, zoom = zoom, case_list = sorted_list, date_start = date_start, date_end = date_end, user = current_user, bound_end=bound_end, bound_start = bound_start, menu_active='timeline')

@app.route('/case/<int:id>/',  methods = ['GET', 'POST'])
def case(id):
	# Get case and corresponding images
	case = Case.query.get(id)
	images = []
	for img in case.images:
		images.append((img.id, 'pic/' + str(img.id)))
	images = sorted(images)
	# Print out of case
	if request.method == 'POST':
		if 'validator_diagnosis' in request.form.keys() or 'validator_remarks' in request.form.keys():
			if request.form['validator_diagnosis']:
				case.parasite_validator = request.form['validator_diagnosis']
				
			if request.form['validator_remarks']:
				case.description_validator = request.form['validator_remarks']
				
			db.session.commit();
		else:
			def t(x, y):
				return {'x': x + 20, 'y': 580 - y}
			c = canvas.Canvas('malaria.pdf', pagesize=landscape(letter))
			"""
			560 bottom
			for i in xrange(70):
				x = 10 * i
				y = 10 * i
				temp = t(x,y)
				c.drawString(temp['x'], temp['y'], "(%s,%s)" % (str(x), str(y)))
			"""
			width, height = letter
			reportString = 'Location: ' + str(case.id) + '<br>' + 'Date: ' + case.date.strftime('%B %d, %Y') +  '<br>' + 'Parasite: ' + case.parasite + '<br>' + 'Description: ' + case.description + '<br>'
			reportString = "Date: %s\nRegion: %s\nProvince %s\nMunicipality: %s\nMicroscopist diagnosis: %s\nMicroscopist remarks: %s\nValidator diagnosis: %s\nValidator remarks: %s\nCoordinates: %s\nMicroscopist: %s\nContact details: %s" % (case.date.strftime('%B %d, %Y'), case.region, case.province, case.municipality, case.parasite, case.description, case.parasite_validator, case.description_validator, "%s, %s" % (case.lat, case.lng), "%s (%s %s)" % (case.user.username, case.user.firstname, case.user.lastname), "%s / %s" % (case.user.contact, case.user.email))
		
			for i, s in enumerate(reportString.split('\n')):
				z = t(0,i*15)
				c.drawString(z['x'], z['y'], s)
			z = t(700,0)
			c.drawString(z['x'], z['y'], '1')
			c.showPage()

			counter = 0
			page = 2
			if request.form:
				for i in range (0, len(images)):
					if str('checkbox_' + str(i)) in request.form:
						id = str(images[i][1]).split('/')[1]
						x = Image.query.get(id).im
						with open('image%s.jpg' % id,'w') as f:
							f.write(x)
						im = PIL.open('image%s.jpg' % id)
						im2 = im.resize((320, 240), PIL.NEAREST)
						im2.save('image%s.jpg' % id)
						z = t(500 * counter, 400)
						c.drawImage('image%s.jpg' % id, z['x'], z['y'])
						counter += 1
						if counter == 1:
							z = t(700,0)
							c.drawString(z['x'], z['y'], str(page))
					if counter == 2:
						counter = 0
						page += 1
						c.showPage()
			c.save()
			with open('malaria.pdf','r') as f:
				pdf = f.read()
			response = make_response(pdf)
			response.headers["Content-Disposition"] = "attachment; filename=malaria.pdf"
			return response
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
			return redirect("/monitoring")
		else:
			error = True
			error_message = "Invalid username or password!"
			return render_template("index.html",login_form = LoginForm(), recovery_form = RecoveryForm(), error_message = error_message)
	else:
		error = True
	return redirect("/index")

"""Returns a CSV file of the cases stored."""
@app.route('/csv/', methods = ['GET'])
@allowed([get_admin, get_doctor])
def csv():
	x = ['date,parasite,description,latitude,longitude']
	for case in Case.query.all():
		y = [case.date, case.parasite, case.description, case.lat, case.lng]
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
			parasite = mapping['species'].replace('Plasmodium ', '').capitalize()
			description = mapping['description']
			test = mapping['flags'] == 'true'
			region = mapping['region']
			province = mapping['province']
			municipality = mapping['municipality']

			dt = datetime.datetime(year, month, day, hours, minutes, seconds)
			region = Region.query.filter(Region.name == region).first()
			province = Province.query.filter(Province.name == province).first()
			municipality = Municipality.query.filter(Municipality.name == municipality).first()
			case = Case(date=dt,parasite=parasite,description=description,lat=latitude,lng=longitude,test=test,region=region,province=province,municipality=Municipality)

			user = User.query.filter(User.username == username).first()
			case.user = user
			hex_aes_key = ''.join(x.encode('hex') for x in aes_key)
			if hex_aes_key == user.password[:32]:
				db.session.add(case)
				db.session.commit()

				# store images in database
				for i, img_file in enumerate(sorted(glob.glob(os.path.join(folder, "*.jpg")))):
					img = Image()
					img.create_image(img_file, case)
					img.number = i + 1
					db.session.add(img)
					db.session.commit()

				return 'OK'
			else:
				# {'username': (tries, case, folder)
				upload_cache[username] = (0, case, folder)
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
@app.route('/api/retype2/', methods=['GET','POST'])
def retype2():
	if request.method == 'POST':
		x = request.form['message'].split('\n')
		username = x[0]
		aes_key = base64.b64decode(x[1])
		hex_aes_key = ''.join(x.encode('hex') for x in aes_key)

		print username
		user = User.query.filter(User.username == username).first()
		print '1', hex_aes_key == user.password[:32]
		print '2', hex_aes_key
		print '3', user.password[:32]

		print upload_cache
		entry = upload_cache.get(username)
		if not entry:
			return 'RETYPE 5'
		tries = entry[0]
		case = entry[1]
		folder = entry[2]
		if hex_aes_key == user.password[:32]:
			db.session.add(case)
			db.session.commit()

			# store images in database
			for img_file in glob.glob(os.path.join(folder, "*.jpg")):
				img = Image()
				img.create_image(img_file, case)
				db.session.add(img)
				db.session.commit()

			return 'OK'
		else:
			if tries != 4:
				upload_cache[username] = (tries + 1, case, folder)
			else:
				upload_cache.pop(username)
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
		print date_string
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
			response = make_response(base64.b64encode(g))
			response.headers["Expires"] = 'Thu, 01 Jan 1970 00:00:00 GMT'
			return response
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
	
@app.route('/thumb/pic/<int:picture_id>/', methods=['GET'])
def fetch_thumbnail(picture_id):
	x = Image.query.get(picture_id)
	img = PILImage.open(StringIO(x.im))
	img = img.resize((320,240), PILImage.ANTIALIAS)
	a = StringIO()
	img.save(a, 'JPEG', quality=85)
	a.seek(0)
	return send_file(a, mimetype='image/jpeg')

"""."""
@app.route('/api/chunk/', methods=['GET','POST'])
def upload_chunk():
	if request.method == 'POST':
		print 'CHUNK'
		# get chunk from form
		f = request.files['file']
		# if form is not empty
		if f:
			# temporarily save uploaded archive in folder with same name as archive filename
			filename = secure_filename(f.filename)
			folder = (app.config['UPLOAD_FOLDER'] + filename).split('.zip')[0]
			#TODO: check if folder exists
			f.save(os.path.join(folder, filename))

			# calculate md5
			with open(os.path.join(folder, filename), 'r') as f:
				m = hashlib.md5()
				m.update(f.read())
			md5 = m.digest()

			chunk = Chunk.query.filter(Chunk.filename == filename, Chunk.done == False, Chunk.checksum == md5).first()
			if chunk:
				with open(os.path.join(folder, filename), 'r') as f:
					chunk.data = f.read()
					chunk.done = True
					db.session.add(chunk)
					db.session.commit()
				if REMOVE_TEMP:
					os.remove(f.name)

				#pending_chunks = Chunk.query.filter(Chunk.chunklist == chunk.chunklist, Chunk.done == False).first()
				pending_chunks = chunk.chunklist.chunks.filter(Chunk.done == False).first()
				if not pending_chunks:
					# get all chunks in chunklist
					chunks = chunk.chunklist.chunks
					filename = chunk.chunklist.filename
					chunk_data = []

					# store chunk data in list and concatenate to file
					# assumption: chunklist filenames are sortable (correct order)
					for chunk_filename in sorted([chunk.filename for chunk in chunks]):
						with open(os.path.join(folder, chunk_filename), 'r') as f:
							chunk_data.append(f.read())
					data = ''.join(chunk_data)
					with open(os.path.join(folder, chunk.chunklist.filename), 'w') as f:
						f.write(data)

					# read concatenated archive and extract content
					print os.path.join(folder, filename)
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
					parasite = mapping['species'].replace('Plasmodium ', '').capitalize()
					description = mapping['description']
					test = mapping['flags'] == 'true'
					region = mapping['region']
					province = mapping['province']
					municipality = mapping['municipality']

					dt = datetime.datetime(year, month, day, hours, minutes, seconds)
					region = Region.query.filter(Region.name == region).first()
					province = Province.query.filter(Province.name == province).first()
					municipality = Municipality.query.filter(Municipality.name == municipality).first()
					case = Case(date=dt,parasite=parasite,description=description,lat=latitude,lng=longitude,test=test,region=region,province=province,municipality=Municipality)

					user = User.query.filter(User.username == username).first()
					case.user = user
					hex_aes_key = ''.join(x.encode('hex') for x in aes_key)
					if hex_aes_key == user.password[:32]:
						db.session.add(case)
						db.session.commit()

						# store images in database
						for i, img_file in enumerate(sorted(glob.glob(os.path.join(folder, "*.jpg")))):
							img = Image()
							img.create_image(img_file, case)
							img.number = i + 1
							db.session.add(img)
							db.session.commit()

						return 'OK'
					else:
						# {'username': (tries, case, folder)
						upload_cache[username] = (0, case, folder)
						return 'RETYPE 0'
				return 'OK'
			else:
				if REMOVE_TEMP:
					os.remove(f.name)
				return 'NO'


	return '''
	<!doctype html>
	<title>Upload chunk file</title>
	<h1>Upload chunk file</h1>
	<form action="" method=post enctype=multipart/form-data>
	  <p><input type=file name=file>
		 <input type=submit value=Upload>
	</form>
	'''

"""."""
@app.route('/api/init/', methods=['GET','POST'])
def upload_start_file():
	if request.method == 'POST':
		print 'INIT'
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
			with open(os.path.join(folder, 'cipher_listahan'), 'r') as f:
				enc_list = f.read()
				cipher = AES.new(aes_key, AES.MODE_ECB, 'dummy_parameter')
				msg = cipher.decrypt(enc_list)

			# store decrypted text file on disk
			with open(os.path.join(folder, 'decrypted.txt'), 'w') as f:
				f.write(msg)
			if REMOVE_TEMP:
				os.remove(os.path.join(folder, 'cipher_listahan'))

			# store chunks in list
			chunks = []
			user = User.query.filter(User.username == username).first()
			with open(os.path.join(folder, 'decrypted.txt'), 'r') as f:
				for line in f.readlines():
					if ' ' in line:
						chunk_filename, checksum = line.split(' ')
						chunks.append(Chunk(filename=chunk_filename,checksum=checksum,user=user))

			hex_aes_key = ''.join(x.encode('hex') for x in aes_key)
			if hex_aes_key == user.password[:32]:
				# append chunks to new chunklist
				chunklist = Chunklist(filename=filename.replace('.zip',''), date=datetime.datetime.now())
				for chunk in chunks:
					db.session.add(chunk)
					chunklist.chunks.append(chunk)
				db.session.add(chunklist)
				db.session.commit()
				return 'OK'
			else:
				# {'username': (tries, filename, chunks, folder)
				upload_cache[username] = (0, filename.replace('.zip',''), chunks, folder)
				return 'RETYPE 0'


	return '''
	<!doctype html>
	<title>Upload header file</title>
	<h1>Upload header file</h1>
	<form action="" method=post enctype=multipart/form-data>
	  <p><input type=file name=file>
		 <input type=submit value=Upload>
	</form>
	'''

"""Handles retyping of passwords from app."""
@app.route('/api/retype/', methods=['GET','POST'])
def retype():
	if request.method == 'POST':
		# get username and encrypted password
		x = request.form['message'].split('\n')
		username = x[0].lower()
		password_cipher = base64.b64decode(x[1])

		# decrypt encrypted password using RSA
		private_key = RSA.importKey(Key.query.first().private_key) #TODO: own key
		password_hash = ''.join(x.encode('hex') for x in private_key.decrypt(password_cipher))

		# check if user has cache
		entry = upload_cache.get(username)
		if not entry:
			return 'RETYPE 5'

		# check if password is correct
		tries, chunks, folder = entry
		user = User.query.filter(User.username == username).first()
		if password_hash == user.password[:32]:
			# append chunks to new chunklist
			chunklist = Chunklist(filename=filename, date=datetime.datetime.now())
			for chunk in chunks:
				db.session.add(chunk)
				chunklist.chunks.append(chunk)
			db.session.add(chunklist)
			db.session.commit()
			return 'OK'
		else:
			if tries != 4:
				upload_cache[username] = (tries + 1, filename, chunks, folder)
			else:
				upload_cache.pop(username)
			return "RETYPE %s" % tries
