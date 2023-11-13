import sqlite3
from flask import g 

def create_table(db):
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            firstname TEXT NOT NULL,
            lastname TEXT NOT NULL,
            country TEXT NOT NULL,
            title TEXT NOT NULL,
            email TEXT ,
            password TEXT NOT NULL
        );          
    ''')
    db.commit()

def get_db():
    db  = getattr(g, '_database', None )
    if db is None:
        db = g._database = sqlite3.connect('./user.db')
        create_table(db)
    return db

def add_user(username,firstname, lastname, country, title, email, password):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("INSERT INTO users (username,firstname, lastname, country, title, email, password) VALUES (?, ?, ?,?,?,?,?)", (username,firstname, lastname, country, title, email, password))

    db.commit()
    
    return 0

def check_user(email):
    db = get_db()
    cursor = db.cursor()

    cursor.execute(f"SELECT * FROM USERS WHERE email= '{email}'")

    data = cursor.fetchone()

    db.commit()
    
    return data

def is_username_taken(username):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(f"SELECT username FROM users where username= '{username}'")

    result = cursor.fetchone()

    db.commit()



    return result is not None

def get_by_id(user_id):
    db = get_db()
    cursor = db.cursor()

    # Execute the SQL query to retrieve a user by ID
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user_data = cursor.fetchone()

    db.commit()


    return user_data

# ---------------------------------------------------------------------------------------------------------------------------------------------
