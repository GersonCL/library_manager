from flask import render_template, request, redirect, url_for, flash
from config import app
from models.loan import Loan
from models.student import Student
from models.book import Book

@app.route('/loans')
def list_loans():
    loans = Loan.get_all()
    return render_template('loans/list.html', loans=loans)

@app.route('/loans/create', methods=['GET', 'POST'])
def create_loan():
    if request.method == 'POST':
        id_student = request.form['id_student']
        loan_days = int(request.form['loan_days'])
        book_ids = request.form.getlist('book_ids')
        
        success, message = Loan.create(id_student, loan_days, book_ids)
        if success:
            flash(message, 'success')
            return redirect(url_for('list_loans'))
        else:
            flash(message, 'error')
    
    students = Student.get_all()
    books = Book.get_available()
    return render_template('loans/create.html', students=students, books=books)

@app.route('/loans/edit/<int:id>', methods=['GET', 'POST'])
def edit_loan(id):
    loan = Loan.get_by_id(id)
    if request.method == 'POST':
        return_date = request.form['return_date']
        renewals = int(request.form['renewals'])
        late_fee = float(request.form['late_fee'])
        
        Loan.update(id, return_date, renewals, late_fee)
        flash('Pretamos editado', 'success')
        return redirect(url_for('list_loans'))
    
    return render_template('loans/edit.html', loan=loan)

@app.route('/loans/delete/<int:id>')
def delete_loan(id):
    Loan.delete(id)
    flash('Prestamo eliminado', 'success')
    return redirect(url_for('list_loans'))