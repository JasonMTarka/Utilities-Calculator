from datetime import datetime
from os import system, path

from bill import Bill
from database import Database


class Application:
    def __init__(self, db):
        self.db = db
        self.user1_upper = self.db.get_user(1)  # Upper is used for user-facing print strings
        self.user2_upper = self.db.get_user(2)
        self.user1 = self.user1_upper.lower()  # Lower is used for variables and arguments
        self.user2 = self.user2_upper.lower()

        # Utility Menu is static, so only initialized once here in init.
        # The other Main Menu is dynamic, so it is initialized below as a function with the property decorator.
        self.utility_menu_options = {
            'add bill': {'func': self.add_bill, 'description': "Add a new bill.", 'name': "'Add Bill'"},
            'check unpaid bills': {'func': self.check_unpaid_bills, 'description': "Check unpaid bills for a given utility.", 'name': "'Check Unpaid Bills'"},
            'pay bill': {'func': self.pay_bill, 'description': "Pay a bill.", 'name': "'Pay Bill'"},
            'remove bill': {'func': self.remove_bill, 'description': "Remove a bill.", 'name': "'Remove Bill'"}
        }

    @property
    def main_menu_options(self):
        # Blank entry added before utilities for spacing
        options = {
            'add utility': {'func': self.add_utility, 'description': "Enter a new utility and bill.", 'name': '"Add Utility"'},
            'remove utility': {'func': self.remove_utility, 'description': "Remove a utility and all associated bills.", 'name': '"Remove Utility"'},
            self.user1: {'func': self.user_page, 'description': f"See information for {self.user1_upper}", 'arg': self.user1, 'name': f'"{self.user1_upper}"'},
            self.user2: {'func': self.user_page, 'description': f"See information for {self.user2_upper}", 'arg': self.user2, 'name': f'"{self.user2_upper}"'},
            '': {'name': "", 'description': ""}
        }

        for utility in self.utilities:
            options[utility] = {'func': self.utility_menu, 'arg': utility, 'name': f'"{utility[0].upper() + utility[1:]}"', 'description': f"Access your {utility} record."}

        # Returns a dictionary of all possible menu options containing descriptions, corresponding functions, names, and arguments
        return options

    @property
    def utilities(self):
        collector = []
        for tupl in self.db.get_utilities():
            collector.append(tupl[0])
        return collector

    @property
    def user1_owes(self):
        return self.db.get_total_owed(self.user1)

    @property
    def user2_owes(self):
        return self.db.get_total_owed(self.user2)

    @property
    def today(self):
        return datetime.today().strftime('%B %d, %Y at %I:%M %p')

    def start(self):
        system('cls')
        print()
        print(f"Welcome to {self.user1_upper} and {self.user2_upper}'s utility calculator.")
        print(f"Today is {self.today}")
        self.main_menu()

    def quit_program(self):
        print("Closing program...")
        self.db.conn.close()
        quit()

    def main_menu(self):
        print("****************************")
        print()
        print(f"{self.user1_upper} currently owes {self.user1_owes} yen and {self.user2_upper} currently owes {self.user2_owes} yen.")
        print(f"You can examine a particular utility or either {self.user1_upper} or {self.user2_upper}'s payment history.")
        print()
        for key in self.main_menu_options.keys():
            option = self.main_menu_options.get(key)
            print(f"{option.get('name')} - {option.get('description')}")
        print()
        print("You can return to this page by entering 'main' at any point.")
        print("You can also quit this program at any point by entering 'quit'.")
        intent = self.input_handler(acceptable_inputs=self.main_menu_options.keys())

        # Try block handles menu requests which require an argument
        # Except block handles menu requests which do not require an argument
        option = self.main_menu_options.get(intent)
        try:
            option.get('func')(option.get('arg'))
        except TypeError:
            self.option.get('func')()

    def user_page(self, user):
        print(f"{user[0].upper() + user[1:]} owes", self.db.get_total_owed(user))
        print("Here are their unpaid bills:")
        for entry in self.db.get_bills_owed(user):
            print(entry)
        self.main_menu()

    def utility_menu(self, utility, display=True):
        if display:
            self.check_record(utility)
        print(f"What would you like to do with {utility}?")
        print()
        for key in self.utility_menu_options.keys():
            option = self.utility_menu_options.get(key)
            print(f"{option.get('name')} - {option.get('description')}")

        intent = self.input_handler(destination='utility menu', acceptable_inputs=self.utility_menu_options.keys(), utility=utility, display=False)
        self.utility_menu_options.get(intent).get('func')(utility)

    def add_utility(self):
        print("What is the name of your new utility?")
        intent = self.input_handler()
        self.add_bill(intent)

    def remove_utility(self):
        print("What utility would you like to remove?")
        for utility in self.utilities:
            print(f"{utility[0].upper() + utility[1:]}")
        print("WARNING: removing a utility will also remove all bills associated with that utility!")
        intent = self.input_handler()
        print(f"Are you sure you want to remove {intent}?")
        removal_intent = self.input_handler(boolean=True)
        if removal_intent:
            self.db.remove_utility(intent)
            self.redirect(message=f"{intent} has been removed.")
        else:
            self.redirect(message=None)

    def add_bill(self, utility):
        print()
        print("How much is the bill for?")
        print("Enter the amount in yen:")
        amount_intent = self.input_handler(destination="bill addition", integer=True, utility=utility)

        print("What month(s) is this bill for?")
        print("Enter the bill date like the following: '04-21' for April 9th.")
        print("In the event that there is more than one month listed, please list with a ',' between the dates.")
        date_intent = self.input_handler()

        print("If you want to add more information, type 'yes'.  Otherwise, press any key to continue.")
        moreinfo_intent = self.input_handler()

        if moreinfo_intent == "yes":

            print(f"Has {self.user1_upper} paid?")
            j_intent = self.input_handler(destination="bill addition", utility=utility, boolean=True)

            print(f"Has {self.user2_upper} paid?")
            x_intent = self.input_handler(destination="bill addition", utility=utility, boolean=True)

            print("Do you have any notes you'd like to make about this bill? (Press enter to skip)")
            note_intent = input()
            print("*****")
            print("Creating bill...")

            if j_intent == "yes":
                j_intent = True
            else:
                j_intent = False

            if x_intent == "yes":
                x_intent = True
            else:
                x_intent = False

            if j_intent is True and x_intent is True:
                paid_intent = True
            else:
                paid_intent = False

            bill = Bill(utility, date_intent, amount_intent, user1_paid=j_intent, user2_paid=x_intent, paid=paid_intent, note=note_intent)

        else:
            print("Creating bill...")
            bill = Bill(utility, date_intent, amount_intent)

        self.db.add_bill(bill)
        print(f"Bill has been successfully created and added to the {bill.utility} bill record!")
        print("Returning to main menu...")
        self.main_menu()

    def remove_bill(self, utility):
        records = self.db.get_utility_record(utility)
        if not records:
            self.redirect(message=f"There are no bills in {utility}.", destination="utility menu", utility=utility)

        for record in records:
            print(record)
        print("Which bill would you like to remove?")
        print("Input bill ID:")
        intent = self.input_handler(destination="bill removal", integer=True, utility=utility)

        for entry in records:
            if entry.id == intent:
                print(entry)
                print(f"Will you remove this bill?")
                intent = self.input_handler(destination="bill removal", boolean=True, utility=utility)

                if intent == "yes":
                    self.db.remove_bill(entry)
                    self.redirect(message=None)
                else:
                    self.redirect(message="Returning to main menu.")

        self.redirect(message="The input bill ID could not be found.", destination="bill removal", utility=utility)

    def check_record(self, utility):
        for record in self.db.get_utility_record(utility):
            print(record)

    def check_unpaid_bills(self, utility):
        records = self.db.get_utility_record(utility)
        if not records:
            self.redirect(message=f"There are no bills in {utility}.", destination="utility menu", utility=utility)
        checker = False
        for entry in records:
            if entry.paid is False:
                checker = True
                print(entry)
        if not checker:
            self.redirect(message=f"You have no unpaid bills in {utility}.", destination="utility menu", utility=utility)

        self.utility_menu(utility, display=False)

    def pay_bill(self, utility):

        def payment(bill, user):
            if user == self.user1:
                bill.user1_paid = True
                bill.note += f"\n{self.user1_upper} paid {bill.owed_amount} for bill (ID {bill.id}) on {self.today}, paying off their portion of the bill."
            else:
                bill.user2_paid = True
                bill.note += f"\n{self.user2_upper} paid {bill.owed_amount} for bill (ID {bill.id}) on {self.today}, paying off their portion of the bill."

            if bill.user1_paid is True and bill.user2_paid is True:
                bill.paid = True
                self.db.pay_bill(bill)
                print(f"Bill ID {bill.id} has been completely paid off!")

            else:
                self.db.pay_bill(bill)

            print("You successfully paid your bill!")

        records = self.db.get_utility_record(utility)
        if not records:
            self.redirect(message=f"There are no bills in {utility}.", destination="utility menu", utility=utility)

        print("Who are you?")
        print(f"Enter '{self.user1_upper}' or '{self.user2_upper}'.")
        identity = self.input_handler(destination="bill payment", acceptable_inputs={self.user1, self.user2}, utility=utility)

        if identity == self.user1:
            collector = []
            for entry in records:
                if entry.user1_paid is False:
                    collector.append(entry)

            if len(collector) == 0:
                print("You don't have any bills to pay.")
                print(self.redirect(message=None))

            for entry in collector:
                print(entry)

        else:
            collector = []
            for entry in records:
                if entry.user2_paid is False:
                    collector.append(entry)

            if len(collector) == 0:
                print("You don't have any bills to pay.")
                print(self.redirect(message=None))

            for entry in collector:
                print(entry)

        print("Which bill would you like to pay?")
        print("You can pay multiple bills at once by entering multiple IDs separated by a space.")
        print("Enter the ID:")
        intent = self.input_handler(destination="bill payment", utility=utility)

        intent_list = intent.split(" ")

        # Paying by a single ID
        if len(intent_list) == 1:
            for entry in records:
                if entry.id == int(intent):
                    print(entry)
                    print(f"You owe {entry.owed_amount} yen.")
                    print(f"Will you pay your bill?")
                    intent = self.input_handler(destination="bill payment", utility=utility, boolean=True)

                    if intent == "yes":
                        payment(entry, identity)
                        self.redirect(message=None)

                    elif intent == "no":
                        self.redirect(message=None)

                    else:
                        self.redirect(destination="bill payment", utility=utility)

            self.redirect(message="The inputted bill ID could not be found.", destination="bill payment", utility=utility)

        # Paying by multiple IDs
        elif len(intent_list) > 1:
            for id_intent in intent_list:
                for entry in records:
                    if int(id_intent) == entry.id:
                        payment(entry, identity)

            self.redirect(message=None)

        else:
            self.redirect(destination="bill payment", utility=utility)

    def input_handler(self, message="Please enter a valid input.", destination="main menu", **kwargs):
        # Checks user inputs based on parameters and redirects them if their inputs are not valid.
        # Following keyword arguments are accepted:
        # boolean for yes / no inputs
        # integer for integer inputs
        # acceptable_inputs can be a tuple, list, or set of valid inputs
        if kwargs.get('boolean'):
            print("Enter 'yes' or 'no'.")
        intent = input().lower()
        print("****************************")
        print()

        if intent == 'main' or intent == 'back':
            self.main_menu()
        if intent == 'quit':
            self.quit_program()
        if kwargs.get('integer'):
            try:
                intent = int(intent)
            except ValueError:
                self.redirect(message="Please enter an integer.", destination=destination, utility=kwargs.get('utility'))
        if kwargs.get('acceptable_inputs'):
            acceptable_inputs = kwargs.get('acceptable_inputs')
            if intent not in acceptable_inputs:
                self.redirect(message=message, destination=destination, utility=kwargs.get('utility'))
        if kwargs.get('boolean'):
            if intent not in {'yes', 'no'}:
                self.redirect(message="Please enter 'yes' or 'no'.", destination=destination, utility=kwargs.get('utility'))

        return intent

    def redirect(self, message="Please enter a valid input.", destination="main menu", **kwargs):
        # Sends users back to the specified destination and sends them an appropriate message.
        if message:
            print(message)
        print(f"Returning to {destination}.")
        print()

        utility = kwargs.get('utility')
        if destination == "bill payment":
            self.pay_bill(utility)
        elif destination == "bill addition":
            self.add_bill(utility)
        elif destination == "bill removal":
            self.remove_bill(utility)
        elif destination == "utility menu":
            self.utility_menu(utility, display=kwargs.get('display'))
        else:
            self.main_menu()


def main():
    # Passing in a "test=True" argument to Database will instead open an in-memory database for testing purposes
    if not path.isfile('records.db'):
        print("No records file found.  Beginning first time setup.")
        print("Enter the name of the first user:")
        user1 = input()
        print("Enter the name of the second user:")
        user2 = input()
        db = Database(setup=True, user1=user1, user2=user2)
    else:
        db = Database()
    app = Application(db)
    app.start()


if __name__ == "__main__":
    main()
