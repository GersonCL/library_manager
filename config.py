from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)


#version v 1.0.5.3


# Configuración de la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'admin'
app.config['MYSQL_DB'] = 'library_db'

mysql = MySQL(app)