from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProjectForm
from .models import Project


def project_list_view(request):
    """Представление списка всех проектов с пагинацией"""
    projects = (
        Project.objects.select_related("owner")
        .prefetch_related("participants")
        .order_by("-created_at")
    )

    paginator = Paginator(projects, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "projects/project_list.html",
        {"projects": page_obj, "page_obj": page_obj},
    )


def project_detail_view(request, project_id):
    """Представление детальной информации о проекте"""
    project = get_object_or_404(
        Project.objects.select_related("owner").prefetch_related("participants"),
        pk=project_id,
    )
    
    participants = list(project.participants.all())
    if all(member.id != project.owner_id for member in participants):
        participants.append(project.owner)

    return render(
        request,
        "projects/project-details.html",
        {
            "project": project,
            "project_participants": participants,
            "participants_count": len(participants),
        },
    )


@login_required
def project_create_view(request):
    """Представление для создания нового проекта"""
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            project.participants.add(request.user)
            return redirect("projects:detail", project_id=project.id)
    else:
        form = ProjectForm()
    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": False},
    )


@login_required
def project_edit_view(request, project_id):
    """Представление для редактирования существующего проекта"""
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id:
        return HttpResponseForbidden("Only owner can edit this project")

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect("projects:detail", project_id=project.id)
    else:
        form = ProjectForm(instance=project)

    return render(
        request,
        "projects/create-project.html",
        {"form": form, "is_edit": True, "project": project},
    )


@login_required
@require_POST
def project_complete_view(request, project_id):
    """Представление для закрытия проекта владельцем"""
    project = get_object_or_404(Project, pk=project_id)
    if project.owner_id != request.user.id or project.status != "open":
        return JsonResponse({"status": "error"}, status=403)
    project.status = "closed"
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": "closed"})


@login_required
@require_POST
def toggle_participate_view(request, project_id):
    """Представление для присоединения/отписки пользователя к проекту"""
    project = get_object_or_404(Project, pk=project_id)
    user = request.user
    if project.owner_id == user.id:
        return JsonResponse({"status": "error"}, status=400)
    if project.status == "closed":
        return JsonResponse({"status": "error"}, status=400)

    if project.participants.filter(pk=user.id).exists():
        project.participants.remove(user)
        participant = False
    else:
        project.participants.add(user)
        participant = True

    return JsonResponse({"status": "ok", "participant": participant})


@login_required
@require_POST
def toggle_favorite_view(request, project_id):
    """Представление для добавления/удаления проекта из избранного пользователя"""
    project = get_object_or_404(Project, pk=project_id)
    user = request.user

    if user.favorites.filter(pk=project.id).exists():
        user.favorites.remove(project)
        favorited = False
    else:
        user.favorites.add(project)
        favorited = True

    return JsonResponse({"status": "ok", "favorited": favorited})


@login_required
def favorites_list_view(request):
    """Представление списка проектов, добавленных пользователем в избранное"""
    projects = (
        request.user.favorites.select_related("owner")
        .prefetch_related("participants")
        .all()
    )
    return render(request, "projects/favorite_projects.html", {"projects": projects})
