from django.shortcuts import render, redirect
from store.models import Product, Variation
from .models import Cart, CartItem
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from orders.forms import OrderForm


# Create your views here.
def _getCartId(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    variation_list = []

    # Collect variations from GET or POST
    variation_source = request.GET if request.method == "GET" else request.POST
    for key in ["color", "size"]:
        if key in variation_source:
            value = variation_source[key]
            try:
                variation_obj = Variation.objects.get(
                    variation_category__iexact=key,
                    variation_value__iexact=value,
                    product=product,
                )
                variation_list.append(variation_obj)
            except Variation.DoesNotExist:
                pass

    # Ensure cart exists
    if request.user.is_authenticated:
        cart = None
        cart_items_list = CartItem.objects.filter(user=request.user, product=product)
    else:
        cart_id = _getCartId(request)  # make sure this never returns None
        cart, created = Cart.objects.get_or_create(cart_id=cart_id)
        cart_items_list = CartItem.objects.filter(product=product, cart=cart)

    # Check if the same variation exists
    cart_item = None
    for item in cart_items_list:
        if set(item.variation.all()) == set(variation_list):
            cart_item = item
            break

    # Handle POST request
    if request.method == "POST":
        if cart_item:  # Existing item
            if request.POST.get("remove"):
                cart_item.delete()
            else:
                action = request.POST.get("action")
                quantity_input = int(request.POST.get("quantity", 1))

                if action == "increase":
                    cart_item.quantity += 1
                elif action == "decrease":
                    cart_item.quantity = max(1, cart_item.quantity - 1)
                elif "quantity" in request.POST:
                    cart_item.quantity = quantity_input

                cart_item.total_price = cart_item.quantity * product.price
                cart_item.save()
        else:  # Create new CartItem
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                total_price=product.price,
                user=request.user if request.user.is_authenticated else None,
                cart=cart if not request.user.is_authenticated else None,
            )
            if variation_list:
                cart_item.variation.set(variation_list)
            cart_item.save()

    # Handle GET request (or increment quantity if not POST)
    else:
        if cart_item:
            cart_item.quantity += 1
            cart_item.total_price = cart_item.quantity * product.price
            cart_item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product,
                quantity=1,
                total_price=product.price,
                user=request.user if request.user.is_authenticated else None,
                cart=cart if not request.user.is_authenticated else None,
            )
            if variation_list:
                cart_item.variation.set(variation_list)
            cart_item.save()

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
    form = OrderForm()
    return render(
        request,
        "checkout.html",
        {
            "cartItem": cartItem,
            "total": total,
            "quantity": quantity,
            "tax": tax,
            "grand_total": grand_total,
            "form": form,
        },
    )
