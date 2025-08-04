from django.shortcuts import render, redirect
from store.models import Product, Variation
from .models import Cart, CartItem
from django.http import HttpResponse


# Create your views here.
def _getCartId(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    variation_list = []
    variation_source = request.GET if request.method == "GET" else request.POST
    for item in variation_source:
        if item == "color" or item == "size":
            key = item
            value = variation_source[key]
            variationObject = Variation.objects.get(
                variation_category__iexact=key,
                variation_value__iexact=value,
                product=product,
            )
            variation_list.append(variationObject)
    if request.method == "POST":
        cart = Cart.objects.get(cart_id=_getCartId(request))
        cartItemsList = CartItem.objects.filter(product=product, cart=cart)
        for item in cartItemsList:
            variation_check = list(item.variation.all())
            if set(variation_check) == set(variation_list):
                cartItem = item
                break
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

    else:
        try:
            cart = Cart.objects.get(cart_id=_getCartId(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(cart_id=_getCartId(request))
            cart.save()
        try:
            cartItem = CartItem.objects.get(product=product, cart=cart)
            variation_in_cartItem = list(cartItem.variation.all())
            if set(variation_list) == set(variation_in_cartItem):
                cartItem.quantity += 1
                cartItem.total_price += product.price
                cartItem.save()
            else:
                raise CartItem.DoesNotExist

        except CartItem.DoesNotExist:
            cartItem = CartItem.objects.create(
                product=product, quantity=1, cart=cart, total_price=product.price
            )
            cartItem.variation.set(variation_list)
            cartItem.save()

    return redirect("cart")


def cart(request):
    cart = Cart.objects.get(cart_id=_getCartId(request))
    cartItem = CartItem.objects.filter(cart=cart)
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
