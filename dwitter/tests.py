from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Dweet, Profile


class DashboardFeedTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="viewer", password="secret123")
        self.followed_user = User.objects.create_user(username="followed", password="secret123")
        self.recommended_user = User.objects.create_user(username="recommended", password="secret123")

        self.user.profile.follows.add(self.followed_user.profile)
        self.user.profile.save()

        self.followed_dweet = Dweet.objects.create(user=self.followed_user, body="Followed post")
        self.recommended_dweet = Dweet.objects.create(user=self.recommended_user, body="Recommended post")

    def test_recommended_view_shows_non_followed_posts(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("dwitter:dashboard"), {"view": "recommended"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recommended post")
        self.assertNotContains(response, "Followed post")


class ProfileCustomizationTests(TestCase):
    def test_profile_settings_update(self):
        user = User.objects.create_user(username="profileuser", password="secret123")
        self.client.force_login(user)

        response = self.client.post(
            reverse("dwitter:profile", kwargs={"pk": user.profile.pk}),
            {"display_name": "Ada Lovelace", "about_me": "Maker of things"},
        )

        self.assertEqual(response.status_code, 302)
        profile = Profile.objects.get(pk=user.profile.pk)
        self.assertEqual(profile.display_name, "Ada Lovelace")
        self.assertEqual(profile.about_me, "Maker of things")

    def test_verified_flag_defaults_to_false_and_can_be_toggled(self):
        user = User.objects.create_user(username="verifieduser", password="secret123")

        profile = Profile.objects.get(pk=user.profile.pk)
        self.assertFalse(profile.is_verified)

        profile.is_verified = True
        profile.save()

        refreshed_profile = Profile.objects.get(pk=user.profile.pk)
        self.assertTrue(refreshed_profile.is_verified)

    def test_mentions_render_as_profile_links(self):
        mentioned_user = User.objects.create_user(username="test_user1", password="secret123")
        self.client.force_login(User.objects.create_user(username="poster", password="secret123"))

        response = self.client.post(
            reverse("dwitter:dashboard"),
            {"body": "Hello @test_user1"},
        )

        self.assertEqual(response.status_code, 302)
        dashboard_response = self.client.get(reverse("dwitter:dashboard"))
        self.assertContains(dashboard_response, f'href="/profile/{mentioned_user.profile.pk}"')
        self.assertContains(dashboard_response, "@test_user1")


class SuperProgramAndFeedTests(TestCase):
    def test_non_super_user_does_not_see_new_feed_and_editor_controls(self):
        user = User.objects.create_user(username="basicuser", password="secret123")
        self.client.force_login(user)

        response = self.client.get(reverse("dwitter:dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "?view=new")
        self.assertNotContains(response, "Bold with")

    def test_new_view_shows_all_posts_across_the_network(self):
        user = User.objects.create_user(username="superviewer", password="secret123")
        user.profile.is_lightwave_super = True
        user.profile.save()
        followed_user = User.objects.create_user(username="followed_user", password="secret123")
        other_user = User.objects.create_user(username="other_user", password="secret123")
        user.profile.follows.add(followed_user.profile)
        user.profile.save()

        Dweet.objects.create(user=followed_user, body="Followed post")
        Dweet.objects.create(user=other_user, body="Global post")

        self.client.force_login(user)
        response = self.client.get(reverse("dwitter:dashboard"), {"view": "new"})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Global post")
        self.assertContains(response, "Followed post")

    def test_theme_preference_is_saved_on_profile(self):
        user = User.objects.create_user(username="themer", password="secret123")
        user.profile.is_lightwave_super = True
        user.profile.save()
        self.client.force_login(user)

        response = self.client.post(
            reverse("dwitter:profile", kwargs={"pk": user.profile.pk}),
            {"display_name": "Theme Tester", "about_me": "Hello", "accent_theme": "cyan"},
        )

        self.assertEqual(response.status_code, 302)
        refreshed_profile = Profile.objects.get(pk=user.profile.pk)
        self.assertEqual(refreshed_profile.accent_theme, "cyan")
