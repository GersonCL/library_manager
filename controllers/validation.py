import re

#A partir de aqui son validaciones para el formulario LIBROS
def validate_title(title):
    if len(title) > 150:
        return False, "El límite de título es de 150 caracteres."
    if not title or not re.match(r'^[\w\s]+$', title):
        return False, 'El título es obligatorio y no puede contener caracteres especiales.'
    return True, ''

def validate_code(code):
    if len(code) > 10:
        return False, "El limite de codigo es de 10 digitos"
    if not code or not re.match(r'^[\w\s]+$', code):
        return False, 'El código es obligatorio.'
    return True, ''

#todo: esto se puede hacer en html
def validate_acquisition_date(acquisition_date):
    if not acquisition_date:
        return False, 'La fecha de ingreso es obligatoria'
    return True,''

def validate_quantity(quantity):
    try:
        quantity = int(quantity)
        return True, quantity
    except ValueError:
        return False, 'La cantidad debe ser un número entero.'
    
    #A partir de aqui son validaciones para el formulario ESTUDIANTE
def validate_name(name):
    if len(name) > 50:
        return False, 'El limite de nombre es de 50 caracteres'
    if not name or not re.match(r'^[a-zA-Z\s]+$', name):
        return False, 'El nombre no puede contener numeros ni caracteres especiales'
    return True, ''

def validate_lastname(lastname):
    if len(lastname) > 50:
        return False, 'El limite de nombre es de 50 caracteres'
    if not lastname or not re.match(r'^[a-zA-Z\s]+$', lastname):
        return False, 'El nombre no puede contener numeros ni caracteres especiales'
    return True, ''

#todo: esta validacion no debe ir, el código debe ser automatico
def validate_student_id(student_id):
    if len(student_id) > 10:
        return False, 'El limite de codigo es de 10 digitos'
    if not student_id or not re.match(r'^[\w\s]+$', student_id):
        return False, 'El Codigo estudiante es obligatorio y no puede contener caracteres especiales'
    return True, ''

def validate_secondary_school(secondary_school):
    if len(secondary_school) > 10:
        return False, 'El limite de Escuela es de 10 digitos'
    if not secondary_school or not re.match(r'^[\w\s]+$', secondary_school):
        return False, 'Escuela es obligatorio y no puede contener caracteres especiales'
    return True, ''

def validate_grade(grade):
    if len(grade) > 20:
        return False, 'El limite de grado es de 20 digitos'
    if not grade or not re.match(r'^[a-zA-Z\s]+$', grade):
        return False, 'El grado es obligatorio y no puede contener numero ni caracter especial'
    return True, ''

def validate_section(section):
    if len(section) > 10:
        return False, 'el limite de seccion es de 10 digitos'
    if not section or not re.match(r'^[a-zA-Z\s]+$', section):
        return False, 'La seccion es obligatorio y no puede contener numero ni caracter especial'
    return True, ''

#aqui vamos a validar el fprmulario prestamo.

def validate_loan_days(loan_days):
    try:
        loan_days = int(loan_days)
        return True, loan_days
    except ValueError:
        return False, 'La cantidad debe ser un número entero.'