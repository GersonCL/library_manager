from flask import render_template, request, redirect, url_for, flash
from config import app
from models.returns import Returns
from models.loan import Loan

@app.route('/returns')
def list_returns():
    returns = Returns.get_all()
    return render_template('returns/list.html', returns=returns)

@app.route('/returns/create', methods=['GET', 'POST'])
def create_return():
    if request.method == 'POST':
        id_loan = request.form['id_loan']
        late_fee = float(request.form.get('late_fee', 0))
        success, message = Returns.create(id_loan, late_fee)
        if success:
            flash(message, 'success')
        else:
            flash(message, 'error')
        return redirect(url_for('list_returns'))
    
    active_loans = Loan.get_active_loans()
    return render_template('returns/create.html', loans=active_loans)