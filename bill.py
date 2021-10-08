class Bill:
    """Class which stores information about a single database record."""

    def __init__(
        self,
        utility: str,
        date: str,
        amount: int,
        user1_paid: bool = False,
        user2_paid: bool = False,
        paid: bool = False,
        note: str = "",
        primary_key: int = 1,
        **kwargs,
    ) -> None:
        """Create a bill object with the given values."""

        self.utility = utility
        self.amount = amount
        self.owed_amount = int(amount) / 2
        self.date = date

        if user2_paid == 1:
            self.user2_paid = True
        elif user2_paid == 0:
            self.user2_paid = False
        else:
            self.user2_paid = user2_paid

        if user1_paid == 1:
            self.user1_paid = True
        elif user1_paid == 0:
            self.user1_paid = False
        else:
            self.user1_paid = user1_paid

        if paid == 1:
            self.paid = True
        elif paid == 0:
            self.paid = False
        else:
            self.paid = paid

        self.note = note
        self.id = primary_key
        self.kwargs = kwargs

    def __repr__(self) -> str:
        return (
            "Bill("
            f"{self.utility},"
            f"{self.date},"
            f"{self.amount},"
            f"user1_paid={self.user1_paid},"
            f"user2_paid={self.user2_paid},"
            f"paid={self.paid},"
            f"note='{self.note}',"
            f"primary_key={self.id}"
        )

    def __str__(self) -> str:
        if self.user1_paid is True:
            user1_var = "paid"
        else:
            user1_var = "not paid yet"

        if self.user2_paid is True:
            user2_var = "paid"
        else:
            user2_var = "not paid yet"

        if self.kwargs.get("user1"):
            user1 = self.kwargs.get("user1")
        else:
            user1 = "User1"
        if self.kwargs.get("user2"):
            user2 = self.kwargs.get("user2")
        else:
            user2 = "User2"

        return f"""
Date: {self.date} A {self.utility} bill for {self.amount} yen.
ID: {self.id}       {user1} has {user1_var} and {user2} has {user2_var}.

Notes: {self.note}
            """
