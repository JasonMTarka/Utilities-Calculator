import sys
import os
from typing import TYPE_CHECKING

from bill import Bill
from menus import Menu
from database import Database
from helpers import (input_handler, redirect, formatted_today,
                     cmd_line_arg_handler)

'''
You can see a list of command line arguments by
passing '--help' or '-h' flag to the command line.
'''


class Application:
    """Class for getting input from user and printing text to terminal."""

    def __init__(self, db: Database) -> None:
        """Initialize database and get user information."""

        self.db = db
        # Upper is used for user-facing print strings
        # Lower is used for variables and arguments
        self.user1_upper = self.db.get_user(1)
        self.user1 = self.user1_upper.lower()
        self.user2_upper = self.db.get_user(2)
        self.user2 = self.user2_upper.lower()
        self.menus = Menu(self, db)

    def utilities(self) -> list:
        """Get a list of present utilities from the database."""

        utilities = []
        for tupl in self.db.get_utilities():
            utilities.append(tupl[0])
        return utilities

    def user_owes(self, user: int) -> float:
        """Get total owed by a given user."""

        if user == 1:
            return self.db.get_total_owed(self.user1)
        else:
            return self.db.get_total_owed(self.user2)

    def start(self) -> None:
        """Display information on initial launch of application."""

        os.system('cls')
        print(f"\nWelcome to {self.user1_upper}"
              f" and {self.user2_upper}'s utility calculator.\n"
              f"Today is {formatted_today()}")
        self.main_menu()

    def quit_program(self) -> None:
        """Close database connection and exit program."""

        self.db.conn.close()
        sys.exit("Closing program...")

    def main_menu(self) -> None:
        """Display main menu."""

        self.menus.update_main_options()
        if self.db.debug is True:
            print("****************************\n"
                  "------DEBUGGING MODE!------")
        print("****************************\n"
              f"{self.user1_upper} currently owes "
              f"{self.user_owes(1)} yen "
              f"and {self.user2_upper} currently owes "
              f"{self.user_owes(2)} yen.\n"
              "You can examine a particular utility "
              f"or either {self.user1_upper}"
              f"or {self.user2_upper}'s payment history.\n")

        self.menus.print_main_menu()

        acceptable_inputs = set(self.menus.main_options.keys())

        intent = input_handler(
            self,
            prompt=("\nYou can return to this page "
                    "by entering 'main' at any point."
                    "\nYou can also quit this program at any point "
                    "by entering 'quit'."),
            acceptable_inputs=acceptable_inputs)

        option = self.menus.main_options.get(intent, {})
        option_func = option.get('func')
        if TYPE_CHECKING:
            assert callable(option_func)

        try:
            # Handle menu requests which require an argument
            option_func(option.get('arg'))

        except TypeError:
            # Handle menu requests which do not require an argument
            option_func()

    def user_page(self, user: str) -> None:
        """Display total owed and unpaid bills and return to main menu."""

        print(
            f"{user[0].upper() + user[1:]} owes",
            self.db.get_total_owed(user))

        print("Here are their unpaid bills:")
        for entry in self.db.get_bills_owed(user):
            print(entry)
        self.main_menu()

    def utility_menu(self, utility: str, display=True) -> None:
        """Display utility menu options."""

        if display:
            self.check_record(utility)
        print(f"What would you like to do with {utility}?\n")

        for key in self.menus.utility_options.keys():
            option = self.menus.utility_options.get(key, {})

            print(f"{option.get('name')} - {option.get('description')}")

        acceptable_inputs = set(self.menus.utility_options.keys())
        intent = input_handler(
            self,
            destination='utility menu',
            acceptable_inputs=acceptable_inputs,
            utility=utility,
            display=False)

        option_func = self.menus.utility_options.get(intent, {}).get('func')
        if TYPE_CHECKING:
            assert callable(option_func)
        option_func(utility)

    def add_utility(self) -> None:
        """Add a new utility to the database."""

        intent = input_handler(
            self,
            prompt="What is the name of your new utility?")
        self.add_bill(intent)

    def remove_utility(self) -> None:
        """Remove a utility and all associated bills."""

        print("What utility would you like to remove?")
        for utility in self.utilities():
            print(f"{utility[0].upper() + utility[1:]}")

        intent = input_handler(
            self,
            prompt=(
                "WARNING: removing a utility "
                "will also remove all bills associated with that utility!"))

        removal_intent = input_handler(
            self,
            prompt=f"Are you sure you want to remove {intent}?",
            boolean=True)

        if removal_intent:
            self.db.remove_utility(intent)
            redirect(self,
                     message=f"{intent} has been removed.")
        else:
            redirect(self,
                     message=None)

    def add_bill(self, utility: str) -> None:
        """Add a bill to the database."""

        amount_intent = input_handler(
            self,
            prompt="\nHow much is the bill for?\nEnter the amount in yen:",
            destination="bill addition",
            integer=True,
            utility=utility)

        print("What month(s) is this bill for?\n"
              "Enter the bill date like the following:"
              " '04-21' for April 9th.\n"
              "In the event that there is more than one month listed,"
              " please list with a ',' between the dates.")

        date_intent = input_handler(self)

        moreinfo_intent = input_handler(
            self,
            prompt="If you want to add more information, type 'yes'. "
            " Otherwise, press any key to continue.")

        if moreinfo_intent == "yes":

            user1_intent = input_handler(
                self,
                prompt=f"Has {self.user1_upper} paid?",
                destination="bill addition",
                utility=utility,
                boolean=True)

            user2_intent = input_handler(
                self,
                prompt=f"Has {self.user2_upper} paid?",
                destination="bill addition",
                utility=utility,
                boolean=True)

            print("Do you have any notes you'd like to make about this bill? "
                  "(Press enter to skip)")
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

            bill = Bill(utility,
                        date_intent,
                        amount_intent,
                        user1_paid=user1_intent,
                        user2_paid=user2_intent,
                        paid=paid_intent,
                        note=note_intent)

        else:
            print("Creating bill...")

            bill = Bill(utility,
                        date_intent,
                        amount_intent)

        self.db.add_bill(bill)
        print(
            "Bill has been successfully created "
            f"and added to the {bill.utility} bill record!\n"
            "Returning to main menu...")
        self.main_menu()

    def remove_bill(self, utility: str) -> None:
        """Remove a bill from the database."""

        records = self.db.get_utility_record(utility)
        if not records:
            redirect(self,
                     message=f"There are no bills in {utility}.",
                     destination="utility menu",
                     utility=utility)

        for record in records:
            print(record)

        intent = input_handler(self,
                               prompt=("Which bill would you like to remove?\n"
                                       "Input bill ID:"),
                               destination="bill removal",
                               integer=True,
                               utility=utility)

        for entry in records:
            if entry.id == intent:
                print(entry)
                intent = input_handler(self,
                                       prompt=f"Will you remove this bill?",
                                       destination="bill removal",
                                       boolean=True,
                                       utility=utility)

                if intent == "yes":
                    self.db.remove_bill(entry)
                    redirect(self,
                             message=None)
                else:
                    redirect(self,
                             message="Returning to main menu.")

        redirect(self,
                 message="The input bill ID could not be found.",
                 destination="bill removal",
                 utility=utility)

    def check_record(self, utility: str) -> None:
        """Print all bills under a given utility."""

        for record in self.db.get_utility_record(utility):
            print(record)

    def check_unpaid_bills(self, utility: str) -> None:
        """Print all unpaid bills under a given utility."""

        records = self.db.get_utility_record(utility)
        if not records:
            redirect(self,
                     message=f"There are no bills in {utility}.",
                     destination="utility menu",
                     utility=utility)

        checker = False
        for entry in records:
            if not entry.paid:
                checker = True
                print(entry)
        if not checker:
            redirect(self,
                     message=f"You have no unpaid bills in {utility}.",
                     destination="utility menu",
                     utility=utility)

        self.utility_menu(utility, display=False)

    def pay_bill(self, utility: str) -> None:
        """Pay a bill."""

        def payment(bill: Bill, user: str) -> None:
            """Write information to bill object and send it to the database."""

            if user == self.user1:
                bill.user1_paid = True
                bill.note += (f"\n{self.user1_upper} paid {bill.owed_amount} "
                              f"for bill (ID {bill.id}) "
                              f"on {formatted_today()}, "
                              "paying off their portion of the bill.")
            else:
                bill.user2_paid = True
                bill.note += (f"\n{self.user2_upper} paid {bill.owed_amount} "
                              f"for bill (ID {bill.id}) "
                              f"on {formatted_today()}, "
                              "paying off their portion of the bill.")

            if bill.user1_paid is True and bill.user2_paid is True:
                bill.paid = True
                self.db.pay_bill(bill)
                print(f"Bill ID {bill.id} has been completely paid off!")

            else:
                self.db.pay_bill(bill)

            print("You successfully paid your bill!")

        records = self.db.get_utility_record(utility)
        if not records:
            redirect(self,
                     message=f"There are no bills in {utility}.",
                     destination="utility menu",
                     utility=utility)

        identity = input_handler(
            self,
            prompt=("Who are you?\n"
                    f"Enter '{self.user1_upper}' or '{self.user2_upper}'."),
            destination="bill payment",
            acceptable_inputs={self.user1, self.user2},
            utility=utility)

        if identity == self.user1:
            collector = []
            for entry in records:
                if not entry.user1_paid:
                    collector.append(entry)

            if len(collector) == 0:
                print("You don't have any bills to pay.")
                redirect(self,
                         message=None)

            for entry in collector:
                print(entry)

        else:
            collector = []
            for entry in records:
                if not entry.user2_paid:
                    collector.append(entry)

            if len(collector) == 0:
                print("You don't have any bills to pay.")
                redirect(self,
                         message=None)

            for entry in collector:
                print(entry)

        intent = input_handler(
            self,
            prompt=("Which bill would you like to pay?\n"
                    "You can pay multiple bills at once "
                    "by entering multiple IDs separated by a space.\n"
                    "Enter the ID:"),
            destination="bill payment",
            utility=utility)

        intent_list = intent.split(" ")

        # Paying by a single ID
        if len(intent_list) == 1:
            for entry in records:
                if entry.id == int(intent):
                    intent = input_handler(
                        self,
                        prompt=(f"{entry}\nYou owe {entry.owed_amount} yen\n"
                                "Will you pay your bill?"),
                        destination="bill payment",
                        utility=utility,
                        boolean=True)

                    if intent == "yes":
                        payment(entry, identity)
                        redirect(self,
                                 message=None)

                    elif intent == "no":
                        redirect(self,
                                 message=None)

                    else:
                        redirect(self,
                                 destination="bill payment",
                                 utility=utility)

            redirect(self,
                     message="The inputted bill ID could not be found.",
                     destination="bill payment",
                     utility=utility)

        # Paying by multiple IDs
        elif len(intent_list) > 1:
            for id_intent in intent_list:
                for entry in records:
                    if int(id_intent) == entry.id:
                        payment(entry, identity)

            redirect(self,
                     message=None)

        else:
            redirect(self,
                     destination="bill payment",
                     utility=utility)


def main() -> None:
    """Start program."""

    cmd_line_args = cmd_line_arg_handler()
    debug = cmd_line_args.get("debug", False)

    if not os.path.isfile('records.db') and not debug:
        print(
            "No records file found.  Beginning first time setup.\n"
            "Enter the name of the first user:\n")
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
