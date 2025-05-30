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
    
    def verify_login(self, username: str, password: str) -> bool:
        db = sql.connect(".database/accounts.db")
        cursor = db.cursor()
        # raise Exception(db, cursor)
        res = cursor.execute(
            f"SELECT * FROM accounts WHERE username == '{username}';"
        )
        user_details = res.fetchall()
        if len(user_details) > 1:
            abc = user_details
            db.close()
            raise Exception("More than one account with username", abc)
        elif len(user_details) == 0 or user_details is None:
            db.close()
            return False
        res = cursor.execute(
            f"SELECT password FROM accounts WHERE username = '{username}'"
        )
        fetch = res.fetchone()
        password_hash = fetch[0]
        print(password_hash) # debug
        db.close()
        return check_hash(password, password_hash)
    
    def fetch_username(self, id: int) -> str:
        db = sql.connect(".database/accounts.db")
        cursor = db.cursor()
        res = cursor.execute(
            f"SELECT username FROM accounts WHERE id = {id}"
        )
        username = res.fetchone()[0]
        db.close()
        return username
    
    def user_id(self, username: str, password: str) -> int:
        if self.verify_login(username, password):
            db = sql.connect(".database/accounts.db")
            cursor = db.cursor()
            res = cursor.execute(
            f"SELECT id FROM accounts WHERE username = '{username}'"
            )
            user_id = res.fetchone()[0]
            db.close()
            return user_id
        else:
            raise ValueError("User wasn't valid to fetch id")
        
    
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

