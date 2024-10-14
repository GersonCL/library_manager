from config import mysql
from datetime import datetime, timedelta
from models.book import Book
from models.student import Student
import logging

class Loan:
    def __init__(self, id_student, loan_date, return_date, loan_days, renewals=0, late_fee=0.00):
        self.id_student = id_student
        self.loan_date = loan_date
        self.return_date = return_date
        self.loan_days = loan_days
        self.renewals = renewals
        self.late_fee = late_fee

    @staticmethod
    def create(id_student, loan_days, books):
        logging.info(f"Creating loan: student={id_student}, days={loan_days}, books={books}")
        cur = mysql.connection.cursor()
        loan_date = datetime.now().date()
        return_date = loan_date + timedelta(days=loan_days)
        
        try:
            # Verificar si el estudiante ya tiene el máximo de libros prestados
            current_loans = Student.get_borrowed_books_count(id_student)
            total_books = sum(book['quantity'] for book in books)
            logging.info(f"Current loans: {current_loans}, Total new books: {total_books}")
            
            if current_loans + total_books > 3:
                logging.warning("Exceeded maximum books limit")
                return False, "El estudiante no puede prestar más de 3 libros en total."

            # Insertar el nuevo préstamo en la tabla loans
            cur.execute("INSERT INTO loans (id_student, loan_date, return_date, loan_days) VALUES (%s, %s, %s, %s)",
                        (id_student, loan_date, return_date, loan_days))
            id_loan = cur.lastrowid
            logging.info(f"Created loan with ID: {id_loan}")

            # Asociar cada libro al préstamo y actualizar su cantidad
            for book in books:
                book_id = book['id']
                quantity = book['quantity']
                
                logging.info(f"Processing book: id={book_id}, quantity={quantity}")
                
                # Verificar disponibilidad
                cur.execute("SELECT quantity FROM books WHERE id_book = %s", (book_id,))
                available = cur.fetchone()[0]
                logging.info(f"Available quantity for book {book_id}: {available}")
                
                if available < quantity:
                    raise Exception(f"No hay suficientes copias disponibles del libro con ID {book_id}")

                # Insertar en la tabla loan_books
                cur.execute("INSERT INTO loan_books (id_loan, id_book, return_date) VALUES (%s, %s, %s)",
                            (id_loan, book_id, return_date))
                
                # Actualizar la cantidad disponible del libro
                cur.execute("UPDATE books SET quantity = quantity - %s WHERE id_book = %s", (quantity, book_id))
                logging.info(f"Updated book quantity for book {book_id}")

            # Incrementar el contador de libros prestados del estudiante
            Student.increment_borrowed_books(id_student, total_books)
            logging.info(f"Incremented borrowed books count for student {id_student}")

            mysql.connection.commit()
            logging.info("Transaction committed successfully")
            return True, id_loan  # Devolvemos el ID del préstamo en lugar del mensaje
        except Exception as e:
            mysql.connection.rollback()
            logging.error(f"Error creating loan: {str(e)}")
            return False, str(e)
        finally:
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
    def get_active_loans():
        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                SELECT l.*, s.name, s.lastname, 
                       GROUP_CONCAT(b.title SEPARATOR ', ') as books
                FROM loans l
                JOIN students s ON l.id_student = s.id_student
                JOIN loan_books lb ON l.id_loan = lb.id_loan
                JOIN books b ON lb.id_book = b.id_book
                LEFT JOIN returns r ON l.id_loan = r.id_loan
                WHERE r.id_return IS NULL
                GROUP BY l.id_loan
                ORDER BY l.loan_date DESC
            """)
            active_loans = cur.fetchall()
            print(active_loans)
            return active_loans
        finally:
            cur.close()

    @staticmethod
    def get_by_id(id_loan):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM loans WHERE id_loan = %s", (id_loan,))
        loan = cur.fetchone()
        cur.close()
        return loan

    @staticmethod
    def get_books_for_loan(id_loan):
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT b.id_book, b.title, lb.return_date
            FROM loan_books lb
            JOIN books b ON lb.id_book = b.id_book
            WHERE lb.id_loan = %s
        """, (id_loan,))
        books = cur.fetchall()
        cur.close()
        return books

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