import sys
import os

from shutil import copy2
from csv import writer
from typing import Union, Optional, Any
from datetime import datetime

from database import Database

if False:
    # For forward-reference type-checking:
    from UtilityCalculator import Application


def cmd_line_arg_handler() -> dict:
    """Handle command line arguments."""

    opts = [opt for opt in sys.argv[1:] if opt.startswith("-")]

    cmd_line_args = {"debug": False}

    if opts:

        if "-h" in opts or "--help" in opts:
            print(
                "Utilities Calculator by Jason Tarka"
                "Accepted command line arguments:"
                '"-v" or "--version": Display version information'
                '"-b" or "--backup": Backup database'
                '"-r" or "--restore": Restore database from backup'
                '"-e" or "--export": Export a list of Bill objects '
                'for use in database recovery.'
                '"-d" or "--debug": Enter debugging mode')
            sys.exit()

        PYTHON_VERSION = "Python version: 3.9.2"

        if "-v" in opts or "--version" in opts:
            print("Application version: 1.1.2\n"
                  f"{PYTHON_VERSION}")
            sys.exit()

        if "-b" in opts or "--backup" in opts:
            print("Backing up database...")

            destination_address = os.environ.get(
                "Utilities-Calculator-Backup-Address", "")

            copy2("records.db", destination_address)

            print(f"Database has successfully been backed up "
                  "to {destination_address}.")
            sys.exit()

        if "-r" in opts or "--restore" in opts:
            print("Restoring database from backup...")
            original_address = os.environ.get(
                'Utilities-Calculator-Backup-Address', "")
            destination_address = os.environ.get(
                'Utilities-Calculator-Address', "")
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


def input_handler(app: "Application",
                  prompt: str = "",
                  error_msg: str = "Please enter a valid input.",
                  destination: str = "main menu",
                  **kwargs) -> Any:
    """Checks input and redirects them if invalid.

    Following keyword arguments are supported:
    boolean for yes / no inputs
    integer for integer inputs
    acceptable_inputs can be a tuple, list, or set of valid inputs
    """

    if prompt:
        print(prompt)
    if kwargs.get('boolean'):
        print("Enter 'yes' or 'no'.")
    intent: Union[int, str] = input().lower()
    print("****************************\n")

    if intent == 'main' or intent == 'back':
        app.main_menu()

    if intent == 'quit':
        app.quit_program()

    if kwargs.get('integer'):
        try:
            intent = int(intent)
        except ValueError:
            redirect(app,
                     message="Please enter an integer.",
                     destination=destination,
                     utility=kwargs.get('utility'))

    if kwargs.get('acceptable_inputs'):
        acceptable_inputs = kwargs.get('acceptable_inputs', set())
        if intent not in acceptable_inputs:
            redirect(app,
                     message=error_msg,
                     destination=destination,
                     utility=kwargs.get('utility'))

    if kwargs.get('boolean'):
        if intent not in ('yes', 'no'):
            redirect(app,
                     message="Please enter 'yes' or 'no'.",
                     destination=destination,
                     utility=kwargs.get('utility'))

    return intent


def redirect(app: "Application",
             message: Optional[str] = "Please enter a valid input.",
             destination: str = "main menu",
             **kwargs: Any) -> None:
    """Send users to destination and an appropriate message."""

    if message:
        print(message)
    print(f"Returning to {destination}.\n")

    utility = kwargs.get('utility', '')
    if not utility:
        app.main_menu()

    if destination == "bill payment":
        app.pay_bill(utility)

    elif destination == "bill addition":
        app.add_bill(utility)

    elif destination == "bill removal":
        app.remove_bill(utility)

    elif destination == "utility menu":
        app.utility_menu(utility, display=kwargs.get('display'))


def formatted_today() -> str:
    """Return a formatted version of today's date."""

    return datetime.today().strftime('%B %d, %Y at %I:%M %p')
