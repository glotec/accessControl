from flask import render_template, url_for, redirect, request, session
from .. import db
from ..models import Admin
from app.authentification.forms import AddAdminForm

from . import auth
from . import user

@auth.route('/super-admin/register', methods=['GET', 'POST'])
def super_add_register():

   title = 'Super Administrateur'

   #initialize form
   form=AddAdminForm()

   return render_template('authentification/admin.html', title=title, form=form)

@auth.route('/login', methods=('GET', 'POST'))
def login():
   title = 'Connexion'
   
   #Requete de verification adin dans la db
   ver_user = Admin.query.filter(Admin.role=='admin').first()

   #Verification existance admin
   if ver_user:
      pass
   else:
      return redirect(url_for('auth.super_add_register'))

   return render_template('authentification/login.html', title=title)

@auth.route('/cours', methods=('GET', 'POST'))
def cours():
   return render_template('authentification/cours.html')

@user.route('/attendance', methods=['GET', 'POST'])
def attendance():
   return render_template('user/login.html')