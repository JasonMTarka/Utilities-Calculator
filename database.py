import sqlite3
from bill import Bill


class Database:
    def __init__(self):
        self.conn = sqlite3.connect("records.db")
        self.c = self.conn.cursor()

    def add_bill(self, bill):
        with self.conn:
            self.c.execute("INSERT INTO bills VALUES (NULL, :utility, :date, :amount, :x_paid, :j_paid, :paid, :note)",
                           {"utility": bill.utility, "date": bill.date, "amount": bill.amount, "x_paid": bill.xiaochen_paid, "j_paid": bill.jason_paid, "paid": bill.paid, "note": bill.note})

    def remove_bill(self, bill):
        with self.conn:
            self.c.execute("DELETE FROM bills WHERE id=:id", {"id": bill.id})

    def pay_bill(self, bill):
        with self.conn:
            self.c.execute("""
                UPDATE bills
                SET x_paid = :xiaochen_paid,
                    j_paid = :jason_paid,
                    paid = :paid,
                    note = :note
                WHERE id = :id
                """, {"xiaochen_paid": bill.xiaochen_paid, "jason_paid": bill.jason_paid, "paid": bill.paid, "id": bill.id, "note": bill.note})

    def pay_multiple_bills(self, bill_list):
        with self.conn:
            for bill in bill_list:
                self.pay_bill(bill)

    def get_all_records(self):
        self.c.execute("SELECT * FROM bills")
        collector = [self._convert_to_object(record) for record in self.c.fetchall()]
        return collector

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
        if person == "jason":
            self.c.execute("SELECT * FROM bills WHERE j_paid=False")
        else:
            self.c.execute("SELECT * FROM bills WHERE x_paid=False")

        collector = [self._convert_to_object(record) for record in self.c.fetchall()]
        return collector

    def get_total_owed(self, person):
        if person == "jason":
            self.c.execute("SELECT * FROM bills WHERE j_paid=False")
        else:
            self.c.execute("SELECT * FROM bills WHERE x_paid=False")
        records = self.c.fetchall()
        holder = 0
        for bill in records:
            holder += int(bill[3]) / 2
        return holder

    def _convert_to_object(self, record):
        return Bill(record[1], record[2], record[3], xiaochen_paid=record[4], jason_paid=record[5], paid=record[6], note=record[7], primary_key=record[0])
