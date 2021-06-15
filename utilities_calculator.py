import sys
import os
from datetime import datetime
from os import system, path
from typing import Optional, Any, Union, Iterable
from shutil import copy2

from bill import Bill
from database import Database

'''
You can enter debug mode by passing in a '-debug' or '-d' argument into the command line.

Mypy does not like my implementation of menus, so I type check ignore all lines dealing with menus with '# type: ignore'.
'''

class Application:

    def __init__(self, db: Database) -> None:
        self.db = db
        self.user1_upper = self.db.get_user(1)  # Upper is used for user-facing print strings
        self.user2_upper = self.db.get_user(2)
        self.user1 = self.user1_upper.lower()  # Lower is used for variables and arguments
        self.user2 = self.user2_upper.lower()

        self.utility_menu_options = {
            'add bill': {'func': self.add_bill, 'description': "Add a new bill.", 'name': "'Add Bill'"},
            'check unpaid bills': {'func': self.check_unpaid_bills, 'description': "Check unpaid bills for a given utility.", 'name': "'Check Unpaid Bills'"},
            'pay bill': {'func': self.pay_bill, 'description': "Pay a bill.", 'name': "'Pay Bill'"},
            'remove bill': {'func': self.remove_bill, 'description': "Remove a bill.", 'name': "'Remove Bill'"}
        }

        # Main menu options are updated to include utility names by 'update_main_menu_options' method below.
        self.main_menu_options = {
            'add utility': {'func': self.add_utility, 'description': "Enter a new utility and bill.", 'name': '"Add Utility"'},
            'remove utility': {'func': self.remove_utility, 'description': "Remove a utility and all associated bills.", 'name': '"Remove Utility"'},
            self.user1: {'func': self.user_page, 'description': f"See information for {self.user1_upper}", 'arg': self.user1, 'name': f'"{self.user1_upper}"'},
            self.user2: {'func': self.user_page, 'description': f"See information for {self.user2_upper}", 'arg': self.user2, 'name': f'"{self.user2_upper}"'},
            'create backup': {'func': self.backup, 'description': "Make a backup of your records file.", 'name': '"Create Backup"'}
        }

        self._orig_main_menu_len = len(self.main_menu_options)  # Used for formatting the division between above options and utilities

    @property
    def utilities(self) -> list:
        collector = []
        for tupl in self.db.get_utilities():
            collector.append(tupl[0])
        return collector

    @property
    def user1_owes(self) -> float:
        return self.db.get_total_owed(self.user1)

    @property
    def user2_owes(self) -> float:
        return self.db.get_total_owed(self.user2)

    @property
    def today(self) -> str:
        return datetime.today().strftime('%B %d, %Y at %I:%M %p')

    # This update function is run at each opening of the main menu.
    def update_main_menu_options(self) -> None:

        def add_new_utils() -> None:
            for utility in self.utilities:
                if utility not in self.main_menu_options.keys():
                    self.main_menu_options[utility] = {'func': self.utility_menu, 'arg': utility,
                                                       'name': f'"{utility[0].upper() + utility[1:]}"', 'description': f"Access your {utility} record."}

        def remove_utils() -> None:
            for option in main_menu_shortlist:
                if option not in utilities_shortlist:
                    self.main_menu_options.pop(option)

        main_menu_shortlist = list(self.main_menu_options)[self._orig_main_menu_len:]
        utilities_shortlist = [tpl[0] for tpl in self.db.get_utilities()]

        if len(utilities_shortlist) > len(main_menu_shortlist):
            add_new_utils()
        elif len(utilities_shortlist) < len(main_menu_shortlist):
            remove_utils()

    def start(self) -> None:
        system('cls')
        print(f"\nWelcome to {self.user1_upper} and {self.user2_upper}'s utility calculator.")
        print(f"Today is {self.today}")
        self.main_menu()

    def quit_program(self) -> None:
        self.db.conn.close()
        sys.exit("Closing program...")

    def main_menu(self) -> None:
        self.update_main_menu_options()
        if self.db.debug is True:
            print("****************************\n")
            print("------DEBUGGING MODE!------")
        print("****************************\n")
        print(f"{self.user1_upper} currently owes {self.user1_owes} yen and {self.user2_upper} currently owes {self.user2_owes} yen.")
        print(f"You can examine a particular utility or either {self.user1_upper} or {self.user2_upper}'s payment history.\n")

        keys_list = list(self.main_menu_options.keys())
        keys_list.insert(self._orig_main_menu_len, 'spacer')
        for key in keys_list:
            if key == 'spacer':
                print()
                continue
            option = self.main_menu_options.get(key)
            assert option is not None
            print(f"{option.get('name')} - {option.get('description')}")

        acceptable_inputs = set(self.main_menu_options.keys())
        intent = self.input_handler(prompt="\nYou can return to this page by entering 'main' at any point.\nYou can also quit this program at any point by entering 'quit'.",
                                    acceptable_inputs=acceptable_inputs)

        # Try block handles menu requests which require an argument
        # Except block handles menu requests which do not require an argument
        option = self.main_menu_options.get(intent)
        assert option is not None
        try:
            option.get('func')(option.get('arg'))  # type: ignore
        except TypeError:
            option.get('func')()  # type: ignore

    def user_page(self, user: str) -> None:
        print(f"{user[0].upper() + user[1:]} owes", self.db.get_total_owed(user))
        print("Here are their unpaid bills:")
        for entry in self.db.get_bills_owed(user):
            print(entry)
        self.main_menu()

    def backup(self) -> None:
        self.db.backup()
        print("Backup has been created.")
        self.main_menu()

    def utility_menu(self, utility: str, display=True) -> None:
        if display:
            self.check_record(utility)
        print(f"What would you like to do with {utility}?\n")

        for key in self.utility_menu_options.keys():
            option = self.utility_menu_options.get(key)
            assert option is not None
            print(f"{option.get('name')} - {option.get('description')}")

        acceptable_inputs = set(self.utility_menu_options.keys())
        intent = self.input_handler(destination='utility menu', acceptable_inputs=acceptable_inputs,
                                    utility=utility, display=False)

        self.utility_menu_options.get(intent).get('func')(utility)  # type: ignore

    def add_utility(self) -> None:
        intent = self.input_handler(prompt="What is the name of your new utility?")
        self.add_bill(intent)

    def remove_utility(self) -> None:
        print("What utility would you like to remove?")
        for utility in self.utilities:
            print(f"{utility[0].upper() + utility[1:]}")
        intent = self.input_handler(prompt="WARNING: removing a utility will also remove all bills associated with that utility!")
        removal_intent = self.input_handler(prompt=f"Are you sure you want to remove {intent}?", boolean=True)
        if removal_intent:
            self.db.remove_utility(intent)
            self.redirect(message=f"{intent} has been removed.")
        else:
            self.redirect(message=None)

    def add_bill(self, utility: str) -> None:
        amount_intent = self.input_handler(prompt="\nHow much is the bill for?\nEnter the amount in yen:",
                                           destination="bill addition", integer=True, utility=utility)

        print("What month(s) is this bill for?")
        print("Enter the bill date like the following: '04-21' for April 9th.")
        print("In the event that there is more than one month listed, please list with a ',' between the dates.")
        date_intent = self.input_handler()
        moreinfo_intent = self.input_handler(prompt="If you want to add more information, type 'yes'.  Otherwise, press any key to continue.")

        if moreinfo_intent == "yes":

            j_intent = self.input_handler(prompt=f"Has {self.user1_upper} paid?", destination="bill addition", utility=utility, boolean=True)
            x_intent = self.input_handler(prompt=f"Has {self.user2_upper} paid?", destination="bill addition", utility=utility, boolean=True)

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

    def remove_bill(self, utility: str) -> None:
        records = self.db.get_utility_record(utility)
        if not records:
            self.redirect(message=f"There are no bills in {utility}.", destination="utility menu", utility=utility)

        for record in records:
            print(record)

        intent = self.input_handler(prompt="Which bill would you like to remove?\nInput bill ID:",
                                    destination="bill removal", integer=True, utility=utility)

        for entry in records:
            if entry.id == intent:
                print(entry)
                intent = self.input_handler(prompt=f"Will you remove this bill?", destination="bill removal", boolean=True, utility=utility)

                if intent == "yes":
                    self.db.remove_bill(entry)
                    self.redirect(message=None)
                else:
                    self.redirect(message="Returning to main menu.")

        self.redirect(message="The input bill ID could not be found.", destination="bill removal", utility=utility)

    def check_record(self, utility: str) -> None:
        for record in self.db.get_utility_record(utility):
            print(record)

    def check_unpaid_bills(self, utility: str) -> None:
        records = self.db.get_utility_record(utility)
        if not records:
            self.redirect(message=f"There are no bills in {utility}.", destination="utility menu", utility=utility)
        checker = False
        for entry in records:
            if not entry.paid:
                checker = True
                print(entry)
        if not checker:
            self.redirect(message=f"You have no unpaid bills in {utility}.", destination="utility menu", utility=utility)

        self.utility_menu(utility, display=False)

    def pay_bill(self, utility: str) -> None:

        def payment(bill: Bill, user: str) -> None:
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

        identity = self.input_handler(prompt=f"Who are you?\nEnter '{self.user1_upper}' or '{self.user2_upper}'.",
                                      destination="bill payment", acceptable_inputs={self.user1, self.user2}, utility=utility)

        if identity == self.user1:
            collector = []
            for entry in records:
                if not entry.user1_paid:
                    collector.append(entry)

            if len(collector) == 0:
                print("You don't have any bills to pay.")
                self.redirect(message=None)

            for entry in collector:
                print(entry)

        else:
            collector = []
            for entry in records:
                if not entry.user2_paid:
                    collector.append(entry)

            if len(collector) == 0:
                print("You don't have any bills to pay.")
                self.redirect(message=None)

            for entry in collector:
                print(entry)

        intent = self.input_handler(prompt="Which bill would you like to pay?\nYou can pay multiple bills at once by entering multiple IDs separated by a space.\nEnter the ID:",
                                    destination="bill payment", utility=utility)

        intent_list = intent.split(" ")

        # Paying by a single ID
        if len(intent_list) == 1:
            for entry in records:
                if entry.id == int(intent):
                    intent = self.input_handler(prompt=f"{entry}\nYou owe {entry.owed_amount} yen\nWill you pay your bill?",
                                                destination="bill payment", utility=utility, boolean=True)

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

    def input_handler(self, prompt: Optional[str] = None, error_msg: Optional[str] = "Please enter a valid input.", destination: str = "main menu", **kwargs: Union[str, int, bool, Iterable]) -> Any:
        '''
        Checks user inputs based on parameters and redirects them if their inputs are not valid.
        Following keyword arguments are supported:
        boolean for yes / no inputs
        integer for integer inputs
        acceptable_inputs can be a tuple, list, or set (preferred b/c hashing) of valid inputs
        '''
        if prompt:
            print(prompt)
        if kwargs.get('boolean'):
            print("Enter 'yes' or 'no'.")
        intent: Union[int, str] = input().lower()
        print("****************************\n")

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
            if intent not in acceptable_inputs:  # type: ignore
                self.redirect(message=error_msg, destination=destination, utility=kwargs.get('utility'))
        if kwargs.get('boolean'):
            if intent not in ('yes', 'no'):
                self.redirect(message="Please enter 'yes' or 'no'.", destination=destination, utility=kwargs.get('utility'))

        return intent

    # Sends users back to the specified destination and sends them an appropriate message.
    def redirect(self, message: Optional[str] = "Please enter a valid input.", destination: str = "main menu", **kwargs: Any) -> None:

        if message:
            print(message)
        print(f"Returning to {destination}.\n")

        utility = kwargs.get('utility')
        if utility is None:
            self.main_menu()
        assert utility is not None

        if destination == "bill payment":
            self.pay_bill(utility)
        elif destination == "bill addition":
            self.add_bill(utility)
        elif destination == "bill removal":
            self.remove_bill(utility)
        elif destination == "utility menu":
            self.utility_menu(utility, display=kwargs.get('display'))

def main() -> None:

    debug = False
    print("test")
    opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]

    if "-h" in opts or "--help" in opts:
        print("Utilities Calculator by Jason Tarka")
        print("Accepted command line arguments:")
        print('"-d" or "--debug": Enter debugging mode')
        print('"-v" or "--version": Display version information')
        print('"-r" or "--restore": Restore database backup')
        sys.exit()

    if "-v" in opts or "--version" in opts:
        print("Application version: 1.1.0")
        print(f"Python version: {sys.version}")
        sys.exit()

    if "-r" in opts or "--restore" in opts:
        print("Restoring database from backup...")
        copy2(f"{os.environ.get('Utilities-Calculator-Backup-Address')}/records.db", os.environ.get('Utilities-Calculator-Address'))
        sys.exit()

    if "-d" in opts or "--debug" in opts:
        debug = True

    if not path.isfile('records.db') and not debug:
        print("No records file found.  Beginning first time setup.")
        print("Enter the name of the first user:")
        user1 = input()
        print("Enter the name of the second user:")
        user2 = input()
        db = Database(setup=True, user1=user1, user2=user2)
    else:
        db = Database(debug=debug)

    app = Application(db)
    app.start()


if __name__ == "__main__":
    main()
