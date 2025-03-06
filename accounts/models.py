from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    balance = models.IntegerField(default=20000, null=True)

    def deposit(self, amount):
        if amount < 0:
            raise Exception('amount must be positive number and {} is not accepted'.format(amount))
        else:
            self.balance += amount
            self.save()

    def spend(self, amount):
        if amount < 0:
            raise Exception('amount must be positive number and {} is not accepted'.format(amount))
        else:
            if self.balance - amount >= 0:
                self.balance -= amount
                self.save()
            else:
                raise Exception('balance of {} is {} and it is lower than {}'.format(self.user, self.balance, amount))
