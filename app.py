from flask import Flask, render_template
from db_config import get_connection

app = Flask(__name__)

@app.route('/')
def dashboard():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Available books
    cursor.execute("SELECT * FROM Books WHERE available_copies > 0;")
    available_books = cursor.fetchall()

    # Currently borrowed books
    cursor.execute("""
        SELECT B.title, M.name AS member_name, T.borrow_date
        FROM Transactions T
        JOIN Books B ON T.book_id = B.book_id
        JOIN Members M ON T.member_id = M.member_id
        WHERE T.return_date IS NULL;
    """)
    borrowed_books = cursor.fetchall()

    # Overdue books (15+ days)
    cursor.execute("""
        SELECT B.title, M.name AS member_name, T.borrow_date
        FROM Transactions T
        JOIN Books B ON T.book_id = B.book_id
        JOIN Members M ON T.member_id = M.member_id
        WHERE T.return_date IS NULL AND T.borrow_date < CURDATE() - INTERVAL 15 DAY;
    """)
    overdue_books = cursor.fetchall()

    # Top members
    cursor.execute("""
        SELECT M.name, COUNT(*) AS borrow_count
        FROM Transactions T
        JOIN Members M ON T.member_id = M.member_id
        GROUP BY T.member_id
        ORDER BY borrow_count DESC
        LIMIT 5;
    """)
    top_members = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("dashboard.html",
        available_books=available_books,
        borrowed_books=borrowed_books,
        overdue_books=overdue_books,
        top_members=top_members
    )

if __name__ == '__main__':
    app.run(debug=True)
