from datetime import datetime
from os import system

from bill import Bill
from database import Database


class Application:
    def __init__(self, db):
        self.db = db

    @property
    def jason_owes(self):
        return self.db.get_total_owed("jason")

    @property
    def xiaochen_owes(self):
        return self.db.get_total_owed("xiaochen")

    @property
    def today(self):
        return datetime.today().strftime('%B %d, %Y at %I:%M %p.')

    def intro(self):
        system('cls')
        print()
        print("Welcome to Jason and Xiaochen's utility calculator.")
        print(f"Today is {self.today}")
        self.main_menu()

    def main_menu(self):
        print()
        print(f"Jason currently owes {self.jason_owes} yen and Xiaochen currently owes {self.xiaochen_owes} yen.")
        print()
        print("You can examine a particular utility or either Jason or Xiaochen's payment history.")
        print("Enter 'Rent', 'Gas', 'Electric', 'Water', 'Jason', or 'Xiaochen':")
        print()
        print("You can return to this page by entering 'main' at any point.")
        intent = input().lower()
        print("*****")
        if intent == 'main':
            self.main_menu()
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
            print("*****")

            if utility_intent == 'main':
                self.main_menu()

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
        print("*****")
        if amount_intent == 'main':
            self.main_menu()
        try:
            amount_intent = int(amount_intent)
        except ValueError:
            self._input_handler(message="Please enter an integer.", destination="bill addition", arg=utility)

        print("What month(s) is this bill for?")
        print("Enter the bill date like the following: '04-21' for April 9th.")
        print("In the event that there is more than one month listed, please list with a ',' between the dates.")
        date_intent = input().lower()
        print("*****")
        if date_intent == 'main':
            self.main_menu()

        print("Is there anything more you'd like to add?")
        moreinfo_intent = input("Enter 'yes' or 'no'.").lower()
        print("*****")
        if moreinfo_intent == 'main':
            self.main_menu()
        if moreinfo_intent == "yes":

            print("Has Xiaochen paid?")
            x_intent = input("Enter 'yes' or 'no'.").lower()
            print("*****")
            if x_intent == 'main':
                self.main_menu()
            if x_intent not in {"yes", "no"}:
                print("Please enter 'yes' or 'no'.")
                self.add_bill(utility)
            print("Has Jason paid?")
            j_intent = input("Enter 'yes' or 'no'.").lower()
            print("*****")
            if j_intent == 'main':
                self.main_menu()
            if j_intent not in {"yes", "no"}:
                print("Please enter 'yes' or 'no'.")
                self.add_bill(utility)
            print("Has the bill been fully paid?")
            paid_intent = input("Enter 'yes' or 'no'.").lower()
            print("*****")
            if paid_intent == 'main':
                self.main_menu()
            if paid_intent not in {"yes", "no"}:
                print("Please enter 'yes' or 'no'.")
                self.add_bill(utility)
            print("Do you have any notes you'd like to make about this bill? (Press enter to skip)")
            note_intent = input().lower()
            print("*****")
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
        print("*****")
        if intent == 'main':
            self.main_menu()
        try:
            intent = int(intent)
        except ValueError:
            self._input_handler(destination="bill removal", arg=utility)

        for entry in records:
            if entry.id == intent:
                print(entry)
                print(f"Will you remove this bill?")
                intent = input("Type 'yes' or 'no'.").lower()
                print("*****")
                if intent == 'main':
                    self.main_menu()
                if intent == "yes":
                    self.db.remove_bill(entry)
                    self._input_handler(message=None)
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
        print("*****")
        if identity == 'main':
            self.main_menu()

        if identity == "xiaochen":
            collector = []
            for entry in records:
                if entry.xiaochen_paid is False:
                    collector.append(entry)

            if len(collector) == 0:
                print("You don't have any bills to pay.")
                print(self._input_handler(message=None))

            for entry in collector:
                print(entry)

        elif identity == "jason":
            collector = []
            for entry in records:
                if entry.jason_paid is False:
                    collector.append(entry)

            if len(collector) == 0:
                print("You don't have any bills to pay.")
                print(self._input_handler(message=None))

            for entry in collector:
                print(entry)

        else:
            self._input_handler(destination="bill payment", arg=utility)

        print("Which bill would you like to pay?")
        print("You can pay multiple bills at once by entering multiple IDs separated by a space.")
        print("Enter the ID:")
        intent = input().lower()
        print("*****")
        if intent == 'main':
            self.main_menu()

        intent_list = intent.split(" ")
        print(intent_list)
        if len(intent_list) == 1:
            for entry in records:
                if entry.id == int(intent):
                    print(entry)
                    print(f"You owe {entry.owed_amount} yen.")
                    print(f"Will you pay your bill?")
                    intent = input("Type 'yes' or 'no'.").lower()
                    print("*****")
                    if intent == 'main':
                        self.main_menu()

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


def main():

    db = Database()
    app = Application(db)
    app.intro()


if __name__ == "__main__":
    main()
