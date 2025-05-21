import sqlite3 as sql
from public.scripts.tools import hash, check_hash


class AccountsManager:
    def __init__(self) -> None:
        pass

    def create_account(self, username: str, password: str) -> None:
        hashed_password = hash(password)
        db = sql.connect(".database/accounts.db")
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO accounts (username,password) VALUES (?,?)", # Maybe will need quotation marks here, could make f string
            (username, hashed_password),
        )
        db.commit()
        db.close()
        return
    
    def verify_login(self, username: str, password: str) -> tuple:
        db = sql.connect(".database/accounts.db")
        cursor = db.cursor()
        res = cursor.execute(
            f"SELECT * FROM accounts WHERE username = '{username}'"
        )
        if len(res.fetchall()) > 1:
            abc = res.fetchall()
            db.close()
            raise Exception("More than one account with username", abc)
        elif res.fetchone() is None:
            db.close()
            return (False, 1)
        res = cursor.execute(
            f"SELECT password FROM accounts WHERE username = '{username}'"
        )
        fetch = res.fetchone()
        password_hash = fetch[0]
        print(password_hash)
        if not check_hash(password, password_hash):
            db.close()
            return (False, 2)
        res = cursor.execute(
            f"SELECT id FROM accounts WHERE username = '{username}'"
        )
        user_id = res.fetchone()[0]
        db.close()
        return (True, user_id)
    
    def fetch_username(self, id: int) -> str:
        db = sql.connect(".database/accounts.db")
        cursor = db.cursor()
        res = cursor.execute(
            f"SELECT username FROM accounts WHERE id = {id}"
        )
        username = res.fetchone()[0]
        db.close()
        return username
    
    def username_is_unique(self, username: str) -> bool:
        db = sql.connect(".database/accounts.db")
        cursor = db.cursor()
        res = cursor.execute(
            f"SELECT * FROM accounts WHERE username = '{username}'"
        )
        if res.fetchone() is None:
            db.close()
            return True
        else:
            db.close()
            return False

