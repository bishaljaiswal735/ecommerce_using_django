from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from carts.models import CartItem
from .models import Order, OrderProduct, Payment
from .forms import OrderForm
from django.contrib import messages
from django.urls import reverse
import datetime
import hmac
import hashlib
import base64, json

# Create your views here


def generate_esewa_signature(data, secret):
    # data is dict in correct order
    message = ",".join([f"{k}={data[k]}" for k in data.keys()])
    hmac_sha256 = hmac.new(
        secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256
    )
    digest = hmac_sha256.digest()
    signature = base64.b64encode(digest).decode("utf-8")
    return signature


@login_required(login_url="login")
def payment_page(request):
    return redirect("checkout")


@login_required(login_url="login")
def payment_success(request):
    # First, try to get Base64-encoded data
    encoded_data = request.GET.get("data")

    if encoded_data:
        try:
            decoded_bytes = base64.b64decode(encoded_data)
            decoded_str = decoded_bytes.decode("utf-8")
            data = json.loads(decoded_str)
            transaction_uuid = data.get("transaction_uuid")
            status = data.get("status")
            amount = data.get("total_amount")
            ref_id = data.get("transaction_code") or data.get("refId")
        except Exception:
            messages.error(request, "Error decoding payment data.")
            return redirect("store")
    else:
        # Fallback: check if eSewa sent normal GET params
        transaction_uuid = request.GET.get("transaction_uuid")
        ref_id = request.GET.get("refId")
        amount = request.GET.get("amount")
        status = "COMPLETE" if transaction_uuid and ref_id and amount else None

    if not transaction_uuid or not ref_id or not amount:
        messages.error(request, "Invalid payment access.")
        return redirect("store")

    if status == "COMPLETE":
        # Save payment to DB (if not already saved)
        payment, created = Payment.objects.get_or_create(
            payment_id=ref_id,
            defaults={
                "user": request.user,
                "payment_method": "eSewa",
                "amount_paid": amount,
            },
        )
        return render(
            request,
            "payment_success.html",
            {"payment": payment, "order_number": transaction_uuid},
        )
    else:
        # Redirect to failed page
        return redirect(f"/payment/failed/?transaction_uuid={transaction_uuid}")


@login_required(login_url="login")
def payment_failed(request):
    transaction_uuid = request.GET.get("transaction_uuid")
    if not transaction_uuid:
        messages.error(request, "Invalid payment access.")
        return redirect("store")
    return render(request, "payment_failed.html", {"order_number": transaction_uuid})


@login_required(login_url="login")
def place_order(request):
    current_user = request.user
    cart_item = CartItem.objects.filter(user=current_user)
    # This is for checking any item is in or not in cart
    cart_item_count = cart_item.count()
    if cart_item_count <= 0:
        return redirect("store")
    # this is for grandtotal to add in order model
    total = 0
    quantity = 0
    for item in cart_item:
        quantity += item.quantity
        total += item.total_price
    tax = total * 0.13
    grand_total = tax + total
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()  # creating object of model order
            data.first_name = form.cleaned_data["first_name"]
            data.last_name = form.cleaned_data["last_name"]
            data.email = form.cleaned_data["email"]
            data.phone = form.cleaned_data["phone"]
            data.address_line_1 = form.cleaned_data["address_line_1"]
            data.address_line_2 = form.cleaned_data["address_line_2"]
            data.city = form.cleaned_data["city"]
            data.state = form.cleaned_data["state"]
            data.country = form.cleaned_data["country"]
            data.order_note = form.cleaned_data["order_note"]
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get("REMOTE_ADDR")
            data.save()
            # creating ordernumber from datestring
            yr = int(datetime.date.today().strftime("%Y"))
            dt = int(datetime.date.today().strftime("%d"))
            mt = int(datetime.date.today().strftime("%m"))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            data.order_number = current_date + str(data.id)
            data.save()

            # for creating signature
            fields = {
                "total_amount": data.order_total,
                "transaction_uuid": data.order_number,
                "product_code": "EPAYTEST",
            }

            secret = "8gBm/:&EnhH.1/q"  # sandbox secret
            signature = generate_esewa_signature(fields, secret)
            return render(
                request,
                "payment.html",
                {
                    "order": data,
                    "cart_items": cart_item,
                    "total": total,
                    "tax": tax,
                    "grand_total": grand_total,
                    "signature": signature,
                },
            )

        else:
            return redirect("checkout")
