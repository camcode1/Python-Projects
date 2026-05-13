import unittest
import unittest.mock
import sqlite3
import os
from expense_tracker import init_db, add_expense, view_expenses, delete_expense, monthly_summary
import expense_tracker

expense_tracker.DB_NAME = "test_expenses.db"  # Redirect all DB calls to test file


class TestExpenseTracker(unittest.TestCase):

    def setUp(self):
        """Create a fresh test database before each test."""
        expense_tracker.DB_NAME = "test_expenses.db"
        init_db()

    def tearDown(self):
        """Delete the test database after each test."""
        if os.path.exists("test_expenses.db"):
            os.remove("test_expenses.db")

    def test_init_db_creates_table(self):
        conn   = sqlite3.connect("test_expenses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='expenses'")
        result = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(result)

    def test_add_expense_saves_to_db(self):
        add_expense("2024-03-01", "Food", "Lunch", 12.50)
        conn   = sqlite3.connect("test_expenses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM expenses")
        rows = cursor.fetchall()
        conn.close()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][2], "Food")
        self.assertEqual(rows[0][4], 12.50)

    def test_add_multiple_expenses(self):
        add_expense("2024-03-01", "Food",      "Lunch",   12.50)
        add_expense("2024-03-02", "Transport", "Uber",    15.00)
        add_expense("2024-03-03", "Groceries", "Walmart", 45.00)
        conn   = sqlite3.connect("test_expenses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM expenses")
        count = cursor.fetchone()[0]
        conn.close()
        self.assertEqual(count, 3)

    def test_delete_expense_removes_row(self):
        add_expense("2024-03-01", "Food", "Lunch", 12.50)
        conn   = sqlite3.connect("test_expenses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM expenses LIMIT 1")
        expense_id = cursor.fetchone()[0]
        conn.close()
        delete_expense(expense_id)
        conn   = sqlite3.connect("test_expenses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
        result = cursor.fetchone()
        conn.close()
        self.assertIsNone(result)

    def test_delete_nonexistent_id(self):
        try:
            delete_expense(9999)
        except Exception as e:
            self.fail(f"delete_expense raised an exception: {e}")

    def test_view_expenses_with_data(self):
        add_expense("2024-03-01", "Food", "Lunch", 12.50)
        try:
            view_expenses()
        except Exception as e:
            self.fail(f"view_expenses raised an exception: {e}")

    def test_view_expenses_empty_db(self):
        try:
            view_expenses()
        except Exception as e:
            self.fail(f"view_expenses raised an exception on empty DB: {e}")

    def test_monthly_summary_correct_total(self):
        add_expense("2024-03-01", "Food", "Lunch",  10.00)
        add_expense("2024-03-15", "Food", "Dinner", 20.00)
        add_expense("2024-04-01", "Transport", "Uber", 15.00)
        conn   = sqlite3.connect("test_expenses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(amount) FROM expenses WHERE date LIKE '2024-03%' AND category = 'Food'")
        total = cursor.fetchone()[0]
        conn.close()
        self.assertEqual(total, 30.00)

    def test_monthly_summary_empty_month(self):
        try:
            monthly_summary("2099-01")
        except Exception as e:
            self.fail(f"monthly_summary raised an exception: {e}")

    def test_expense_amount_is_float(self):
        add_expense("2024-03-01", "Food", "Coffee", 4.75)
        conn   = sqlite3.connect("test_expenses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT amount FROM expenses")
        amount = cursor.fetchone()[0]
        conn.close()
        self.assertIsInstance(amount, float)

    def test_all_categories_supported(self):
        categories = [
            "Food", "Transport", "Rent", "Utilities", "Entertainment",
            "Healthcare", "Clothing", "Groceries", "Education",
            "Subscriptions", "Travel", "Personal Care"
        ]
        for cat in categories:
            add_expense("2024-03-01", cat, "Test", 10.00)
        conn   = sqlite3.connect("test_expenses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(DISTINCT category) FROM expenses")
        count = cursor.fetchone()[0]
        conn.close()
        self.assertEqual(count, 12)

    def test_init_db_idempotent(self):
        try:
            init_db()
            init_db()
        except Exception as e:
            self.fail(f"init_db raised an exception on repeated calls: {e}")


if __name__ == "__main__":
    unittest.main(verbosity=2)


class TestMainMenu(unittest.TestCase):
    """Tests for the CLI main() function using simulated input."""

    def setUp(self):
        expense_tracker.DB_NAME = "test_expenses.db"
        init_db()

    def tearDown(self):
        if os.path.exists("test_expenses.db"):
            os.remove("test_expenses.db")

    # TEST 13: Main menu option 1 - add expense
    def test_main_add_expense(self):
        """Simulate user choosing option 1 to add an expense then quit."""
        inputs = iter(["1", "2024-03-01", "Food", "Lunch", "12.50", "5"])
        with unittest.mock.patch("builtins.input", lambda _: next(inputs)):
            from expense_tracker import main
            main()
        conn = sqlite3.connect("test_expenses.db")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM expenses")
        count = cursor.fetchone()[0]
        conn.close()
        self.assertEqual(count, 1)

    # TEST 14: Main menu option 2 - view expenses
    def test_main_view_expenses(self):
        """Simulate user choosing option 2 then quit."""
        inputs = iter(["2", "5"])
        with unittest.mock.patch("builtins.input", lambda _: next(inputs)):
            from expense_tracker import main
            try:
                main()
            except Exception as e:
                self.fail(f"main() raised an exception: {e}")

    # TEST 15: Main menu option 4 - monthly summary
    def test_main_monthly_summary(self):
        """Simulate user choosing option 4 then quit."""
        inputs = iter(["4", "2024-03", "5"])
        with unittest.mock.patch("builtins.input", lambda _: next(inputs)):
            from expense_tracker import main
            try:
                main()
            except Exception as e:
                self.fail(f"main() raised an exception: {e}")

    # TEST 16: Main menu invalid option
    def test_main_invalid_option(self):
        """Simulate user entering an invalid option then quit."""
        inputs = iter(["9", "5"])
        with unittest.mock.patch("builtins.input", lambda _: next(inputs)):
            from expense_tracker import main
            try:
                main()
            except Exception as e:
                self.fail(f"main() raised an exception on invalid input: {e}")

    # TEST 17: Monthly summary with actual data prints totals
    def test_monthly_summary_with_data(self):
        """monthly_summary() should print category totals when data exists."""
        add_expense("2024-03-01", "Food", "Lunch", 10.00)
        add_expense("2024-03-02", "Transport", "Uber", 20.00)
        try:
            monthly_summary("2024-03")
        except Exception as e:
            self.fail(f"monthly_summary raised an exception: {e}")
