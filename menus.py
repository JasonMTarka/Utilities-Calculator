if False:
    # For forward-reference type-checking:
    from UtilityCalculator import Application, Database


class Menu:
    """Class for storing and updating Utility Calculator menus."""

    def __init__(self, app: "Application", db: "Database") -> None:
        """Set menu options."""

        self.db = db
        self.app = app

        self.main_options = {
            'add utility':
                {'func': app.add_utility,
                 'description': "Enter a new utility and bill.",
                 'name': '"Add Utility"'},
            'remove utility':
                {'func': app.remove_utility,
                 'description': "Remove a utility and all associated bills.",
                 'name': '"Remove Utility"'},
            app.user1:
                {'func': app.user_page,
                 'description': f"See information for {app.user1_upper}",
                 'arg': app.user1,
                 'name': f'"{app.user1_upper}"'},
            app.user2:
                {'func': app.user_page,
                 'description': f"See information for {app.user2_upper}",
                 'arg': app.user2,
                 'name': f'"{app.user2_upper}"'}
        }

        # Main menu options are updated to include utility names
        # by 'update_main_options' method below.

        self._orig_main_menu_len = len(self.main_options)
        # Used for formatting the division between above options and utilities

        self.utility_options = {

            'add bill':
                {'func': app.add_bill,
                 'description': "Add a new bill.",
                 'name': "'Add Bill'"},

            'check unpaid bills':
                {'func': app.check_unpaid_bills,
                 'description': "Check unpaid bills for a given utility.",
                 'name': "'Check Unpaid Bills'"},

            'pay bill':
                {'func': app.pay_bill,
                 'description': "Pay a bill.",
                 'name': "'Pay Bill'"},

            'remove bill':
                {'func': app.remove_bill,
                 'description': "Remove a bill.",
                 'name': "'Remove Bill'"}
        }

    def update_main_options(self) -> None:
        """Reconcile main menu options with utilities present in database."""

        def add_new_utils() -> None:
            """Add new utilities to main menu options."""

            for utility in self.app.utilities():

                if utility not in self.main_options.keys():

                    self.main_options[utility] = {
                        'func': self.app.utility_menu,
                        'arg': utility,
                        'name': f'"{utility[0].upper() + utility[1:]}"',
                        'description': f"Access your {utility} record."}

        def remove_utils() -> None:
            """Remove utilities which have been removed from the database."""

            for option in main_menu_shortlist:
                if option not in utilities_shortlist:
                    self.main_options.pop(option)

        main_menu_shortlist = (
            list(self.main_options)[self._orig_main_menu_len:])

        utilities_shortlist = [tpl[0] for tpl in self.db.get_utilities()]

        if len(utilities_shortlist) > len(main_menu_shortlist):
            add_new_utils()
        elif len(utilities_shortlist) < len(main_menu_shortlist):
            remove_utils()

    def print_main_menu(self) -> None:
        """Insert spacer and print out main menu options."""

        keys_list = list(self.main_options.keys())
        keys_list.insert(self._orig_main_menu_len, 'spacer')
        for key in keys_list:
            if key == 'spacer':
                print()
                continue
            option = self.main_options.get(key, {})

            print(f"{option.get('name')} - {option.get('description')}")
