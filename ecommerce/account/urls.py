from django.urls import path
from . import views


urlpatterns = [
    path("registration/", views.registration, name="registration"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("dashboard/my_orders/", views.my_orders, name="my_orders"),
    path('forgetpasssword/',views.forgetpassword,name="forgetpassword"),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path("resetpassword_validation/<uidb64>/<token>/", views.resetpassword_validation, name="resetpassword_validation"),

]
