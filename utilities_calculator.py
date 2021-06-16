import sys
import os
from datetime import datetime
from os import system, path
from typing import Optional, Any, Union, TYPE_CHECKING
from shutil import copy2
from csv import writer

from bill import Bill
from database import Database

'''
You can see a list of command line arguments by passing in a '--help' or '-h' flag into the command line.
'''

class Application:

    def __init__(self, db: Database) -> None:
        """Initialize database, get user information, set utility menu and main menu options."""

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
            self.user2: {'func': self.user_page, 'description': f"See information for {self.user2_upper}", 'arg': self.user2, 'name': f'"{self.user2_upper}"'}
        }

        self._orig_main_menu_len = len(self.main_menu_options)  # Used for formatting the division between above options and utilities

    def utilities(self) -> list:
        """Get a list of present utilities from the database."""

        utilities = []
        for tupl in self.db.get_utilities():
            utilities.append(tupl[0])
        return utilities

    def today(self) -> str:
        """Return a formatted version of today's date."""

        return datetime.today().strftime('%B %d, %Y at %I:%M %p')

    def user_owes(self, user: int) -> float:
        """Get total owed by a given user."""

        if user == 1:
            return self.db.get_total_owed(self.user1)
        else:
            return self.db.get_total_owed(self.user2)

    def update_main_menu_options(self) -> None:
        """Reconcile main menu options with utilities present in database."""

        def add_new_utils() -> None:
            """Add new utilities to main menu options."""

            for utility in self.utilities():
                if utility not in self.main_menu_options.keys():
                    self.main_menu_options[utility] = {'func': self.utility_menu, 'arg': utility,
                                                       'name': f'"{utility[0].upper() + utility[1:]}"', 'description': f"Access your {utility} record."}

        def remove_utils() -> None:
            """Remove utilities which have been removed from the database."""

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
        """Display information on initial launch of application."""

        system('cls')
        print(f"\nWelcome to {self.user1_upper} and {self.user2_upper}'s utility calculator.")
        print(f"Today is {self.today()}")
        self.main_menu()

    def quit_program(self) -> None:
        """Close database connection and exit program."""

        self.db.conn.close()
        sys.exit("Closing program...")

    def main_menu(self) -> None:
        """Display main menu."""

        self.update_main_menu_options()
        if self.db.debug is True:
            print("****************************\n")
            print("------DEBUGGING MODE!------")
        print("****************************\n")
        print(f"{self.user1_upper} currently owes {self.user_owes(1)} yen and {self.user2_upper} currently owes {self.user_owes(2)} yen.")
        print(f"You can examine a particular utility or either {self.user1_upper} or {self.user2_upper}'s payment history.\n")

        keys_list = list(self.main_menu_options.keys())
        keys_list.insert(self._orig_main_menu_len, 'spacer')
        for key in keys_list:
            if key == 'spacer':
                print()
                continue
            option = self.main_menu_options.get(key, {})

            print(f"{option.get('name')} - {option.get('description')}")

        acceptable_inputs = set(self.main_menu_options.keys())
        intent = self.input_handler(prompt="\nYou can return to this page by entering 'main' at any point.\nYou can also quit this program at any point by entering 'quit'.",
                                    acceptable_inputs=acceptable_inputs)

        option = self.main_menu_options.get(intent, {})
        option_func = option.get('func')
        if TYPE_CHECKING:
            assert callable(option_func)

        # Try block handles menu requests which require an argument
        # Except block handles menu requests which do not require an argument
        try:
            option_func(option.get('arg'))
        except TypeError:
            option_func()

    def user_page(self, user: str) -> None:
        """Display total owed by the user and their unpaid bills before returning to main menu."""

        print(f"{user[0].upper() + user[1:]} owes", self.db.get_total_owed(user))
        print("Here are their unpaid bills:")
        for entry in self.db.get_bills_owed(user):
            print(entry)
        self.main_menu()

    def utility_menu(self, utility: str, display=True) -> None:
        """Display utility menu options."""

        if display:
            self.check_record(utility)
        print(f"What would you like to do with {utility}?\n")

        for key in self.utility_menu_options.keys():
            option = self.utility_menu_options.get(key, {})

            print(f"{option.get('name')} - {option.get('description')}")

        acceptable_inputs = set(self.utility_menu_options.keys())
        intent = self.input_handler(destination='utility menu', acceptable_inputs=acceptable_inputs,
                                    utility=utility, display=False)

        option_func = self.utility_menu_options.get(intent, {}).get('func')
        if TYPE_CHECKING:
            assert callable(option_func)
        option_func(utility)

    def add_utility(self) -> None:
        """Add a new utility to the database."""

        intent = self.input_handler(prompt="What is the name of your new utility?")
        self.add_bill(intent)

    def remove_utility(self) -> None:
        """Remove a utility and all associated bills."""

        print("What utility would you like to remove?")
        for utility in self.utilities():
            print(f"{utility[0].upper() + utility[1:]}")
        intent = self.input_handler(prompt="WARNING: removing a utility will also remove all bills associated with that utility!")
        removal_intent = self.input_handler(prompt=f"Are you sure you want to remove {intent}?", boolean=True)
        if removal_intent:
            self.db.remove_utility(intent)
            self.redirect(message=f"{intent} has been removed.")
        else:
            self.redirect(message=None)

    def add_bill(self, utility: str) -> None:
        """Add a bill to the database."""

        amount_intent = self.input_handler(prompt="\nHow much is the bill for?\nEnter the amount in yen:",
                                           destination="bill addition", integer=True, utility=utility)

        print("What month(s) is this bill for?")
        print("Enter the bill date like the following: '04-21' for April 9th.")
        print("In the event that there is more than one month listed, please list with a ',' between the dates.")
        date_intent = self.input_handler()
        moreinfo_intent = self.input_handler(prompt="If you want to add more information, type 'yes'.  Otherwise, press any key to continue.")

        if moreinfo_intent == "yes":

            user1_intent = self.input_handler(prompt=f"Has {self.user1_upper} paid?", destination="bill addition", utility=utility, boolean=True)
            user2_intent = self.input_handler(prompt=f"Has {self.user2_upper} paid?", destination="bill addition", utility=utility, boolean=True)

            print("Do you have any notes you'd like to make about this bill? (Press enter to skip)")
            note_intent = input()
            print("*****")
            print("Creating bill...")

            if user1_intent == "yes":
                user1_intent = True
            else:
                user1_intent = False

            if user2_intent == "yes":
                user2_intent = True
            else:
                user2_intent = False

            if user1_intent is True and user2_intent is True:
                paid_intent = True
            else:
                paid_intent = False

            bill = Bill(utility, date_intent, amount_intent, user1_paid=user1_intent, user2_paid=user2_intent, paid=paid_intent, note=note_intent)

        else:
            print("Creating bill...")
            bill = Bill(utility, date_intent, amount_intent)

        self.db.add_bill(bill)
        print(f"Bill has been successfully created and added to the {bill.utility} bill record!")
        print("Returning to main menu...")
        self.main_menu()

    def remove_bill(self, utility: str) -> None:
        """Remove a bill from the database."""

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
        """Print all bills under a given utility."""

        for record in self.db.get_utility_record(utility):
            print(record)

    def check_unpaid_bills(self, utility: str) -> None:
        """Print all unpaid bills under a given utility."""

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
        """Pay a bill."""

        def payment(bill: Bill, user: str) -> None:
            """Write new information to a bill object and then send it to the database to be paid."""

            if user == self.user1:
                bill.user1_paid = True
                bill.note += f"\n{self.user1_upper} paid {bill.owed_amount} for bill (ID {bill.id}) on {self.today()}, paying off their portion of the bill."
            else:
                bill.user2_paid = True
                bill.note += f"\n{self.user2_upper} paid {bill.owed_amount} for bill (ID {bill.id}) on {self.today()}, paying off their portion of the bill."

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

    def input_handler(self, prompt: str = "", error_msg: str = "Please enter a valid input.", destination: str = "main menu", **kwargs) -> Any:
        """Checks user inputs based on parameters and redirects them if their inputs are not valid.
        Following keyword arguments are supported:
        boolean for yes / no inputs
        integer for integer inputs
        acceptable_inputs can be a tuple, list, or set (preferred b/c hashing) of valid inputs
        """

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
            acceptable_inputs = kwargs.get('acceptable_inputs', set())
            if intent not in acceptable_inputs:
                self.redirect(message=error_msg, destination=destination, utility=kwargs.get('utility'))
        if kwargs.get('boolean'):
            if intent not in ('yes', 'no'):
                self.redirect(message="Please enter 'yes' or 'no'.", destination=destination, utility=kwargs.get('utility'))

        return intent

    def redirect(self, message: Optional[str] = "Please enter a valid input.", destination: str = "main menu", **kwargs: Any) -> None:
        """Send users back to the specified destination and send them an appropriate message."""

        if message:
            print(message)
        print(f"Returning to {destination}.\n")

        utility = kwargs.get('utility', '')
        if not utility:
            self.main_menu()

        if destination == "bill payment":
            self.pay_bill(utility)
        elif destination == "bill addition":
            self.add_bill(utility)
        elif destination == "bill removal":
            self.remove_bill(utility)
        elif destination == "utility menu":
            self.utility_menu(utility, display=kwargs.get('display'))


def main() -> None:
    """Start program."""

    def cmd_line_arg_handler() -> dict:
        """Handle command line arguments."""

        opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]

        cmd_line_args = {"debug": False}

        if opts:

            if "-h" in opts or "--help" in opts:
                print("Utilities Calculator by Jason Tarka")
                print("Accepted command line arguments:")
                print('"-v" or "--version": Display version information')
                print('"-b" or "--backup": Backup database')
                print('"-r" or "--restore": Restore database from backup')
                print('"-e" or "--export": Export a list of Bill objects for use in database recovery.')
                print('"-d" or "--debug": Enter debugging mode')
                sys.exit()

            if "-v" in opts or "--version" in opts:
                print("Application version: 1.1.2")
                print(f"Python version: {sys.version}")
                sys.exit()

            if "-b" in opts or "--backup" in opts:
                print("Backing up database...")
                destination_address = os.environ.get("Utilities-Calculator-Backup-Address", "")
                copy2("records.db", destination_address)
                print(f"Database has successfully been backed up to {destination_address}.")
                sys.exit()

            if "-r" in opts or "--restore" in opts:
                print("Restoring database from backup...")
                original_address = os.environ.get('Utilities-Calculator-Backup-Address', "")
                destination_address = os.environ.get('Utilities-Calculator-Address', "")
                copy2(f"{original_address}/records.db", destination_address)
                sys.exit()

            if "-e" in opts or "--export" in opts:
                print("Exporting database entries...")
                db = Database(debug=False)
                all_records = db.get_all_records()

                with open("bill_list.csv", "w", newline="") as file:
                    csv_writer = writer(file)
                    csv_writer.writerow(["bills ="])
                    for record in all_records:
                        csv_writer.writerow([record.__repr__()])

                print("Database entries exported to CSV!")
                sys.exit()

            if "-d" in opts or "--debug" in opts:
                cmd_line_args["debug"] = True

        return cmd_line_args

    cmd_line_args = cmd_line_arg_handler()
    debug = cmd_line_args.get("debug", False)

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
