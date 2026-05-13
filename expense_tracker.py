import sqlite3  # Built-in Python library for working with SQLite databases

DB_NAME = "expenses.db"  # Database file — tests can override this to avoid touching real data

# ─────────────────────────────────────────────
# STEP 1: Initialize the database
# ─────────────────────────────────────────────

def init_db():
    conn = sqlite3.connect(DB_NAME)   # Creates 'expenses.db' file if it doesn't exist
    cursor = conn.cursor()                  # Cursor lets us run SQL commands
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,  -- Auto-incrementing unique ID
            date        TEXT,                               -- Date string e.g. "2024-03-01"
            category    TEXT,                               -- e.g. "Food", "Transport"
            description TEXT,                              -- Short note e.g. "Lunch"
            amount      REAL                               -- Dollar amount e.g. 12.50
        )
    """)
    conn.commit()   # Save changes to the database
    conn.close()    # Close the connection when done

# ─────────────────────────────────────────────
# STEP 2: Add an expense
# ─────────────────────────────────────────────

def add_expense(date, category, description, amount):
    conn = sqlite3.connect(DB_NAME)           # Open the database
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (date, category, description, amount) VALUES (?, ?, ?, ?)",
        (date, category, description, amount)       # '?' placeholders prevent SQL injection
    )
    conn.commit()   # Save the new row
    conn.close()
    print(f"✅ Added: {description} (${amount}) under '{category}'")

# ─────────────────────────────────────────────
# STEP 3: View all expenses
# ─────────────────────────────────────────────

def view_expenses():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses")    # Fetch every row in the table
    rows = cursor.fetchall()                    # Returns a list of tuples
    conn.close()

    if not rows:
        print("No expenses found.")
        return

    print(f"\n{'ID':<5} {'Date':<12} {'Category':<15} {'Description':<20} {'Amount':>8}")
    print("-" * 65)
    for row in rows:
        # row = (id, date, category, description, amount)
        print(f"{row[0]:<5} {row[1]:<12} {row[2]:<15} {row[3]:<20} ${row[4]:>7.2f}")

# ─────────────────────────────────────────────
# STEP 4: Delete an expense by ID
# ─────────────────────────────────────────────

def delete_expense(expense_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))  # Match row by ID
    conn.commit()
    conn.close()
    print(f"🗑️  Deleted expense with ID {expense_id}")

# ─────────────────────────────────────────────
# STEP 5: Monthly summary report
# ─────────────────────────────────────────────

def monthly_summary(year_month):    # year_month should be in format "YYYY-MM" e.g. "2024-03"
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT category, SUM(amount)        -- Add up spending per category
        FROM expenses
        WHERE date LIKE ?                   -- Match rows where date starts with "YYYY-MM"
        GROUP BY category                   -- One row per category
    """, (f"{year_month}%",))               # e.g. "2024-03%" matches all March 2024 dates
    rows = cursor.fetchall()
    conn.close()

    print(f"\n📊 Summary for {year_month}")
    print("-" * 30)
    total = 0
    for category, subtotal in rows:
        print(f"  {category:<20} ${subtotal:.2f}")
        total += subtotal                   # Accumulate grand total
    print("-" * 30)
    print(f"  {'TOTAL':<20} ${total:.2f}")

# ─────────────────────────────────────────────
# STEP 6: CLI Menu (main loop)
# ─────────────────────────────────────────────

def main():
    init_db()   # Always initialize the DB first (safe to call multiple times)

    while True:     # Keep showing the menu until the user quits
        print("\n====== Expense Tracker ======")
        print("1. Add expense")
        print("2. View all expenses")
        print("3. Delete expense")
        print("4. Monthly summary")
        print("5. Quit")
        choice = input("Choose an option: ").strip()    # .strip() removes accidental whitespace

        if choice == "1":
            date        = input("Date (YYYY-MM-DD): ")
            category    = input("Category (e.g. Food, Transport): ")
            description = input("Description: ")
            amount      = float(input("Amount ($): "))  # Convert string input to a number
            add_expense(date, category, description, amount)

        elif choice == "2":
            view_expenses()

        elif choice == "3":
            view_expenses()                                     # Show list first so user knows IDs
            expense_id = int(input("Enter ID to delete: "))    # Convert to int for SQL query
            delete_expense(expense_id)

        elif choice == "4":
            year_month = input("Enter month (YYYY-MM): ")
            monthly_summary(year_month)

        elif choice == "5":
            print("Goodbye! 👋")
            break   # Exit the while loop and end the program

        else:
            print("Invalid option, please try again.")  # Handle unexpected input

# ─────────────────────────────────────────────
# Entry point — only runs when executed directly
# (not when imported as a module in tests)
# ─────────────────────────────────────────────
if __name__ == "__main__":
    main()
