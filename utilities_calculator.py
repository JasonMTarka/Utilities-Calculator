from datetime import datetime
from os import system

from bill import Bill
from database import Database


class Application:
    def __init__(self, db):
        self.db = db

    @property
    def user1_owes(self):
        return self.db.get_total_owed(self.db.get_user(1))

    @property
    def user2_owes(self):
        return self.db.get_total_owed(self.db.get_user(2))

    @property
    def today(self):
        return datetime.today().strftime('%B %d, %Y at %I:%M %p.')

    def intro(self):
        system('cls')
        print()
        print(f"Welcome to {self.db.get_user(1)} and {self.db.get_user(2)}'s utility calculator.")
        print(f"Today is {self.today}")
        self.main_menu()

    def main_menu(self):
        print()
        print(f"{self.db.get_user(1)} currently owes {self.user1_owes} yen and {self.db.get_user(2)} currently owes {self.user2_owes} yen.")
        print()
        print(f"You can examine a particular utility or either {self.db.get_user(1)} or {self.db.get_user(2)}'s payment history.")
        print(f"Enter 'Rent', 'Gas', 'Electric', 'Water', '{self.db.get_user(1)}', or '{self.db.get_user(2)}':")
        print()
        print("You can return to this page by entering 'main' at any point.")
        print("You can also quit this program at any point by entering 'quit'.")
        intent = self._input_handler(acceptable_inputs={'rent', 'gas', 'electric', 'water', self.db.get_user(1).lower(), self.db.get_user(2).lower()})

        if intent in {'rent', 'gas', 'electric', 'water'}:
            self.utility_menu(intent)

        elif intent == self.db.get_user(1).lower():
            print(f"{self.db.get_user(1)} owes", self.db.get_total_owed(self.db.get_user(1)))
            print("Here are their unpaid bills:")
            for entry in self.db.get_bills_owed(self.db.get_user(1)):
                print(entry)
            self.main_menu()

        else:
            print(f"{self.db.get_user(2)} owes ", self.db.get_total_owed(self.db.get_user(2)))
            print("Here are their unpaid bills:")
            for entry in self.db.get_bills_owed(self.db.get_user(2)):
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

        intent = self._input_handler(destination='utility menu', acceptable_inputs={'add bill', 'check unpaid bills', 'pay bill', 'remove bill'}, utility=utility, display=False)

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

    def quit_program(self):
        print("Closing program...")
        self.db.conn.close()
        quit()

    def add_bill(self, utility):

        print()
        print("How much is the bill for?")
        print("Enter the amount in yen:")
        amount_intent = self._input_handler(destination="bill addition", integer=True, utility=utility)

        print("What month(s) is this bill for?")
        print("Enter the bill date like the following: '04-21' for April 9th.")
        print("In the event that there is more than one month listed, please list with a ',' between the dates.")
        date_intent = self._input_handler()

        print("Is there anything more you'd like to add?")
        moreinfo_intent = self._input_handler(boolean=True)

        if moreinfo_intent == "yes":

            print(f"Has {self.db.get_user(2)} paid?")
            x_intent = self._input_handler(destination="bill addition", utility=utility, boolean=True)

            print(f"Has {self.db.get_user(1)} paid?")
            j_intent = self._input_handler(destination="bill addition", utility=utility, boolean=True)

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

            bill = Bill(utility, date_intent, amount_intent, user2_paid=x_intent, user1_paid=j_intent, paid=paid_intent, note=note_intent)

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
        intent = self._input_handler(destination="bill removal", integer=True, utility=utility)

        for entry in records:
            if entry.id == intent:
                print(entry)
                print(f"Will you remove this bill?")
                intent = self._input_handler(destination="bill removal", boolean=True, utility=utility)

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
        print(f"Enter '{self.db.get_user(1)}' or '{self.db.get_user(2)}'.")
        identity = self._input_handler(destination="bill payment", acceptable_inputs={self.db.get_user(2).lower(), self.db.get_user(1).lower()}, utility=utility)

        if identity == self.db.get_user(2):
            collector = []
            for entry in records:
                if entry.user2_paid is False:
                    collector.append(entry)

            if len(collector) == 0:
                print("You don't have any bills to pay.")
                print(self._error_handler(message=None))

            for entry in collector:
                print(entry)

        else:
            collector = []
            for entry in records:
                if entry.user1_paid is False:
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
                        if identity == self.db.get_user(1):
                            entry.user1_paid = True
                            self.db.pay_bill(entry)
                            entry.note += f"{self.db.get_user(1)} paid {entry.owed_amount} for bill (ID {entry.id}) on {self.today}, paying off their portion of the bill."

                        elif identity == self.db.get_user(2):
                            entry.user2_paid = True
                            self.db.pay_bill(entry)
                            entry.note += f"{self.db.get_user(2)} paid {entry.owed_amount} for bill (ID {entry.id}) on {self.today}, paying off their portion of the bill."

                        if entry.user1_paid is True and entry.user2_paid is True:
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
                        if identity == self.db.get_user(1):
                            entry.user1_paid = True
                            self.db.pay_bill(entry)
                            entry.note += f"{self.db.get_user(1)} paid {entry.owed_amount} for bill (ID {entry.id}) on {self.today}, paying off their portion of the bill."
                            print(f"You successfully paid your bill (ID:{entry.id})!")

                        elif identity == self.db.get_user(2):
                            entry.user2_paid = True
                            self.db.pay_bill(entry)
                            entry.note += f"{self.db.get_user(2)} paid {entry.owed_amount} for bill (ID {entry.id}) on {self.today}, paying off their portion of the bill."
                            print(f"You successfully paid your bill (ID:{entry.id})!")

            self._error_handler(message="The inputted bill ID could not be found.", destination="bill payment", utility=utility)

        else:
            self._error_handler(destination="bill payment", utility=utility)

    def _input_handler(self, message="Please enter a valid input.", destination="main menu", **kwargs):
        if kwargs.get('boolean'):
            print("Enter 'yes' or 'no'.")
        intent = input().lower()
        print("*****")
        print()

        if intent == 'main' or intent == 'back':
            self.main_menu()
        if intent == 'quit':
            self.quit_program()
        if kwargs.get('integer'):
            try:
                intent = int(intent)
            except ValueError:
                self._error_handler(message="Please enter an integer.", destination=destination, utility=kwargs.get('utility'))
        if kwargs.get('acceptable_inputs'):
            acceptable_inputs = kwargs.get('acceptable_inputs')
            if intent not in acceptable_inputs:
                self._error_handler(message=message, destination=destination, utility=kwargs.get('utility'))
        if kwargs.get('boolean'):
            if intent not in {'yes', 'no'}:
                self._error_handler(message="Please enter 'yes' or 'no'.", destination=destination, utility=kwargs.get('utility'),)

        return intent

    def _error_handler(self, message="Please enter a valid input.", destination="main menu", **kwargs):
        if message:
            print(message)
        print(f"Returning to {destination}.")
        if destination == "bill payment":
            self.pay_bill(kwargs.get('utility'))
        elif destination == "bill addition":
            self.add_bill(kwargs.get('utility'))
        elif destination == "bill removal":
            self.remove_bill(kwargs.get('utility'))
        elif destination == "utility menu":
            self.utility_menu(kwargs.get('utility'), display=kwargs.get('display'))
        else:
            self.main_menu()


def main():

    db = Database(test=True)
    app = Application(db)
    app.intro()


if __name__ == "__main__":
    main()
