from django.contrib import admin
from django.urls import path
# from test_chcirybu import views as t_views
from orders.views import Home, Finish, Stats, Fish_xls
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', Home.as_view(), name='home'),
    path('hotovo/<int:order_pk>/', Finish.as_view(), name='finish'),
    path('stats/', Stats.as_view(), name='stats'),
    path('fish/', Fish_xls.as_view(), name='fish'),

    #path('test/ejaibo3c/', t_views.TestSendSMS.as_view(), name='test_send_sms'),
    #path('test/ig2jeeng/', t_views.SMSSended.as_view(), name='sms_sended'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
