from django.urls import path
from . import views


urlpatterns = [
    path("registration/", views.registration, name="registration"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("my_orders/", views.my_orders, name="my_orders"),
    path("edit_profile/", views.edit_profile, name="edit_profile"),
    path("change_password/", views.change_password, name="change_password"),
    path("order_detail/", views.order_detail, name="order_detail"),
    path("forgetpasssword/", views.forgetpassword, name="forgetpassword"),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path(
        "resetpassword_validation/<uidb64>/<token>/",
        views.resetpassword_validation,
        name="resetpassword_validation",
    ),
]
