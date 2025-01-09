import sqlite3


def initiate_db():
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Products(
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            price TEXT NOT NULL
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Users(
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            age INTEGER NOT NULL,
            balance INTEGER NOT NULL
        )
        ''')


def add_user(username, email, age):
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO Users (username, email, age, balance) VALUES (?, ?, ?, ?)",
            (username, email, age, 1000)
        )


def is_included(username):
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Users WHERE username = ?", (username,))
        user = cursor.fetchone()
        return user is not None


def check_and_populate_products():
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM Products')
        count = cursor.fetchone()[0]

        if count == 0:
            for i in range(1, 5):
                cursor.execute(
                    'INSERT INTO Products (title, description, price) VALUES (?, ?, ?)',
                    (f'Продукт {i}', f'Описание {i}', f'{i * 100}')
                )


def get_all_products():
    with sqlite3.connect('database.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM Products')
        return cursor.fetchall()
