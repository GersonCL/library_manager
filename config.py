from flask import Flask, render_template, request
from flask_mysqldb import MySQL

app = Flask(__name__)


#version v 1.0.5.3


# Configuración de la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Niarosa70./@'
app.config['MYSQL_DB'] = 'library_db'

mysql = MySQL(app)

@app.route('/students', methods=['GET'])
def list_students():
    query = request.args.get('query', '').strip()
    cursor = mysql.connection.cursor()

    if query:
        cursor.execute("SELECT * FROM students WHERE name LIKE %s OR student_id LIKE %s", (f'%{query}%', f'%{query}%'))
        filtered_students = cursor.fetchall()
    else:
        filtered_students = []  # Lista vacía si no hay búsqueda

    cursor.close()

    return render_template('students/list.html', students=filtered_students, query=query)
