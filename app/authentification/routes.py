from flask import render_template

from . import auth
from . import user

@auth.route('/register', methods=['GET', 'POST'])
def register():
   return render_template('authentification/admin.html')

@auth.route('/login', methods=('GET', 'POST'))
def login():
   return render_template('authentification/login.html')

@auth.route('/cours', methods=('GET', 'POST'))
def cours():
   return render_template('authentification/cours.html')

@user.route('/attendance', methods=['GET', 'POST'])
def attendance():
   return render_template('user/login.html')