from django.urls import path
from django.contrib import admin
from .views import dashboard, notifications, profile, profile_list, post, shutdown, like_dweet, dislike_dweet, dweet_detail

app_name = "dwitter"

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("profile_list/", profile_list, name="profile_list"),
    path("profile/<int:pk>", profile, name="profile"),
    path("post/", post, name="post"),
    path("notifications/", notifications, name="notifications"),
    path("shutdown/", shutdown, name="shutdown"),
    path("dweet/<int:pk>/", dweet_detail, name="dweet_detail"),
    path("dweet/<int:pk>/like/", like_dweet, name="like_dweet"),
    path("dweet/<int:pk>/dislike/", dislike_dweet, name="dislike_dweet"),
]

