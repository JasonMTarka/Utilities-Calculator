import sqlite3
from typing import Any

from bill import Bill


class Database:
    def __init__(self, debug: bool = False, setup: bool = False, **kwargs: str) -> None:

        self.debug = debug
        if debug is True:
            self.conn = sqlite3.connect(':memory:')
        else:
            self.conn = sqlite3.connect("records.db")

        self.c = self.conn.cursor()

        if setup is True or debug is True:
            if debug is True:
                kwargs = {'user1': 'TestUser1', 'user2': 'TestUser2'}
            self.setup(kwargs)

    def setup(self, kwargs: dict) -> None:
        with self.conn:
            self.c.execute("""
                    CREATE TABLE bills (
                    id integer primary key,
                    utility text,
                    date text,
                    amount integer,
                    x_paid integer,
                    j_paid integer,
                    paid integer,
                    note text
                    )""")

            self.c.execute("""
                    CREATE TABLE users (
                    id integer primary key,
                    name text
                    )""")

            self.c.execute("""
                INSERT INTO users VALUES(NULL, :user1), (NULL, :user2)
                """, {'user1': kwargs.get('user1'), 'user2': kwargs.get('user2')})

            if self.debug is True:
                self.c.execute("""
                    INSERT INTO bills VALUES
                    (NULL, "gas", "05-21", 2000, 1, 0, 0, "Note"),
                    (NULL, "gas", "04-21", 3000, 1, 1, 1, "Note"),
                    (NULL, "electric", "03-21", 4500, 0, 1, 0, "Note"),
                    (NULL, "water", "02-21", 6211, 1, 0, 0, "Note"),
                    (NULL, "travel", "01-21", 8799, 1, 1, 1, "Note"),
                    (NULL, "gas", "12-20", 999, 0, 0, 0, "Note")
                    """)

    def get_user(self, user_id: int) -> str:
        self.c.execute("SELECT * FROM users WHERE id=:id", {"id": user_id})
        return self.c.fetchone()[1]

    def remove_utility(self, utility: str) -> None:
        with self.conn:
            self.c.execute("DELETE FROM bills WHERE utility=:utility", {"utility": utility})

    def add_bill(self, bill: Bill) -> None:
        with self.conn:
            self.c.execute("INSERT INTO bills VALUES (NULL, :utility, :date, :amount, :x_paid, :j_paid, :paid, :note)",
                           {"utility": bill.utility, "date": bill.date, "amount": bill.amount, "x_paid": bill.user2_paid, "j_paid": bill.user1_paid, "paid": bill.paid, "note": bill.note})

    def remove_bill(self, bill: Any) -> None:
        with self.conn:
            try:
                self.c.execute("DELETE FROM bills WHERE id=:id", {"id": bill.id})
            except AttributeError:
                self.c.execute("DELETE FROM bills WHERE id=:id", {"id": bill})

    def pay_bill(self, bill: Bill) -> None:
        with self.conn:
            self.c.execute("""
                UPDATE bills
                SET x_paid = :user2_paid,
                    j_paid = :user1_paid,
                    paid = :paid,
                    note = :note
                WHERE id = :id
                """, {"user2_paid": bill.user2_paid, "user1_paid": bill.user1_paid, "paid": bill.paid, "note": bill.note, "id": bill.id})

    def get_all_records(self) -> list[Bill]:
        self.c.execute("SELECT * FROM bills")
        collector = [self._convert_to_object(record) for record in self.c.fetchall()]
        return collector

    def get_record(self, bill) -> Any:
        try:
            # First check that bill is a Bill object
            self.c.execute("SELECT * FROM bills WHERE id=:id", {"id": bill.id})
        except AttributeError:
            # Next check that bill is a bill ID
            self.c.execute("SELECT * FROM bills WHERE id=:id", {"id": bill})

        try:
            return self._convert_to_object(self.c.fetchone())
        except TypeError:
            return None

    def get_utilities(self) -> list:
        self.c.execute("SELECT DISTINCT utility FROM bills")
        return self.c.fetchall()

    def get_utility_record(self, utility: str) -> list[Bill]:
        self.c.execute("SELECT * FROM bills WHERE utility=:utility", {"utility": utility})
        collector = [self._convert_to_object(record) for record in self.c.fetchall()]
        return collector

    def get_unpaid_bills(self) -> list[Bill]:
        self.c.execute("SELECT * FROM bills WHERE paid=False")
        collector = [self._convert_to_object(record) for record in self.c.fetchall()]
        return collector

    def get_paid_bills(self) -> list[Bill]:
        self.c.execute("SELECT * FROM bills WHERE paid=True")
        collector = [self._convert_to_object(record) for record in self.c.fetchall()]
        return collector

    def get_bills_owed(self, person: str) -> list[Bill]:
        if person == self.get_user(1).lower():
            self.c.execute("SELECT * FROM bills WHERE j_paid=False")
        else:
            self.c.execute("SELECT * FROM bills WHERE x_paid=False")

        collector = [self._convert_to_object(record) for record in self.c.fetchall()]
        return collector

    def get_total_owed(self, person: str) -> float:
        if person == self.get_user(1).lower():
            self.c.execute("SELECT * FROM bills WHERE j_paid=False")
        else:
            self.c.execute("SELECT * FROM bills WHERE x_paid=False")
        records = self.c.fetchall()
        holder = 0.0
        for bill in records:
            holder += int(bill[3]) / 2
        return holder

    def _convert_to_object(self, record) -> Bill:
        # Takes data from a database entry and converts it to a Bill object for use in the main application
        return Bill(record[1], record[2], record[3], user2_paid=record[4], user1_paid=record[5], paid=record[6], note=record[7], primary_key=record[0], user1=self.get_user(1), user2=self.get_user(2))

        # Example bill instantiation:
        # Bill("electric", "10-20", 5345, user1_paid=True, user2_paid=True, paid=True, note="Paid by credit card")

        # Example database entry:
        # (1, "rent", 04-21, 6350, 1, 0, 0, "Paid on 5-21")
