from flask import render_template, request, redirect, url_for, flash, jsonify
from config import app
from models.book import Book
from controllers.validation import validate_title, validate_code, validate_acquisition_date, validate_quantity
from config import mysql

@app.route('/books')
def list_books():
    books = Book.get_all()
    return render_template('books/list.html', books=books)

@app.route('/books/create', methods=['GET', 'POST'])
def create_book():
    if request.method == 'POST':
        title = request.form.get('title')
        code = request.form.get('code')
        acquisition_date = request.form.get('acquisition_date')
        quantity = request.form.get('quantity')
        status = request.form.get('status')

        # Aqui validamos el titulo 
        is_valid, message = validate_title(title)
        if not is_valid:
            flash(message, 'error')
            return redirect(url_for('create_book'))

        # Aqui validamos el código
        is_valid, message = validate_code(code)
        if not is_valid:
            flash(message, 'error')
            return redirect(url_for('create_book'))
        
        # Aqui validamos la Fecha Ingreso
        is_valid, message = validate_acquisition_date(acquisition_date)
        if not is_valid:
            flash(message, 'error')
            return redirect(url_for('create_book'))

        # Aqui validamos cantidad
        is_valid, quantity = validate_quantity(quantity)
        if not is_valid:
            flash(quantity, 'error')  # Aquí usamos 'quantity' porque contiene el mensaje de error.
            return redirect(url_for('create_book'))

        # Creamos el libro si todas las validaciones son exitosas
        Book.create(title, code, acquisition_date, quantity, status)
        flash('Libro Agregado', 'success')
        return redirect(url_for('list_books'))

    return render_template('books/create.html')

@app.route('/books/edit/<int:id>', methods=['GET', 'POST'])
def edit_book(id):
    book = Book.get_by_id(id)

    if not book:
        flash('Libro no encontrado.', 'error')
        return redirect(url_for('list_book'))
    
    if request.method == 'POST':
        title = request.form['title']
        code = request.form['code']
        acquisition_date = request.form['acquisition_date']
        quantity = int(request.form['quantity'])
        status = request.form['status']

        fields = {
            'title': title,
            'code': code,
            'acquisition_date': acquisition_date,
            'quantity': quantity,
            
        }

        for field_name, field_value in fields.items():
            validator = globals().get(f'validate_{field_name}')
            if validator:
                is_valid, message = validator(field_value)
                if not is_valid:
                    flash(message, 'error')
                    return redirect(url_for('edit_book', id=id))

        Book.update(id, title, code, acquisition_date, status, quantity)
        flash('Libro editado con éxito', 'success')
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


@app.route('/books/search')
def search_books():
    query = request.args.get('query', '')
    print(f"Searching for: {query}")
    
    cur = mysql.connection.cursor()
    sql_query = """
        SELECT id_book, title, code, quantity 
        FROM books 
        WHERE title LIKE %s AND quantity > 0 AND status = 'DISPONIBLE'
        LIMIT 10
    """
    print(f"SQL Query: {sql_query}")
    
    cur.execute(sql_query, (f'%{query}%',))
    books = cur.fetchall()
    cur.close()
    
    print(f"Found {len(books)} books")
    
    result = [{
        'id': book[0],
        'title': book[1],
        'code': book[2],
        'available': book[3]
    } for book in books]
    
    print(f"Returning: {result}")
    return jsonify(result)