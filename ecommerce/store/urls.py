from django.urls import path
from . import views


urlpatterns = [
    path('',views.store, name= 'store'),
    path("search/", views.search_products , name = "search"),
    path('<slug:category_slug>/', views.slug, name ="category_detail"),
    path('<slug:category_slug>/<slug:product_slug>/', views.product_slug, name="product_detail")
] 