from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)

# Configuración de la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Niarosa70./@'
app.config['MYSQL_DB'] = 'biblioteca'

mysql = MySQL(app)