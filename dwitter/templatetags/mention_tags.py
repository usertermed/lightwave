import html
import re

from django import template
from django.urls import reverse
from django.utils.html import format_html

from ..models import Profile

register = template.Library()


@register.filter
def render_mentions(value):
    if not value:
        return ""

    escaped_text = html.escape(value)

    def replace_mentions(match):
        username = match.group(1)
        try:
            profile = Profile.objects.get(user__username=username)
        except Profile.DoesNotExist:
            return match.group(0)

        url = reverse("dwitter:profile", kwargs={"pk": profile.pk})
        return format_html('<a href="{}" class="mention-link">@{}</a>', url, html.escape(username))

    escaped_text = re.sub(r"@([A-Za-z0-9_]+)", replace_mentions, escaped_text)

    lines = []
    in_list = False
    for line in escaped_text.splitlines():
        if line.startswith("- "):
            if not in_list:
                lines.append("<ul>")
                in_list = True
            lines.append(f"<li>{line[2:]}</li>")
        else:
            if in_list:
                lines.append("</ul>")
                in_list = False
            if line:
                lines.append(line)
            else:
                lines.append("<br>")

    if in_list:
        lines.append("</ul>")

    formatted = "<br>".join(lines)
    formatted = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", formatted)
    formatted = re.sub(r"\*(.+?)\*", r"<em>\1</em>", formatted)

    return format_html(formatted)
