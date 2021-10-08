from app import db, login_manager
from datetime import datetime, date
from sqlalchemy.orm import backref

#initialize db data for user
@login_manager.user_loader
def load_user():
    return Admin.query.get(int(user_id))

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100))
    username = db.Column(db.String(30))
    password = db.Column(db.String(128))
    photo = db.Column(db.String(100), default='avatar.jpg')
    etat = db.Column(db.Boolean)

class Year(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Date)
    status = db.Column(db.Boolean)

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100))
    genre = db.Column(db.String(8))
    contact = db.Column(db.String(15))
    email = db.Column(db.String(50))
    address = db.Column(db.String(150))
    photo = db.Column(db.String(100), default='avatar.jpg')
    lecturers = db.relationship('Lecturer', backref='person_lecturer', lazy='dynamic')
    students = db.relationship('Student', backref='person_student', lazy='dynamic')

class Lecturer(db.Model):
    matricule = db.Column(db.String(15), primary_key=True)
    status = db.Column(db.Boolean)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    affectations_lect = db.relationship('Affectation', backref='lecturer_affectation', lazy='dynamic')

class Course(db.Model):
    id = db.Column(db.String(15), primary_key=True)
    designation = db.Column(db.String(30))
    duration = db.Column(db.Integer)
    affectations = db.relationship('Affectation', backref='course_affectation', lazy='dynamic')

class Affectation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    lecturer_id = db.Column(db.String(15), db.ForeignKey('lecturer.matricule'), nullable=False)
    course_id = db.Column(db.String(15), db.ForeignKey('course.id'), nullable=False)

class Student(db.Model):
    matricule = db.Column(db.String(15), primary_key=True)
    status = db.Column(db.Boolean)
    attendances = db.relationship('Attendance', backref='student_attendance', lazy='dynamic')
    schoolfees = db.relationship('SchoolFees', backref='student_schoolfees', lazy='dynamic')
    person_sid = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    faculty_sid = db.Column(db.String(15), db.ForeignKey('faculty.id'), nullable=False)

class Faculty(db.Model):
    id = db.Column(db.String(15), primary_key=True)
    name = db.Column(db.String(20))
    students_fac = db.relationship('Student', backref='faculty_student', lazy='dynamic')
    depatments = db.relationship('Department', backref='faculty_department', lazy='dynamic')

class Department(db.Model):
    id = db.Column(db.String(15), primary_key=True)
    name = db.Column(db.String(20))
    levels = db.relationship('Level', backref='department_level', lazy='dynamic')
    faculty_id = db.Column(db.String(15), db.ForeignKey('faculty.id'), nullable=False)

class Level(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    designation = db.Column(db.String(30))
    department_id = db.Column(db.String(15), db.ForeignKey('department.id'), nullable=False)

class SchoolFees(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer)
    student_fid = db.Column(db.String(15), db.ForeignKey('student.matricule'), nullable=False)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=date.today())
    time = db.Column(db.Time)
    types = db.relationship('Type', backref='attendance_type', lazy='dynamic')
    student_id = db.Column(db.String(15), db.ForeignKey('student.matricule'), nullable=False)

class Type(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    designation = db.Column(db.String(20))
    attendance_id = db.Column(db.Integer, db.ForeignKey('attendance.id'), nullable=False)