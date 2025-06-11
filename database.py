import sqlite3

def create_tables():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # Create users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    );
    """)

    # Create questions table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        option1 TEXT NOT NULL,
        option2 TEXT NOT NULL,
        option3 TEXT NOT NULL,
        option4 TEXT NOT NULL,
        answer INTEGER NOT NULL CHECK(answer BETWEEN 1 AND 4)
    );
    """)

    # Create user_progress table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_progress (
        username TEXT,
        section TEXT,
        progress INTEGER DEFAULT 0,
        PRIMARY KEY (username, section),
        FOREIGN KEY (username) REFERENCES users(username)
    );
    """)

    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS user_scores (
        username TEXT,
        section TEXT,
        score INTEGER DEFAULT 0,
        PRIMARY KEY (username, section),
        FOREIGN KEY (username) REFERENCES users(username)
    );
    """)

    conn.commit()
    conn.close()
    print("All tables created successfully.")

if __name__ == "__main__":
    create_tables()
