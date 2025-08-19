from django.contrib import admin
from .models import Product,Variation,ReviewRating,ProductGallery
# Register your models here.

class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('product_name',)}
    list_display = ("product_name",'slug','price','category','stock','created_date')
    inlines = [ProductGalleryInline]


class VariationAdmin(admin.ModelAdmin):
    list_display=("product","variation_category","variation_value","is_active")
    list_editable = ('is_active',)

class ReviewAdmin(admin.ModelAdmin):
    list_display=("product","user","rating","subject",'created_at','updated_at')

admin.site.register(Product, ProductAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ReviewRating, ReviewAdmin)
admin.site.register(ProductGallery)