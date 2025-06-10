import os, sqlite3
from cryptography.fernet import Fernet
from werkzeug.security import generate_password_hash, check_password_hash

DB_DIR = os.path.join(os.path.dirname(__file__), 'sqldb')
DB_PATH = os.path.join(DB_DIR, 'admin_users.db')
KEY_PATH = os.path.join(DB_DIR, 'key.bin')

os.makedirs(DB_DIR, exist_ok=True)

def get_fernet():
    if not os.path.exists(KEY_PATH):
        key = Fernet.generate_key()
        with open(KEY_PATH, 'wb') as f:
            f.write(key)
    else:
        with open(KEY_PATH, 'rb') as f:
            key = f.read()
    return Fernet(key)

class AdminAuthManager:
    def __init__(self):
        self.fernet = get_fernet()
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    def register_admin(self, username, password):
        if not username or not password:
            return False, "Username and password required."
        try:
            password_hash = generate_password_hash(password)
            encrypted_hash = self.fernet.encrypt(password_hash.encode()).decode()
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('INSERT INTO admins (username, password_hash) VALUES (?, ?)', (username, encrypted_hash))
            conn.commit()
            conn.close()
            return True, "Admin registered."
        except sqlite3.IntegrityError:
            return False, "Username already exists."
        except Exception as e:
            return False, str(e)

    def verify_admin(self, username, password):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT password_hash FROM admins WHERE username = ?', (username,))
        row = c.fetchone()
        conn.close()
        if not row:
            return False
        encrypted_hash = row[0]
        try:
            password_hash = self.fernet.decrypt(encrypted_hash.encode()).decode()
            return check_password_hash(password_hash, password)
        except Exception:
            return False

    def get_all_admins(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT username FROM admins ORDER BY username')
        admins = [row[0] for row in c.fetchall()]
        conn.close()
        return admins

    def delete_admin(self, username):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('DELETE FROM admins WHERE username = ?', (username,))
            conn.commit()
            deleted = c.rowcount > 0
            conn.close()
            if deleted:
                return True, "Deleted"
            else:
                return False, "Admin not found"
        except Exception as e:
            return False, str(e)
