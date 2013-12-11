import datetime
import random
import re

from flask import request, render_template, redirect
from flask.ext.login import current_user, login_user, logout_user, login_required
from crowd import crowd
from serveus.forms import LoginForm, RecoveryForm
# IMPORT MODELS HERE
from serveus.models import User
from crowd.models import db, Labeler, LabelerType, TrainingImage, TrainingImageLabel, TrainingImageLabelCell

# global values
top_n_labels = 5
label_limit = 3

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

def makeTrainingImageLabel(labeler, diagnosis, coordinates):
    global label_limit
    label = TrainingImageLabel(labeler.id, labeler.current_training_image_id, datetime.datetime.now().date(), labeler.last_session.time(), datetime.datetime.now().time(), diagnosis, None, None)
    db.session.add(label)
    db.session.commit()
    if coordinates != None:
        cell_list = [TrainingImageLabelCell(label.id, x, y, None, None) for x,y in coordinates]
        for i in cell_list:
            db.session.add(i)
        db.session.commit()
    
    current_training_image = label.trainingimage
    if current_training_image.total_labels >= label_limit:
        return 'Not accepting anymore labels for this image'
        
    if current_training_image.total_labels < label_limit:
        current_training_image.total_labels += 1
    
    # limit reached
    if current_training_image.total_labels >= label_limit:
        label_list = {'No Malaria':[], 'Falciparum':[], 'Vivax':[]}
        label_total = 0
        percent_list = {'No Malaria':0, 'Falciparum':0, 'Vivax':0}
        sorted_keys = ('No Malaria', 'Falciparum', 'Vivax')
        label_count = {'No Malaria':0, 'Falciparum':0, 'Vivax':0}
        for i in current_training_image.training_image_labels[0:]:
            label_list[i.initial_label].append(i)
            label_total += 1
        # 1cho
        x = sorted(map(lambda x: (x, len(x), x[0].initial_label), filter(label_list.values(), lambda x: len(x) != 0)))[:2]
        
        # Calculate %
        for i in label_list:
            percent_list[i] = float(len(label_list[i]))/float(label_total)
        # POP THE LEAST
            
        # messy stuff here, finalize training image, each label and each labeler
        
    
@crowd.route('/crowd/session/',  methods = ['GET', 'POST'])
@login_required
def session():
    # Constants
    labeler = Labeler.query.filter_by(user_id=current_user.id).first()
    
    # LABEL SUBMITTED
    if request.method == 'POST' and request.form:
        # Check if data submitted in request.form is valid
        
        # Print all for debugging
        for i in request.form:
            print i + ': ' + request.form[i]
        
        # Unsure
        if request.form.getlist('unsure'):
            makeTrainingImageLabel(labeler, 'Undeterminable', None)
            
        else:
            # No Malaria
            if not request.form.getlist('with_malaria'):
                makeTrainingImageLabel(labeler, 'No Malaria', None)
                
            else:
                # With Falciparum
                if request.form.getlist('with_falciparum'):
                    # String to tuples
                    coordinates = [(tuple(int(j) for j in re.split(',',i))) for i in re.findall('[0-9]+,[0-9]+', str(request.form.getlist('falciparum_coordinates')))]
                    makeTrainingImageLabel(labeler, 'Falciparum', coordinates)
                
                # With Vivax
                if request.form.getlist('with_vivax'):
                    coordinates = [(tuple(int(j) for j in re.split(',',i))) for i in re.findall('[0-9]+,[0-9]+', str(request.form.getlist('vivax_coordinates')))]
                    makeTrainingImageLabel(labeler, 'Vivax', coordinates)
            
        # DONE LABELING
        # UNCOMMENT NEXT LINES TO REMOVE PENDING LABEL FROM LABELER
        labeler.current_training_image_id = None
        labeler.last_session = datetime.datetime.now()
        db.session.add(labeler)
        db.session.commit()
        return redirect('/crowd/index/')
        
    # START LABELING
    
    # Check if labeler still has pending labels
    if labeler.current_training_image_id !=  None:
        training_image_to_label = TrainingImage.query.filter_by(id=labeler.current_training_image_id).first()
        # Check if pending label still has to be labeled
        if training_image_to_label.total_labels < label_limit:
            return render_template("/crowd/session.html", user = current_user, labeler = labeler, training_image_to_label = training_image_to_label)
        # else give him another training image
            
    # Normal procedure
    # Adjust top_n_labels if there are fewer TrainingImages
    global top_n_labels

    '''
    total_training_images = TrainingImage.query.count()
    if total_training_images < top_n_labels:
        top_n_labels = total_training_images
    
    # Get 1 random from top n labels
    training_image_to_label = TrainingImage.query.order_by(TrainingImage.total_labels.desc())[random.randrange(top_n_labels)]

    prevLabeled = TrainingImageLabel.query(image_id).filter_by(labeler_id = labeler.id) 
    availableImgs = TrainingImage.query(image_id, total_labels).outerjoin(prevLabeled,TrainingImage.image_id = prevLabeled.image_id, prevLabeled.image_id=None)
    training_image_to_label = availableImgs.query.order_by(availableImgs.total_labels.desc())[random.randrange(top_n_labels)]
    '''
    
    training_images = TrainingImage.query.order_by(TrainingImage.total_labels.desc()).all()

    for i in training_images:
        for j in i.training_image_labels:
            if j.labeler_id == labeler.id:
                training_images.remove(i)
    
    training_image_to_label = random.choice(training_images[:top_n_labels])
    
    # If there are no more images to label
    if training_image_to_label == None:
        return render_template("/crowd/session.html", user = current_user, labeler = labeler, training_image_to_label = None)
    
    # UNCOMMENT NEXT LINES TO SAVE PENDING LABEL TO LABELER
    labeler.current_training_image_id = training_image_to_label.id
    labeler.last_session = datetime.datetime.now()
    db.session.add(labeler)
    db.session.commit()
    
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