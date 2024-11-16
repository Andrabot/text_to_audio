import sqlite3

# Fungsi untuk membuat tabel users
def create_table():
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        usage_count INTEGER DEFAULT 0,
        license_expiry TEXT,
        payment_method TEXT,
        payment_proof TEXT,
        payment_status TEXT DEFAULT 'pending',
        role TEXT DEFAULT 'user'
    );
    ''')
    conn.commit()
    print("Table 'users' created successfully.")
    conn.close()

# Fungsi untuk menambahkan kolom role jika tabel users sudah ada
def add_role_column():
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(users);")
    columns = [col[1] for col in cursor.fetchall()]
    if 'role' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user';")
        conn.commit()
        print("Column 'role' added successfully.")
    conn.close()

# Fungsi untuk menambahkan user baru
def add_user(username, password, role='user'):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
    conn.commit()
    conn.close()
    print(f"User {username} added successfully with role {role}.")

# Eksekusi fungsi untuk setup database dan menambahkan user
create_table()
add_role_column()
add_user('danil', 'citra', 'user')  # Tambahkan user dengan role 'user'
