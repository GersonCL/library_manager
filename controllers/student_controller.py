from flask import render_template, request, redirect, url_for, flash
from config import app
from models.student import Student
from controllers.validation import validate_name, validate_lastname, validate_student_id, validate_grade, validate_secondary_school, validate_section

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

        #Aqui validamos los campos a partir de validation.py
        is_valid, message = validate_name(name)
        if not is_valid:
            flash(message, 'error')
            return redirect(url_for('create_student'))
        
        is_valid, message = validate_lastname(lastname)
        if not is_valid:
            flash(message, 'error')
            return redirect(url_for('create_student'))
        
        is_valid, message = validate_student_id(student_id)
        if not is_valid:
            flash(message, 'error')
            return redirect(url_for('create_student'))
        
        is_valid, message = validate_secondary_school(secondary_school)
        if not is_valid:
            flash(message, 'error')
            return redirect(url_for('create_student'))
        
        is_valid, message = validate_grade(grade)
        if not is_valid:
            flash(message, 'error')
            return redirect(url_for('create_student'))
        
        is_valid, message = validate_section(section)
        if not is_valid:
            flash(message, 'error')
            return redirect(url_for('create_student'))

        Student.create(name, lastname, student_id, secondary_school, grade, section)
        flash('Alumno Agregado', 'success')
        return redirect(url_for('list_students'))
    return render_template('students/create.html')

@app.route('/students/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    student = Student.get_by_id(id)
    if not student:
        flash('Estudiante no encontrado.', 'error')
        return redirect(url_for('list_students'))

    if request.method == 'POST':
        name = request.form['name']
        lastname = request.form['lastname']
        student_id = request.form['student_id']
        secondary_school = request.form['secondary_school']
        grade = request.form['grade']
        section = request.form['section']

        fields = {
            'name': name,
            'lastname': lastname,
            'student_id': student_id,
            'secondary_school': secondary_school,
            'grade': grade,
            'section': section,
        }

        for field_name, field_value in fields.items():
            validator = globals().get(f'validate_{field_name}')
            if validator:
                is_valid, message = validator(field_value)
                if not is_valid:
                    flash(message, 'error')
                    return redirect(url_for('edit_student', id=id))

        Student.update(id, name, lastname, student_id, secondary_school, grade, section)
        flash('Alumno editado con éxito', 'success')
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