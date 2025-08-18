from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Variation, ReviewRating
from carts.models import CartItem, Cart
from carts.views import _getCartId
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import ReviewForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from orders.models import OrderProduct

# Create your views here.
def store(request):
    products = Product.objects.all()
    paginator = Paginator(products, 6)
    page_number = request.GET.get("page")
    product_page = paginator.get_page(page_number)
    return render(request, "store.html", {"products": product_page})


def slug(request, category_slug):
    products = Product.objects.filter(category__slug=category_slug, is_available=True)
    count = products.count()
    paginator = Paginator(products, 1)
    page_number = request.GET.get("page")
    product_page = paginator.get_page(page_number)
    return render(request, "store.html", {"products": product_page, "count": count})


# this is for product_detail page
def product_slug(request, category_slug, product_slug):
    product = get_object_or_404(Product, slug=product_slug, is_available=True)
    color_variation = Variation.objects.filter(
        product=product, variation_category="color"
    )
    size_variation = Variation.objects.filter(
        product=product, variation_category="size"
    )
    addedCheck = CartItem.objects.filter(
        cart__cart_id=_getCartId(request), product__slug=product_slug
    ).exists()
    # checking is this product added in cart or not)
    form = ReviewForm()
    order_product = OrderProduct.objects.filter(product__slug = product_slug).exists()
    review_list = ReviewRating.objects.filter(product__slug = product_slug)
    stars = range(1,6)
    return render(
        request,
        "product_detail.html",
        {
            "product": product,
            "addedCheck": addedCheck,
            "color_variation": color_variation,
            "size_variation": size_variation,
            "form": form,
            "order_product":order_product,
            'review_list':review_list,
            'stars': stars
        },
    )


def search_products(request):
    qeury = request.GET.get("q").strip()
    if qeury:
        try:
            product = Product.objects.filter(
                Q(product_name__icontains=qeury)
                | Q(category__category_name__icontains=qeury)
                | Q(description__icontains=qeury)
            ).distinct()
            paginator = Paginator(product, 6)
            page_number = request.GET.get("page")
            product_page = paginator.get_page(page_number)
            return render(request, "store.html", {"products": product_page, "q": qeury})
        except product.DoesNotExist():
            return render(request, "store.html")

    else:
        return redirect("store")

@login_required(login_url="login")
def review_rating(request, product_id):
    product = Product.objects.get(id = product_id)
    previous_url = request.META.get('HTTP_REFERER')
    if request.method == "POST":
        try:
           review = ReviewRating.objects.get(user = request.user, product = product) 
           form = ReviewForm(request.POST,instance=review)
           if form.is_valid():
               form.save()
               messages.success(request, 'Thank you! Your review has been updated ')
               return redirect(previous_url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = ReviewRating()
                review.user = request.user
                review.product = product
                review.subject = form.cleaned_data['subject']
                review.review = form.cleaned_data['review']
                review.rating = form.cleaned_data['rating']
                review.ip = request.META.get('REMOTE_ADDR')
                review.save()
                messages.success(request, 'Thank you! Your review has been created ')
                return redirect(previous_url)



            