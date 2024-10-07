from config import mysql
from datetime import datetime, timedelta
from models.book import Book
from models.student import Student

class Loan:
    def __init__(self, id_student, loan_date, return_date, loan_days, renewals=0, late_fee=0.00):
        self.id_student = id_student
        self.loan_date = loan_date
        self.return_date = return_date
        self.loan_days = loan_days
        self.renewals = renewals
        self.late_fee = late_fee

    @staticmethod
    def create(id_student, loan_days, book_ids):
        # Verificar si el estudiante ya tiene el máximo de libros prestados
        current_loans = Student.get_borrowed_books_count(id_student)
        if current_loans + len(book_ids) > 3:
            return False, "El estudiante no puede prestar más de 3 libros en total."

        cur = mysql.connection.cursor()
        loan_date = datetime.now().date()
        return_date = loan_date + timedelta(days=loan_days)
        
        try:
            # Insertar el nuevo préstamo en la tabla loans
            cur.execute("INSERT INTO loans (id_student, loan_date, return_date, loan_days) VALUES (%s, %s, %s, %s)",
                        (id_student, loan_date, return_date, loan_days))
            id_loan = cur.lastrowid  # Obtener el ID del préstamo recién creado

            # Asociar cada libro al préstamo y actualizar su cantidad
            for book_id in book_ids:
                # Insertar en la tabla loan_books
                cur.execute("INSERT INTO loan_books (id_loan, id_book, return_date) VALUES (%s, %s, %s)",
                            (id_loan, book_id, return_date))
                
                # Disminuir la cantidad disponible del libro
                cur.execute("UPDATE books SET quantity = quantity - 1 WHERE id_book = %s", (book_id,))

            # Incrementar el contador de libros prestados del estudiante
            Student.increment_borrowed_books(id_student)

            # Confirmar todos los cambios en la base de datos
            mysql.connection.commit()

            return True, "Préstamo creado."
        except Exception as e:
            # Si ocurre algún error, deshacer todos los cambios
            mysql.connection.rollback()
            return False, f"Error al crear el préstamo: {str(e)}"
        finally:
            # Cerrar el cursor de la base de datos
            cur.close()

    @staticmethod
    def get_all():
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT l.*, s.name, s.lastname, GROUP_CONCAT(b.title SEPARATOR ', ') as books
            FROM loans l
            JOIN students s ON l.id_student = s.id_student
            JOIN loan_books lb ON l.id_loan = lb.id_loan
            JOIN books b ON lb.id_book = b.id_book
            GROUP BY l.id_loan
        """)
        loans = cur.fetchall()
        cur.close()
        return loans

    @staticmethod
    def get_by_id(id_loan):
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT l.*, s.name, s.lastname, GROUP_CONCAT(b.title SEPARATOR ', ') as books
            FROM loans l
            JOIN students s ON l.id_student = s.id_student
            JOIN loan_books lb ON l.id_loan = lb.id_loan
            JOIN books b ON lb.id_book = b.id_book
            WHERE l.id_loan = %s
            GROUP BY l.id_loan
        """, (id_loan,))
        loan = cur.fetchone()
        cur.close()
        return loan

    @staticmethod
    def update(id_loan, return_date, renewals, late_fee):
        #todo: autoincrementar las renovaciones, calcular la fecha de devolucion
        cur = mysql.connection.cursor()
        cur.execute("UPDATE loans SET return_date = %s, renewals = %s, late_fee = %s WHERE id_loan = %s",
                    (return_date, renewals, late_fee, id_loan))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def delete(id_loan):
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_book FROM loan_books WHERE id_loan = %s", (id_loan,))
        book_ids = [row[0] for row in cur.fetchall()]
        
        for book_id in book_ids:
            Book.increase_quantity(book_id)
        
        cur.execute("DELETE FROM loan_books WHERE id_loan = %s", (id_loan,))
        cur.execute("DELETE FROM loans WHERE id_loan = %s", (id_loan,))
        mysql.connection.commit()
        cur.close()