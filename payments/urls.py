from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('upgrade/', views.upgrade_view, name='upgrade'),
    path('initiate/', views.initiate_payment, name='initiate'),
    path('callback/', views.mpesa_callback, name='callback'),
    path('status/<int:payment_id>/', views.payment_status, name='status'),
]