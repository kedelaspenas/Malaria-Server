from flask import request, render_template, redirect
from flask.ext.login import current_user, login_user, logout_user, login_required
from crowd import crowd
from serveus.forms import LoginForm, RecoveryForm
# IMPORT MODELS HERE
from serveus.models import User
from crowd.models import db, Labeler, LabelerType

@crowd.route('/crowd/')
@crowd.route('/crowd/index/')
def index():
    if current_user.is_authenticated():
        return redirect('/crowd/dashboard/')
    return render_template("/crowd/index.html", login_form = LoginForm())
    
@crowd.route('/crowd/dashboard/')
@login_required
def dashboard():
    labeler = Labeler.query.filter_by(user_id=current_user.id).first()
    return render_template("/crowd/dashboard.html", user = current_user, labeler = labeler)

@crowd.route('/crowd/session/',  methods = ['GET', 'POST'])
@login_required
def session():
    # LABEL SUBMITTED
    if request.method == 'POST':
        # if request.form: error check if data submitted is valid
        
        # When html form is submitted, answers are stored in request.form
        # To access use request.form['name attribute of <input> in session.html file']
        with_malaria = request.form['with_malaria']
        
        # If input of type checkbox is left blank/untouched, di siya masasama
        for i in request.form:
            print i + ': ' + request.form[i]
        

    '''
    # LABEL SUBMITTED
    # if request.method == 'POST': # if we're using post, submission is encrypted
    # if request.args: # if we're using get, submission not encrypted
    
    Recieve duration from the submission and compute time end, adjust if there were two/more malaria specie and compute time ends accordingly
    
    # No Malaria
        Dump to "No Malaria" dump, proceed to next session
        
    # Falciparum    
        If no, goto # Vivax
        If yes, make a new TrainingImageLabel
        Collect coordinates of markers and make a TrainingImageLabelCell for each
        Check if corresponding TrainingImage has reached N (magic number of dumping) and if yes
            process TrainingImage and all its TrainingImageLabel
            update all who labeled as correct/otherwise
            update participating labeler's stats
            dump
    
    # Vivax    
        If no, goto # Dunno
        If yes, make a new TrainingImageLabel
        Collect coordinates of markers and make a TrainingImageLabelCell for each
        Check if corresponding TrainingImage has reached N (magic number of dumping) and if yes
            process TrainingImage and all its TrainingImageLabel
            update all who labeled as correct/otherwise
            update participating labeler's stats
            dump    
    
    # Dunno
        Labeler was a noob, level down
        Will we have an don't know/unsure count? Image might have been a selfie
        
    '''
    '''
    # START OF LABELING
    Query TrainingImage to be labeled. If none, create a new TrainingImage from an Image. How to do this?
    
    pass to render_template, and give server's time as time start

    '''
    # How to make a new db entry, check reset.py
    # TL;DR
    # check models.py and follow the constructor
    # newEntry = Score("Kirong", 0)
    
    # Modify individual columns by
    # newEntry.columnname = something
    
    # Finally
    # db.session.add(newEntry)
    # db.session.commit()
    
    
    # How to query:
    # import ModelName above
    # ModelName.query.all() or 
    # ModelName.query.filter_by(ModelColumn=something)
    # it returns a db query so put .first() like 
    # ModelName.query.filter_by(ModelColumn=something).first() if you want the first
    
    # get sorted by Case.query.order_by(Case.date.desc())
    
    # IT RETURNS QUERY (select * * * * *) not a list so
    # Transfer it to a list if you want to iterate:
    # caseList = Case.query.all()
    # caseList = [i for i in caseList]
    # 2 lines, crazy stuff happens if everything's on 1 line
    
    labeler = Labeler.query.filter_by(user_id=current_user.id).first()
    
    return render_template("/crowd/session.html", user = current_user, labeler = labeler)
    
@crowd.route('/crowd/login/',  methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    error = False
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username,password=password).first()
        if user:
            login_user(user)
            return redirect("/crowd/dashboard")
        else:
            error = True
            error_message = "Invalid username or password!"
            return render_template("/crowd/index.html",login_form = LoginForm(), recovery_form = RecoveryForm(), error_message = error_message)
    else:
        error = True
    return redirect("/crowd/index")
    
@crowd.route('/crowd/logout/')
def logout():
    logout_user()
    return redirect('/crowd/index')