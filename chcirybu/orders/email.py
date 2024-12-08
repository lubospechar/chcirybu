from django.core.mail import send_mail

def email_recap(order):
    mail_body = 'Dobrý den,\nVaše předpobjednávka na Chcirybu.cz byla vytvořena.\n\nZde je rekapitulace:\n\n'
    mail_body = mail_body + f'jméno a příjmení: {order.first_name} {order.surname}\n'
    mail_body = mail_body + f'telefon: {order.phonenumber}\n'
    mail_body = mail_body + f'vyzvednutí: {order.delivery.delivery}, {order.delivery.day} - {order.delivery.part}\n\n\n'
    
    if order.package:
        mail_body = mail_body + 'Balíček Vám připravíme na stánku. Až bude připravený, zašleme Vám SMS.\n\n\n'
    else:
        mail_body = mail_body + 'Rybu budete mít připravenou živou na stánku, na počkání Vám ji zpracujeme.\n\n\n'
    
    for f in order.order_fish.all():
        mail_body = mail_body + f'Druh: {f.fish.fish} {f.fish.desc}, Počet: {f.amount} ks, Zpracování: {f.finish}\n'
        
    mail_body = mail_body + '\n*Pokud jste si předobjednali druh ryby, označený hvězdičkou, budeme Vás kontaktovat a domluvíme podrobnosti.\n\n\n'
    
    mail_body = mail_body + 'Jakékoliv dotazy Vám zodpovíme, stačí pouze odpovědět, na tento email nebo zavolat na telefonní číslo +420 725 606 312'
    
    mail_body = mail_body + '\n\n\n\nS pozdravem team Chcirybu.cz.'
    
    send_mail(
        f'Předobjednávka Chcirybu.cz číslo: {order.pk}',
        mail_body,
        'ja@chcirybu.cz',
        [order.email,]
    )


def email_payment(order):
    complete_price = order.complete_price()
    mail_body = 'Dobrý den,\n\nděkujeme za Váš nákup na www.chcirybu.cz. Zde je rekapitulace a vyúčtování.\n\n\n'
    
    mail_body = mail_body + f'jméno a příjmení: {order.first_name} {order.surname}\n'
    mail_body = mail_body + f'telefon: {order.phonenumber}\n'
    mail_body = mail_body + f'vyzvednutí: {order.delivery.delivery}, {order.delivery.day} - {order.delivery.part}\n\n\n'

    for f in order.order_fish.all():
        item_price = f.item_price()
        mail_body = mail_body + f'Druh: {f.fish.fish} {f.fish.desc}, Počet: {f.amount} ks, Zpracování: {f.finish}, Váha: {f.weight} kg, Cena za položku: {item_price} kč\n'
    
    mail_body = mail_body + f'\n\n\nCena celkem: {complete_price}\n'
    
    mail_body = mail_body + f'Prosíme o úhradu na účet: 247633301/0600\n'
    mail_body = mail_body + f'Variabilní symbol: { order.pk }\n'
    
    mail_body = mail_body + f'\n\nPřejeme příjemné prožití svátků\n'
    mail_body = mail_body + 'S pozdravem team Chcirybu.cz.\n'
    mail_body = mail_body + '+420 725 606 312'
    send_mail(
        f'Vyúčtování Chcirybu.cz, objednávka číslo: {order.pk}',
        mail_body,
        'ja@chcirybu.cz',
        [order.email,]
    )
        
    
