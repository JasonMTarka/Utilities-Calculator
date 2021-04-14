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
        intent = self._input_handler(acceptable_inputs={'rent', 'gas', 'electric', 'water', 'jason', 'xiaochen'})

        if intent in {'rent', 'gas', 'electric', 'water'}:
            self.utility_menu(intent)

        elif intent == "jason":
            print("Jason owes", self.db.get_total_owed("jason"))
            print("Here are his unpaid bills:")
            for entry in self.db.get_bills_owed("jason"):
                print(entry)
            self.main_menu()

        else:
            print("Xiaochen owes ", self.db.get_total_owed("xiaochen"))
            print("Here are her unpaid bills:")
            for entry in self.db.get_bills_owed("xiaochen"):
                print(entry)
            self.main_menu()

    def utility_menu(self, utility, display=True):
        if display:
            self.check_record(utility)
        print(f"What would you like to do with {utility}?")
        print()
        print("'add bill' - Add a new bill.")
        print("'check unpaid bills' - Check unpaid bills for a given utility.")
        print("'pay bill' - Pay an outstanding bill.")
        print("'remove bill' - Remove a bill.")

        intent = self._input_handler(acceptable_inputs={'add bill', 'check unpaid bills', 'pay bill', 'remove bill'})

        if intent == 'add bill':
            self.add_bill(utility)

        elif intent == 'check unpaid bills':
            self.check_unpaid_bills(utility)

        elif intent == 'pay bill':
            self.pay_bill(utility)

        elif intent == 'remove bill':
            self.remove_bill(utility)

        else:
            self._error_handler()

    def add_bill(self, utility):

        print()
        print("How much is the bill for?")
        print("Enter the amount in yen:")
        amount_intent = self._input_handler(integer=True, utility=utility, destination="bill addition")

        print("What month(s) is this bill for?")
        print("Enter the bill date like the following: '04-21' for April 9th.")
        print("In the event that there is more than one month listed, please list with a ',' between the dates.")
        date_intent = self._input_handler()

        print("Is there anything more you'd like to add?")
        moreinfo_intent = self._input_handler(boolean=True)

        if moreinfo_intent == "yes":

            print("Has Xiaochen paid?")
            x_intent = self._input_handler(message="Please enter 'yes' or 'no'.", destination="bill addition", utility=utility, boolean=True)

            print("Has Jason paid?")
            j_intent = self._input_handler(message="Please enter 'yes' or 'no'.", destination="bill addition", utility=utility, boolean=True)

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

            if x_intent is True and j_intent is True:
                paid_intent = True
            else:
                paid_intent = False

            bill = Bill(utility, date_intent, amount_intent, xiaochen_paid=x_intent, jason_paid=j_intent, paid=paid_intent, note=note_intent)

        elif moreinfo_intent == "no":
            print("Creating bill...")
            bill = Bill(utility, date_intent, amount_intent)

        self.db.add_bill(bill)
        print(f"Bill has been successfully created and added to the {bill.utility} bill record!")
        print("Returning to main menu...")
        self.main_menu()

    def remove_bill(self, utility):
        records = self.db.get_utility_record(utility)
        for record in records:
            print(record)
        print("Which bill would you like to remove?")
        print("Input bill ID:")
        intent = self._input_handler(integer=True, destination="bill removal", utility=utility)

        for entry in records:
            if entry.id == intent:
                print(entry)
                print(f"Will you remove this bill?")
                intent = self._input_handler(boolean=True, utility=utility, destination="bill removal")

                if intent == "yes":
                    self.db.remove_bill(entry)
                    self._error_handler(message=None)
                else:
                    self._error_handler(message="Returning to main menu.")

        self._error_handler(message="The input bill ID could not be found.", destination="bill removal", utility=utility)

    def check_record(self, utility):
        for record in self.db.get_utility_record(utility):
            print(record)

    def check_unpaid_bills(self, utility):
        for entry in self.db.get_utility_record(utility):
            if entry.paid is False:
                print(entry)
        self.utility_menu(utility, display=False)

    def pay_bill(self, utility):
        records = self.db.get_utility_record(utility)
        print("Who are you?")
        print("Enter 'Xiaochen' or 'Jason'.")
        identity = self._input_handler(acceptable_inputs={'xiaochen', 'jason'}, utility=utility, destination="bill payment")

        if identity == "xiaochen":
            collector = []
            for entry in records:
                if entry.xiaochen_paid is False:
                    collector.append(entry)

            if len(collector) == 0:
                print("You don't have any bills to pay.")
                print(self._error_handler(message=None))

            for entry in collector:
                print(entry)

        else:
            collector = []
            for entry in records:
                if entry.jason_paid is False:
                    collector.append(entry)

            if len(collector) == 0:
                print("You don't have any bills to pay.")
                print(self._error_handler(message=None))

            for entry in collector:
                print(entry)

        print("Which bill would you like to pay?")
        print("You can pay multiple bills at once by entering multiple IDs separated by a space.")
        print("Enter the ID:")
        intent = self._input_handler(destination="bill payment", utility=utility)

        intent_list = intent.split(" ")
        if len(intent_list) == 1:
            for entry in records:
                if entry.id == int(intent):
                    print(entry)
                    print(f"You owe {entry.owed_amount} yen.")
                    print(f"Will you pay your bill?")
                    intent = self._input_handler(destination="bill payment", utility=utility, boolean=True)

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
                        self._error_handler(message=None)

                    else:
                        self._error_handler(destination="bill payment", utility=utility)

            self._error_handler(message="The inputted bill ID could not be found.", destination="bill payment", utility=utility)

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

            self._error_handler(message="The inputted bill ID could not be found.", destination="bill payment", utility=utility)

        else:
            self._error_handler(destination="bill payment", utility=utility)

    def _input_handler(self, acceptable_inputs=None, message="Please enter a valid input.", utility=None, destination="main menu", integer=False, boolean=False):
        if boolean:
            print("Enter 'yes' or 'no'.")
        intent = input().lower()
        print("*****")
        print()

        if intent == 'main' or intent == 'back':
            self.main_menu()
        if integer:
            try:
                int(intent)
            except ValueError:
                self._error_handler(message="Please enter an integer.", destination=destination, utility=utility)
        if acceptable_inputs:
            if intent not in acceptable_inputs:
                self._error_handler(message=message, utility=utility, destination=destination)
        if boolean:
            if intent not in {'yes', 'no'}:
                self._error_handler(message="Please enter 'yes' or 'no'.", utility=utility, destination=destination)

        if integer:
            return int(intent)
        return intent

    def _error_handler(self, message="Please enter a valid input.", destination="main menu", utility=None):
        if message:
            print(message)
        print(f"Returning to {destination}.")
        if destination == "bill payment":
            self.pay_bill(utility)
        elif destination == "bill addition":
            self.add_bill(utility)
        elif destination == "bill removal":
            self.remove_bill(utility)
        elif destination == "utility menu":
            self.utility_menu(utility)
        else:
            self.main_menu()


def main():

    db = Database()
    app = Application(db)
    app.intro()


if __name__ == "__main__":
    main()
