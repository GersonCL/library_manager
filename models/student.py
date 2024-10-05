from config import mysql

class Student:
    def __init__(self, name, lastname, student_id, secondary_school, grade, section):
        self.name = name
        self.lastname = lastname
        self.student_id = student_id
        self.secondary_school = secondary_school
        self.grade = grade
        self.section = section

    @staticmethod
    def create(name, lastname, student_id, secondary_school, grade, section):
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO students (name, lastname, student_id, secondary_school, grade, section) VALUES (%s, %s, %s, %s, %s, %s)", 
                    (name, lastname, student_id, secondary_school, grade, section))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def get_all():
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM students")
        students = cur.fetchall()
        cur.close()
        return students

    @staticmethod
    def get_by_id(id_student):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM students WHERE id_student = %s", (id_student,))
        student = cur.fetchone()
        cur.close()
        return student

    @staticmethod
    def update(id_student, name, lastname, student_id, secondary_school, grade, section):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE students SET name = %s, lastname = %s, student_id = %s, secondary_school = %s, grade = %s, section = %s WHERE id_student = %s",
                    (name, lastname, student_id, secondary_school, grade, section, id_student))
        mysql.connection.commit()
        cur.close()

    def delete(id_student):
        """
        Intenta eliminar un estudiante. Si tiene préstamos, no permite la eliminación.
        """
        if Student.has_loans(id_student):
            return False, "No se puede eliminar el estudiante porque tiene préstamos registrados."
        
        cur = mysql.connection.cursor()
        try:
            cur.execute("DELETE FROM students WHERE id_student = %s", (id_student,))
            mysql.connection.commit()
            return True, "Estudiante eliminado."
        except Exception as e:
            mysql.connection.rollback()
            return False, f"Error al eliminar el estudiante: {str(e)}"
        finally:
            cur.close()


    #funciones para obtener la cantidad de libros prestamos por alumno

    @staticmethod
    def increment_borrowed_books(id_student):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE students SET books_borrowed = books_borrowed + 1 WHERE id_student = %s", (id_student,))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def decrement_borrowed_books(id_student):
        cur = mysql.connection.cursor()
        cur.execute("UPDATE students SET books_borrowed = books_borrowed - 1 WHERE id_student = %s", (id_student,))
        mysql.connection.commit()
        cur.close()

    @staticmethod
    def get_borrowed_books_count(id_student):
        cur = mysql.connection.cursor()
        cur.execute("SELECT books_borrowed FROM students WHERE id_student = %s", (id_student,))
        count = cur.fetchone()[0]
        cur.close()
        return count
    
    #metodo para validar si tiene historico de prestamos

    @staticmethod
    def has_loans(id_student):
        """
        Verifica si un estudiante tiene préstamos (históricos o activos).
        """
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) FROM loans WHERE id_student = %s", (id_student,))
        count = cur.fetchone()[0]
        cur.close()
        return count > 0