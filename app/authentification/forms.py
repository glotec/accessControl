from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask.ext.wtf.html5 import URLField
from wrforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField, DecimalField
from wrforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, url
from wrforms.ext.sqlalchemy.fields import QuerySelectField

from ..models import Admin, Type, Cours

def AddAdminForm(FlaskForm):
    fullname = StringField('fullname', validators=[DataRequired("Champ noms obligatoire"), Length(min=2, max=100, message="Veillez respecté les caractères")])
    username = StringField('username', validators=[DataRequired("Champs nom d'utilisateur oblicatoire"), Length(min=2, max=100, message="Veillez respecté les caractères")])
    password = PasswordField('password', validators=[DataRequired("Champs mot de passe obligatoire")])
    role = StringField('role', validators=[DataRequired("Champ role obligatoire"), Length(min=4, max=10, message="Veillez respecté les caractères")])
    photo = FileField('profileImage', validators=[FileAllowed(['jpg', 'png', 'jpeg'], 'Seul jpg, png et jpeg sont autorisés')])
    status = BooleanField('status', validators=[DataRequired("Champs etat admin obligatoire")])
    submit = SubmitField('signup')

    def validate_username(self, username):
        user = Admin.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError("Cet utilisateur existe déjà")

# def AddCourseForm(FlaskForm):
#     designation = StringField('designation')