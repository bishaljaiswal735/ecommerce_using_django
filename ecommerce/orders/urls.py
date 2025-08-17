from django.urls import path
from . import views

urlpatterns = [
    path("place_order/", views.place_order, name="order"),
    path("payment/page/", views.payment_page, name="payment"),
    path("payment/success/", views.payment_success, name="payment_success"),
    path("payment/failed/", views.payment_failed, name="payment_failed"),
    ]
