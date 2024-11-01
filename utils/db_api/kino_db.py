# kino_database.py: Kinolar bilan bog'liq operatsiyalar
from .database import Database
from datetime import datetime

class KinoDatabase(Database):
    def create_table_kino(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Kino (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id BIGINT NOT NULL UNIQUE,
            file_id VARCHAR(2000) NOT NULL,
            caption TEXT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME
        );
        """
        self.execute(sql, commit=True)

    def add_kino(self, post_id: int, file_id: str, caption: str):
        sql = """
        INSERT INTO Kino(post_id, file_id, caption, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        """
        timestamp = datetime.now().isoformat()
        self.execute(sql, parameters=(post_id, file_id, caption, timestamp, timestamp), commit=True)

    def update_kino_caption(self, post_id: int, new_caption: str):
        sql = """
        UPDATE Kino
        SET caption = ?, updated_at = ?
        WHERE post_id = ?
        """
        updated_at = datetime.now().isoformat()
        self.execute(sql, parameters=(new_caption, updated_at, post_id), commit=True)

    def get_kino_by_post_id(self, post_id: int):
        sql = """
        SELECT file_id, caption FROM Kino
        WHERE post_id = ?
        """
        result = self.execute(sql, parameters=(post_id,), fetchone=True)

        # Agar natija mavjud bo'lsa, dict shaklida qaytaramiz
        return {"file_id": result[0], "caption": result[1]} if result else None

    def get_all_kinos(self):
        sql = """
        SELECT * FROM Kino
        """
        return self.execute(sql, fetchall=True)

    def delete_movie(self, post_id: int):
        sql = """
        DELETE FROM Kino WHERE post_id = ?
        """
        self.execute(sql, parameters=(post_id,), commit=True)

    def search_kino_by_caption(self, keyword: str):
        sql = """
        SELECT * FROM Kino
        WHERE caption LIKE ?
        """
        return self.execute(sql, parameters=(f"%{keyword}%",), fetchall=True)

    def get_recent_kinos(self, days: int = 7):
        sql = """
        SELECT * FROM Kino
        WHERE created_at >= datetime('now', ? || ' days')
        """
        return self.execute(sql, parameters=(-days,), fetchall=True)

    def count_all_kinos(self):
        sql = """
        SELECT COUNT(*) as total FROM Kino
        """
        result = self.execute(sql, fetchone=True)
        return result['total'] if result else 0
