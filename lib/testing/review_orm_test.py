from employee import Employee, CONN, CURSOR
from department import Department
from review import Review
import pytest  # Fixed typo from "pytesct" to "pytest"


class TestReview:
    '''Class Review in review.py'''

    @pytest.fixture(autouse=True)
    def drop_tables(self):
        '''Drop tables prior to each test.'''
        CURSOR.execute("DROP TABLE IF EXISTS reviews")
        CURSOR.execute("DROP TABLE IF EXISTS employees")
        CURSOR.execute("DROP TABLE IF EXISTS departments")

    def test_creates_table(self):
        '''Contains method "create_table()" that creates table "reviews" if it does not exist.'''
        Department.create_table()
        Employee.create_table()
        Review.create_table()
        assert CURSOR.execute("SELECT * FROM reviews").fetchone() is not None

    def test_drops_table(self):
        '''Contains method "drop_table()" that drops table "reviews" if it exists.'''
        Department.create_table()
        Employee.create_table()
        Review.create_table()

        Review.drop_table()

        # Confirm employees table exists
        sql_table_names = """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='employees'
            LIMIT 1
        """
        result = CURSOR.execute(sql_table_names).fetchone()
        assert result

        # Confirm reviews table does not exist
        sql_table_names = """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='reviews'
            LIMIT 1
        """
        result = CURSOR.execute(sql_table_names).fetchone()
        assert result is None

    def test_saves_review(self):
        '''Contains method "save()" that saves a Review instance to the db and sets the instance id.'''
        Department.create_table()
        department = Department("Payroll", "Building A, 5th Floor")
        department.save()

        Employee.create_table()
        employee = Employee("Sasha", "Manager", department.id)
        employee.save()

        Review.create_table()
        review = Review(2023, "Excellent Python skills!", employee.id)
        review.save()

        row = CURSOR.execute("SELECT * FROM reviews").fetchone()
        assert (row[0], row[1], row[2], row[3]) == (review.id, review.year, review.summary, review.employee_id)

    def test_creates_review(self):
        '''Contains method "create()" that creates a new row in the db and returns a Review instance.'''
        Department.create_table()
        department = Department("Payroll", "Building A, 5th Floor")
        department.save()

        Employee.create_table()
        employee = Employee.create("Kai", "Web Developer", department.id)

        Review.create_table()
        review = Review.create(2023, "Excellent Python skills!", employee.id)

        row = CURSOR.execute("SELECT * FROM reviews").fetchone()
        assert (row[0], row[1], row[2], row[3]) == (review.id, review.year, review.summary, review.employee_id)

    def test_instance_from_db(self):
        '''Contains method "instance_from_db()" that takes a db row and creates a Review instance.'''
        Department.create_table()
        department = Department.create("Payroll", "Building A, 5th Floor")

        Employee.create_table()
        employee = Employee.create("Raha", "Accountant", department.id)

        Review.create_table()
        CURSOR.execute("INSERT INTO reviews (year, summary, employee_id) VALUES (2022, 'Amazing coder!', ?)", (employee.id,))

        row = CURSOR.execute("SELECT * FROM reviews").fetchone()

        review = Review.instance_from_db(row)
        assert (row[0], row[1], row[2], row[3]) == (review.id, review.year, review.summary, review.employee_id)

    def test_finds_by_id(self):
        '''Contains method "find_by_id()" that returns a Review instance corresponding to its db row retrieved by id.'''
        Department.create_table()
        department = Department.create("Payroll", "Building A, 5th Floor")

        Employee.create_table()
        employee = Employee.create("Raha", "Accountant", department.id)

        Review.create_table()
        review1 = Review.create(2020, "Great coder!", employee.id)
        id1 = review1.id
        review2 = Review.create(2000, "Awesome coder!", employee.id)
        id2 = review2.id

        review = Review.find_by_id(review1.id)
        assert (review.id, review.year, review.summary, review.employee_id) == (id1, 2020, "Great coder!", employee.id)

        review = Review.find_by_id(review2.id)
        assert (review.id, review.year, review.summary, review.employee_id) == (id2, 2000, "Awesome coder!", employee.id)

        review = Review.find_by_id(3)
        assert review is None

    def test_updates_row(self):
        '''Contains a method "update()" that updates an instance's corresponding database record.'''
        Department.create_table()
        department = Department.create("Payroll", "Building A, 5th Floor")

        Employee.create_table()
        employee = Employee.create("Raha", "Accountant", department.id)

        Review.create_table()
        review1 = Review.create(2020, "Usually double checks their work", employee.id)
        id1 = review1.id
        review2 = Review.create(2000, "Takes long lunches", employee.id)
        id2 = review2.id

        review1.year = 2023
        review1.summary = "Always double checks their work"
        review1.update()

        # Confirm review1 updated
        review = Review.find_by_id(id1)
        assert (review.id, review.year, review.summary, review.employee_id) == (review1.id, review1.year, review1.summary, employee.id)

        # Confirm review2 not updated
        review = Review.find_by_id(id2)
        assert (review.id, review.year, review.summary, review.employee_id) == (review2.id, review2.year, review2.summary, employee.id)

    def test_deletes_row(self):
        '''Contains a method "delete()" that deletes the instance's corresponding database record.'''
        Department.create_table()
        department = Department.create("Payroll", "Building A, 5th Floor")

        Employee.create_table()
        employee = Employee.create("Raha", "Accountant", department.id)

        Review.create_table()
        review1 = Review.create(2020, "Usually double checks their work", employee.id)
        id1 = review1.id
        review2 = Review.create(2000, "Takes long lunches", employee.id)
        id2 = review2.id

        review1.delete()
        # Assert row deleted
        assert Review.find_by_id(id1) is None
        # Assert Review object state is correct, id should be None
        assert (review1.id, review1.year, review1.summary, review1.employee_id) == (None, 2020, "Usually double checks their work", employee.id)
        # Assert dictionary entry was deleted
        assert Review.all.get(id1) is None
        
        review = Review.find_by_id(id2)
        # Assert review2 row not modified, review2 object not modified
        assert (review.id, review.year, review.summary, review.employee_id) == (review2.id, review2.year, review2.summary, employee.id)

    def test_gets_all(self):
        '''Contains method "get_all()" that returns a list of Review instances for every record in the db.'''
        Department.create_table()
        department = Department.create("Payroll", "Building A, 5th Floor")

        Employee.create_table()
        employee = Employee.create("Raha", "Accountant", department.id)

        Review.create_table()
        review1 = Review.create(2020, "Great coder!", employee.id)
        id1 = review1.id
        review2 = Review.create(2000, "Awesome coders!", employee.id)
        id2 = review2.id

        reviews = Review.get_all()
        assert len(reviews) == 2
        assert (reviews[0].id, reviews[0].year, reviews[0].summary, reviews[0].employee_id) == (review1.id, review1.year, review1.summary, review1.employee_id)
        assert (reviews[1].id, reviews[1].year, reviews[1].summary, reviews[1].employee_id) == (review2.id, review2.year, review2.summary, review2.employee_id)
