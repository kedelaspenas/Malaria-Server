import random
import re

from flask import request, render_template, redirect
from flask.ext.login import current_user, login_user, logout_user, login_required
from crowd import crowd
from serveus.forms import LoginForm, RecoveryForm
# IMPORT MODELS HERE
from serveus.models import User
from crowd.models import db, Labeler, LabelerType, TrainingImage

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
    # Constants
    top_n_labels = 5
    label_limit = 3
    labeler = Labeler.query.filter_by(user_id=current_user.id).first()
    
    # LABEL SUBMITTED
    if request.method == 'POST' and request.form:
        # Check if data submitted in request.form is valid
        
        # Print all for debugging
        for i in request.form:
            print i + ': ' + request.form[i]
        
        # Unsure
        if request.form.getlist('unsure'):
            # UNCOMMENT NEXT LINES TO REMOVE PENDING LABEL FROM LABELER
            # labeler.current_training_image_id = None
            # db.session.add(labeler)
            # db.session.commit()
            return redirect('/crowd/index/')
        
        # No Malaria
        if not request.form.getlist('with_malaria'):
            # Make TrainingImageLabel
            # Do adjustments and evaluation
            pass
        
        # With Falciparum
        if request.form.getlist('with_falciparum'):
            # Make TrainingImageLabel
            # String to tuples
            coordinates = [(tuple(int(j) for j in re.split(',',i))) for i in re.findall('[0-9]+,[0-9]+', str(request.form.getlist('falciparum_coordinates')))]
            print coordinates
            # Do adjustments and evaluation
            pass
        
        # With Vivax
        if request.form.getlist('with_vivax'):
            # Make TrainingImageLabel
            coordinates = [(tuple(int(j) for j in re.split(',',i))) for i in re.findall('[0-9]+,[0-9]+', str(request.form.getlist('vivax_coordinates')))]
            print coordinates
            # Do adjustments and evaluation
            pass
            
        # DONE LABELING
        # UNCOMMENT NEXT LINES TO REMOVE PENDING LABEL FROM LABELER
        # labeler.current_training_image_id = None
        # db.session.add(labeler)
        # db.session.commit()
        return redirect('/crowd/index/')
        
    # START LABELING
    
    # Check if labeler still has pending labels
    if labeler.current_training_image_id !=  None:
        training_image_to_label = TrainingImage.query.filter_by(id=labeler.current_training_image_id).first()
        # Check if pending label still has to be labeled
        if training_image_to_label.total_labels < label_limit:
            return render_template("/crowd/session.html", user = current_user, labeler = labeler, training_image_to_label = training_image_to_label)
            
    # Normal procedure
    # Get 1 random from top n labels
    training_image_to_label = TrainingImage.query.order_by(TrainingImage.total_labels.desc())[random.randrange(top_n_labels)]
    
    # If there are no more images to label
    if training_image_to_label == None:
        return render_template("/crowd/session.html", user = current_user, labeler = labeler, training_image_to_label = None)
    
    # UNCOMMENT NEXT LINES TO SAVE PENDING LABEL TO LABELER
    # labeler.current_training_image_id = training_image_to_label
    # db.session.add(labeler)
    # db.session.commit()
    
    return render_template("/crowd/session.html", user = current_user, labeler = labeler, training_image_to_label = training_image_to_label)
    
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