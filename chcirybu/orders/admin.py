from django.contrib import admin
from orders.models import (
    Delivery, Order, Fish,  OrderFish, Finish, Voucher, DiscountPeriod
)
from django.urls import path, reverse
from django.utils.safestring import mark_safe

from django.shortcuts import redirect
from django.db.models.functions import Concat
from django.db.models import Value, F, CharField


@admin.register(DiscountPeriod)
class DiscountPeriodAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'discount_percentage',
        'start_date',
        'end_date',
        'is_active',
        'is_current_discount',
    )
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('name', 'description')
    ordering = ['start_date']
    fieldsets = (
        (None, {
            'fields': ('name', 'description')
        }),
        ('Nastavení slevy', {
            'fields': ('discount_percentage', 'start_date', 'end_date', 'is_active')
        }),
    )

    def is_current_discount(self, obj):
        """Zobrazí True/False, pokud je sleva právě aktivní."""
        return obj.is_current()
    is_current_discount.short_description = "Aktuální sleva"
    is_current_discount.boolean = True  # V administraci zobrazí ikonu místo textu

@admin.register(Delivery)
class DelivaryAdmin(admin.ModelAdmin):
    list_display = ('delivery', 'day', 'part', 'ordering', 'alive_fish')
    list_editable = ('ordering', )

@admin.register(Fish)
class FishAdmin(admin.ModelAdmin):
    list_display = ('fish', 'desc', 'price', 'store', 'cons')
    list_editable = ('price', )

class OrderFishInline(admin.TabularInline):
    model = OrderFish


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'full_name', 'id','email',
        'phonenumber', 'delivery',
        'status', 'note', 'adress', 'complete_price', 'send_sms_button', 'payment_button',
    )

    list_filter = ('status', 'delivery',)
    
    search_fields = (
        'surname', 'first_name', 'phonenumber', 'pk',
    )

    inlines = [OrderFishInline, ]

    def send_sms_button(self, obj):
        url = reverse('admin:send_info_sms_for_order', args=[obj.pk])
        return mark_safe(f"<a href='{url}' class='button'>Připraveno</a>")

    send_sms_button.short_description = "INFO SMS"

    def payment_button(self, obj):
        url = reverse('admin:send_payment_for_order', args=[obj.pk])
        return mark_safe(f"<a href='{url}' class='button'>Platba</a>")

    payment_button.short_description = "PLATBA"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:pk>/send_info_sms/',
                self.admin_site.admin_view(self.send_info_sms),
                name='send_info_sms_for_order',
            ),
            path(
                '<int:pk>/send_payment/',
                self.admin_site.admin_view(self.send_payment),
                name='send_payment_for_order',
            ),
        ]
        return custom_urls + urls

    def send_info_sms(self, request, pk):
        obj = self.get_object(request, pk)
        if obj:
            result = obj.send_sms_info()  # Předpokládám, že tato metoda je v modelu
            self.message_user(request, result)
        else:
            self.message_user(request, "Objekt nenalezen.", level=messages.ERROR)
        return redirect('../')

    def send_payment(self, request, pk):
        obj = self.get_object(request, pk)
        if obj:
            result = obj.send_payment_email_sms()
            self.message_user(request, result)
        else:
            self.message_user(request, "Objekt nenalezen.", level=messages.ERROR)
        return redirect('../')

    def send_info_sms_action(self, request, queryset):
        for obj in queryset:
            result = obj.send_sms_info()
            self.message_user(request, f"SMS pro {obj} byla odeslána: {result}")
    send_info_sms_action.short_description = "Odeslat informační SMS"

    actions = [send_info_sms_action]

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            _full_name=Concat(F('first_name'), Value(' '), F('surname'), output_field=CharField())
        )

    def full_name(self, obj):
        return obj._full_name
    full_name.admin_order_field = '_full_name'  # Umožní třídění podle anotace
    full_name.short_description = "Jméno"


@admin.register(OrderFish)
class OrderFishAdmin(admin.ModelAdmin):
    list_display = ('fish', 'amount', 'finish', 'order', 'order_phoneumber', 'item_price')
    search_fields = ('order__first_name', 'order__surname', 'order__phonenumber',)
    list_filter = ('order__status', 'fish__fish', 'order__delivery')
    
@admin.register(Finish)
class FinishAdin(admin.ModelAdmin):
    list_display = ('procedure', 'price')
    list_editable = ('price',)

@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ('voucher_code', 'discount')  # Zobrazené sloupce v přehledu
    search_fields = ('voucher_code',)  # Možnost vyhledávat podle slevového kódu
    list_filter = ('discount',)  # Možnost filtrovat podle hodnoty slevy
    ordering = ('voucher_code',)  # Řazení podle slevového kódu
    fields = ('voucher_code', 'discount')  # Pole zobrazená ve formuláři
