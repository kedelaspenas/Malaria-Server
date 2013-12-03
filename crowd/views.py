from flask import render_template
from crowd import crowd
from serveus.models import Region
from crowd.models import LabelerType

@crowd.route('/crowd/')
def show():
    regionList = Region.query.all()
    return render_template("home.html", regionList = regionList[1:])
