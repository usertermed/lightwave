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