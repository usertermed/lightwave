from django.contrib import admin
from django.contrib.auth.models import Group, User

from .models import Dweet, Notification, Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    fields = ["display_name", "about_me", "is_verified", "is_lightwave_super", "accent_theme"]


class UserAdmin(admin.ModelAdmin):
    model = User
    fields = ["username"]
    inlines = [ProfileInline]


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "is_verified", "is_lightwave_super", "accent_theme", "display_name")
    list_filter = ("is_verified", "is_lightwave_super", "accent_theme")
    search_fields = ("user__username", "display_name")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "notification_type", "actor", "dweet", "reply", "read", "created_at")
    list_filter = ("notification_type", "read", "created_at")
    search_fields = ("user__username", "actor__username", "message")


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.unregister(Group)
admin.site.register(Dweet)
