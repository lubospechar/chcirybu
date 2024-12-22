from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.db.models import Sum
from orders.models import Fish, Order, Delivery, OrderFish, DiscountPeriod
from orders.forms import OrderForm, OrderFishForm
from orders.email import email_recap
from django.forms import formset_factory
from django.http import HttpResponse, Http404
import datetime
from django.conf import settings
from orders.sms_sender import SMSSender
from openpyxl import Workbook
import pandas as pd


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
            day__gte=datetime.date.today(),
            enable=True,
        )
    else:
        delivery_queryset = Delivery.objects.filter(
            day__gt=datetime.date.today(),
            enable=True,
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


            discount = DiscountPeriod.get_current_discount()

            if discount:
                order.discount_percentage = discount.discount_percentage


            for f in formset:
                if f.cleaned_data: # tohle chytá prázdnou řádku z formfactory, jen nevím zda je to úplne OK řešení
                    fish = f.save(commit=False)
                    fish.order = order
                    fish.save()

            order.status = 0
            order.save()

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

        #TODO platnost stránky časově.
        if order.status == 1:
            raise Http404 # platnost stránky vypršela



        if order.email:
            email_recap(order)

        if order.phonenumber:
            new_sms = SMSSender(
                login=settings.SMS_SENDER_LOGIN,
                secret_key=settings.SMS_SENDER_SECRET
            )

            new_sms.send_sms(order.phonenumber.as_e164, "CHCIRYBU.CZ: Vase predobjednavka byla prijata.")

        order.status = 1
        order.save()


        return render(request, 'orders/finish.html', {'order': order})


class ExcelExport(View):
    def get(self, request, pk, *args, **kwargs):
        # Získání konkrétního Delivery podle pk
        delivery = get_object_or_404(Delivery, pk=pk)

        # Filtrování OrderFish na základě Order s daným Delivery
        fish_items = OrderFish.objects.filter(
            order__in=Order.objects.filter(delivery=delivery)
        ).select_related('order', 'fish', 'finish', 'order__processed_by',)

        # Příprava dat pro export
        data = []
        for item in fish_items:
            data.append({
                "Číslo objednávky": item.order.pk,
                "Jméno": item.order.first_name,
                "Příjmení": item.order.surname,
                "Email": item.order.email or "N/A",
                "Telefon": str(item.order.phonenumber),
                "Ryba": item.fish.fish,
                "Popis ryby": item.fish.desc,
                "Množství": item.amount,
                "Zpracování": item.finish.procedure,
                "Zpracovává": item.order.processed_by or 'N/A',
                "Poznámka": item.desc or "N/A",
                "Adresa": item.order.adress,
            })

        # Vytvoření pandas DataFrame
        df = pd.DataFrame(data)

        # Nastavení odpovědi pro stažení Excelového souboru
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = f'attachment; filename="orders_export_delivery_{pk}.xlsx"'

        # Uložení DataFrame do Excelového souboru
        with pd.ExcelWriter(response, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Export objednávek")

        return response

