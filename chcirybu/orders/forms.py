from django.forms import ModelForm
from orders.models import Order,OrderFish


class OrderForm(ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'surname', 'email', 'phonenumber', 'delivery', 'adress', 'package', 'commercial', 'voucher']
        

class OrderFishForm(ModelForm):
    class Meta:
        model = OrderFish
        fields = ['fish', 'amount', 'finish', 'desc']
