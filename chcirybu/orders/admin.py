from django.contrib import admin
from orders.models import (
    Delivery, Order, Fish,  OrderFish, Finish, Voucher
)
from django.urls import path, reverse
from django.utils.safestring import mark_safe

from django.shortcuts import redirect

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
        'surname', 'first_name','email',
        'phonenumber', 'delivery',
        'status', 'note', 'adress', 'complete_price', 'commercial', 'view_on_site',
    )

    list_filter = ('status', 'commercial',)
    
    search_fields = (
        'surname', 'phonenumber',
    )
    
    
    inlines = [OrderFishInline, ]

    def view_on_site(self, obj):
        url = reverse('admin:send_info_sms_for_order', args=[obj.pk])
        return mark_safe(f"<a href='{url}' class='button'>Odeslat</a>")

    view_on_site.short_description = "INFO SMS"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:pk>/send_info_sms/',
                self.admin_site.admin_view(self.send_info_sms),
                name='send_info_sms_for_order',
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

    def send_info_sms_action(self, request, queryset):
        for obj in queryset:
            result = obj.send_sms_info()
            self.message_user(request, f"SMS pro {obj} byla odeslána: {result}")
    send_info_sms_action.short_description = "Odeslat informační SMS"

    actions = [send_info_sms_action]



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
