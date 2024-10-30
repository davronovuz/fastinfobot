
# subscription_channels.py: Obuna kanallari bilan ishlash
from .database import Database
from datetime import datetime

class SubscriptionChannelDatabase(Database):
    def create_table_subscription_channels(self):
        sql = """
        CREATE TABLE IF NOT EXISTS SubscriptionChannels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id BIGINT NOT NULL UNIQUE,
            channel_name VARCHAR(255) NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
        self.execute(sql, commit=True)

    def add_subscription_channel(self, channel_id: int, channel_name: str):
        sql = """
        INSERT INTO SubscriptionChannels(channel_id, channel_name, created_at)
        VALUES (?, ?, ?)
        """
        created_at = datetime.now().isoformat()
        self.execute(sql, parameters=(channel_id, channel_name, created_at), commit=True)

    def get_subscription_channels(self):
        sql = """
        SELECT * FROM SubscriptionChannels
        """
        return self.execute(sql, fetchall=True)

    def delete_subscription_channel(self, channel_id: int):
        sql = """
        DELETE FROM SubscriptionChannels WHERE channel_id = ?
        """
        self.execute(sql, parameters=(channel_id,), commit=True)