from flask import render_template, request, redirect, url_for, flash
from config import app
from models.book import Book

@app.route('/books')
def list_books():
    books = Book.get_all()
    return render_template('books/list.html', books=books)

@app.route('/books/create', methods=['GET', 'POST'])
def create_book():
    if request.method == 'POST':
        title = request.form['title']
        code = request.form['code']
        acquisition_date = request.form['acquisition_date']
        quantity = int(request.form['quantity'])
        status = request.form['status']

        
        Book.create(title, code, acquisition_date, quantity, status)
        flash('Libro Agregado', 'success')
        return redirect(url_for('list_books'))
    return render_template('books/create.html')

@app.route('/books/edit/<int:id>', methods=['GET', 'POST'])
def edit_book(id):
    book = Book.get_by_id(id)
    if request.method == 'POST':
        title = request.form['title']
        code = request.form['code']
        acquisition_date = request.form['acquisition_date']
        quantity = int(request.form['quantity'])
        status = request.form['status']

        
        Book.update(id, title, code, acquisition_date, quantity, status)
        flash('Libro Actualizado', 'success')
        return redirect(url_for('list_books'))
    return render_template('books/edit.html', book=book)

@app.route('/books/delete/<int:id>')
def delete_book(id):
    success, message = Book.delete(id)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')
    return redirect(url_for('list_books'))