from django.db.models import Case, Count, F, IntegerField, Value, When
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView

from .forms import DweetForm, ProfileSettingsForm, ReplyForm
from .models import Dweet, DweetDislike, DweetLike, Profile, Reply

class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"
    
def dashboard(request):
    if not request.user.is_authenticated:
        return render(
            request,
            "dwitter/onboarding.html",
        )

    form = DweetForm(request.POST or None)
    active_view = request.GET.get("view", "following")
    if active_view not in {"following", "recommended"}:
        active_view = "following"

    if request.method == "POST":
        if form.is_valid():
            dweet = form.save(commit=False)
            dweet.user = request.user
            dweet.save()
            return redirect(f"{reverse('dwitter:dashboard')}?view={active_view}")

    followed_user_ids = list(request.user.profile.follows.values_list("user_id", flat=True))
    if active_view == "following":
        feed_dweets = Dweet.objects.filter(user_id__in=followed_user_ids).order_by("-created_at")
    else:
        feed_dweets = (
            Dweet.objects.exclude(user=request.user)
            .exclude(user_id__in=followed_user_ids)
            .annotate(
                follower_count=Count("user__profile__followed_by", distinct=True),
                like_count=Count("likes", distinct=True),
                reply_count=Count("replies", distinct=True),
                recency_score=Case(
                    When(created_at__gte=Value("2026-07-01"), then=Value(3)),
                    default=Value(1),
                    output_field=IntegerField(),
                ),
            )
            .annotate(
                score=(
                    F("follower_count") * 3
                    + F("like_count") * 2
                    + F("reply_count") * 2
                    + F("recency_score")
                )
            )
            .order_by("-score", "-created_at")
        )

    dweet_ids = feed_dweets.values_list("pk", flat=True)
    liked_ids = set(DweetLike.objects.filter(user=request.user, dweet_id__in=dweet_ids).values_list("dweet_id", flat=True))
    disliked_ids = set(DweetDislike.objects.filter(user=request.user, dweet_id__in=dweet_ids).values_list("dweet_id", flat=True))

    return render(
        request,
        "dwitter/dashboard.html",
        {
            "form": form,
            "dweets": feed_dweets,
            "liked_ids": liked_ids,
            "disliked_ids": disliked_ids,
            "active_view": active_view,
        },
    )

@login_required
def post(request):
    form = DweetForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            dweet = form.save(commit=False)
            dweet.user = request.user
            dweet.save()
            return redirect("dwitter:dashboard")
    return render(
        request,
        "dwitter/post.html",
        {"form":form},
    )

@login_required
def profile_list(request):
    profiles = Profile.objects.exclude(user=request.user)
    return render(request, "dwitter/profile_list.html", {"profiles": profiles})


@login_required
def profile(request, pk):
    profile = Profile.objects.get(pk=pk)
    settings_form = None

    if request.method == "POST":
        if request.user.profile == profile:
            settings_form = ProfileSettingsForm(request.POST, instance=profile)
            if settings_form.is_valid():
                settings_form.save()
                return redirect("dwitter:profile", pk=profile.pk)
        else:
            current_user_profile = request.user.profile
            data = request.POST
            action = data.get("follow")
            if action == "follow":
                current_user_profile.follows.add(profile)
            elif action == "unfollow":
                current_user_profile.follows.remove(profile)
            current_user_profile.save()

    if settings_form is None:
        settings_form = ProfileSettingsForm(instance=profile)

    dweet_ids = profile.user.dweets.values_list("pk", flat=True)
    liked_ids = set(DweetLike.objects.filter(user=request.user, dweet_id__in=dweet_ids).values_list("dweet_id", flat=True))
    disliked_ids = set(DweetDislike.objects.filter(user=request.user, dweet_id__in=dweet_ids).values_list("dweet_id", flat=True))

    return render(
        request,
        "dwitter/profile.html",
        {
            "profile": profile,
            "liked_ids": liked_ids,
            "disliked_ids": disliked_ids,
            "settings_form": settings_form,
        },
    )

def shutdown(request):
    return render(request, "dwitter/shutdown.html")


@login_required
def like_dweet(request, pk):
    if request.method == "POST":
        dweet = get_object_or_404(Dweet, pk=pk)
        # Remove any existing dislike first (mutually exclusive)
        DweetDislike.objects.filter(user=request.user, dweet=dweet).delete()
        # Toggle the like
        like, created = DweetLike.objects.get_or_create(user=request.user, dweet=dweet)
        if not created:
            like.delete()
    referer = request.META.get("HTTP_REFERER", "/")
    return redirect(referer)


@login_required
def dislike_dweet(request, pk):
    if request.method == "POST":
        dweet = get_object_or_404(Dweet, pk=pk)
        # Remove any existing like first (mutually exclusive)
        DweetLike.objects.filter(user=request.user, dweet=dweet).delete()
        # Toggle the dislike
        dislike, created = DweetDislike.objects.get_or_create(user=request.user, dweet=dweet)
        if not created:
            dislike.delete()
    referer = request.META.get("HTTP_REFERER", "/")
    return redirect(referer)


@login_required
def dweet_detail(request, pk):
    dweet = get_object_or_404(Dweet, pk=pk)
    replies = dweet.replies.select_related("user").order_by("created_at")
    form = ReplyForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.dweet = dweet
            reply.save()
            return redirect("dwitter:dweet_detail", pk=dweet.pk)

    user_liked = DweetLike.objects.filter(user=request.user, dweet=dweet).exists()
    user_disliked = DweetDislike.objects.filter(user=request.user, dweet=dweet).exists()

    return render(request, "dwitter/dweet_detail.html", {
        "dweet": dweet,
        "replies": replies,
        "form": form,
        "user_liked": user_liked,
        "user_disliked": user_disliked,
    })