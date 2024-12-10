import hashlib
import requests


class SMSSender:
    # URL API pro odesílání SMS
    api_url = "https://smsgateapi.sms-sluzba.cz/apipost30/sms"

    def __init__(self, login, secret_key):
        """
        Inicializace třídy SMSSender.

        :param login: Přihlašovací jméno uživatele.
        :param secret_key: Tajný klíč uživatele pro autentizaci.
        """
        self.secret_key = secret_key
        self.login = login

    def generate_api_key(self, message):
        """
        Vygeneruje autentizační klíč (auth) na základě hesla, loginu a zprávy.

        :param message: Obsah SMS zprávy.
        :return: Autentizační klíč (auth) jako hexadecimální řetězec.
        """
        # Vytvoření MD5 hashe tajného klíče
        md5_secret_key = hashlib.md5(self.secret_key.encode()).hexdigest()

        # Získání prvních 31 znaků zprávy (truncated_text)
        truncated_text = message[:31]

        # Spojení hodnot do jednoho řetězce
        combined = md5_secret_key + self.login + "send" + truncated_text

        # Vytvoření výsledného MD5 hashe jako autentizační klíč
        auth = hashlib.md5(combined.encode()).hexdigest()
        return auth

    def send_sms(self, to_number, message):
        """
        Odeslání SMS pomocí API.

        :param to_number: Telefonní číslo příjemce ve formátu +420123456789.
        :param message: Text SMS zprávy.
        :return: Odezva z API jako objekt Response.
        """

        # Vygenerování autentizačního klíče pro danou zprávu
        api_key = self.generate_api_key(message)

        # Příprava dat pro odeslání (payload)
        payload = {
            "msg": message,             # Obsah SMS zprávy
            "msisdn": to_number,        # Telefonní číslo příjemce
            "act": "send",              # Akce, zde pevně nastaveno na "send"
            "login": self.login,        # Přihlašovací jméno uživatele
            "auth": api_key,            # Vygenerovaný autentizační klíč
        }

        # Odeslání POST požadavku na API
        response = requests.post(self.api_url, data=payload)

        # Vrácení odpovědi API volajícímu
        return response


#
#
# def send_demo_sms():
#     """
#     Ukázková funkce pro odeslání SMS pomocí třídy SMSSender.
#     """
#     # Přihlašovací údaje (nahraďte skutečnými hodnotami)
#     login = "lubospechar"  # Nahraďte přihlašovacím jménem
#     secret_key = ""  # Nahraďte tajným klíčem
#
#     # Telefonní číslo příjemce a zpráva
#     to_number = "+420123456789"  # Nahraďte cílovým telefonním číslem
#     message = "Toto je ukázková SMS zpráva."
#
#     # Vytvoření instance třídy SMSSender
#     sms_sender = SMSSender(login, secret_key)
#
#     # Odeslání SMS zprávy
#     try:
#         response = sms_sender.send_sms(to_number, message)
#
#         # Zpracování odpovědi API
#         if response.status_code == 200:
#             print("SMS byla úspěšně odeslána!")
#             print("Odpověď API:", response.text)
#         else:
#             print("Při odesílání SMS nastala chyba.")
#             print("Status kód:", response.status_code)
#             print("Odpověď API:", response.text)
#     except Exception as e:
#         print("Nastala výjimka při odesílání SMS:", str(e))
#
# # Zavolání funkce pro ukázku
# send_demo_sms()
