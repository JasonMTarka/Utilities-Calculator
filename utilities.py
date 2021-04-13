from datetime import datetime
import sqlite3


class Application:
    def __init__(self, db):
        self.db = db

    def __repr__(self):
        return f"Application()"

    def __str__(self):
        return "Primary application"

    @property
    def jason_owes(self):
        return self.db.get_total_owed("jason")

    @property
    def xiaochen_owes(self):
        return self.db.get_total_owed("xiaochen")

    @property
    def today(self):
        return datetime.today().strftime('%B %d, %Y at %I:%M %p')

    def main_menu(self):
        print()
        print("Welcome to Jason and Xiaochen's utility calculator.")
        print(f"Today is {self.today}")
        print(f"Jason currently owes {self.jason_owes} yen and Xiaochen currently owes {self.xiaochen_owes} yen.")

        print()
        print("You can examine a particular utility or either Jason or Xiaochen's payment history.")
        print("Enter 'Rent', 'Gas', 'Electric', 'Water', 'Jason', or 'Xiaochen':")
        intent = input().lower()
        print()
        if intent not in {'rent', 'gas', 'electric', 'water', 'jason', 'xiaochen'}:
            self._input_handler()

        if intent in {'rent', 'gas', 'electric', 'water'}:
            print(f"What would you like to do with {intent}?")
            print()
            print("'add bill' - Add a new bill.")
            print("'check record' - Check a utility record.")
            print("'check unpaid bills' - Check unpaid bills for a given utility.")
            print("'pay bill' - Pay an outstanding bill.")
            print("'remove bill' - Remove a bill.")

            utility_intent = input().lower()

            if utility_intent == 'add bill':
                self.add_bill(intent)

            elif utility_intent == 'check record':
                self.check_record(intent)

            elif utility_intent == 'check unpaid bills':
                self.check_unpaid_bills(intent)

            elif utility_intent == 'pay bill':
                self.pay_bill(intent)

            elif utility_intent == 'remove bill':
                self.remove_bill(intent)

            else:
                self._input_handler()

        else:
            if intent == "jason":
                print("Jason owes", self.db.get_total_owed("jason"))
                print("Here are his unpaid bills:")
                for entry in self.db.get_bills_owed("jason"):
                    print(entry)
                self.main_menu()

            elif intent == "xiaochen":
                print("Xiaochen owes ", self.db.get_total_owed("xiaochen"))
                print("Here are her unpaid bills:")
                for entry in self.db.get_bills_owed("xiaochen"):
                    print(entry)
                self.main_menu()

            else:
                self._input_handler()

    def add_bill(self, utility):
        print()

        print("How much is the bill for?")
        print("Enter the amount in yen:")
        amount_intent = input().lower()
        try:
            amount_intent = int(amount_intent)
        except ValueError:
            self._input_handler(message="Please enter an integer.", destination="bill addition", arg=utility)

        print("What month(s) is this bill for?")
        print("Enter the bill date like the following: '04-21' for April 9th.")
        print("In the event that there is more than one month listed, please list with a ',' between the dates.")
        date_intent = input().lower()

        print("Is there anything more you'd like to add?")
        moreinfo_intent = input("Enter 'yes' or 'no'.").lower()

        if moreinfo_intent == "yes":

            print("Has Xiaochen paid?")
            x_intent = input("Enter 'yes' or 'no'.").lower()
            if x_intent not in {"yes", "no"}:
                print("Please enter 'yes' or 'no'.")
                self.add_bill(utility)
            print("Has Jason paid?")
            j_intent = input("Enter 'yes' or 'no'.").lower()
            if j_intent not in {"yes", "no"}:
                print("Please enter 'yes' or 'no'.")
                self.add_bill(utility)
            print("Has the bill been fully paid?")
            paid_intent = input("Enter 'yes' or 'no'.").lower()
            if paid_intent not in {"yes", "no"}:
                print("Please enter 'yes' or 'no'.")
                self.add_bill(utility)
            print("Do you have any notes you'd like to make about this bill? (Press enter to skip)")
            note_intent = input().lower()
            print("Creating bill...")

            if x_intent == "yes":
                x_intent = True
            else:
                x_intent = False

            if j_intent == "yes":
                j_intent = True
            else:
                j_intent = False

            bill = Bill(utility, date_intent, amount_intent, xiaochen_paid=x_intent, jason_paid=j_intent, paid=paid_intent, note=note_intent)

        elif moreinfo_intent == "no":
            print("Creating bill...")
            bill = Bill(utility, date_intent, amount_intent)

        else:
            self._input_handler(destination="bill addition", arg=utility)

        self.db.add_bill(bill)
        print(f"Bill has been successfully created and added to the {bill.utility} bill record!")
        self.main_menu()

    def remove_bill(self, utility):
        records = self.db.get_utility_record(utility)
        for record in records:
            print(record)
        print("Which bill would you like to remove?")
        print("Input bill ID:")
        intent = input().lower()
        try:
            intent = int(intent)
        except ValueError:
            self._input_handler(destination="bill removal", arg=utility)

        for entry in records:
            if entry.id == intent:
                print(entry)
                print(f"Will you remove this bill?")
                intent = input("Type 'yes' or 'no'.").lower()
                if intent == "yes":
                    self.db.remove_bill(entry)
                    self._input_handler()
                else:
                    self._input_handler(message="Returning to main menu.")

        self._input_handler(message="The inputted bill ID could not be found.", destination="bill removal", arg=utility)

    def check_record(self, utility):
        for record in self.db.get_utility_record(utility):
            print(record)
        self.main_menu()

    def check_unpaid_bills(self, utility):
        for entry in self.db.get_utility_record(utility):
            if entry.paid is False:
                print(entry)
        self.main_menu()

    def pay_bill(self, utility):
        records = self.db.get_utility_record(utility)
        print("Who are you?")
        print("Enter 'Xiaochen' or 'Jason'.")
        identity = input().lower()

        if identity == "xiaochen":
            for entry in records:
                if entry.xiaochen_paid is False:
                    print(entry)

        elif identity == "jason":
            for entry in records:
                if entry.jason_paid is False:
                    print(entry)

        else:
            self._input_handler(destination="bill payment", arg=utility)

        print("Which bill would you like to pay?")
        print("You can pay multiple bills at once by entering multiple IDs separated by a space.")
        print("Enter the ID:")
        intent = input().lower()

        intent_list = intent.split(" ")
        print(intent_list)
        if len(intent_list) == 1:
            for entry in records:
                if entry.id == int(intent):
                    print(entry)
                    print(f"You owe {entry.owed_amount} yen.")
                    print(f"Will you pay your bill?")
                    intent = input("Type 'yes' or 'no'.").lower()

                    if intent == "yes":
                        if identity == 'jason':
                            entry.jason_paid = True
                            self.db.pay_bill(entry)
                            entry.note += f"Jason paid {entry.owed_amount} for bill (ID {entry.id}) on {self.today}, paying off his portion of the bill."

                        elif identity == 'xiaochen':
                            entry.xiaochen_paid = True
                            self.db.pay_bill(entry)
                            entry.note += f"Xiaochen paid {entry.owed_amount} for bill (ID {entry.id}) on {self.today}, paying off her portion of the bill."

                        if entry.jason_paid is True and entry.xiaochen_paid is True:
                            entry.paid = True
                            print("This bill has been completely paid off!")

                        print("You successfully paid your bill!")
                        print("Returning to main menu...")
                        self.main_menu()

                    elif intent == "no":
                        self._input_handler(message=None)

                    else:
                        self._input_handler(destination="bill payment", arg=utility)

            self._input_handler(message="The inputted bill ID could not be found.", destination="bill payment", arg=utility)

        elif len(intent_list) > 1:
            for _id in intent_list:
                for entry in records:
                    if int(_id) == entry.id:
                        if identity == 'jason':
                            entry.jason_paid = True
                            self.db.pay_bill(entry)
                            entry.note += f"Jason paid {entry.owed_amount} for bill (ID {entry.id}) on {self.today}, paying off his portion of the bill."
                            print(f"You successfully paid your bill (ID:{entry.id})!")

                        elif identity == 'xiaochen':
                            entry.xiaochen_paid = True
                            self.db.pay_bill(entry)
                            entry.note += f"Xiaochen paid {entry.owed_amount} for bill (ID {entry.id}) on {self.today}, paying off her portion of the bill."
                            print(f"You successfully paid your bill (ID:{entry.id})!")

            self._input_handler(message="The inputted bill ID could not be found.", destination="bill payment", arg=utility)

        else:
            self._input_handler(destination="bill payment", arg=utility)

    def _input_handler(self, message="Please enter a valid input.", destination="main menu", arg=None):
        if message:
            print(message)
        print(f"Returning to {destination}.")
        if destination == "bill payment":
            self.pay_bill(arg)
        elif destination == "bill addition":
            self.add_bill(arg)
        elif destination == "bill removal":
            self.remove_bill(arg)
        else:
            self.main_menu()


class Bill:

    ID = 0

    def __init__(self, utility, date, amount, xiaochen_paid=True, jason_paid=False, paid=False, note=""):

        self.utility = utility
        self.amount = amount
        self.owed_amount = int(amount) / 2
        self.date = date

        if xiaochen_paid == 1:
            self.xiaochen_paid = True
        elif xiaochen_paid == 0:
            self.xiaochen_paid = False
        else:
            self.xiaochen_paid = xiaochen_paid

        if jason_paid == 1:
            self.jason_paid = True
        elif jason_paid == 0:
            self.jason_paid = False
        else:
            self.jason_paid = jason_paid

        if paid == 1:
            self.paid = True
        elif paid == 0:
            self.paid = False
        else:
            self.paid = paid

        self.note = note

        self.id = Bill.ID
        Bill.ID += 1

    def __repr__(self):
        return f"""
            Bill({self.utility}, {self.date}, {self.amount},
            xiaochen_paid={self.xiaochen_paid}, jason_paid={self.jason_paid},
            paid={self.paid}, note={self.note})
            """

    def __str__(self):
        if self.xiaochen_paid is True:
            x = "paid"
        else:
            x = "not paid yet"

        if self.jason_paid is True:
            j = "paid"
        else:
            j = "not paid yet"

        return f"""
            A {self.utility} bill for {self.amount} yen for {self.date}.
            Xiaochen has {x} and Jason has {j}.
            ID: {self.id}
            Notes: {self.note}
            """


class Database:
    def __init__(self):
        self.conn = sqlite3.connect("records.db")
        self.c = self.conn.cursor()

    def add_bill(self, bill):
        with self.conn:
            self.c.execute("INSERT INTO bills VALUES (:id, :utility, :date, :amount, :x_paid, :j_paid, :paid, :note)",
                           {"id": bill.id, "utility": bill.utility, "date": bill.date, "amount": bill.amount, "x_paid": bill.xiaochen_paid, "j_paid": bill.jason_paid, "paid": bill.paid, "note": bill.note})

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
        bill = Bill(record[1], record[2], record[3], xiaochen_paid=record[4], jason_paid=record[5], paid=record[6], note=record[7])
        bill.id = record[0]
        Bill.ID -= 1  # Correcting to avoid ID class variable from growing too much
        return bill

def main():

    db = Database()
    app = Application(db)
    app.main_menu()


if __name__ == "__main__":
    main()
