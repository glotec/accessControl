from flask import Blueprint

auth = Blueprint('auth', __name__, url_prefix='/auth')

user = Blueprint('user', __name__, url_prefix='/user')
# never forget 
from . import routes