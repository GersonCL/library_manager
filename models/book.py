from config import mysql
from datetime import date
import random, datetime, string

class Book:
    def __init__(self, title, author, materia, code, acquisition_date, status, quantity):
        self.title = title
        self.code = code
        self.author = author
        self.materia = materia
        self.acquisition_date = acquisition_date
        self.status = status
        self.quantity = quantity
        self.stock = quantity

    '''@staticmethod
    def create(title, author, materia, code, acquisition_date, quantity, status='AVAILABLE'):
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO books (title, author, materia, code, acquisition_date, quantity, stock, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", 
                    (title, author, materia, code, acquisition_date, quantity, quantity, status))
        mysql.connection.commit()
        cur.close()'''

    @staticmethod
    def create(title, author, materia, code, acquisition_date, quantity, status='AVAILABLE'):
        # creando book_id para generar el codigo automatico en la consulta -- Victor Orellana
        code = Book.generate_book_id(title.upper())
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO books (title, author, materia, code, acquisition_date, quantity, stock, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (title, author, materia, code, acquisition_date, quantity, quantity, status))
        mysql.connection.commit()
        book_id = cur.lastrowid  # Obtén el ID del último libro insertado
        cur.close()
        return book_id


    @staticmethod
    def generate_book_id(bookname):

#creando variable para manejar la fecha -- Victor Orellana
        current_date = datetime.datetime.now()

# 4 variables declaradas para la fecha, mes  y año -- Victor Orellana
        current_year = current_date.year
# el año idica que solo sera en cuenta dos digitos -- Victor Orellana
        year_two_digit = str(current_year)[-2:]
        month_two_digit = current_date.strftime("%m")
        day_one_digit = current_date.day

  # Obtener las iniciales del libro -- Victor Orellana
        words = bookname.split()
        initials_book_ = ''.join(word[0].upper() for word in words[:2])

        cur = mysql.connection.cursor()
        while True:
# generar 3 digitos aleatorios -- Victor Orellana
            random_digits = ''.join(random.choices(string.digits, k=3))

#obtener el book_id -- Victor Orellana
            code = f"{initials_book_}{random_digits}{day_one_digit}{month_two_digit}{year_two_digit}"

# verificar si ya existe
            cur.execute("SELECT COUNT(1) FROM books WHERE id_book = %s", (code,))
            if cur.fetchone()[0] == 0:
                cur.close()
                return code

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
    def update(id_book, title, author, materia, code, acquisition_date, status, quantity):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE books SET title = %s, author = %s, materia = %s, code = %s, acquisition_date = %s, quantity = %s, status = %s  WHERE id_book = %s",
                    (title, author, materia, code, acquisition_date, quantity, status, id_book))
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
    def archive(id_book):
        cur = mysql.connection.cursor()
        
        # Verificar el estado del libro
        cur.execute("SELECT status FROM books WHERE id_book = %s", (id_book,))
        status = cur.fetchone()[0]
        
        # Verificar si hay libros prestados
        cur.execute("""
            SELECT SUM(quantity) 
            FROM loan_books 
            WHERE id_book = %s AND return_date >= %s
        """, (id_book, date.today()))
        quantity_borrowed = cur.fetchone()[0] or 0
        
        if status == 'PRESTADO' or quantity_borrowed > 0:
            cur.close()
            return False, "No se puede archivar un libro que está prestado"
        
        cur.execute("UPDATE books SET status = 'OBSOLETO' WHERE id_book = %s", (id_book,))
        mysql.connection.commit()
        cur.close()
        return True, "Libro archivado exitosamente."
    
    @staticmethod
    def get_available():
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM books WHERE quantity > 0")
        available_books = cur.fetchall()
        cur.close()
        return available_books
    
    @staticmethod
    def get_total_stock(id_book):
        cur = mysql.connection.cursor()
        cur.execute("SELECT stock FROM books WHERE id_book = %s", (id_book,))
        result = cur.fetchone()
        cur.close()
        return result[0] if result else 0 
    
    @staticmethod
    def get_available_books(id_book):
        cur = mysql.connection.cursor()
        cur.execute("SELECT quantity FROM books WHERE quantity > 0 and id_book = %s", (id_book,))
        available_books = cur.fetchone()
        cur.close()
        return available_books[0] if available_books else 0
    
    @staticmethod
    def get_total_borrowed(id_book):
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT lb.quantity
            FROM loan_books lb
            INNER JOIN books b ON lb.id_book = b.id_book
            WHERE b.id_book = %s
        """, (id_book,))
        result = cur.fetchone()
        cur.close()
        return result[0] if result else 0

    @staticmethod
    def decrease_quantity(id_book):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE books SET quantity = quantity - 1 WHERE id_book = %s AND quantity > 0", (id_book,))
        affected_rows = cur.rowcount
        mysql.connection.commit()
        cur.close()
        return affected_rows > 0

    @staticmethod
    def increase_quantity(id_book, quantity=1):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE books SET quantity = quantity + %s WHERE id_book = %s", (quantity, id_book))
        mysql.connection.commit()
        cur.close()