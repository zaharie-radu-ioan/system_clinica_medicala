import os
import mariadb
import bcrypt
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT",3307))
DB_NAME = os.getenv("DB_NAME")
ROOT_USER = os.getenv("DB_USER")
ROOT_PASS = os.getenv("DB_PASSWORD")


AES_KEY = os.getenv("AES_KEY").encode('utf-8')
AES_IV = os.getenv("AES_IV").encode('utf-8')


def get_root_connection():
    return mariadb.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=ROOT_USER,
        password=ROOT_PASS,
        database=DB_NAME
    )


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(
        plain.encode(),
        bcrypt.gensalt()
    ).decode()


def create_db_users():
    conn = get_root_connection()
    cur = conn.cursor()

    db_users = [
        ("manager_db", "manager123", "ALL PRIVILEGES"),
        ("receptie_app ", "insert123", "SELECT, INSERT"),
        ("medic_app", "update123", "SELECT, INSERT, UPDATE"),
        ("mentenanta_db", "delete123", "SELECT, DELETE")
    ]

    for username, password, privileges in db_users:
        try:
            cur.execute(f"DROP USER IF EXISTS '{username}'@'%'")
            cur.execute(f"CREATE USER '{username}'@'%' IDENTIFIED BY '{password}'")
            cur.execute(f"GRANT {privileges} ON {DB_NAME}.* TO '{username}'@'%'")
            print(f"[OK] Created DB user: {username}")
        except Exception as e:
            print("Error:", e)

    cur.execute("FLUSH PRIVILEGES")
    conn.commit()
    conn.close()


def encrypt_app_users():
    conn = get_root_connection()
    cur = conn.cursor()

    cur.execute("SELECT id_utilizator, parola FROM utilizator")
    rows = cur.fetchall()

    for user_id, pwd in rows:
        if not str(pwd).startswith("$2b$") and not str(pwd).startswith("$2a$"):
            hashed = hash_password(pwd)
            cur.execute(
                "UPDATE utilizator SET parola=? WHERE id_utilizator=?",
                (hashed, user_id)
            )
            print(f"[UPDATED] User ID {user_id} password encrypted")

    conn.commit()
    conn.close()


def encrypt_aes(plain_text: str) -> str:
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    padded_data = pad(plain_text.encode('utf-8'), AES.block_size)
    encrypted_bytes = cipher.encrypt(padded_data)
    return base64.b64encode(encrypted_bytes).decode('utf-8')


def encrypt_cnp_pacienti():
    conn = get_root_connection()
    cur = conn.cursor()

    cur.execute("SELECT id_pacient, CNP FROM pacient")
    rows = cur.fetchall()

    for id_pacient, cnp in rows:
        if len(str(cnp)) == 13:
            cnp_encrypted = encrypt_aes(str(cnp))
            cur.execute(
                "UPDATE pacient SET CNP=? WHERE id_pacient=?",
                (cnp_encrypted, id_pacient)
            )
            print(f"[UPDATED] Pacient ID {id_pacient} CNP encrypted (AES-256)")

    conn.commit()
    conn.close()


def main():
    print("\n=== CREATE DB USERS + GRANT ===")
    create_db_users()

    print("\n=== ENCRYPT APP USERS PASSWORDS ===")
    encrypt_app_users()

    print("\n=== ENCRYPT SENSITIVE DATA (AES-256) ===")
    encrypt_cnp_pacienti()

    print("\n SECURITY SETUP COMPLETED")


if __name__ == "__main__":
    main()