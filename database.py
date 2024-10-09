import sqlite3


def create_connection():
    conn = sqlite3.connect("bank.db")
    return conn

def create_tables(conn):
    cur = conn.cursor()

    # Create users table with additional fields
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        checking_balance REAL DEFAULT 0,
        savings_balance REAL DEFAULT 0,
        email TEXT,
        phone TEXT
    )
    """)

    # Transactions table (remains the same)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        date TEXT,
        type TEXT,
        account TEXT,
        amount REAL,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    """)

    # New table for beneficiaries
    cur.execute("""
    CREATE TABLE IF NOT EXISTS beneficiaries (
        beneficiary_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        name TEXT,
        account_number TEXT,
        bank_name TEXT,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    )
    """)

    conn.commit()

def add_user(conn, user):
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO users (user_id, username, password_hash, checking_balance, savings_balance, email, phone)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user.user_id, user.username, user.password_hash, user.checking_balance, user.savings_balance, user.email, user.phone))
    conn.commit()

def get_user(conn, username):
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    return cur.fetchone()

def update_balance(conn, user_id, account_type, new_balance):
    cur = conn.cursor()
    if account_type == "Checking":
        cur.execute("UPDATE users SET checking_balance = ? WHERE user_id = ?", (new_balance, user_id))
    elif account_type == "Savings":
        cur.execute("UPDATE users SET savings_balance = ? WHERE user_id = ?", (new_balance, user_id))
    conn.commit()

def add_transaction(conn, transaction):
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO transactions (user_id, date, type, account, amount)
    VALUES (?,?,?,?,?)
    """, (transaction['user_id'], transaction['date'],
          transaction['type'], transaction['account'], transaction['amount']))
    conn.commit()

def get_transactions(conn, user_id):
    cur = conn.cursor()
    cur.execute("SELECT date, type, account, amount FROM transactions WHERE user_id = ?", (user_id,))
    return cur.fetchall()

def add_beneficiary(conn, beneficiary):
    cur = conn.cursor()
    cur.execute("""
    INSERT INTO beneficiaries (user_id, name, account_number, bank_name)
    VALUES (?, ?, ?, ?)
    """, (beneficiary['user_id'], beneficiary['name'], beneficiary['account_number'], beneficiary['bank_name']))
    conn.commit()

def get_beneficiaries(conn, user_id):
    cur = conn.cursor()
    cur.execute("SELECT * FROM beneficiaries WHERE user_id = ?", (user_id,))
    return cur.fetchall()


def update_user_profile(conn, user_id, email, phone):
    cur = conn.cursor()

    # Check if email and phone columns exist
    cur.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cur.fetchall()]

    if 'email' in columns and 'phone' in columns:
        cur.execute("""
        UPDATE users 
        SET email = ?, phone = ?
        WHERE user_id = ?
        """, (email, phone, user_id))
    elif 'email' in columns:
        cur.execute("""
        UPDATE users 
        SET email = ?
        WHERE user_id = ?
        """, (email, user_id))
    elif 'phone' in columns:
        cur.execute("""
        UPDATE users 
        SET phone = ?
        WHERE user_id = ?
        """, (phone, user_id))
    else:
        print("Neither email nor phone columns exist in the users table.")

    conn.commit()

# Initialize DB
if __name__ == "__main__":
    conn = create_connection()
    create_tables(conn)
    conn.close()