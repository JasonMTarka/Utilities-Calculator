

class Bill:

    def __init__(self, utility, date, amount, xiaochen_paid=True, jason_paid=False, paid=False, note="", primary_key=None):

        self.utility = utility
        self.amount = amount
        self.owed_amount = int(amount) / 2
        self.date = date

        if xiaochen_paid == 1:
            self.xiaochen_paid = True
        elif xiaochen_paid == 0:
            self.xiaochen_paid = False
        else:
            self.xiaochen_paid = xiaochen_paid

        if jason_paid == 1:
            self.jason_paid = True
        elif jason_paid == 0:
            self.jason_paid = False
        else:
            self.jason_paid = jason_paid

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
            xiaochen_paid={self.xiaochen_paid}, jason_paid={self.jason_paid},
            paid={self.paid}, note={self.note})
            """

    def __str__(self):
        if self.xiaochen_paid is True:
            x = "paid"
        else:
            x = "not paid yet"

        if self.jason_paid is True:
            j = "paid"
        else:
            j = "not paid yet"

        return f"""
            A {self.utility} bill for {self.amount} yen for {self.date}.
            Xiaochen has {x} and Jason has {j}.
            ID: {self.id}
            Notes: {self.note}
            """
