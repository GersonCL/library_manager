from config import mysql
from datetime import date

class Book:
    def __init__(self, title, code, acquisition_date, status, quantity):
        self.title = title
        self.code = code
        self.acquisition_date = acquisition_date
        self.status = status
        self.quantity = quantity

    @staticmethod
    def create(title, code, acquisition_date, quantity, status='AVAILABLE'):
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO books (title, code, acquisition_date, quantity, status) VALUES (%s, %s, %s, %s, %s)", 
                    (title, code, acquisition_date, quantity, status))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def get_all():
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM books")
        books = cur.fetchall()
        cur.close()
        return books

    @staticmethod
    def get_by_id(id_book):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM books WHERE id_book = %s", (id_book,))
        book = cur.fetchone()
        cur.close()
        return book

    @staticmethod
    def update(id_book, title, code, acquisition_date, status, quantity):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE books SET title = %s, code = %s, acquisition_date = %s, quantity = %s, status = %s  WHERE id_book = %s",
                    (title, code, acquisition_date, quantity, status, id_book))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def is_borrowed(id_book):
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT COUNT(*) 
            FROM loan_books lb
            JOIN loans l ON lb.id_loan = l.id_loan
            WHERE lb.id_book = %s AND l.return_date >= %s
        """, (id_book, date.today()))
        count = cur.fetchone()[0]
        cur.close()
        return count > 0

    @staticmethod
    def delete(id_book):
        if Book.is_borrowed(id_book):
            return False, "No se puede eliminar un libro que está prestado."
        
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM books WHERE id_book = %s", (id_book,))
        mysql.connection.commit()
        cur.close()
        return True, "Libro eliminado con éxito."
    
    @staticmethod
    def get_available():
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM books WHERE quantity > 0")
        available_books = cur.fetchall()
        cur.close()
        return available_books

    @staticmethod
    def decrease_quantity(id_book):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE books SET quantity = quantity - 1 WHERE id_book = %s AND quantity > 0", (id_book,))
        affected_rows = cur.rowcount
        mysql.connection.commit()
        cur.close()
        return affected_rows > 0

    @staticmethod
    def increase_quantity(id_book):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE books SET quantity = quantity + 1 WHERE id_book = %s", (id_book,))
        mysql.connection.commit()
        cur.close()