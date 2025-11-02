-- ==============================================
--  Payroll Management System Database Schema
--  Database: payroll.db
--  Author: Aryan Bhatt
--  Description: SQLite schema for employee payroll records
-- ==============================================

-- Create the employees table
CREATE TABLE IF NOT EXISTS employees (
    emp_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    position TEXT,
    base_salary REAL NOT NULL
);

-- Optional: Sample Data
INSERT INTO employees (name, position, base_salary) VALUES
('Amit Khanna', 'Manager', 55000),
('Sonia Mehta', 'Accountant', 40000),
('Vikram Das', 'HR Executive', 35000),
('Pooja Nair', 'Sales Associate', 30000);

-- Query Example: Retrieve all employees
SELECT * FROM employees;

-- Query Example: Update base salary
-- UPDATE employees SET base_salary = 60000 WHERE emp_id = 1;

-- Query Example: Delete an employee record
-- DELETE FROM employees WHERE emp_id = 3;
