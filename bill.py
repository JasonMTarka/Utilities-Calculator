

class Bill:

    def __init__(self, utility, date, amount, user1_paid=False, user2_paid=True, paid=False, note="", primary_key=1):

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

    def __repr__(self):
        return f"""
            Bill({self.utility}, {self.date}, {self.amount},
            user2_paid={self.user2_paid}, user1_paid={self.user1_paid},
            paid={self.paid}, note={self.note}, primary_key={self.id})
            """

    def __str__(self):
        if self.user2_paid is True:
            x = "paid"
        else:
            x = "not paid yet"

        if self.user1_paid is True:
            j = "paid"
        else:
            j = "not paid yet"

        return f"""
Date: {self.date}  A {self.utility} bill for {self.amount} yen.
ID: {self.id}       User1 has {j} and User2 has {x}.
            
             Notes: {self.note}
            """
