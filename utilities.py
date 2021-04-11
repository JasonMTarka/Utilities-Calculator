# import datetime
from random import randint, choice


class Application:
    def __init__(self):
        self.gas = Utility("Gas")
        self.rent = Utility("Rent")
        self.electric = Utility("Electric")
        self.water = Utility("Water")
        self.utilities = {'gas': self.gas,
                          'rent': self.rent,
                          'electric': self.electric,
                          'water': self.water}

        self.__tester__()
        self.jason_owes, self.xiaochen_owes = self.calculate_amount_owed()
        # self.current_date = datetime.datetime()

    def __repr__(self):
        return f"Application()"

    def __str__(self):
        return "Primary application"

    def __tester__(self):
        for _ in range(3):
            self.gas.record.append(Bill('gas', randint(2000, 4000), choice(["04-21", "01-21", "03-21", "02-21", "05-21"]), note="Xiaochen loves poop"))
            self.rent.record.append(Bill('rent', 94000, choice(["04-21", "01-21", "03-21", "02-21", "05-21"]), note="Xiaochen loves poop"))
            self.water.record.append(Bill('water', randint(5000, 6000), choice(["04-21", "01-21", "03-21", "02-21", "05-21"]), note="Xiaochen loves poop"))
            self.electric.record.append(Bill('electric', randint(7000, 8000), choice(["04-21", "01-21", "03-21", "02-21", "05-21"]), note="Xiaochen loves poop"))

    def calculate_amount_owed(self):
        j_collector = 0
        x_collector = 0

        for utility in self.utilities.values():
            for bill in utility.unpaid_bills():
                if bill.jason_paid is False:
                    j_collector += bill.owed_amount
                if bill.xiaochen_paid is False:
                    x_collector += bill.owed_amount
        return (j_collector, x_collector)

    def main_menu(self):
        print()
        print("Welcome to Jason and Xiaochen's utility calculator.")
        print(f"Today is PLACEHOLDER.")
        print(f"Jason currently owes {self.jason_owes} yen and Xiaochen currently owes {self.xiaochen_owes} yen.")

        print()
        print("What utility would you like to view?")
        print("Enter 'Rent', 'Gas', 'Electric', or 'Water':")
        utility_intent = input().lower()
        if utility_intent not in {'rent', 'gas', 'electric', 'water'}:
            print(f"{utility_intent} is not one of our bills.  Check your spelling and try again.")
            self.main_menu()

        print()
        print(f"What would you like to do with {utility_intent}?")
        print()
        print("'add bill' - Add a new bill.")
        print("'check record' - Check a utility record.")
        print("'check unpaid bills' - Check unpaid bills for a given utility.")
        print("'pay bill' - Pay an outstanding bill.")
        intent = input().lower()

        if intent == 'add bill':
            self.add_bill(utility_intent)

        if intent == 'check record':
            self.check_record(utility_intent)

        if intent == 'check unpaid bills':
            self.check_unpaid_bills(utility_intent)

        if intent == 'pay bill':
            self.pay_bill(utility_intent)

    def add_bill(self, utility):
        print()

        print("How much is the bill for?")
        print("Enter the amount in yen:")
        amount_intent = input().lower()

        print("What month(s) is this bill for?")
        print("Enter the bill date like the following: '04-21' for April 9th.")
        print("In the event that there is more than one month listed, please list with a ',' between the dates.")
        date_intent = input().lower()

        print("Is there anything more you'd like to add?")
        moreinfo_intent = input("Enter 'yes' or 'no'.")

        if moreinfo_intent == "yes":

            print("Has Xiaochen paid?")
            x_intent = input("Enter 'yes' or 'no'.").lower()
            print("Has Jason paid?")
            j_intent = input("Enter 'yes' or 'no'.").lower()
            print("Has the bill been fully paid?")
            paid_intent = input("Enter 'yes' or 'no'.").lower()
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

            bill = Bill(utility, amount_intent, date_intent, xiaochen_paid=x_intent, jason_paid=j_intent, paid=paid_intent, note=note_intent)

        else:
            print("Creating bill...")
            bill = Bill(utility, amount_intent, date_intent)

        self.utilities[bill.utility].record.append(bill)
        print(f"Bill has been successfully created and added to the {bill.utility} bill record!")
        self.main_menu()

    def check_record(self, utility):
        for entry in self.utilities[utility].record:
            print(entry)
        self.main_menu()

    def check_unpaid_bills(self, utility):
        for entry in self.utilities[utility].record:
            if entry.paid is False:
                print(entry)

    def pay_bill(self, utility):
        record = self.utilities[utility].record
        print("Who are you?")
        print("Enter 'Xiaochen' or 'Jason'.")
        identity = input().lower()

        if identity == "xiaochen":
            for entry in record:
                if entry.xiaochen_paid is False:
                    print(entry)

        if identity == "jason":
            for entry in record:
                if entry.jason_paid is False:
                    print(entry)

        print("Which bill would you like to pay?")
        print("Enter the bill's ID:")
        intent = input().lower()
        for entry in record:
            if entry.ID == int(intent):
                print(entry)
                print(f"You owe {entry.owed_amount} yen.")
                print(f"Will you pay your bill?")
                intent = input("Type 'yes' or 'no'.").lower()

                if intent == "yes":
                    if identity == 'jason':
                        entry.jason_paid = True
                        self.utilities[utility].payment_log.append((f"Jason paid {entry.owed_amount} for bill (ID {entry.ID}) on PLACEHOLDER, paying off his portion of the bill."))
                        self.jason_owes -= entry.owed_amount

                    elif identity == 'xiaochen':
                        entry.xiaochen_paid = True
                        self.utilities[utility].payment_log.append((f"Xiaochen paid {entry.owed_amount} for bill (ID {entry.ID}) on PLACEHOLDER, paying off her portion of the bill."))
                        self.xiaochen_owes -= entry.owed_amount

                    if entry.jason_paid is True and entry.xiaochen_paid is True:
                        entry.paid = True
                        print("This bill has been completely paid off!")

                    print("Returning to main menu...")
                    self.main_menu()
        print("Not a valid bill ID.")
        self.main_menu()


class Utility:

    def __init__(self, name, payment_method="Credit Card"):
        self.name = name
        self.record = []
        self.payment_log = []
        self.last_payment = []
        self.payment_method = payment_method

    def __repr__(self):
        return f"Utility({self.name})"

    def __str__(self):
        return f"{self.name}"

    def unpaid_bills(self):
        collector = []
        for entry in self.record:
            if entry.paid is False:
                collector.append(entry)
        return collector


class Bill:

    ID = 0

    def __init__(self, utility, amount, date, xiaochen_paid=True, jason_paid=False, paid=False, note=""):
        self.utility = utility
        self.amount = amount
        self.date = date
        self.xiaochen_paid = xiaochen_paid
        self.jason_paid = jason_paid
        self.paid = paid
        self.note = note

        self.owed_amount = amount / 2
        self.ID = Bill.ID
        Bill.ID += 1

    def __repr__(self):
        return f"""
            Bill({self.utility}, {self.amount}, {self.date},
            xiaochen_paid={self.xiaochen_paid}, jason_paid={self.jason_paid})
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
            A {self.utility} bill for {self.amount} for {self.date}.
            Xiaochen has {x} and Jason has {j}.
            ID: {self.ID}
            Notes: {self.note}
            """


def main():
    app = Application()
    app.main_menu()


if __name__ == "__main__":
    main()
