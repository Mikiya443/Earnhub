from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Task, TaskCompletion, Transaction, Withdrawal

@admin.register(User)
class UserAdminConfig(UserAdmin):
    list_display = ("username","email","role","status","wallet_balance","referral_code")
    fieldsets = UserAdmin.fieldsets + (("Earnhubs", {"fields": ("role","status","wallet_balance","referral_code","referred_by")}),)

admin.site.register(Task)
admin.site.register(TaskCompletion)
admin.site.register(Transaction)
admin.site.register(Withdrawal)
