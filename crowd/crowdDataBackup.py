import datetime
from crowd.models import *

'''
Already appended to reset.py file, look for the "# CROWDSOURCING START" comment
'''

#LabelerType
db.session.add(LabelerType('Novice'))
db.session.add(LabelerType('Regular'))
db.session.add(LabelerType('Expert'))

#Labeler
db.session.add(Labeler(1,0,0, datetime.datetime(2013,12,5,0,0), 1.0, 1))
db.session.add(Labeler(2,0,0, datetime.datetime(2013,12,5,0,0), 1.0, 2))
db.session.add(Labeler(3,0,0, datetime.datetime(2013,12,5,0,0), 1.0, 3))

#TrainingImage
for i in xrange(1,9):
    db.session.add(TrainingImage(i,0,'notYetKnown',None))

#TrainingImageLabel
for i in xrange(1,9):
    for j in range(1,9):
        db.session.add(TrainingImageLabel(i,datetime.date(2013,12,5),datetime.time(j,j), datetime.time(j,j+2),1, None, None))

#TrainingImageLabelCell
for i in xrange(1,9):
    for j in xrange(1,9):
        for k in xrange(1,9):
            db.session.add(TrainingImageLabelCell(j,k*100,k*100, None,None))

db.session.commit()
