import argparse
import csv
import sqlite3
from datetime import datetime
from typing import List, Tuple

DB_NAME = "expenses.db"


def init_db() -> None:
    """Initialize SQLite database with an expenses table."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                description TEXT,
                date TEXT NOT NULL
            )
            """
        )
        conn.commit()


def add_expense(amount: float, category: str, description: str) -> None:
    """Add a new expense to the database."""
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)",
            (amount, category.title(), description, date_str),
        )
        conn.commit()
    print(f"Added expense: ${amount:.2f} for '{category}' on {date_str[:10]}.")


def list_expenses() -> List[Tuple]:
    """Retrieve all logged expenses."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, amount, category, description, date FROM expenses ORDER BY id DESC")
        rows = cursor.fetchall()

    if not rows:
        print("No expenses recorded yet.")
        return []

    print(f"\n{'ID':<4} | {'Amount':<10} | {'Category':<15} | {'Date':<12} | {'Description'}")
    print("-" * 65)
    for r in rows:
        print(f"{r[0]:<4} | ${r[1]:<9.2f} | {r[2]:<15} | {r[4][:10]:<12} | {r[3]}")
    return rows


def show_summary() -> None:
    """Show spending breakdown by category and overall total."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
        summary = cursor.fetchall()
        cursor.execute("SELECT SUM(amount) FROM expenses")
        total = cursor.fetchone()[0] or 0.0

    if not summary:
        print("No expenses to summarize.")
        return

    print("\n--- Spending Summary by Category ---")
    for category, cat_total in summary:
        print(f"• {category:<15}: ${cat_total:.2f}")
    print("-" * 36)
    print(f"Total Spent:       ${total:.2f}\n")


def export_csv(filename: str = "expenses_export.csv") -> None:
    """Export all expenses to a CSV file."""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, amount, category, description, date FROM expenses")
        rows = cursor.fetchall()

    if not rows:
        print("No data available to export.")
        return

    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["ID", "Amount", "Category", "Description", "Date"])
        writer.writerows(rows)

    print(f"Data successfully exported to '{filename}'.")


def main():
    init_db()
    parser = argparse.ArgumentParser(description="CLI Personal Expense Tracker")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new expense")
    add_parser.add_argument("--amount", "-a", type=float, required=True, help="Expense amount")
    add_parser.add_argument("--category", "-c", type=str, required=True, help="Category (e.g. Food, Bills)")
    add_parser.add_argument("--desc", "-d", type=str, default="", help="Optional description")

    # List command
    subparsers.add_parser("list", help="List all expenses")

    # Summary command
    subparsers.add_parser("summary", help="Show category spending breakdown")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export expenses to CSV")
    export_parser.add_argument("--out", "-o", type=str, default="expenses_export.csv", help="Output filename")

    args = parser.parse_args()

    if args.command == "add":
        add_expense(args.amount, args.category, args.desc)
    elif args.command == "list":
        list_expenses()
    elif args.command == "summary":
        show_summary()
    elif args.command == "export":
        export_csv(args.out)


if __name__ == "__main__":
    main()