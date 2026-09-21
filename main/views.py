from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from main.forms import ProjectForm
from main.models import Experience, Project


def show_main(request):
    context = {
        "name": "Andy Aulia Akbar",
        "npm": "2506613590",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "Information Systems student at Universitas Indonesia with experience "
            "in product ideation, project management, digital marketing, and "
            "cross-functional collaboration."
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Andy Aulia Akbar",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)

def show_projects(request):
    json_response = get_projects_json(request)

    projects = serializers.deserialize(
        "json",
        json_response.content.decode("utf-8"),
    )
    projects = [project.object for project in projects]
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Andy Aulia Akbar",
        "project_list": projects,
        "title_query": title_query,
    }
    return render(request, "projects.html", context)

####################################################################
#   projects crud (no updates yet)   

def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()

    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize("json", projects)
    return HttpResponse(projects_json, content_type="application/json")

def create_project(request):
    form = ProjectForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_projects")

    context = {
        "name": "Andy Aulia Akbar",
        "form": form,
    }
    return render(request, "projects_form.html", context)


def delete_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        project.delete()
        messages.success(request, "Project berhasil dihapus!")
        return redirect("main:show_projects")

    return redirect("main:show_projects")

####################################################################

####################################################################
# Experience Crud



####################################################################