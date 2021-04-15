import unittest
import utilities_calculator

from random import choice, randint

from bill import Bill
from database import Database


class TestUtilityCalculator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = Database(test=True)
        cls.db.c.execute("""
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

    @classmethod
    def tearDownClass(cls):
        cls.db.conn.close()

    def setUp(self):
        pass

    def tearDown(self):
        self.db.c.execute("""
        DELETE FROM bills
        """)

    def bill_generator(self, **kwargs):
        if kwargs.get('utility'):
            utility = kwargs.get('utility')
        else:
            utility = choice(("electric", "rent", "gas", "water"))

        if kwargs.get('amount'):
            amount = int(kwargs.get('amount'))
        else:
            amount = randint(2000, 10000)

        if kwargs.get('date'):
            date = kwargs.get('date')
        else:
            date = choice(("02-17", "03-17,04-17", "10-18", "10-20"))

        if kwargs.get('xiaochen_paid') is False or kwargs.get('xiaochen_paid') is True:
            xiaochen_paid = kwargs.get('xiaochen_paid')
        else:
            xiaochen_paid = choice((True, False))

        if kwargs.get('jason_paid') is False or kwargs.get('jason_paid') is True:
            jason_paid = kwargs.get('jason_paid')
        else:
            jason_paid = choice((True, False))

        if xiaochen_paid and jason_paid:
            paid = True
        else:
            paid = False

        return Bill(utility, date, amount, xiaochen_paid=xiaochen_paid, jason_paid=jason_paid, paid=paid, note="Test Note")

    def test_get_record(self):
        self.db.add_bill(self.bill_generator())
        self.db.add_bill(self.bill_generator())
        self.db.add_bill(self.bill_generator())
        self.db.add_bill(self.bill_generator())

        self.assertEqual(self.db.get_record(2).id, 2)
        self.assertEqual(self.db.get_record(1).id, 1)
        self.assertEqual(self.db.get_record(4).id, 4)
        self.assertIsNone(self.db.get_record(5))

    def test_db_add_bill(self):
        self.db.add_bill(self.bill_generator())
        self.assertEqual(len(self.db.get_all_records()), 1)
        self.db.add_bill(self.bill_generator())
        self.assertEqual(len(self.db.get_all_records()), 2)
        self.assertIsInstance(self.db.get_all_records()[0], type(self.bill_generator()))

    def test_db_remove_bill(self):

        amount = 3

        for _ in range(amount):
            self.db.add_bill(self.bill_generator())

        for i in range(1, amount + 1):
            self.db.remove_bill(i)
            self.assertEqual(len(self.db.get_all_records()), amount - 1)
            amount -= 1

    def test_db_pay_bill(self):
        bill = self.bill_generator(jason_paid=False, paid=False)

        self.db.add_bill(bill)

        self.assertEqual(self.db.get_all_records()[0].jason_paid, False)
        self.assertEqual(self.db.get_all_records()[0].paid, False)

        bill.xiaochen_paid = True
        bill.jason_paid = True
        bill.paid = True
        self.db.pay_bill(bill)

        self.assertEqual(self.db.get_all_records()[0].jason_paid, True)
        self.assertEqual(self.db.get_all_records()[0].paid, True)

    def test_db_pay_multiple_bills(self):

        amount = 3
        bill_list = []

        for _ in range(amount):
            bill = self.bill_generator(jason_paid=False, paid=False)
            bill.jason_paid = False
            bill.paid = False
            self.db.add_bill(bill)
            bill_list.append(bill)

        self.assertEqual(self.db.get_all_records()[0].paid, False)
        self.assertEqual(self.db.get_all_records()[1].paid, False)
        self.assertEqual(self.db.get_all_records()[2].paid, False)
        self.assertEqual(len(self.db.get_all_records()), 3)

        bill_id = 1
        for bill in bill_list:
            bill.id = bill_id
            bill_id += 1
            bill.xiaochen_paid = True
            bill.jason_paid = True
            bill.paid = True

        self.db.pay_multiple_bills(bill_list)

        self.assertEqual(self.db.get_all_records()[0].paid, True)
        self.assertEqual(self.db.get_all_records()[1].paid, True)
        self.assertEqual(self.db.get_all_records()[2].paid, True)

    def test_get_utility_record(self):

        self.db.add_bill(self.bill_generator(utility='rent'))
        self.db.add_bill(self.bill_generator(utility='rent'))
        self.db.add_bill(self.bill_generator(utility='rent'))
        self.db.add_bill(self.bill_generator(utility='gas'))
        self.db.add_bill(self.bill_generator(utility='electric'))
        self.db.add_bill(self.bill_generator(utility='electric'))

        self.assertEqual(len(self.db.get_utility_record('rent')), 3)
        self.assertEqual(len(self.db.get_utility_record('water')), 0)
        self.assertEqual(len(self.db.get_utility_record('gas')), 1)
        self.assertEqual(len(self.db.get_utility_record('electric')), 2)


if __name__ == "__main__":
    unittest.main()
