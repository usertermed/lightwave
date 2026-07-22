import re

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Dweet(models.Model):
    user = models.ForeignKey(
        User, related_name="dweets", on_delete=models.CASCADE
    )
    body = models.CharField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.user} "
            f"({self.created_at:%Y-%m-%d %H:%M}): "
            f"{self.body[:30]}..."
        )


class DweetLike(models.Model):
    user = models.ForeignKey(User, related_name="likes", on_delete=models.CASCADE)
    dweet = models.ForeignKey(Dweet, related_name="likes", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "dweet")

    def __str__(self):
        return f"{self.user} likes {self.dweet.id}"


class DweetDislike(models.Model):
    user = models.ForeignKey(User, related_name="dislikes", on_delete=models.CASCADE)
    dweet = models.ForeignKey(Dweet, related_name="dislikes", on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "dweet")

    def __str__(self):
        return f"{self.user} dislikes {self.dweet.id}"


class Reply(models.Model):
    user = models.ForeignKey(User, related_name="replies", on_delete=models.CASCADE)
    dweet = models.ForeignKey(Dweet, related_name="replies", on_delete=models.CASCADE)
    body = models.CharField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return (
            f"{self.user} -> dweet {self.dweet.id} "
            f"({self.created_at:%Y-%m-%d %H:%M}): "
            f"{self.body[:30]}..."
        )


class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ("mention", "Mention"),
        ("reply", "Reply"),
        ("announcement", "Announcement"),
    ]

    user = models.ForeignKey(User, related_name="notifications", on_delete=models.CASCADE)
    actor = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name="actor_notifications",
        on_delete=models.SET_NULL,
    )
    dweet = models.ForeignKey(
        Dweet,
        null=True,
        blank=True,
        related_name="notifications",
        on_delete=models.CASCADE,
    )
    reply = models.ForeignKey(
        Reply,
        null=True,
        blank=True,
        related_name="notifications",
        on_delete=models.CASCADE,
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.CharField(max_length=180)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.notification_type} - {self.message}"


def create_notifications_for_mentions(body, actor, dweet=None, reply=None):
    usernames = set(re.findall(r"@([A-Za-z0-9_]+)", body or ""))
    notifications = []
    for username in usernames:
        try:
            mentioned_user = User.objects.get(username=username)
        except User.DoesNotExist:
            continue

        if mentioned_user == actor:
            continue

        notifications.append(
            Notification(
                user=mentioned_user,
                actor=actor,
                dweet=dweet,
                reply=reply,
                notification_type="mention",
                message=f"{actor.username} mentioned you.",
            )
        )

    if notifications:
        Notification.objects.bulk_create(notifications)


def notify_lightwave_updates(dweet):
    if dweet.user.username != "LightwaveUpdates":
        return

    recipients = User.objects.exclude(pk=dweet.user.pk)
    notifications = [
        Notification(
            user=user,
            actor=dweet.user,
            dweet=dweet,
            notification_type="announcement",
            message=f"Lightwave update: {dweet.body[:100]}",
        )
        for user in recipients
    ]
    if notifications:
        Notification.objects.bulk_create(notifications)


def create_reply_notification(reply):
    target = reply.dweet.user
    if target == reply.user:
        return

    Notification.objects.create(
        user=target,
        actor=reply.user,
        dweet=reply.dweet,
        reply=reply,
        notification_type="reply",
        message=f"{reply.user.username} replied to your post.",
    )


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=50, blank=True, default="")
    about_me = models.TextField(blank=True, default="")
    is_verified = models.BooleanField(default=False, help_text="Show a verified badge next to this profile.")
    follows = models.ManyToManyField(
        "self", related_name="followed_by", symmetrical=False, blank=True
    )

    def __str__(self):
        return self.user.username

class Extra(models.Model):
    badges= models.CharField(max_length=5, default="")
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile.objects.create(user=instance)
        if hasattr(instance, "profile"):
            try:
                user_profile.follows.add(instance.profile)
            except Exception:
                pass
        user_profile.save()


@receiver(post_save, sender=Dweet)
def handle_dweet_notifications(sender, instance, created, **kwargs):
    if not created:
        return

    create_notifications_for_mentions(instance.body, instance.user, dweet=instance)
    notify_lightwave_updates(instance)