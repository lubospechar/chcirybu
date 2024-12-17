from django.conf import settings

def main_phone_contact(request):
    return {'MAIN_PHONE_CONTACT': settings.MAIN_PHONE_CONTACT}
