from .. import CURSOR, CONN  # Adjust the import path as necessary
from ..employee import Employee
from ..department import Department
from ..review import Review
from faker import Faker
import pytest

class TestEmployee:
    '''Class Employee in employee.py'''

    @pytest.fixture(autouse=True)
    def drop_tables(self):
        '''Drop tables prior to each test.'''
        CURSOR.execute("DROP TABLE IF EXISTS employees")
        CURSOR.execute("DROP TABLE IF EXISTS departments")
        CURSOR.execute("DROP TABLE IF EXISTS reviews")
        
        Department.all = {}
        Employee.all = {}
        Review.all = {}
        
    def test_creates_table(self):
        '''Test create_table() for employees.'''
        Department.create_table()  # Ensure Department table exists due to FK constraint
        Employee.create_table()
        assert CURSOR.execute("SELECT * FROM employees").fetchall() == []

    def test_drops_table(self):
        '''Test drop_table() for employees.'''
        sql = """
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY,
                name TEXT,
                location TEXT)
        """
        CURSOR.execute(sql)

        Employee.create_table()
        Employee.drop_table()

        # Confirm departments table exists
        result = CURSOR.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='departments' LIMIT 1").fetchone()
        assert result is not None

        # Confirm employees table does not exist
        result = CURSOR.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='employees' LIMIT 1").fetchone()
        assert result is None

    def test_saves_employee(self):
        '''Test save() for an Employee instance.'''
        Department.create_table()
        department = Department("Payroll", "Building A, 5th Floor")
        department.save()

        Employee.create_table()
        employee = Employee("Sasha", "Manager", department.id)
        employee.save()

        row = CURSOR.execute("SELECT * FROM employees").fetchone()
        assert (row[0], row[1], row[2], row[3]) == (employee.id, employee.name, employee.job_title, employee.department_id)

    def test_creates_employee(self):
        '''Test create() for Employee.'''
        Department.create_table()
        department = Department("Payroll", "Building A, 5th Floor")
        department.save()

        Employee.create_table()
        employee = Employee.create("Kai", "Web Developer", department.id)

        row = CURSOR.execute("SELECT * FROM employees").fetchone()
        assert (row[0], row[1], row[2], row[3]) == (employee.id, employee.name, employee.job_title, employee.department_id)

    def test_instance_from_db(self):
        '''Test instance_from_db() for Employee.'''
        Department.create_table()
        department = Department("Payroll", "Building A, 5th Floor")
        department.save()

        Employee.create_table()
        CURSOR.execute("INSERT INTO employees (name, job_title, department_id) VALUES ('Amir', 'Programmer', ?)", (department.id,))
        row = CURSOR.execute("SELECT * FROM employees").fetchone()

        employee = Employee.instance_from_db(row)
        assert (row[0], row[1], row[2], row[3]) == (employee.id, employee.name, employee.job_title, employee.department_id)

    def test_finds_by_id(self):
        '''Test find_by_id() for Employee.'''
        Department.create_table()
        department = Department("Payroll", "Building A, 5th Floor")
        department.save()
        Employee.create_table()
        faker = Faker()
        employee1 = Employee.create(faker.name(), "Manager", department.id)
        employee2 = Employee.create(faker.name(), "Web Developer", department.id)

        employee = Employee.find_by_id(employee1.id)
        assert (employee.id, employee.name, employee.job_title, employee.department_id) == (employee1.id, employee1.name, employee1.job_title, employee1.department_id)

        employee = Employee.find_by_id(employee2.id)
        assert (employee.id, employee.name, employee.job_title, employee.department_id) == (employee2.id, employee2.name, employee2.job_title, employee2.department_id)

        employee = Employee.find_by_id(3)
        assert employee is None

    def test_finds_by_name(self):
        '''Test find_by_name() for Employee.'''
        Department.create_table()
        department = Department("Payroll", "Building A, 5th Floor")
        department.save()
        Employee.create_table()
        faker = Faker()
        employee1 = Employee.create(faker.name(), "Manager", department.id)
        employee2 = Employee.create(faker.name(), "Web Developer", department.id)

        employee = Employee.find_by_name(employee1.name)
        assert (employee.id, employee.name, employee.job_title, employee.department_id) == (employee1.id, employee1.name, employee1.job_title, employee1.department_id)

        employee = Employee.find_by_name(employee2.name)
        assert (employee.id, employee.name, employee.job_title, employee.department_id) == (employee2.id, employee2.name, employee2.job_title, employee2.department_id)

        employee = Employee.find_by_name("Unknown")
        assert employee is None

    def test_updates_row(self):
        '''Test update() for Employee.'''
        Department.create_table()
        department1 = Department("Payroll", "Building A, 5th Floor")
        department1.save()
        department2 = Department("Human Resources", "Building C, 2nd Floor")
        department2.save()

        Employee.create_table()

        employee1 = Employee.create("Raha", "Accountant", department1.id)
        employee2 = Employee.create("Tal", "Benefits Coordinator", department2.id)
        id1 = employee1.id
        id2 = employee2.id

        employee1.name = "Raha Lee"
        employee1.job_title = "Senior Accountant"
        employee1.department_id = department2.id
        employee1.update()

        employee = Employee.find_by_id(id1)
        assert (employee.id, employee.name, employee.job_title, employee.department_id) == (id1, "Raha Lee", "Senior Accountant", department2.id)

        employee = Employee.find_by_id(id2)
        assert (employee.id, employee.name, employee.job_title, employee.department_id) == (id2, "Tal", "Benefits Coordinator", department2.id)

    def test_deletes_row(self):
        '''Test delete() for Employee.'''
        Department.create_table()
        department = Department("Payroll", "Building A, 5th Floor")
        department.save()

        Employee.create_table()

        employee1 = Employee.create("Raha", "Accountant", department.id)
        id1 = employee1.id
        employee2 = Employee.create("Tal", "Benefits Coordinator", department.id)
        id2 = employee2.id

        employee1.delete()
        assert Employee.find_by_id(employee1.id) is None
        assert (employee1.id, employee1.name, employee1.job_title, employee1.department_id) == (None, "Raha", "Accountant", department.id)
        assert Employee.all.get(id1) is None

        employee = Employee.find_by_id(id2)
        assert (employee.id, employee.name, employee.job_title, employee.department_id) == (employee2.id, employee2.name, employee2.job_title, employee2.department.id)

    def test_gets_all(self):
        '''Test get_all() for Employee.'''
        Department.create_table()
        department = Department("Payroll", "Building A, 5th Floor")
        department.save()

        Employee.create_table()
        employee1 = Employee.create("Tristan", "Fullstack Developer", department.id)
        employee2 = Employee.create("Sasha", "Manager", department.id)

        employees = Employee.get_all()
        assert len(employees) == 2
        assert (employees[0].id, employees[0].name, employees[0].job_title, employees[0].department_id) == (employee1.id, employee1.name, employee1.job_title, employee1.department_id)
        assert (employees[1].id, employees[1].name, employees[1].job_title, employees[1].department_id) == (employee2.id, employee2.name, employee2.job_title, employee2.department_id)

    def test_get_reviews(self):
        '''Test reviews() for Employee.'''
        Review.all = {}
        CURSOR.execute("DROP TABLE IF EXISTS reviews")

        Department.create_table()
        department1 = Department.create("Payroll", "Building A, 5th Floor")
        
        Employee.create_table()
        employee1 = Employee.create("Raha", "Accountant", department1.id)
        employee2 = Employee.create("Tal", "Senior Accountant", department1.id)
        
        Review.create_table()
        review1 = Review.create(2022, "Good Python coding skills", employee1.id)
        review2 = Review.create(2023, "Great Python coding skills", employee1.id)
        review3 = Review.create(2022, "Good SQL coding skills", employee2.id)
        
        reviews = employee1.reviews()
        assert len(reviews) == 2
        assert (reviews[0].id, reviews[0].year, reviews[0].summary, reviews[0].employee_id) == (review1.id, review1.year, review1.summary, review1.employee_id)
        assert (reviews[1].id, reviews[1].year, reviews[1].summary, reviews[1].employee_id) == (review2.id,
