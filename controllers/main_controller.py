from flask import render_template, request, redirect, url_for, flash
from config import app

@app.route('/')
def index():
    return render_template('index.html')