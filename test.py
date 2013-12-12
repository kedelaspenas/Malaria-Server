from crowd.models import *
import datetime
approval_percent = 0.51

labeler = Labeler.query.all(2)
current_training_image = TrainingImage.query.all()[0]

label_list = {'No Malaria':[], 'Falciparum':[], 'Vivax':[]}
label_total = 0
percent_list = {'No Malaria':0, 'Falciparum':0, 'Vivax':0}
for i in current_training_image.training_image_labels[0:]:
    label_list[i.initial_label].append(i)
    label_total += 1

'''    
# 1cho's sorting algo
sorted_list = sorted(map(lambda x: (x, len(x), x[0].initial_label), filter(label_list.values(), lambda x: len(x) != 0)))[:2]
'''

# Calculate label weights with respect to labeler rating
total_label_weight = 0.0
label_weight = {'No Malaria':0.0, 'Falciparum':0.0, 'Vivax':0.0}

for i in label_list:
    for j in label_list[i]:
        label_weight[i] += j.labeler.labeler_rating
        total_label_weight += j.labeler.labeler_rating

print label_weight

# Calculate percents with respect to weights
label_percent = {'No Malaria':0.0, 'Falciparum':0.0, 'Vivax':0.0}
for i in label_weight:
    label_percent[i] = label_weight[i]/total_label_weight

print label_percent

# Get majority label >= approval_percent
final_label = 'Undeterminable'
for i in label_percent:
    if label_percent[i] >= approval_percent:
        final_label = i
        break

print final_label

# IF LABELER IS AN EXPERT
'''
if labeler.labelertype == 'Expert':
    final_label = label.initial_diagnosis
'''

# Finalize label
current_training_image.final_label_1 = final_label
current_training_image.date_finalized = datetime.datetime.now()
db.session.add(current_training_image)

for i in label_list:
    for j in label_list[i]:
        j.correct_label = final_label
        j.labeler.total_images_labeled += 1
        if j.initial_label == final_label:
            j.labeler_correct = True
            j.labeler.total_correct_images_labeled += 1
            # INCREASE LABELER RATING
        else:
            # DECREASE LABELER RATING
            pass
        db.session.add(j)
        db.session.add(j.labeler)

db.session.commit()
            
