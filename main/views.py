from django.contrib import messages
from django.shortcuts import redirect, render

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
    context = {
        "name": "Andy Aulia Akbar",
        "project_list": Project.objects.all(),
    }
    return render(request, "projects.html", context)


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
