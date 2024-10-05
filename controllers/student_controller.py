from flask import render_template, request, redirect, url_for, flash
from config import app
from models.student import Student

@app.route('/students')
def list_students():
    students = Student.get_all()
    return render_template('students/list.html', students=students)

@app.route('/students/create', methods=['GET', 'POST'])
def create_student():
    if request.method == 'POST':
        name = request.form['name']
        lastname = request.form['lastname']
        student_id = request.form['student_id']
        secondary_school = request.form['secondary_school']
        grade = request.form['grade']
        section = request.form['section']
        Student.create(name, lastname, student_id, secondary_school, grade, section)
        flash('Alumno Agregado', 'success')
        return redirect(url_for('list_students'))
    return render_template('students/create.html')

@app.route('/students/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    student = Student.get_by_id(id)
    if request.method == 'POST':
        name = request.form['name']
        lastname = request.form['lastname']
        student_id = request.form['student_id']
        secondary_school = request.form['secondary_school']
        grade = request.form['grade']
        section = request.form['section']
        Student.update(id, name, lastname, student_id, secondary_school, grade, section)
        flash('Alumno Editado', 'success')
        return redirect(url_for('list_students'))
    return render_template('students/edit.html', student=student)

@app.route('/students/delete/<int:id>')
def delete_student(id):
    success, message = Student.delete(id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    return redirect(url_for('list_students'))