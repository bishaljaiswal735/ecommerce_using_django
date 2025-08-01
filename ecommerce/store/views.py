from django.shortcuts import render, get_object_or_404
from .models import Product


# Create your views here.
def store(request):
    products = Product.objects.all()
    return render(request, "store.html", {"products": products})


def slug(request, category_slug):
    products = Product.objects.filter(category__slug=category_slug, is_available=True)
    count = products.count()
    return render(request, "store.html", {"products": products, "count": count})

#this is for product_detail page
def product_slug(request,category_slug, product_slug):
    product = get_object_or_404(Product, slug=product_slug, is_available=True)
    return render(request, "product_detail.html", {"product": product})
