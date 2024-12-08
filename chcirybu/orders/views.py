from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.db.models import Sum
from orders.models import Fish, Order, Delivery, OrderFish
from orders.forms import OrderForm, OrderFishForm
from orders.email import email_recap
from django.forms import formset_factory
from django.http import HttpResponse, Http404
import datetime
import xlwt


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

class Stats(View):
    def get(self, request):
        data = OrderFish.objects.filter(
            order__in=Order.objects.filter(status=1)
        ).values('fish', 'order__delivery').annotate(Sum('amount'))

        data_dict = dict()
        for d in data:
            if not d['fish'] in data_dict:
                data_dict[d['fish']] = dict()

            data_dict[d['fish']][d['order__delivery']] = d['amount__sum']

        fish = Fish.objects.filter(pk__in={f['fish'] for f in data})
        delivery = Delivery.objects.filter(pk__in={f['order__delivery'] for f in data})

        wb = xlwt.Workbook()
        ws = wb.add_sheet('stats')

        ws.write(0,0, 'Ryba/Výdej')

        row = 1
        for d in delivery:
            ws.write(row, 0, f'{d.day} - {d.delivery} - {d.part}')
            col = 1
            for f in fish:
                if row == 1:
                    ws.write(row-1, col, f'{f.fish} - {f.desc}')

                try:
                    ws.write(row, col, data_dict[f.pk][d.pk])
                except KeyError:
                    ws.write(row, col, 0)

                col += 1


            row += 1

        response = HttpResponse(content_type="application/ms-excel")
        response['Content-Disposition'] = 'attachment; filename=stats.xls'
        wb.save(response)
        return response

class Fish_xls(View):
    def get(self, request):
        data = OrderFish.objects.filter(
            order__in=Order.objects.filter(status=1),
        ).order_by('order__pk')
        wb = xlwt.Workbook()
        ws = wb.add_sheet('ryby')
        ws.write(0,0, 'objednávka')
        ws.write(0,1, 'ryba')
        ws.write(0,2, 'desc')
        ws.write(0,3, 'počet')
        ws.write(0,4, 'jmeno')
        ws.write(0,5, 'příjmení')
        ws.write(0,6, 'telefon')
        ws.write(0,7, 'vyzvednutí')
        ws.write(0,8, 'adresa')
        ws.write(0,9, 'zpracovani')

        row = 1
        for d in data:
            ws.write(row, 0, d.order.pk)
            ws.write(row, 1, d.fish.fish)
            ws.write(row, 2, d.fish.desc)
            ws.write(row, 3, d.amount)
            ws.write(row, 4, d.order.first_name)
            ws.write(row, 5, d.order.surname)
            ws.write(row, 6, d.order.phonenumber.as_e164)
            ws.write(row, 7, d.order.delivery.__str__())
            ws.write(row, 8, d.order.adress)
            ws.write(row, 9, d.finish.procedure)
            ws.write(row, 10, d.desc)
            row += 1

        response = HttpResponse(content_type="application/ms-excel")
        response['Content-Disposition'] = 'attachment; filename=stats.xls'
        wb.save(response)
        return response

