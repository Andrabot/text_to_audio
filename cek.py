import sqlite3

# Fungsi untuk memeriksa tabel yang ada dalam database
def check_tables():
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    # Menampilkan semua tabel yang ada
    print("Tables in the database:", tables)

    conn.close()

# Memeriksa tabel
check_tables()

