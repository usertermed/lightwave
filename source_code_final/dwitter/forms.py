from django import forms

from .models import Dweet, Profile, Reply


class DweetForm(forms.ModelForm):
    body = forms.CharField(
        required=True,
        widget=forms.widgets.Textarea(
            attrs={
                "placeholder": "What's on your mind?",
                "class": "textarea is-medium",
                "rows": 3,
            }
        ),
        label="",
    )

    class Meta:
        model = Dweet
        exclude = ("user",)


class ReplyForm(forms.ModelForm):
    body = forms.CharField(
        required=True,
        widget=forms.widgets.Textarea(
            attrs={
                "placeholder": "Write a reply...",
                "class": "textarea",
                "rows": 2,
            }
        ),
        label="",
    )

    class Meta:
        model = Reply
        exclude = ("user", "dweet")


class ProfileSettingsForm(forms.ModelForm):
    display_name = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "Display name"}),
        help_text="Choose a public name that is different from your username.",
    )
    about_me = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "textarea", "rows": 3, "placeholder": "Tell people a bit about yourself"}),
        help_text="A short bio for your profile.",
    )

    class Meta:
        model = Profile
        fields = ("display_name", "about_me")

