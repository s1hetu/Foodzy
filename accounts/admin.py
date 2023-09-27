from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin

from .models import User, Activation, UserAddress, Address, City, State


class AddressInlineAdmin(admin.TabularInline):
    model = User.addresses.through


class CustomUserAdmin(UserAdmin):
    inlines = (AddressInlineAdmin,)
    fieldsets = (
        (None, {"fields": ("username", "password", 'mobile_number', 'profile_pic')}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    'is_admin',
                    'is_blocked',
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )


admin.site.register(User, CustomUserAdmin)
admin.site.register(City)
admin.site.register(State)
admin.site.register(UserAddress)
admin.site.register(Address)
admin.site.register(Activation)
