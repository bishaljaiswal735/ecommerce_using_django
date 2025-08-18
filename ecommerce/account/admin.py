from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account,UserProfile
# Register your models here.

admin.site.register(Account)
admin.site.register(UserProfile)