from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.db.models import Sum
from orders.models import Fish, Order, Delivery, OrderFish
from orders.forms import OrderForm, OrderFishForm
from orders.email import email_recap
from django.forms import formset_factory
from django.http import HttpResponse, Http404
import datetime


class Home(View):
    form = OrderForm
    fish_form = OrderFishForm
    # vypne labels v html
    fish_form.base_fields['fish'].label = False
    fish_form.base_fields['amount'].label = False
    fish_form.base_fields['finish'].label = False
    fish_form.base_fields['desc'].label = False

    # udělá filtr na formulářovém poli
    fish_form.base_fields['fish'].queryset = Fish.objects.filter(
        store__gt=0,
    )


    f = Fish.objects.all().order_by('fish')

    if datetime.datetime.now().hour < 18:
        delivery_queryset = Delivery.objects.filter(
            day__gte=datetime.date.today()
        )
    else:
        delivery_queryset = Delivery.objects.filter(
            day__gt=datetime.date.today()
        )

    form.base_fields['delivery'].queryset =  delivery_queryset

    def get(self, request):
        OrderFishFormSet = formset_factory(self.fish_form, extra=2)
        formset = OrderFishFormSet
        return render(request, 'orders/home.html', {
            'form': self.form,
            'formset': formset,
            'fish': self.f
            # 'fish': Fish.objects.all().order_by('fish')
        })

    def post(self, request):
        form = self.form(request.POST)
        OrderFishFormSet = formset_factory(self.fish_form)
        formset = OrderFishFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            order = form.save(commit=False)
            if order.package == True:
                order.alive_fish == False
            else:
                order.alive_fish = True
            order.save()

            for f in formset:
                if f.cleaned_data: # tohle chytá prázdnou řádku z formfactory, jen nevím zda je to úplne OK řešení
                    fish = f.save(commit=False)
                    fish.order = order
                    fish.save()

            return redirect('finish', order_pk=order.pk)


        return render(request, 'orders/home.html', {
            'form': self.form,
            'formset': formset,
            # 'fish': Fish.objects.all().order_by('fish')
            'fish': self.f
        })

class Finish(View):
    def get(self, request, order_pk):
        order = get_object_or_404(Order, pk=order_pk)

        if order.status == 1:
            raise Http404 # platnost stránky vypršela

        for f in order.order_fish.all():
            fish = f.fish
            fish.store = fish.store - f.amount
            fish.save()

        order.status = 1
        order.save()

        if order.email:
            email_recap(order)

        return render(request, 'orders/finish.html', {'order': order})



