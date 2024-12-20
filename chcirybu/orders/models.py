from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings
from orders.sms_sender import SMSSender

from orders.email import email_payment
from django.utils.timezone import now

from decimal import Decimal

class DiscountPeriod(models.Model):
    name = models.CharField(max_length=100, help_text="Název slevy, např. 'Letní akce'")
    description = models.TextField(blank=True, help_text="Popis slevy nebo podmínky")
    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Procento slevy, např. 10.50 pro 10.5% slevu"
    )
    start_date = models.DateTimeField(help_text="Datum a čas začátku slevy")
    end_date = models.DateTimeField(help_text="Datum a čas konce slevy")
    is_active = models.BooleanField(
        default=True,
        help_text="Indikuje, zda je sleva aktivní"
    )

    class Meta:
        verbose_name = "Sleva"
        verbose_name_plural = "Slevy"
        ordering = ['start_date']

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"

    def is_current(self):
        """Vrací True, pokud je sleva právě teď platná."""
        return self.is_active and self.start_date <= now() <= self.end_date

    def clean(self):
        """Validace, aby se data nepřekrývala."""
        super().clean()
        overlapping_discounts = DiscountPeriod.objects.filter(
            is_active=True,
            start_date__lt=self.end_date,
            end_date__gt=self.start_date
        ).exclude(pk=self.pk)

        if overlapping_discounts.exists():
            raise ValidationError("Časový interval této slevy se překrývá s jinou aktivní slevou.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @classmethod
    def get_current_discount(cls):
        """
        Vrací aktuální platnou slevu nebo None, pokud žádná taková sleva neexistuje.
        """
        current_discount = cls.objects.filter(
            is_active=True,
            start_date__lte=now(),
            end_date__gte=now()
        ).first()  # Vrací první nalezenou aktuální slevu nebo None
        return current_discount

    class Meta:
        verbose_name = "Sleva"  # Jednotné číslo
        verbose_name_plural = "Slevy"  # Množné číslo
        ordering = ['start_date']

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

    price = models.PositiveSmallIntegerField(
        verbose_name="Cena živá váha",
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


class ProcessedBy(models.Model):
    processed_by = models.CharField(max_length=30, verbose_name="Zpracování")

    class Meta:
        verbose_name = "Odpovědnost za zpracování"
        verbose_name_plural = "Odpovědnost za zpracování"
        ordering = ["processed_by"]

    def __str__(self):
        return self.processed_by





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
        verbose_name="Telefon",
        region="CZ"
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
            (0, "formuář vyplněn"),
            (1, "objednáno"),
            (2, "připraveno"),
            (3, "odeslána informační SMS"),
            (4, "odeslané platební údaje na email a SMS"),
            (5, "vyřízeno"),
        ),
        default=1
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
        verbose_name="Chci živou rybu a vyzvednu si jí v Lišově na stánku",
        default = False
    )

    package = models.BooleanField(
        verbose_name="balíček",
        help_text="Chci připravit balíček a dostat SMS, že je na stánku vše připraveno.",
        default=False
    )

    voucher = models.CharField(max_length=255, null=True, blank=True)

    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Procento slevy, např. 10.50 pro 10.5% slevu",
        default=0,
        verbose_name="Sleva"
    )

    processed_by = models.ForeignKey(ProcessedBy, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Zpracování")

    class Meta:
        verbose_name='Objednávka'
        verbose_name_plural='Objednávky'
        ordering=('pk', 'surname',)

    def full_name(self):
        return f'{self.first_name} {self.surname}'

    def __str__(self):
        return f'Objednávka č. {self.pk}, {self.full_name()} cena: {self.complete_price()}'

    def total_price(self):
        price = 0
        for p in self.order_fish.all():
            price = price + p.item_price()

        return price

    def complete_price(self):
        return f'{self.total_price()} kč'

    complete_price.short_description="celková cena"


    def complete_discount_price(self):
        total_price = Decimal(self.total_price())  # Převod na Decimal
        return int(round(total_price - (total_price / Decimal(100) * self.discount_percentage)))


    complete_discount_price.short_description = "cena po slevě"

    def send_sms_info(self):
        new_sms = SMSSender(
            login=settings.SMS_SENDER_LOGIN,
            secret_key=settings.SMS_SENDER_SECRET
        )

        new_sms.send_sms(self.phonenumber.as_e164, "CHCIRYBU.CZ: Vase ryba je pripravena na stanku.")

        self.status = 3
        self.save()


    def send_sms_payment(self):
        new_sms = SMSSender(
            login=settings.SMS_SENDER_LOGIN,
            secret_key=settings.SMS_SENDER_SECRET
        )

        new_sms.send_sms(self.phonenumber.as_e164, f"CHCIRYBU.CZ: Cena za vasi objednavku je {self.complete_discount_price()}. Muzete zaplatit prevodem na ucet {settings.ACCOUNT_NUMBER}. Prejeme prijemne svatky.")

        self.status = 4
        self.save()


    def send_email_payment(self):
        email_payment(self)

        self.status = 4
        self.save()


    def send_payment_email_sms(self):
        if self.phonenumber:
            self.send_sms_payment()

        if self.email:
            self.send_email_payment()


    def pk_to_obj(self):
        return self.pk

    pk_to_obj.short_description = "Obj"

    #
    # def full_name(self):
    #     return f'{self.first_name} {self.surname}'
    #
    #
    # full_name.short_description = "Jméno"

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

        price = round((self.weight * self.fish.price) + (self.amount * self.finish.price))

        return price

    item_price.short_description = 'cena za položku'

    class Meta:
        verbose_name = "Objednaná ryba"
        verbose_name_plural = 'Objednané ryby'



class Voucher(models.Model):
    voucher_code = models.CharField(max_length=255, verbose_name='Slevový kód')
    discount = models.PositiveSmallIntegerField(validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        help_text="Hodnota musí být mezi 0 a 100."
    )


