import sqlite3
from bill import Bill


class Database:
    def __init__(self, test=False):
        if test is True:
            self.conn = sqlite3.connect(':memory:')
        else:
            self.conn = sqlite3.connect("records.db")

        self.c = self.conn.cursor()

        self.c.execute("""
                CREATE TABLE bills (
                id integer primary key,
                utility text,
                date text,
                amount integer,
                x_paid boolean,
                j_paid boolean,
                paid boolean,
                note text
                )""")

        self.c.execute("""
                CREATE TABLE users (
                id integer primary key,
                name text
                )""")

        bills = [

            Bill("gas", "07-20", 2120, user1_paid=True, paid=True),
            Bill("gas", "08-20", 4350, user1_paid=True, paid=True),
            Bill("gas", "09-20", 3471, user1_paid=True, paid=True, note="Paid October 4th 2020"),
            Bill("gas", "10-20", 3498, user1_paid=True, paid=True, note="Paid November 7th, through (canceled) Okinawa trip"),
            Bill("gas", "11-20", 2492, user1_paid=True, paid=True, note="Paid by Hakone hotel"),
            Bill("gas", "12-20", 4088),
            Bill("gas", "01-21", 4965),
            Bill("gas", "02-21", 5022),
            Bill("gas", "03-21", 6523),

            Bill("electric", "05-20", 580, user1_paid=True, paid=True),
            Bill("electric", "06-20", 5970, user1_paid=True, paid=True),
            Bill("electric", "07-20", 7029, user1_paid=True, paid=True),
            Bill("electric", "08-20", 8375, user1_paid=True, paid=True, note="Paid October 4th 2020"),
            Bill("electric", "09-20", 9321, user1_paid=True, paid=True, note="Paid October 4th 2020"),
            Bill("electric", "10-20", 5345, user1_paid=True, paid=True, note="Paid November 7th, through (canceled) Okinawa trip"),
            Bill("electric", "11-20", 5251, user1_paid=True, paid=True, note="Paid November 28th by Hakone hotel"),
            Bill("electric", "12-20", 4523, user1_paid=True, paid=True, note="Paid January 12th 2021"),
            Bill("electric", "01-21", 5852, user1_paid=True, paid=True, note="Paid March 1st 2021"),
            Bill("electric", "02-21", 5054),

            Bill("water", "06-20", 2477, user1_paid=True, paid=True),
            Bill("water", "07-20,08-20", 7411, user1_paid=True, paid=True),
            Bill("water", "09-20,10-20", 6364, user1_paid=True, paid=True, note="Paid October 4th 2020"),
            Bill("water", "11-20,12-20", 7673, user1_paid=True, paid=True, note="Paid January 12th 2021"),
            Bill("water", "01-21,02-21", 8197, user1_paid=True, paid=True, note="Paid March 1st 2021"),
            Bill("water", "03-21,04-21", 8720),

            Bill("rent", "05-20", 94000, user1_paid=True, paid=True),
            Bill("rent", "06-20", 94000, user1_paid=True, paid=True),
            Bill("rent", "07-20", 94000, user1_paid=True, paid=True),
            Bill("rent", "08-20", 94000, user1_paid=True, paid=True),
            Bill("rent", "09-20", 94000, user1_paid=True, paid=True),
            Bill("rent", "10-20", 94000, user1_paid=True, paid=True, note="Paid October 4th 2020"),
            Bill("rent", "11-20", 94000, user1_paid=True, paid=True, note="Paid November 7th, through (canceled) Okinawa trip"),
            Bill("rent", "12-20", 94000, user1_paid=True, paid=True, note="Paid by Hakone hotel"),
            Bill("rent", "01-21", 94000, user1_paid=True, paid=True, note="Paid January 12th 2021"),
            Bill("rent", "02-21", 94000, user1_paid=True, paid=True, note="Paid March 1st 2021"),
            Bill("rent", "03-21", 94000, user1_paid=True, paid=True, note="Paid March 1st 2021"),
            Bill("rent", "04-21", 94000)
        ]

        for bill in bills:
            self.add_bill(bill)

        self.c.execute("""
            INSERT INTO users VALUES(NULL, 'Jason')
            """)

        self.c.execute("""
            INSERT INTO users VALUES(NULL, 'Xiaochen')
            """)

        self.c.execute("""
            SELECT * FROM users
            """)

        print(self.c.fetchall())

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
        if person == self.get_user(1):
            self.c.execute("SELECT * FROM bills WHERE j_paid=False")
        else:
            self.c.execute("SELECT * FROM bills WHERE x_paid=False")

        collector = [self._convert_to_object(record) for record in self.c.fetchall()]
        return collector

    def get_total_owed(self, person):
        if person == self.get_user(1):
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
