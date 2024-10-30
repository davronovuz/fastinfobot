import sqlite3
from datetime import datetime


class Database:
    def __init__(self, path_to_db="main.db"):
        self.path_to_db = path_to_db

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = ()
        connection = self.connection
        connection.set_trace_callback(logger)
        cursor = connection.cursor()
        data = None
        try:
            cursor.execute(sql, parameters)
            if commit:
                connection.commit()
            if fetchall:
                data = cursor.fetchall()
            if fetchone:
                data = cursor.fetchone()
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            connection.rollback()
        finally:
            connection.close()
        return data

    def create_table_users(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id BIGINT NOT NULL,
            username VARCHAR(255)  NULL,
            referrer_id INTEGER NULL,
            balance DECIMAL(10, 2) NOT NULL DEFAULT 0.0,
            last_active DATETIME NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (referrer_id) REFERENCES Users (id) ON DELETE SET NULL
        );
        """
        self.execute(sql, commit=True)

    def create_table_referral_rewards(self):
        sql = """
        CREATE TABLE IF NOT EXISTS ReferralRewards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            reward_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.0,
            referrals_count INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES Users (id) ON DELETE CASCADE
        );
        """
        self.execute(sql, commit=True)

    def create_table_transaction_history(self):
        sql = """
        CREATE TABLE IF NOT EXISTS TransactionHistory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount DECIMAL(10, 2) NOT NULL,
            transaction_type VARCHAR(50) NOT NULL, -- 'reward', 'withdraw'
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES Users (id)
        );
        """
        self.execute(sql, commit=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ?" for item in parameters
        ])
        return sql, tuple(parameters.values())

    def add_user(self, telegram_id: int, username: str, referrer_id=None, created_at=None):
        sql = """
        INSERT INTO Users(telegram_id, username, referrer_id, balance, created_at) VALUES(?, ?, ?, 0.0, ?)
        """
        if created_at is None:
            created_at = datetime.now().isoformat()
        self.execute(sql, parameters=(telegram_id, username, referrer_id, created_at), commit=True)

    def select_all_users(self):
        sql = """
        SELECT * FROM Users
        """
        return self.execute(sql, fetchall=True)

    def select_user(self, **kwargs):
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, kwargs)
        return self.execute(sql, parameters=parameters, fetchone=True)

    def count_users(self):
        return self.execute("SELECT COUNT(*) FROM Users;", fetchone=True)

    def delete_users(self):
        self.execute("DELETE FROM Users WHERE TRUE", commit=True)

    def update_referral_reward(self, referrer_id: int, reward_amount: float):
        sql_check = "SELECT * FROM ReferralRewards WHERE user_id = ?"
        reward = self.execute(sql_check, parameters=(referrer_id,), fetchone=True)

        if reward:
            sql_update = """
            UPDATE ReferralRewards 
            SET reward_amount = reward_amount + ?, referrals_count = referrals_count + 1
            WHERE user_id = ?
            """
            self.execute(sql_update, parameters=(reward_amount, referrer_id), commit=True)
        else:
            sql_insert = """
            INSERT INTO ReferralRewards(user_id, reward_amount, referrals_count) VALUES(?, ?, 1)
            """
            self.execute(sql_insert, parameters=(referrer_id, reward_amount), commit=True)

        # Update user balance
        self.update_user_balance(referrer_id, reward_amount)
        # Add transaction history
        self.add_transaction_history(referrer_id, reward_amount, 'reward')

    def update_user_balance(self, user_id: int, amount: float):
        sql = """
        UPDATE Users
        SET balance = balance + ?
        WHERE id = ?
        """
        self.execute(sql, parameters=(amount, user_id), commit=True)

    def withdraw_user_balance(self, user_id: int, amount: float):
        user = self.select_user(id=user_id)
        if user and user[4] >= amount:  # assuming balance is the 5th element
            sql = """
            UPDATE Users
            SET balance = balance - ?
            WHERE id = ?
            """
            self.execute(sql, parameters=(amount, user_id), commit=True)
            self.add_transaction_history(user_id, -amount, 'withdraw')
        else:
            print("Insufficient balance.")

    def add_transaction_history(self, user_id: int, amount: float, transaction_type: str):
        sql = """
        INSERT INTO TransactionHistory(user_id, amount, transaction_type, created_at)
        VALUES (?, ?, ?, ?)
        """
        created_at = datetime.now().isoformat()
        self.execute(sql, parameters=(user_id, amount, transaction_type, created_at), commit=True)

    def update_user_last_active(self, user_id: int):
        sql = """
        UPDATE Users
        SET last_active = ?
        WHERE id = ?
        """
        last_active = datetime.now().isoformat()
        self.execute(sql, parameters=(last_active, user_id), commit=True)

    def get_user_referral_summary(self, user_id: int):
        sql = """
        SELECT reward_amount, referrals_count
        FROM ReferralRewards
        WHERE user_id = ?
        """
        return self.execute(sql, parameters=(user_id,), fetchone=True)

    def get_user_referral_details(self, user_id: int):
        sql = """
        SELECT Users.username, Users.balance, ReferralRewards.reward_amount, ReferralRewards.referrals_count
        FROM Users
        LEFT JOIN ReferralRewards ON Users.id = ReferralRewards.user_id
        WHERE Users.id = ?
        """
        return self.execute(sql, parameters=(user_id,), fetchone=True)

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

    def create_table_admins(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id BIGINT NOT NULL UNIQUE,
            username VARCHAR(255) NULL,
            role VARCHAR(50) NOT NULL DEFAULT 'admin', -- admin yoki superadmin kabi rol turlari
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

    def create_table_groups(self):
        sql = """
        CREATE TABLE IF NOT EXISTS Groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id BIGINT NOT NULL UNIQUE,
            group_name VARCHAR(255) NOT NULL,
            member_count INTEGER NOT NULL DEFAULT 0,
            joined_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_activity DATETIME NULL
        );
        """
        self.execute(sql, commit=True)

    def add_group(self, group_id: int, group_name: str, member_count: int):
        sql = """
        INSERT INTO Groups(group_id, group_name, member_count, joined_at)
        VALUES (?, ?, ?, ?)
        """
        joined_at = datetime.now().isoformat()
        self.execute(sql, parameters=(group_id, group_name, member_count, joined_at), commit=True)

    def update_group_member_count(self, group_id: int, member_count: int):
        sql = """
        UPDATE Groups
        SET member_count = ?, last_activity = ?
        WHERE group_id = ?
        """
        last_activity = datetime.now().isoformat()
        self.execute(sql, parameters=(member_count, last_activity, group_id), commit=True)

    def get_all_groups(self):
        sql = """
        SELECT * FROM Groups
        """
        return self.execute(sql, fetchall=True)

    def delete_group(self, group_id: int):
        sql = """
        DELETE FROM Groups WHERE group_id = ?
        """
        self.execute(sql, parameters=(group_id,), commit=True)


def logger(statement):
    print(f"""
_____________________________________________________        
Executing: 
{statement}
_____________________________________________________
""")
