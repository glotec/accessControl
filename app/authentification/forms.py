from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_wtf.html5 import URLField
from wrforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, IntegerField, DecimalField
from wrforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, url
from wrforms.ext.sqlalchemy.fields import QuerySelectField

from ..models import Admin, Type, Cours

def AddAdminForm(FlaskForm):
    

def AddCourseForm(FlaskForm):
    designation = StringField('designation')