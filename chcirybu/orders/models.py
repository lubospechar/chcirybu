from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from twilio.rest import Client
from chcirybu.settings import (
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_NUMBER
)

from orders.email import email_payment

class Delivery(models.Model):
    day = models.DateField(
        verbose_name="Den vyzvednutí",
    )

    delivery = models.CharField(
        verbose_name="Místo výdeje",
        max_length=30,
    )

    part = models.CharField(
        verbose_name='Část dne',
        max_length=20,
    )

    ordering = models.PositiveSmallIntegerField(
        verbose_name="řazení"
    )

    alive_fish = models.BooleanField(
        verbose_name = "Možnost odebrat živou rybu"
    )

    class Meta:
        verbose_name="Místo a čas výdeje"
        verbose_name_plural="Místa a čas výdeje"
        unique_together = ('day', 'delivery', 'part')
        ordering = ('ordering', 'day', 'part', 'delivery')

    def __str__(self):
        return f'{self.delivery} - {self.day} - {self.part}'

class Fish(models.Model):
    fish = models.CharField(
        max_length=30,
        verbose_name="Ryba",
    )

    desc = models.CharField(
        max_length=30,
        verbose_name="Popis",
    )

    price_alive = models.PositiveSmallIntegerField(
        verbose_name="Cena živá váha (pouze na stánku)",
        default=0
    )

    price = models.PositiveSmallIntegerField(
        verbose_name="Cena kuchaná ryba",
        default=0
    )

    store = models.IntegerField(
        verbose_name="zásoba",
        default=0
    )

    cons = models.BooleanField(
        verbose_name="Nutnost konsultace",
        default=False
    )

    class Meta:
        unique_together = ('fish', 'desc',)
        verbose_name="Ryba"
        verbose_name_plural="Ryby"
        ordering = ['fish', 'desc']

    def store_info(self):
        if self.store < 1:
            store_info = "vyprodáno"
        elif self.store == 1:
            store_info = "1 kus"
        elif self.store > 1 and self.store <= 4:
            store_info = f'{self.store} kusy'
        elif self.store > 4 and self.store <= 10:
            store_info = f'{self.store} kusů'
        elif self.store > 10 and self.store <= 50:
            store_info = 'více než 10 kusů'
        elif self.store > 50:
            store_info = 'více než 50 kusů'

        return store_info

    def __str__(self):
        if self.cons:
            cons = '*'
        else: cons = ''
        return f'{self.fish} - {self.desc} ({self.store_info()}){cons}'

class Order(models.Model):
    first_name = models.CharField(
        verbose_name='Jméno',
        max_length=50,
    )

    surname = models.CharField(
        verbose_name='Příjmení',
        max_length=60,
    )

    email = models.EmailField(
        verbose_name="Email",
        blank=True, null=True,
        help_text="nepovinné"
    )

    phonenumber = PhoneNumberField(
        verbose_name="Telefon"
    )

    commercial = models.BooleanField(
        verbose_name="Reklamní účely",
    )

    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Vytvořeno'
    )

    delivery = models.ForeignKey(
        Delivery, on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="Místo a čas výdeje"
    )

    status = models.PositiveSmallIntegerField(
        choices=(
            (0, "formulář vyplněn"),
            (1, "objednáno"),
            (2, "připraveno"),
            (3, "odeslána informační SMS"),
            (4, "vyřízeno"),
            (5, "odeslané platební údaje na email"),
            (99, "zrušeno"),
        ),
        default=0
    )

    note = models.CharField(
        verbose_name='Poznámka',
        max_length=255,
        null=True, blank=True
    )

    adress = models.CharField(
        verbose_name='Adresa',
        max_length=255,
        null=True, blank=True,
        help_text="nepovinné"
    )

    alive_fish = models.BooleanField(
        verbose_name="Platba za živou váhu",
        default = False
    )

    package = models.BooleanField(
        verbose_name="balíček",
        help_text="Chci připravit balíček a dostat SMS, že je na stánku vše připraveno.",
        default=False
    )

    class Meta:
        verbose_name='Objednávka'
        verbose_name_plural='Objednávky'
        ordering=('pk', 'surname',)

    def full_name(self):
        return f'{self.first_name} {self.surname}'

    def __str__(self):
        return f'Objednávka č. {self.pk}, {self.full_name()} cena: {self.complete_price()}'

    def complete_price(self):
        price = 0
        for p in self.order_fish.all():
            price = price + p.item_price()





        return f'{price} kč'

    complete_price.short_description="celková cena"

    def save(self, *args, **kwargs):
        if self.status == 3:
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body='Vase ryba je pripravena na stanku v Lisove',
                from_="CHCIRYBU",
                to=self.phonenumber.as_e164
            )

            print(message)

        if self.status == 5:
            email_payment(self)
            price = self.complete_price()
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=f'Dekujeme za objednavku na chcirybu.cz. Prosime o uhrazeni castky {price}, Cislo uctu: 247633301/0600, VS: {self.pk}',
                from_="CHCIRYBU",
                to=self.phonenumber.as_e164
            )

        super(Order, self).save(*args, **kwargs)


class Finish(models.Model):
    procedure = models.CharField(
        verbose_name='Procedura',
        max_length=100,
    )

    price = models.PositiveSmallIntegerField(
        verbose_name="Cena"
    )

    class Meta:
        verbose_name = 'Zpracování'
        verbose_name_plural = 'Zpracování'
        ordering = ['price',]

    def __str__(self):
        return f'{self.procedure}: {self.price} kč za kus'

class OrderFish(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name='order_fish',
        verbose_name="objednávka",
    )

    fish = models.ForeignKey(
        Fish, on_delete=models.CASCADE,
        related_name='order_fish',
        verbose_name="Ryba"
    )

    amount = models.PositiveSmallIntegerField(
        verbose_name="Množství"
    )

    finish = models.ForeignKey(
        Finish, on_delete=models.PROTECT,
        verbose_name="Zpracování",
        related_name="order_fish"
    )

    desc = models.CharField(
        verbose_name="Poznámka",
        max_length=255,
        null=True, blank=True
    )

    weight = models.FloatField(
        default=0, verbose_name="Váha",
        help_text = "Po vyplnění váhy bude dopočítána cena",
    )

    def __str__(self):
        return f'{self.amount}x {self.fish}'

    def order_phoneumber(self):
        return self.order.phonenumber

    order_phoneumber.short_description = ('telefon')


    def item_price(self):
        if self.weight == None:
            return 0

        if self.order.package:
            price = round((self.weight * self.fish.price) + (self.amount * self.finish.price)) # cena mrtvou
        else:
            price = round((self.weight * self.fish.price_alive) + (self.amount * self.finish.price)) # cena za zivou

        return price

    item_price.short_description = 'cena za položku'

    class Meta:
        verbose_name = "Objednaná ryba"
        verbose_name_plural = 'Objednané ryby'






