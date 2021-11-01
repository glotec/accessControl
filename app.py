from flask import Flask, render_template, redirect, url_for, session, request, flash, Response
from flask_mysqldb import MySQL, MySQLdb
from werkzeug.utils import secure_filename
from passlib.hash import sha256_crypt
import os

#import magic
import urllib.request

from functools import wraps
from datetime import datetime

import numpy as np
import cv2
import face_recognition

app = Flask(__name__)
app.secret_key = "access_control_app"

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'attendance_control'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

now = datetime.now()

UPLOAD_FOLDER = 'static/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/admin')
def admin():
    return render_template('admin.html')

#Create user
@app.route('/upload', methods=["POST", "GET"])
def upload():
    cursor = mysql.connection.cursor()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        fullname = request.form['fullname']
        username = request.form['username']
        password = sha256_crypt.encrypt(str(request.form['password']))

        cur.execute("INSERT INTO admin(fullname, username, password) VALUES (%s,%s,%s)", [fullname, username, password])
        mysql.connection.commit()
        cur.close()
        flash('Admin ajouté avec succès')
    return redirect('/admin')

#Login
@app.route('/', methods=["POST", "GET"])
def login():
    if request.method == 'POST':
        #get form fields
        username = request.form['username']
        password_candidate = request.form['password']

        #create cursor
        cur = mysql.connection.cursor()

        #get admin by username
        result = cur.execute("SELECT * FROM admin WHERE username = %s", [username])

        #check result
        if result > 0:
            #Get stored hash
            data = cur.fetchone()
            password = data['password']

            #compare password
            if sha256_crypt.verify(password_candidate, password):
                #Passed
                session['logged_in'] = True
                session['username'] = username

                flash('Connecter')
                return redirect(url_for('menu'))
            else:
                flash('Mot de passe incorrect')
                return render_template('login.html')
            #Close connection
            cur.close()
        else:
            flash('Nom d\'utilisateur introuvable')
            return render_template('login.html')

    return render_template('login.html')

#Check if user logged in
def is_logge_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Veillez vous connecter d\'abord', 'danger')
            return redirect(url_for('login'))
    return wrap

#Logout
@app.route('/logout')
def logout():
    session.clear()
    flash('Déconnecter', 'success')
    return redirect(url_for('login'))

# Type
@app.route('/type', methods=["POST", "GET"])
@is_logge_in
def type():
    cursor = mysql.connection.cursor()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        type = request.form['type']
        cur.execute("INSERT INTO faculty(name) VALUES (%s)", [id, type])
        mysql.connection.commit()
        cur.close()
        flash('type de présence enregistré')
        return redirect('/type')
    return render_template('type.html')

@app.route('/attendancetype', methods=["POST", "GET"])
@is_logge_in
def attendancetype():
    cursor = mysql.connection.cursor()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch affectations
    cur.execute("SELECT * FROM type")
    types = cur.fetchall()

    if request.method == 'POST':
        type = request.form['type']
        return redirect(url_for('attedance', type=type))

    return render_template('attendancetype.html', types=types)


# Attendance
@app.route('/attedance', methods=["POST", "GET"])
@is_logge_in
def attedance():
    cursor = mysql.connection.cursor()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # type = request.args.get['type']

    if request.method == 'POST':
        # Get field data
        matricule = request.form['matricule']
        # get student by matricule
        # exist = cur.execute("SELECT matricule, fullname, photo FROM student INNER JOIN person ON student.person_sid = person.id WHERE matricule = %s", [matricule])
        #
        # check if exist
        # if exist > 0:
        # get student data
        results = cur.execute(
            "SELECT matricule, fullname, picture, designation, name FROM student INNER JOIN register ON student.id = register.student_id INNER JOIN promotion ON register.promotion_id = promotion.id INNER JOIN department ON promotion.department_id= department.id WHERE matricule = %s",
            [matricule])
        # flash('cet étudiant existe')

        if results > 0:
            # data = cur.fetchall()
            data = cur.fetchone()
            picture = data['picture']
            # print(picture)
            matricule = data['matricule']
            fulname = data['fullname']

            # Implemente facing recognize

            video_capture = cv2.VideoCapture(0)

            student_image = face_recognition.load_image_file(f'static/upload/{picture}');
            # Esty_image = face_recognition.load_image_file('static/upload/11A0072.jpg');

            student_face_encoding = face_recognition.face_encodings(student_image)[0];
            # esty_face_encoding = face_recognition.face_encodings(Esty_image)[0];

            known_face_encodings = [student_face_encoding];
            known_face_names = [f'{matricule}, {fulname}'];

            while True:

                ret, frame = video_capture.read();

                # Converting the frame from OpenCV's BGR format to the RGB format
                rgb_frame = frame[:, :, ::-1];

                # Finding the face locations and encodings in each frame
                face_locations = face_recognition.face_locations(rgb_frame);
                face_encodings = face_recognition.face_encodings(rgb_frame, face_locations);

                # Now to loop through each face in this frame
                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):

                    # Checking if the face is a match for known faces
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding);

                    name = 'inconnu';

                    # Use the known face with the smallest vector distance to the new face
                    face_distances = face_recognition.face_distance(known_face_encodings, face_encoding);
                    best_match_index = np.argmin(face_distances);

                    if matches[best_match_index]:
                        name = known_face_names[best_match_index];

                    # Draw a box around the face
                    cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2);

                    # Draw a label with the name below the face
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (255, 0, 0), cv2.FILLED);
                    font = cv2.FONT_HERSHEY_DUPLEX;
                    cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1);

                # Display the image
                cv2.imshow('Camera', frame);

                # Hit 'q' on the keyboard to quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break;

                    video_capture.release();
                    cv2.destroyAllWindows();
            # Attendance list
            date_save = now.strftime('%Y-%m-%d %H:%M:%S')
            cur.execute("INSERT INTO attendance (date, register_id, type_id) VALUES(%s, %s, %s)",[date_save, matricule, 1])
            mysql.connection.commit()

        return render_template('attedance.html', data=data)
        # else:
        #     flash('cet étudiant n\'existe pas ):')
    #     return redirect('/attedance')
    return render_template('attedance.html')



#Menu
@app.route('/menu')
@is_logge_in
def menu():
    return render_template('menu.html')

#Dashboard
@app.route('/dashboard')
@is_logge_in
def dashboard():
    return render_template('dashboard.html')


# Course
@app.route('/course', methods=["POST", "GET"])
@is_logge_in
def course():
    cursor = mysql.connection.cursor()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        course = request.form['course']
        hour = request.form['hour']
        cur.execute("INSERT INTO course(designation, duration) VALUES (%s,%s)", [course, hour])
        mysql.connection.commit()
        cur.close()
        flash('Cours enregistré')
        return redirect('/course')
    return render_template('course.html')


# Course
@app.route('/courses')
@is_logge_in
def courses():
    cursor = mysql.connection.cursor()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch affectations
    cur.execute("SELECT * FROM course")
    courses = cur.fetchall()

    return render_template('courses.html', courses=courses)


# Faculty
@app.route('/faculty', methods=["POST", "GET"])
@is_logge_in
def faculty():
    cursor = mysql.connection.cursor()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        faculty = request.form['faculty']
        cur.execute("INSERT INTO faculty(name) VALUES (%s)", [faculty])
        mysql.connection.commit()
        cur.close()
        flash('Faculté enregistré')
        return redirect('/faculty')
    return render_template('faculty.html')


# department
@app.route('/department', methods=["POST", "GET"])
@is_logge_in
def department():
    cursor = mysql.connection.cursor()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch faculty
    cur.execute("SELECT * FROM faculty")
    faculties = cur.fetchall()

    if request.method == 'POST':
        department = request.form['department']
        faculty = request.form['faculty']
        cur.execute("INSERT INTO department(name, faculty_id) VALUES (%s, %s)", [department, faculty])
        mysql.connection.commit()
        cur.close()
        flash('Faculté enregistré')
        return redirect('/department')
    return render_template('department.html', faculties=faculties)


# Promotion
@app.route('/promotion', methods=["POST", "GET"])
@is_logge_in
def promotion():
    cursor = mysql.connection.cursor()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch department
    cur.execute("SELECT * FROM department")
    departments = cur.fetchall()

    if request.method == 'POST':
        promotion = request.form['promotion']
        department = request.form['department']
        cur.execute("INSERT INTO promotion(designation, department_id ) VALUES (%s, %s)", [promotion, department])
        mysql.connection.commit()
        cur.close()
        flash('Faculté enregistré')
        return redirect('/promotion')
    return render_template('promotion.html', departments=departments)


# Fetct year
@app.route('/years')
@is_logge_in
def years():
    cursor = mysql.connection.cursor()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch affectations
    cur.execute("SELECT * FROM year")
    years = cur.fetchall()

    return render_template('years.html', years=years)



# Year
@app.route('/year', methods=["POST", "GET"])
@is_logge_in
def year():
    cursor = mysql.connection.cursor()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        year = request.form['year']
        status = request.form['status']
        cur.execute("INSERT INTO year(year, status) VALUES (%s,%s)", [year, status])
        mysql.connection.commit()
        cur.close()
        flash('Faculté enregistré')
        return redirect('/year')
    return render_template('year.html')


# Student
@app.route('/student', methods=["POST", "GET"])
@is_logge_in
def student():
    cursor = mysql.connection.cursor()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cur.execute("SELECT * FROM year")
    year = cur.fetchall()

    cur.execute("SELECT promotion.id AS p_id, CONCAT(promotion.designation, ' ', department.name) AS promo FROM promotion INNER JOIN department ON promotion.department_id = department.id")
    promotion = cur.fetchall()

    if request.method == 'POST':
        files = request.files.getlist('files[]')
        fullname = request.form['fullname']
        gender = request.form['gender']
        contact = request.form['contact']
        email = request.form['email']
        address = request.form['address']

        print(files)
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                cur.execute(
                    "INSERT INTO student(fullname, gender, contact, email, address, picture) VALUES (%s,%s,%s,%s,%s,%s)",
                    [fullname, gender, contact, email, address, filename])

                # SELECT MAX ID FROM STUDENT
                cur.execute("SELECT MAX(id) AS st_id FROM student")
                data = cur.fetchone()

                # SELECT ACTIF ID FROM YEAR
                cur.execute("SELECT id FROM year WHERE status = 'Actif'")
                y_data = cur.fetchone()

                student = data['st_id']
                year_id = y_data['id']
                matricule = request.form['matricule']
                promotion_id = request.form['promotion']
                # year_id = request.form['year']
                cur.execute("INSERT INTO register (matricule, student_id, promotion_id, year_id) VALUES (%s, %s, %s, %s)",
                            [matricule, student, promotion_id, year_id])
                mysql.connection.commit()
            print(file)
        cur.close()
        flash('Enregistrement étudiant réussi')
        return redirect('/student')
    return render_template('student.html', year=year, promotion=promotion)


# Add new affectation
@app.route('/newaffectation', methods=["POST", "GET"])
@is_logge_in
def newaffectation():
    cursor = mysql.connection.cursor()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch course
    cur.execute("SELECT * FROM course")
    course = cur.fetchall()

    # Fetch promotion
    cur.execute("SELECT * FROM promotion")
    promotions = cur.fetchall()

    if request.method == 'POST':
        date = datetime.now()
        promotion = request.form['promotion']
        course_id = request.form['course_id']
        cur.execute("INSERT INTO affectation(date, promotion_cid, course_id) VALUES (%s,%s,%s)",
                    [date, promotion, course_id])
        mysql.connection.commit()
        cur.close()
        flash('Affectation enregistré')
        return redirect('/affectation')
    return render_template('newaffectation.html', course=course, promotions=promotions)


###############Fetching data ##################
# Affectation
# @app.route('/affectation')
# @is_logge_in
# def affectation():
#     cursor = mysql.connection.cursor()
#     cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#
#     # Fetch affectations
#     cur.execute(
#         "SELECT promotion.id AS p_id, CONCAT(promotion.designation, ' ', department.name) AS promo FROM promotion INNER JOIN department ON promotion.department_id = department.id"
#         # "SELECT course.designation, duration, date, promotion.id AS pid, CONCAT(promotion.designation, ' ', department.name) AS promo FROM course INNER JOIN affectation ON course.id = affectation.course_id INNER JOIN promotion ON affectation.promotion_cid = promotion.id INNER JOIN department ON promotion.department_id = department.id")
#     affect = cur.fetchall()
#
#     return render_template('affectation.html', affect=affect)


# Fees
@app.route('/fees', methods=["POST", "GET"])
@is_logge_in
def fees():
    cursor = mysql.connection.cursor()
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch student
    cur.execute(
        "SELECT matricule, fullname, genre, contact, email, address, photo FROM student INNER JOIN person ON student.person_sid = person.id")
    student = cur.fetchall()

    if request.method == 'POST':
        id = request.form['student_id']
        amount = request.form['amount']
        cur.execute("INSERT INTO school_fees(amount, student_fid ) VALUES (%s, %s)", [amount, id])
        mysql.connection.commit()
        cur.close()
        flash('Payement enregistré')
        return redirect('/fees')
    return render_template('fees.html', student=student)


if __name__ == '__main__':
    app.secret_key = 'access_control'
    app.run(debug=True)