from django.contrib import admin
from .models import Payment, Order, OrderProduct


class PaymentAdmin(admin.ModelAdmin):
    list_display = ("user", "payment_id", "payment_method", "created_at")


class OrderAdmin(admin.ModelAdmin):
    list_display = ("first_name", "status", "created_at", "updated_at")


class OrderProductAdmin(admin.ModelAdmin):
    list_display = ("user", "order", "product")


# Register your models here.
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct, OrderProductAdmin)
