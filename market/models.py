from django.db import models
from django.utils import timezone, dateformat
import datetime
from django.contrib.auth.models import User
from accounts.models import Customer


class Product(models.Model):
    code = models.CharField(max_length=10, unique=True, null=False)
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    inventory = models.IntegerField(default=0)

    def increase_inventory(self, amount):
        if amount < 0:
            raise Exception('amount must be positive number and {} is not accepted'.format(amount))
        else:
            self.inventory += amount
            self.save()

    def decrease_inventory(self, amount):
        amount = abs(amount)
        if self.inventory - amount >= 0:
            self.inventory -= amount
            self.save()
        else:
            raise Exception('{} inventory is {} and it is lower than {}'.format(self.name, self.inventory, amount))


class OrderRow(models.Model):
    product = models.ForeignKey('Product', on_delete=models.PROTECT)
    order = models.ForeignKey('Order', on_delete=models.PROTECT, null=True)
    amount = models.IntegerField()


class Order(models.Model):
    # Status values. DO NOT EDIT
    STATUS_SHOPPING = 1
    STATUS_SUBMITTED = 2
    STATUS_CANCELED = 3
    STATUS_SENT = 4

    status_choices = (
        (STATUS_SHOPPING, 'در حال خرید'),
        (STATUS_SUBMITTED, 'ثبت‌شده'),
        (STATUS_CANCELED, 'لغوشده'),
        (STATUS_SENT, 'ارسال‌شده')
    )

    customer = models.ForeignKey('accounts.Customer', on_delete=models.PROTECT, null=True)
    order_time = models.DateTimeField(null=True)
    total_price = models.IntegerField()
    status = models.IntegerField(choices=status_choices)

    @staticmethod
    def initiate(customer):
        a = Customer.objects.get(user=customer)
        if Order.objects.filter(customer=a, status=1).count() == 1:
            b = Order.objects.get(customer=a, status=1)
            return b
        else:
            b = Order(customer=a)
            return b

    def add_product(self, product, amount):
        pro = Product.objects.get(code=product)
        if OrderRow.objects.filter(product=pro, order=self.id).count() == 1:
            subject = OrderRow.objects.get(product=pro, order=self.id)
            if subject.amount + amount > pro.inventory:
                raise OverflowError
        if amount == 0 or amount > pro.inventory or amount < 0:
            raise ValueError
        else:
            if self.total_price is None:
                self.total_price = (pro.price * amount)
            else:
                self.total_price += (pro.price * amount)
            self.status = 1
            self.save()
            c = self.id
            if OrderRow.objects.filter(product=pro, order=c).count() == 1:
                a = OrderRow.objects.get(product=pro, order=c)
                new_amount = a.amount
                new_amount += amount
                OrderRow.objects.filter(product=pro, order=c).update(amount=new_amount)
                self.save()
            else:
                b = OrderRow.objects.create(product=pro, order=self, amount=amount)
                b.save()

    def remove_product(self, product, amount=None):
        pro = Product.objects.get(code=product)
        f = self.id
        if amount is None:
            c = OrderRow.objects.get(product=pro, order=f)
            self.total_price -= pro.price * c.amount
            self.status = 1
            OrderRow.objects.filter(product=pro, order=f).delete()
            self.save()
        else:
            if amount == 0 or amount < 0:
                raise TypeError
            else:
                if OrderRow.objects.filter(product=pro, order=f).count() == 1:
                    a = OrderRow.objects.get(product=pro, order=f)
                    new_amount = a.amount
                    new_amount -= amount
                    if new_amount == 0:
                        c = OrderRow.objects.filter(product=pro, order=f)
                        c.delete()
                        amon = pro.price * amount
                        self.total_price -= amon
                        self.status = 1
                        self.save()
                    elif new_amount < 0:
                        raise ValueError
                    else:
                        OrderRow.objects.filter(product=pro, order=f).update(amount=new_amount)
                        new = pro.price * amount
                        self.total_price -= new
                        self.status = 1
                        self.save()
                else:
                    raise ZeroDivisionError

    def submit(self):
        new_user = self.customer
        c = self.total_price
        d = self.id
        self.order_time = dateformat.format(timezone.now(), 'Y-m-d H:i:s')
        s = 0
        if new_user.balance < c:
            raise ValueError
        else:
            for item in OrderRow.objects.filter(order=d):
                h = item.product
                if h.inventory < item.amount:
                    s += 1
            if s > 0:
                raise TypeError
            else:
                custom = new_user.user
                new_balance = new_user.balance
                new_balance -= c
                Customer.objects.filter(user=custom).update(balance=new_balance)
                self.status = 2
                for i in OrderRow.objects.filter(order=d):
                    k = i.product
                    prod = k.name
                    new_inventory = k.inventory
                    new_inventory -= i.amount
                    Product.objects.filter(name=prod).update(inventory=new_inventory)
                self.save()

    def cancel(self):
        a = self.customer
        custom = a.user
        total = 0
        for obj in Order.objects.filter(customer=a, status=2):
            total += obj.total_price
            obj.status = 3
            d = obj.id
            obj.save()
            for item in OrderRow.objects.filter(order=d):
                k = item.product
                prod = k.name
                new_inventory = k.inventory
                new_inventory += item.amount
                Product.objects.filter(name=prod).update(inventory=new_inventory)
        new_balance = a.balance
        new_balance += total
        Customer.objects.filter(user=custom).update(balance=new_balance)

    def send(self):
        a = self.customer
        for obj in Order.objects.filter(customer=a, status=2):
            obj.status = 4
            obj.save()
