from django.shortcuts import render, redirect
from store.models import Product, Variation
from .models import Cart, CartItem
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


# Create your views here.
def _getCartId(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    variation_list = []

    # Collect variations
    variation_source = request.GET if request.method == "GET" else request.POST
    for item in variation_source:
        if item in ["color", "size"]:
            key = item
            value = variation_source[key]
            try:
                variationObject = Variation.objects.get(
                    variation_category__iexact=key,
                    variation_value__iexact=value,
                    product=product,
                )
                variation_list.append(variationObject)
            except Variation.DoesNotExist:
                pass

    # Ensure cart exists
    if request.user.is_authenticated:
        cart = None
        cartItemsList = CartItem.objects.filter(user=request.user, product=product)
    else:
        cart, _ = Cart.objects.get_or_create(cart_id=_getCartId(request))
        cartItemsList = CartItem.objects.filter(product=product, cart=cart)

    # Try to find existing item with same variations
    cartItem = None
    for item in cartItemsList:
        if set(item.variation.all()) == set(variation_list):
            cartItem = item
            break

    # If request is POST, handle actions
    if request.method == "POST":
        if cartItem:  # Item exists
            if request.POST.get("remove"):
                cartItem.delete()
            else:
                action = request.POST.get("action")
                quantity_input = int(request.POST.get("quantity", 1))
                if action == "increase":
                    cartItem.quantity += 1
                elif action == "decrease":
                    cartItem.quantity = max(1, cartItem.quantity - 1)
                elif "quantity" in request.POST:
                    cartItem.quantity = quantity_input

                cartItem.total_price = cartItem.quantity * product.price
                cartItem.save()
        else:  # No existing item → create new
            cartItem = CartItem.objects.create(
                product=product,
                quantity=1,
                total_price=product.price,
                user=request.user if request.user.is_authenticated else None,
                cart=None if request.user.is_authenticated else cart,
            )
            if variation_list:
                cartItem.variation.set(variation_list)
            cartItem.save()
    else:
        # GET request → add new if not already exists
        if cartItem:
            cartItem.quantity += 1
            cartItem.total_price = cartItem.quantity * product.price
            cartItem.save()
        else:
            cartItem = CartItem.objects.create(
                product=product,
                quantity=1,
                total_price=product.price,
                user=request.user if request.user.is_authenticated else None,
                cart=None if request.user.is_authenticated else cart,
            )
            if variation_list:
                cartItem.variation.set(variation_list)
            cartItem.save()

    return redirect("cart")


def cart(request):
    if request.user.is_authenticated:
        cartItem = CartItem.objects.filter(user=request.user, is_active=True)
    else:
        try:
            cart = Cart.objects.get(cart_id=_getCartId(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_getCartId(request))
            cart.save()
        cartItem = CartItem.objects.filter(cart=cart, is_active=True)
    total = 0
    quantity = 0
    for item in cartItem:
        quantity += item.quantity
        total += item.total_price
    tax = total * 0.13
    grand_total = tax + total
    return render(
        request,
        "cart.html",
        {
            "cartItem": cartItem,
            "total": total,
            "quantity": quantity,
            "tax": tax,
            "grand_total": grand_total,
        },
    )


@login_required(login_url="login")
def checkout(request):
    cartItem = CartItem.objects.filter(user=request.user, is_active=True)
    total = 0
    quantity = 0
    for item in cartItem:
        quantity += item.quantity
        total += item.total_price
    tax = total * 0.13
    grand_total = tax + total
    return render(
        request,
        "checkout.html",
        {
            "cartItem": cartItem,
            "total": total,
            "quantity": quantity,
            "tax": tax,
            "grand_total": grand_total,
        },
    )
