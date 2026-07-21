from django.contrib import admin
from django.contrib.auth.models import Group, User

from .models import Dweet, Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    fields = ["display_name", "about_me", "is_verified"]


class UserAdmin(admin.ModelAdmin):
    model = User
    fields = ["username"]
    inlines = [ProfileInline]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "is_verified", "display_name")
    list_filter = ("is_verified",)
    search_fields = ("user__username", "display_name")


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
admin.site.register(Dweet)
