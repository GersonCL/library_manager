from flask import render_template, request, redirect, url_for, flash, jsonify
from config import app
from models.returns import Returns
from models.loan import Loan
import logging

@app.route('/returns')
def list_returns():
    try:
        returns = Returns.get_all()
        if not returns:
            flash('No se encontraron devoluciones.', 'info')
        logging.info(f"Número de devoluciones recuperadas: {len(returns)}")
        return render_template('returns/list.html', returns=returns)
    except Exception as e:
        logging.error(f"Error al listar las devoluciones: {e}")
        flash('Ocurrió un error al cargar las devoluciones.', 'error')
        return render_template('returns/list.html', returns=[])

@app.route('/returns/create', methods=['GET', 'POST'])
def create_return():
    if request.method == 'POST':
        # Obtenemos el ID del préstamo (loan) enviado desde el formulario
        id_loan = request.form['id_loan']
        books_to_return = []
        # Iteramos sobre todos los elementos enviados desde el formulario
        for key, value in request.form.items():
            # Verificamos si el campo del formulario se refiere a un libro a devolver
            # 'books_to_return[<book_id>]' y si la cantidad es mayor a 0
            if key.startswith('books_to_return[') and int(value) > 0:
                # Extraemos el 'book_id' del nombre del campo (formato: 'books_to_return[<book_id>]')
                book_id = int(key.split('[')[1].split(']')[0])
                quantity = int(value)
                books_to_return.append((book_id, quantity))
        
        late_fee = float(request.form.get('late_fee', 0))
        
        success, message = Returns.create(id_loan, books_to_return, late_fee)
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
        
    # Obtener préstamos activos actualizados, tanto para GET como para POST
    active_loans = Loan.get_active_loans()
    return render_template('returns/create.html', loans=active_loans)

@app.route('/returns/get_loan_books/<int:id_loan>')
def get_loan_books(id_loan):
    books = Loan.get_books_for_loan(id_loan)
    return jsonify(books)