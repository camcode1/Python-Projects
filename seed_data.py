import sqlite3  # Built-in library to talk to our SQLite database
import random   # Used to randomly pick categories, descriptions, and amounts

# ─────────────────────────────────────────────
# 12 spending categories (fulfills 10+ requirement)
# ─────────────────────────────────────────────
CATEGORIES = [
    "Food",
    "Transport",
    "Rent",
    "Utilities",
    "Entertainment",
    "Healthcare",
    "Clothing",
    "Groceries",
    "Education",
    "Subscriptions",
    "Travel",
    "Personal Care"
]

# ─────────────────────────────────────────────
# Sample descriptions mapped to each category
# ─────────────────────────────────────────────
DESCRIPTIONS = {
    "Food":          ["Lunch", "Dinner", "Coffee", "Takeout", "Brunch"],
    "Transport":     ["Uber", "Bus pass", "Gas", "Parking", "Train ticket"],
    "Rent":          ["Monthly rent", "Rent payment"],
    "Utilities":     ["Electric bill", "Water bill", "Internet bill", "Phone bill"],
    "Entertainment": ["Movie ticket", "Concert", "Netflix", "Video game", "Museum"],
    "Healthcare":    ["Pharmacy", "Doctor visit", "Gym membership", "Vitamins"],
    "Clothing":      ["T-shirt", "Shoes", "Jacket", "Jeans", "Accessories"],
    "Groceries":     ["Weekly groceries", "Supermarket run", "Farmers market"],
    "Education":     ["Textbook", "Online course", "Udemy", "Workshop"],
    "Subscriptions": ["Spotify", "Amazon Prime", "iCloud", "Adobe"],
    "Travel":        ["Flight", "Hotel", "Airbnb", "Travel insurance"],
    "Personal Care": ["Haircut", "Skincare", "Toiletries", "Nail salon"]
}

# ─────────────────────────────────────────────
# Realistic amount ranges per category ($)
# ─────────────────────────────────────────────
AMOUNT_RANGES = {
    "Food":          (5,   30),
    "Transport":     (2,   60),
    "Rent":          (800, 1500),
    "Utilities":     (30,  150),
    "Entertainment": (10,  80),
    "Healthcare":    (15,  200),
    "Clothing":      (20,  120),
    "Groceries":     (30,  100),
    "Education":     (10,  200),
    "Subscriptions": (5,   20),
    "Travel":        (100, 600),
    "Personal Care": (10,  60)
}

# ─────────────────────────────────────────────
# Generate 55 random expense entries
# spread across the last 6 months
# ─────────────────────────────────────────────
def generate_expenses(n=55):
    expenses = []

    # Spread entries across 6 months: 2024-01 through 2024-06
    months = ["2024-01", "2024-02", "2024-03", "2024-04", "2024-05", "2024-06"]

    for _ in range(n):
        category    = random.choice(CATEGORIES)                         # Pick a random category
        description = random.choice(DESCRIPTIONS[category])            # Pick matching description
        low, high   = AMOUNT_RANGES[category]
        amount      = round(random.uniform(low, high), 2)              # Random amount in range
        month       = random.choice(months)                            # Random month
        day         = str(random.randint(1, 28)).zfill(2)              # Random day (1-28, zero-padded)
        date        = f"{month}-{day}"                                 # e.g. "2024-03-14"

        expenses.append((date, category, description, amount))

    return expenses

# ─────────────────────────────────────────────
# Insert all generated expenses into the database
# ─────────────────────────────────────────────
def seed_database():
    conn   = sqlite3.connect("expenses.db")     # Open (or create) the database file
    cursor = conn.cursor()

    # Make sure the table exists before inserting
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date        TEXT,
            category    TEXT,
            description TEXT,
            amount      REAL
        )
    """)

    expenses = generate_expenses(55)            # Generate 55 sample entries

    # Insert all rows in one efficient batch operation
    cursor.executemany(
        "INSERT INTO expenses (date, category, description, amount) VALUES (?, ?, ?, ?)",
        expenses
    )

    conn.commit()   # Save all inserts to disk
    conn.close()

    print(f"✅ Seeded {len(expenses)} expenses across {len(CATEGORIES)} categories.")
    print("   Run `python expense_tracker.py` to view them.")

# ─────────────────────────────────────────────
# Run the seed when this file is executed directly
# ─────────────────────────────────────────────
if __name__ == "__main__":
    seed_database()
