from flask import render_template, flash, redirect
from serveus import app
from forms import LoginForm

@app.route('/')
@app.route('/index')
def index():
    user = { 'name': 'NOOB' }
    return render_template("index.html", title = 'Home', user=user)
    
@app.route('/login',  methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login Data: Username: ' + form.username.data + ' Password: ' + form.password.data)
        return redirect('/index')
        
    error = False
    return render_template('login.html', title = 'Sign In', form = form, error = error)