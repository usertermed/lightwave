import re

from django import template
from django.urls import reverse

from ..models import Profile

register = template.Library()


@register.filter
def render_mentions(value):
    if not value:
        return ""

    def replace(match):
        username = match.group(1)
        try:
            profile = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            return match.group(0)

        url = reverse("dwitter:profile", kwargs={"pk": profile.pk})
        return f'<a href="{url}" class="mention-link">@{username}</a>'

    return re.sub(r"@([A-Za-z0-9_]+)", replace, value)
