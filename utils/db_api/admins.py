# admins.py: Adminlar bilan bog'liq operatsiyalar
from .database import Database
from datetime import datetime

class AdminDatabase(Database):
    def create_table_admins(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id BIGINT NOT NULL UNIQUE,
            username VARCHAR(255) NULL,
            role VARCHAR(50) NOT NULL DEFAULT 'admin',
            added_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
        self.execute(sql, commit=True)

    def add_admin(self, telegram_id: int, username: str, role: str = 'admin'):
        sql = """
        INSERT INTO Admins(telegram_id, username, role, added_at)
        VALUES (?, ?, ?, ?)
        """
        added_at = datetime.now().isoformat()
        self.execute(sql, parameters=(telegram_id, username, role, added_at), commit=True)

    def get_all_admins(self):
        sql = """
        SELECT * FROM Admins
        """
        return self.execute(sql, fetchall=True)

    def delete_admin(self, telegram_id: int):
        sql = """
        DELETE FROM Admins WHERE telegram_id = ?
        """
        self.execute(sql, parameters=(telegram_id,), commit=True)

    def update_admin_role(self, telegram_id: int, new_role: str):
        sql = """
        UPDATE Admins
        SET role = ?
        WHERE telegram_id = ?
        """
        self.execute(sql, parameters=(new_role, telegram_id), commit=True)
