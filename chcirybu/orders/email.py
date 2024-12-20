from django.core.mail import send_mail
from chcirybu import settings
from qrplatba import QRPlatbaGenerator
from datetime import datetime, timedelta
from django.core.mail import EmailMessage
from django.utils.html import format_html, mark_safe
import io
import cairosvg


def email_recap(order):
    mail_body = 'Dobrý den,\nVaše předpobjednávka na Chcirybu.cz byla vytvořena.\n\nZde je rekapitulace:\n\n'
    mail_body = mail_body + f'jméno a příjmení: {order.first_name} {order.surname}\n'
    mail_body = mail_body + f'telefon: {order.phonenumber}\n'
    mail_body = mail_body + f'vyzvednutí: {order.delivery.delivery}, {order.delivery.day} - {order.delivery.part}\n\n\n'
    
    
    for f in order.order_fish.all():
        mail_body = mail_body + f'Druh: {f.fish.fish} {f.fish.desc}, Počet: {f.amount} ks, Zpracování: {f.finish}\n'
        
    mail_body = mail_body + '\n*Pokud jste si předobjednali druh ryby, označený hvězdičkou, budeme Vás kontaktovat a domluvíme podrobnosti.\n\n\n'
    
    mail_body = mail_body + f'Jakékoliv dotazy Vám zodpovíme, stačí pouze odpovědět, na tento email nebo zavolat na telefonní číslo {settings.MAIN_PHONE_CONTACT}'
    
    mail_body = mail_body + '\n\n\n\nS pozdravem team Chcirybu.cz.'
    
    send_mail(
        f'Předobjednávka Chcirybu.cz číslo: {order.pk}',
        mail_body,
        'ja@chcirybu.cz',
        [order.email,]
    )


def email_payment(order):

    complete_price = order.complete_price()
    discount_price = order.complete_discount_price()

    due = datetime(2025, 1, 2)
    generator = QRPlatbaGenerator(settings.ACCOUNT_NUMBER ,round(order.complete_discount_price()) , x_vs=order.pk, message='Platba CHCIRYBU.CZ', due_date=due)
    img = generator.make_image()
    svg_data = img.to_string(encoding='unicode')


    png_output = io.BytesIO()
    cairosvg.svg2png(bytestring=svg_data.encode('utf-8'), write_to=png_output)
    png_output.seek(0)

    # Vygenerování HTML seznamu objednávek
    items = mark_safe(''.join(
        f'<li><strong>Druh:</strong> {f.fish.fish} {f.fish.desc} ({f.fish.price} Kč / kg) '
        f'<strong>Počet:</strong> {f.amount} ks, '
        f'<strong>Zpracování:</strong> {f.finish}, '
        f'<strong>Váha:</strong> {f.weight} kg, '
        f'<strong>Cena:</strong> {f.item_price()} Kč</li>'
        for f in order.order_fish.all()
    ))


    if order.discount_percentage > 0:
        total_price = format_html(
            '''
                <p><strong>Cena celkem:</strong> {complete_price}</p>
                <p><strong>Sleva: </strong> {discount} % </p>
                <p><strong>Cena po slevně:</strong> {discount_price} Kč</p>
            ''',
            complete_price=complete_price,
            discount=order.discount_percentage,
            discount_price=order.complete_discount_price()
        )
    else:
        total_price = format_html(
            f'<p><strong>Cena celkem:</strong> {complete_price}</p>'
        )

    # HTML tělo e-mailu
    html_body = format_html(
        '''
        <p>Dobrý den,</p>

        <p>Děkujeme za Váš nákup na <a href="https://www.chcirybu.cz">www.chcirybu.cz</a>. Zde je rekapitulace a vyúčtování:</p>

        <p><strong>Jméno a příjmení:</strong> {first_name} {surname}<br>
        <strong>Telefon:</strong> {phonenumber}<br>
        <strong>Vyzvednutí:</strong> {delivery}, {day} - {part}</p>

        <h3>Objednávka:</h3>
        <ul>
            {items}
        </ul>

        {total_price}

        <p>Prosíme o úhradu na účet: <strong>{acount}</strong><br>
        Variabilní symbol: <strong>{order_pk}</strong></p>

        <p>Přejeme příjemné prožití svátků.<br>
        S pozdravem,<br>
        <strong>Team Chcirybu.cz</strong><br>
        Kontakt: {main_phone}</p>
        ''',
        first_name=order.first_name,
        surname=order.surname,
        phonenumber=order.phonenumber,
        delivery=order.delivery.delivery,
        day=order.delivery.day,
        part=order.delivery.part,
        items=items,
        complete_price=complete_price,
        order_pk=order.pk,
        main_phone=settings.MAIN_PHONE_CONTACT,
        acount=settings.ACCOUNT_NUMBER,
        total_price=total_price
    )


    # Vytvoření e-mailu s přílohou
    email = EmailMessage(
        subject=f'Vyúčtování Chcirybu.cz, objednávka číslo: {order.pk}',
        body=html_body,  # HTML obsah
        from_email='ja@chcirybu.cz',
        to=[order.email],
    )

    email.content_subtype = 'html'  # Nastavení obsahu na HTML

    email.attach('qr_platba.png', png_output.getvalue(), 'image/png')

    # Odeslání e-mailu
    email.send()

