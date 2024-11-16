import sqlite3

def add_user(username, password, role='user'):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    
    # Hapus user jika sudah ada
    cursor.execute("DELETE FROM users WHERE username = ?", (username,))
    
    # Tambahkan user baru
    cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
    conn.commit()
    conn.close()
    print(f"User {username} added successfully with role {role}.")

# Tambahkan user 'danil' dengan password 'citra' dan role 'user'
add_user('danil', 'citra', 'user')
