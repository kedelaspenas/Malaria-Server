from flask import Blueprint, render_template

crowd =  Blueprint('crowd', __name__, template_folder='templates', static_folder='static', static_url_path='/crowd/static')

from crowd import views