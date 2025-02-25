from flask import render_template, request, redirect, url_for, flash, jsonify
from config import app
from models.book import Book
from controllers.validation import validate_title, validate_author, validate_materia, validate_code, validate_acquisition_date, validate_quantity
from config import mysql

@app.route('/books', methods=['GET'])
def list_books():
    query = request.args.get('query', '')
    books = []  #lista vacia si no hay busquedas 

    if query:
        # Si hay un término de búsqueda, busca los libros
        books = Book.search_by_title_author(query) 

    return render_template('books/list.html', books=books, query=query)

@app.route('/books/create', methods=['GET', 'POST'])
def create_book():
    if request.method == 'POST':
        title = request.form.get('title')
        code = request.form.get('code')
        author = request.form.get('author')
        materia = request.form.get('materia')
        acquisition_date = request.form.get('acquisition_date')
        quantity = request.form.get('quantity')
        status = request.form.get('status')

        # Aqui validamos el titulo 
        is_valid, message = validate_title(title)
        if not is_valid:
            flash(message, 'error')
            return redirect(url_for('create_book'))
        
        # Aqui validamos el autor
        is_valid, message = validate_author(author)
        if not is_valid:
            flash(message, 'error')
            return redirect(url_for('create_book'))
        
        is_valid, message = validate_materia(materia)
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
        Book.create(title, author, materia, code, acquisition_date, quantity, status)
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
        author = request.form['author']
        materia = request.form['materia']
        code = request.form['code']
        acquisition_date = request.form['acquisition_date']
        quantity = int(request.form['quantity'])
        status = request.form['status']

        fields = {
            'title': title,
            'author': author,
            'materia': materia,
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

        Book.update(id, title, author, materia, code, acquisition_date, status, quantity)
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

#ESTE ES EL SEARCH DE PRESTAMOS NO MODIFICAR......
@app.route('/books/search')
def search_books():
    query = request.args.get('query', '')
    print(f"Searching for: {query}")
    
    cur = mysql.connection.cursor()
    sql_query = """
        SELECT id_book, title, author, materia, code, quantity 
        FROM books 
        WHERE (title LIKE %s OR author LIKE %s OR materia LIKE %s OR code LIKE %s)
        AND quantity > 0 AND status = 'DISPONIBLE'
        LIMIT 10
    """
    print(f"SQL Query: {sql_query}")
    
    search_term = f'%{query}%'
    cur.execute(sql_query, (search_term, search_term, search_term, search_term))
    books = cur.fetchall()
    cur.close()
    
    print(f"Found {len(books)} books")
    
    result = [{
        'id': book[0],
        'title': book[1],
        'author': book[2],
        'materia': book[3],
        'code': book[4],
        'available': book[5]
    } for book in books]
    
    print(f"Returning: {result}")
    return jsonify(result)


#----------------------------------------------------------------------------------------------
#ESTA ES LA BUSQUEDA DE LIBROS EN LIBROS -NO MODIFICAR-..........

@app.route('/books/search_by_title_author', methods=['GET'])
def search_books_by_title_author():
    query = request.args.get('query', '')
    print(f"Searching for: {query}")

    # Dividir el término de búsqueda en partes
    search_terms = query.split()
    
    # Crear las condiciones de búsqueda
    title_conditions = ' OR '.join(['title LIKE %s'] * len(search_terms))
    author_conditions = ' OR '.join(['author LIKE %s'] * len(search_terms))
    materia_conditions = ' OR '.join(['materia LIKE %s'] * len(search_terms))

    sql_query = f"""
        SELECT id_book, title, author, materia, code, acquisition_date, quantity, status
        FROM books 
        WHERE ({title_conditions} OR {author_conditions} OR {materia_conditions})
    """
    
    # Preparar los parámetros para la consulta
    params = []
    for term in search_terms:
        like_term = f'%{term}%'
        params.extend([like_term] * 3)  # Se repite el término para título, autor y materia

    cur = mysql.connection.cursor()
    cur.execute(sql_query, params)
    books = cur.fetchall()
    cur.close()

    print(f"Found {len(books)} books")

    # Renderiza la plantilla con los resultados
    return render_template('books/list.html', books=books)