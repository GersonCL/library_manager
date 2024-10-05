from flask import Flask
from config import app, mysql
from controllers import student_controller, book_controller

app.secret_key = 'admin' 


if __name__ == '__main__':
    app.run(debug=True)