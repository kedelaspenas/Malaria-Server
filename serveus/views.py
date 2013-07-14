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
    return render_template("records.html")

@app.route('/map')
def map():
    return render_template("map.html")

@app.route('/case')
def case():
    return render_template("case.html")

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