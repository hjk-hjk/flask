from flask import Blueprint

psd_bp = Blueprint('psd_bp',__name__,
                     template_folder='templates')
from . import routes