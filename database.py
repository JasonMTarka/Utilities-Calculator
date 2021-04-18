import sqlite3
from bill import Bill


class Database:
    def __init__(self, test=False, setup=False, **kwargs):

        if test is True:
            self.conn = sqlite3.connect(':memory:')
        else:
            self.conn = sqlite3.connect("records.db")

        self.c = self.conn.cursor()

        if setup is True or test is True:
            if test is True:
                kwargs = {'user1': 'TestUser1', 'user2': 'TestUser2'}
            self.setup(kwargs)

    def setup(self, kwargs):
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

    def get_user(self, user_id):
        self.c.execute("SELECT * FROM users WHERE id=:id", {"id": user_id})
        return self.c.fetchone()[1]

    def add_bill(self, bill):
        with self.conn:
            self.c.execute("INSERT INTO bills VALUES (NULL, :utility, :date, :amount, :x_paid, :j_paid, :paid, :note)",
                           {"utility": bill.utility, "date": bill.date, "amount": bill.amount, "x_paid": bill.user2_paid, "j_paid": bill.user1_paid, "paid": bill.paid, "note": bill.note})

    def remove_bill(self, bill):
        with self.conn:
            try:
                self.c.execute("DELETE FROM bills WHERE id=:id", {"id": bill.id})
            except AttributeError:
                self.c.execute("DELETE FROM bills WHERE id=:id", {"id": bill})

    def remove_utility(self, utility):
        with self.conn:
            self.c.execute("DELETE FROM bills WHERE utility=:utility", {"utility": utility})

    def pay_bill(self, bill):
        with self.conn:
            self.c.execute("""
                UPDATE bills
                SET x_paid = :user2_paid,
                    j_paid = :user1_paid,
                    paid = :paid,
                    note = :note
                WHERE id = :id
                """, {"user2_paid": bill.user2_paid, "user1_paid": bill.user1_paid, "paid": bill.paid, "note": bill.note, "id": bill.id})

    def pay_multiple_bills(self, bill_list):
        with self.conn:
            for bill in bill_list:
                self.pay_bill(bill)

    def get_all_records(self):
        self.c.execute("SELECT * FROM bills")
        collector = [self._convert_to_object(record) for record in self.c.fetchall()]
        return collector

    def get_record(self, bill):
        try:
            self.c.execute("SELECT * FROM bills WHERE id=:id", {"id": bill.id})
        except AttributeError:
            self.c.execute("SELECT * FROM bills WHERE id=:id", {"id": bill})

        try:
            return self._convert_to_object(self.c.fetchone())
        except TypeError:
            return None

    def get_utilities(self):
        self.c.execute("SELECT DISTINCT utility FROM bills")
        return self.c.fetchall()

    def get_utility_record(self, utility):
        self.c.execute("SELECT * FROM bills WHERE utility=:utility", {"utility": utility})
        collector = [self._convert_to_object(record) for record in self.c.fetchall()]
        return collector

    def get_unpaid_bills(self):
        self.c.execute("SELECT * FROM bills WHERE paid=False")
        collector = [self._convert_to_object(record) for record in self.c.fetchall()]
        return collector

    def get_paid_bills(self):
        self.c.execute("SELECT * FROM bills WHERE paid=True")
        collector = [self._convert_to_object(record) for record in self.c.fetchall()]
        return collector

    def get_bills_owed(self, person):
        if person == self.get_user(1).lower():
            self.c.execute("SELECT * FROM bills WHERE j_paid=False")
        else:
            self.c.execute("SELECT * FROM bills WHERE x_paid=False")

        collector = [self._convert_to_object(record) for record in self.c.fetchall()]
        return collector

    def get_total_owed(self, person):
        if person == self.get_user(1).lower():
            self.c.execute("SELECT * FROM bills WHERE j_paid=False")
        else:
            self.c.execute("SELECT * FROM bills WHERE x_paid=False")
        records = self.c.fetchall()
        holder = 0
        for bill in records:
            holder += int(bill[3]) / 2
        return holder

    def _convert_to_object(self, record):
        return Bill(record[1], record[2], record[3], user2_paid=record[4], user1_paid=record[5], paid=record[6], note=record[7], primary_key=record[0], user1=self.get_user(1), user2=self.get_user(2))

        # Example bill instantiation:
        # Bill("electric", "10-20", 5345, user2_paid=True, user1_paid=True, paid=True, note="Paid November 7th, through (canceled) Okinawa trip")
