CREATE DATABASE IF NOT EXISTS library_db;
USE library_db;

CREATE TABLE IF NOT EXISTS students (
    id_student INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    lastname VARCHAR(50) NOT NULL,
    student_id VARCHAR(10) UNIQUE NOT NULL,
    grade VARCHAR(20) NOT NULL,
    section VARCHAR(10) NOT NULL,
    books_borrowed INT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS books (
    id_book INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    author VARCHAR(50) NOT NULL,
    materia VARCHAR(20) NOT NULL,
    code VARCHAR(10) UNIQUE NOT NULL,
    acquisition_date DATE,
    quantity INT DEFAULT 1,
    status ENUM('DISPONIBLE', 'PRESTADO', 'OBSOLETO') DEFAULT 'DISPONIBLE'
);

CREATE TABLE IF NOT EXISTS loans (
    id_loan INT AUTO_INCREMENT PRIMARY KEY,
    id_student INT NOT NULL,
    loan_date DATE NOT NULL,
    return_date DATE NOT NULL,
    loan_days INT NOT NULL,
    renewals INT DEFAULT 0,
    late_fee DECIMAL(5,2) DEFAULT 0.00,
    status ENUM('active', 'returned') DEFAULT 'active',
    FOREIGN KEY (id_student) REFERENCES students(id_student)
);

CREATE TABLE IF NOT EXISTS loan_books (
    id_loan INT,
    id_book INT,
    return_date DATE NOT NULL,
    quantity INT DEFAULT 1,
    PRIMARY KEY (id_loan, id_book),
    FOREIGN KEY (id_loan) REFERENCES loans(id_loan) ON DELETE CASCADE,
    FOREIGN KEY (id_book) REFERENCES books(id_book)
);

CREATE TABLE IF NOT EXISTS returns (
    id_return INT AUTO_INCREMENT PRIMARY KEY,
    id_loan INT NOT NULL,
    return_date DATE NOT NULL,
    days_late INT DEFAULT 0,
    late_fee DECIMAL(10, 2) DEFAULT 0.00,
    FOREIGN KEY (id_loan) REFERENCES loans(id_loan)
);

CREATE TABLE IF NOT EXISTS returned_books (
    id_return INT,
    id_book INT,
    quantity INT DEFAULT 1,
    PRIMARY KEY (id_return, id_book),
    FOREIGN KEY (id_return) REFERENCES returns(id_return),
    FOREIGN KEY (id_book) REFERENCES books(id_book)
);

-- Indexes
CREATE INDEX idx_student_name ON students(name, lastname);
CREATE INDEX idx_book_title ON books(title);
CREATE INDEX idx_loan_dates ON loans(loan_date, return_date);
CREATE INDEX idx_loan_student ON loans(id_student);
CREATE INDEX idx_loan_book ON loan_books(id_book);