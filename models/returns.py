from config import mysql
from datetime import date
from models.loan import Loan
from models.book import Book
from models.student import Student

class Returns:
    @staticmethod
    def calculate_days_late(expected_date, actual_date):
        if actual_date > expected_date:
            return (actual_date - expected_date).days
        return 0

    @staticmethod
    def update_book_inventory(id_loan):
        cur = mysql.connection.cursor()
        try:
            cur.execute("SELECT id_book FROM loan_books WHERE id_loan = %s", (id_loan,))
            book_ids = [row[0] for row in cur.fetchall()]
            for book_id in book_ids:
                Book.increase_quantity(book_id)
            return len(book_ids)
        finally:
            cur.close()

    @staticmethod
    def create(id_loan, late_fee=0.00):
        cur = mysql.connection.cursor()
        try:
            # Obtener información del préstamo
            cur.execute("SELECT id_student, return_date FROM loans WHERE id_loan = %s", (id_loan,))
            loan_info = cur.fetchone()
            if not loan_info:
                return False, "Préstamo no encontrado."

            id_student, expected_return_date = loan_info
            actual_return_date = date.today()

            # Calcular días de retraso
            days_late = Returns.calculate_days_late(expected_return_date, actual_return_date)

            # Registrar la devolución
            cur.execute("""
                INSERT INTO returns (id_loan, return_date, days_late, late_fee)
                VALUES (%s, %s, %s, %s)
            """, (id_loan, actual_return_date, days_late, late_fee))

            # Actualizar el inventario
            books_returned = Returns.update_book_inventory(id_loan)

            # Actualizar el contador de libros prestados del estudiante
            Student.decrement_borrowed_books_multiple(id_student, books_returned)

            mysql.connection.commit()
            return True, f"Devolución registrada con éxito. Días de retraso: {days_late}"
        except Exception as e:
            mysql.connection.rollback()
            return False, f"Error al registrar la devolución: {str(e)}"
        finally:
            cur.close()

    @staticmethod
    def get_all():
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT r.*, l.id_student, s.name, s.lastname, GROUP_CONCAT(b.title SEPARATOR ', ')
            FROM returns r
            JOIN loans l ON r.id_loan = l.id_loan
            JOIN students s ON l.id_student = s.id_student
            JOIN loan_books lb ON l.id_loan = lb.id_loan
            JOIN books b ON lb.id_book = b.id_book
            GROUP BY r.id_return
        """)
        returns = cur.fetchall()
        cur.close()
        return returns