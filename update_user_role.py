import sqlite3

def update_user_role(username, new_role):
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET role = ? WHERE username = ?", (new_role, username))
    conn.commit()
    conn.close()
    print(f"Role for user {username} updated to {new_role}.")

update_user_role('danil', 'admin')

