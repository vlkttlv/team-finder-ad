from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404, redirect, render

from team_finder.service import paginate_queryset

from .forms import LoginForm, RegisterForm, UserProfileForm
from .models import User


def register_view(request):
    """Представление для регистрации нового пользователя."""
    form = RegisterForm(request.POST or None)

    if form.is_valid():
        form.save()
        return redirect("users:login")

    return render(request, "users/register.html", {"form": form})


def login_view(request):
    """Представление для входа пользователя."""
    form = LoginForm(request.POST or None)

    if form.is_valid():
        login(request, form.cleaned_data["user"])
        return redirect("projects:list")

    return render(request, "users/login.html", {"form": form})


def logout_view(request):
    """Представление для выхода пользователя."""
    logout(request)
    return redirect("projects:list")


def user_detail_view(request, user_id):
    """Представление профиля пользователя."""
    profile_user = get_object_or_404(
        User.objects.prefetch_related("owned_projects__participants"),
        pk=user_id,
    )

    return render(
        request,
        "users/user-details.html",
        {"user": profile_user},
    )


@login_required
def edit_profile_view(request):
    """Представление для редактирования профиля текущего пользователя."""
    user = request.user

    form = UserProfileForm(request.POST or None, request.FILES or None, instance=user)

    if form.is_valid():
        form.save()
        return redirect("users:detail", user_id=user.id)

    return render(
        request,
        "users/edit_profile.html",
        {"form": form, "user": user},
    )


@login_required
def change_password_view(request):
    """Представление для изменения пароля текущего пользователя."""
    form = PasswordChangeForm(user=request.user, data=request.POST or None)

    if form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        return redirect("users:detail", user_id=user.id)

    return render(
        request,
        "users/change_password.html",
        {"form": form},
    )


def participants_list_view(request):
    """Представление списка пользователей."""
    active_filter = request.GET.get("filter")
    participants = User.objects.all()

    if request.user.is_authenticated and active_filter:
        if active_filter == "owners-of-favorite-projects":
            participants = User.objects.filter(
                owned_projects__in=request.user.favorites.all()
            )

        elif active_filter == "owners-of-participating-projects":
            participants = User.objects.filter(
                owned_projects__in=request.user.participated_projects.all()
            )

        elif active_filter == "interested-in-my-projects":
            participants = User.objects.filter(
                favorites__owner=request.user
            )

        elif active_filter == "participants-of-my-projects":
            participants = User.objects.filter(
                participated_projects__owner=request.user
            )

        else:
            active_filter = None
            participants = User.objects.all()

    participants = participants.distinct().order_by("-date_joined")

    page_obj = paginate_queryset(participants, request)

    return render(
        request,
        "users/participants.html",
        {
            "participants": page_obj,
            "page_obj": page_obj,
            "active_filter": active_filter,
            "active_skill": active_filter,
        },
    )
