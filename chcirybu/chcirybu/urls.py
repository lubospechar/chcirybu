from django.contrib import admin
from django.urls import path
from orders.views import Home, Finish
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', Home.as_view(), name='home'),
    path('hotovo/<int:order_pk>/', Finish.as_view(), name='finish'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
