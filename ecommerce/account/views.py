from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Account, UserProfile
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from carts.models import Cart, CartItem
from carts.views import _getCartId
from django.contrib import messages, auth
from orders.models import Order, OrderProduct


# Create your views here.
def registration(request):
    if request.user.is_authenticated:
        return redirect("home")
    message = None
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            email = form.cleaned_data["email"]
            phone = form.cleaned_data["phone"]
            username = email.split("@")[0]
            password = form.cleaned_data["password"]
            confirm_password = form.cleaned_data["confirm_password"]
            if password != confirm_password:
                message = "Password and Confirm Password must be same"
            else:
                user = Account.objects.create_user(
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    username=username,
                    password=password,
                )
                user.phone = phone
                user.save()
                current_site = get_current_site(request)
                mail_subject = "Please activate your account"
                message = render_to_string(
                    "account_verification_email.html",
                    {
                        "user": user,
                        "domain": current_site,
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "token": default_token_generator.make_token(user),
                    },
                )
                to_email = email
                send_email = EmailMessage(mail_subject, message, to=[to_email])
                send_email.send()
                # messages.success(request,'Thank you for registering with us and we have send actiavation link to your email.')
                return redirect("/account/login/?command=verification&email=" + email)
    else:
        form = RegistrationForm()
    return render(request, "registration.html", {"form": form, "message": message})


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = auth.authenticate(request, email=email, password=password)

        if user is not None:
            try:
                # Guest cart before login
                cart = Cart.objects.get(cart_id=_getCartId(request))
                cart_items = CartItem.objects.filter(cart=cart)

                if cart_items.exists():
                    for item in cart_items:
                        # Check if same product+variation already exists in user's cart
                        existing_item = CartItem.objects.filter(
                            user=user, product=item.product
                        )

                        if existing_item.exists():
                            merged = False
                            for e_item in existing_item:
                                # Check if variations are the same
                                if set(e_item.variation.all()) == set(
                                    item.variation.all()
                                ):
                                    # Merge quantities
                                    e_item.quantity += item.quantity
                                    e_item.total_price += item.total_price
                                    e_item.save()
                                    item.delete()  # remove guest cart item
                                    merged = True
                                    break
                            if not merged:
                                item.user = user
                                item.cart = None
                                item.save()
                        else:
                            # No such product in user cart → move it
                            item.user = user
                            item.cart = None
                            item.save()
                        if not CartItem.objects.filter(cart=cart).exists():
                            cart.delete()
            except Cart.DoesNotExist:
                pass

            auth.login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid Login Credentials")

    return render(request, "login.html")


@login_required(login_url="login")
def logout_view(request):
    logout(request)
    messages.success(request, "You are looged out!")
    return redirect("login")


def activate(request, uidb64, token):
    try:
        id = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=id)
    except (user.DoesNotExist(), TypeError, ValueError, OverflowError):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "congratulation Your account is activated!!")
        return redirect("login")
    else:
        messages.error(request, "Invalid Activation Link!!")
        return redirect("registration")


@login_required(login_url="login")
def dashboard_view(request):
    orders = Order.objects.filter(user=request.user)
    orders_count = 0
    for order in orders:
        orders_count += 1
    try:
        userprofile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        userprofile = UserProfile.objects.create(user=request.user)
    return render(
        request,
        "dashboard.html",
        {"orders_count": orders_count, "userprofile": userprofile},
    )


@login_required(login_url="login")
def my_orders(request):
    orders = Order.objects.filter(user=request.user, is_ordered=True).order_by(
        "-created_at"
    )
    context = {
        "orders": orders,
    }
    return render(request, "my_orders.html", context)


@login_required(login_url="login")
def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(
            request.POST, request.FILES, instance=userprofile
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("edit_profile")
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance=userprofile)
    context = {
        "user_form": user_form,
        "profile_form": profile_form,
        "userprofile": userprofile,
    }
    return render(request, "edit_profile.html", context)


@login_required(login_url="login")
def change_password(request):
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # authenticate correctly
        user = Account.objects.get(username__exact=request.user.username)
        success = user.check_password(current_password)

        if success:
            if new_password == confirm_password:
                user.set_password(new_password)  # hashes the password
                user.save()
                messages.success(request, "Your new password was saved successfully!")
                # update session so user doesn't get logged out
                auth.update_session_auth_hash(request, user)
            else:
                messages.error(request, "New password and Confirm password must be the same.")
        else:
            messages.error(request, "Current password is incorrect!")

        return redirect("change_password")

    return render(request, "change_password.html")

@login_required(login_url='login')
def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price * i.quantity

    context = {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal,
    }
    return render(request, 'order_detail.html', context)


def forgetpassword(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if Account.objects.filter(email=email).exists():
            user = Account.objects.get(email__exact=email)
            current_site = get_current_site(request)
            mail_subject = "Reset your password"
            message = render_to_string(
                "reset_password_email.html",
                {
                    "user": user,
                    "domain": current_site,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": default_token_generator.make_token(user),
                },
            )
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()
            messages.success(
                request, "Password reset email has been sent to your email address."
            )
            return redirect("login")
        else:
            messages.error(request, "Account does not exists")
            return redirect("forgetpassword")
    else:
        return render(request, "forget.html")


def resetpassword_validation(request, uidb64, token):
    try:
        id = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk=id)
    except (Account.DoesNotExist, TypeError, ValueError, OverflowError):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")

            if password != confirm_password:
                messages.error(request, "Password and Confirm Password must be same.")
                return redirect("resetpassword_validation", uidb64=uidb64, token=token)

            user.set_password(password)
            user.save()
            messages.success(request, "Successfully reset password")
            return redirect("login")
        return render(
            request, "reset_password.html", {"uidb64": uidb64, "token": token}
        )

    else:
        if user is None:
            messages.error(request, "Invalid reset link!!")
        else:
            messages.error(request, "Link has been expired.")

        return render(
            request, "reset_password.html", {"uidb64": uidb64, "token": token}
        )
