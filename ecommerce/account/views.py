from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage


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
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
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

    return render(request, "dashboard.html")


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
        return render(request, "reset_password.html", {"uidb64": uidb64, "token": token})

    else:
        if user is None:
            messages.error(request, "Invalid reset link!!")
        else:
            messages.error(request, "Link has been expired.")
        
        return render(request, "reset_password.html", {"uidb64": uidb64, "token": token})