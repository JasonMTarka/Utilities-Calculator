import sqlite3
from typing import Any, NamedTuple, Union, TYPE_CHECKING

from bill import Bill


class NamedRecord(NamedTuple):
    Id: int
    utility: str
    date: str
    cost: int
    user1_paid: bool
    user2_paid: bool
    paid: bool
    note: str


class Database:
    def __init__(self, debug: bool = False, setup: bool = False, **kwargs: str) -> None:
        """Initialize database connection and establish cursor."""

        self.debug = debug
        if debug is True:
            self.conn = sqlite3.connect(':memory:')
        else:
            self.conn = sqlite3.connect("records.db")

        self.c = self.conn.cursor()

        if setup is True or debug is True:
            if debug is True:
                kwargs = {'user1': 'TestUser1', 'user2': 'TestUser2'}
            self.setup(kwargs)

    def setup(self, kwargs: dict) -> None:
        """Set up a new database if records.db file not found or in debugging mode."""

        with self.conn:
            self.c.execute("""
                    CREATE TABLE bills (
                    id integer primary key,
                    utility text,
                    date text,
                    amount integer,
                    x_paid integer,
                    j_paid integer,
                    paid integer,
                    note text
                    )""")

            self.c.execute("""
                    CREATE TABLE users (
                    id integer primary key,
                    name text
                    )""")

            self.c.execute("""
                INSERT INTO users VALUES(NULL, :user1), (NULL, :user2)
                """, {'user1': kwargs.get('user1'), 'user2': kwargs.get('user2')})

            if self.debug is True:
                self.c.execute("""
                    INSERT INTO bills VALUES
                    (NULL, "gas", "05-21", 2000, 1, 0, 0, "Note"),
                    (NULL, "gas", "04-21", 3000, 1, 1, 1, "Note"),
                    (NULL, "electric", "03-21", 4500, 0, 1, 0, "Note"),
                    (NULL, "water", "02-21", 6211, 1, 0, 0, "Note"),
                    (NULL, "travel", "01-21", 8799, 1, 1, 1, "Note"),
                    (NULL, "gas", "12-20", 999, 0, 0, 0, "Note")
                    """)

    def get_user(self, user_id: int) -> str:
        """Get name of user at user_id."""

        self.c.execute("SELECT * FROM users WHERE id=:id", {"id": user_id})
        return self.c.fetchone()[1]

    def remove_utility(self, utility: str) -> None:
        """Remove a utility and all associated bills."""

        with self.conn:
            self.c.execute("DELETE FROM bills WHERE utility=:utility", {"utility": utility})

    def add_bill(self, bill: Bill) -> None:
        """Add a bill to the database."""

        with self.conn:
            self.c.execute("INSERT INTO bills VALUES (NULL, :utility, :date, :amount, :x_paid, :j_paid, :paid, :note)",
                           {"utility": bill.utility, "date": bill.date, "amount": bill.amount, "x_paid": bill.user1_paid,
                            "j_paid": bill.user2_paid, "paid": bill.paid, "note": bill.note})

    def remove_bill(self, bill: Any) -> None:
        """Remove a bill from the database."""

        with self.conn:
            try:
                self.c.execute("DELETE FROM bills WHERE id=:id", {"id": bill.id})
            except AttributeError:
                self.c.execute("DELETE FROM bills WHERE id=:id", {"id": bill})

    def pay_bill(self, bill: Bill) -> None:
        """Pay a bill, with new values already set on Bill object sent from calculator."""

        with self.conn:
            self.c.execute("""
                UPDATE bills
                SET x_paid = :user2_paid,
                    j_paid = :user1_paid,
                    paid = :paid,
                    note = :note
                WHERE id = :id
                """, {"user2_paid": bill.user2_paid, "user1_paid": bill.user1_paid, "paid": bill.paid, "note": bill.note, "id": bill.id})

    def get_all_records(self) -> list[Bill]:
        """Select all records in database."""

        self.c.execute("SELECT * FROM bills")
        return self._fetchall_and_convert()

    def get_record(self, bill: Union[int, Bill]) -> Any:
        """Get a record, accepting either a bill id or a Bill object."""

        try:
            # First check that bill is a Bill object
            if TYPE_CHECKING:
                assert isinstance(bill, Bill)
            self.c.execute("SELECT * FROM bills WHERE id=:id", {"id": bill.id})

        except AttributeError:
            # Next check that bill is a bill ID
            self.c.execute("SELECT * FROM bills WHERE id=:id", {"id": bill})

        try:
            return self._convert_to_object(self.c.fetchone())
        except TypeError:
            return None

    def get_utilities(self) -> list:
        """Return a list of all utilities present in the database."""

        self.c.execute("SELECT DISTINCT utility FROM bills")
        return self.c.fetchall()

    def get_utility_record(self, utility: str) -> list[Bill]:
        """Get a list of bills associated with a provided utility."""

        self.c.execute("SELECT * FROM bills WHERE utility=:utility", {"utility": utility})
        return self._fetchall_and_convert()

    def get_unpaid_bills(self) -> list[Bill]:
        """Get a list of all unpaid bills."""

        self.c.execute("SELECT * FROM bills WHERE paid=False")
        return self._fetchall_and_convert()

    def get_paid_bills(self) -> list[Bill]:
        """Get a list of all paid off bills."""

        self.c.execute("SELECT * FROM bills WHERE paid=True")
        return self._fetchall_and_convert()

    def get_bills_owed(self, user: str) -> list[Bill]:
        """Get a list of bills owed by a given user."""

        if user == self.get_user(1).lower():
            self.c.execute("SELECT * FROM bills WHERE j_paid=False")
        else:
            self.c.execute("SELECT * FROM bills WHERE x_paid=False")

        return self._fetchall_and_convert()

    def get_total_owed(self, user: str) -> float:
        """Get a total of the amount owed by a given user."""

        if user == self.get_user(1).lower():
            self.c.execute("SELECT * FROM bills WHERE j_paid=False")
        else:
            self.c.execute("SELECT * FROM bills WHERE x_paid=False")

        records = [NamedRecord(*record) for record in self.c.fetchall()]

        total_owed = 0.0
        for bill in records:
            total_owed += bill.cost / 2
        return total_owed

    def _fetchall_and_convert(self) -> list[Bill]:
        """Return a list of Bills retrieved by self.c.fetchall() after a query."""

        return [self._convert_to_object(record) for record in self.c.fetchall()]

    def _convert_to_object(self, record) -> Bill:
        """Take data from a database entry and converts it to a Bill object for use in the main application."""

        result = NamedRecord(*record)
        return Bill(result.utility, result.date, result.cost, user1_paid=result.user1_paid, user2_paid=result.user2_paid,
                    paid=result.paid, note=result.note, primary_key=result.Id, user1=self.get_user(1), user2=self.get_user(2))
