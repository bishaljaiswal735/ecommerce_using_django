from django.contrib import admin
from .models import Payment, Order, OrderProduct


class PaymentAdmin(admin.ModelAdmin):
    list_display = ("user", "payment_id", "payment_method", "created_at")


class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ('payment','user','product','variation','color','size','quantity','product_price','ordered')
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "first_name",
        "phone",
        "status",
        "created_at",
        "updated_at",
        "is_ordered",
    )
    list_filter = ("status", "is_ordered")
    search_fields = ("order_number", "first_name", "last_name", "phone", "email")
    list_per_page = 20
    inlines = [OrderProductInline]


# Register your models here.
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderProduct)
