from django.contrib import admin
from orders.models import (
    Delivery, Order, Fish,  OrderFish, Finish, Voucher
)

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
        'pk', 'surname', 'first_name','email',
        'phonenumber', 'created', 'delivery',
        'status', 'note', 'adress', 'complete_price', 'commercial'
    )

    list_filter = ('status', 'commercial',)
    
    search_fields = (
        'surname', 'phonenumber',
    )
    
    
    
    inlines = [OrderFishInline, ]
    

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
