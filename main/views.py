import datetime

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from main.forms import ExperienceForm, ProjectForm
from main.models import Experience, Project
from main.permissions import can_create_or_delete, can_update


def show_main(request):
    last_login = request.COOKIES.get('last_login', 'Belum ada sesi login / Cookie tidak ditemukan')
    context = {
        "name": "Andy Aulia Akbar",
        "npm": "2506613590",
        "study_program": "S1 Sistem Informasi",
        "bio": (
            "Information Systems student at Universitas Indonesia with experience "
            "in product ideation, project management, digital marketing, and "
            "cross-functional collaboration."
        ),
        "last_login": last_login,
    }
    return render(request, "index.html", context)

def register(request):
    form = UserCreationForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": "Akbar",
        "form": form,
    }
    return render(request, "register.html", context)

def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect("main:show_main")
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return response

    context = {
        "name": "Akbar",
        "form": form,
    }
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie('last_login')
    return response


def show_experience(request):
    # Daftar pengalaman dimuat lewat AJAX dari api:experience-list; view ini cukup mengirim kerangka halaman.
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Andy Aulia Akbar",
        "title_query": title_query,
        "form": ExperienceForm(),
        # auto_id berbeda supaya id input modal edit tidak bentrok dengan modal tambah.
        "edit_form": ExperienceForm(auto_id="edit_%s"),
        "can_create_or_delete": can_create_or_delete(request.user),
        "can_update": can_update(request.user),
    }
    return render(request, "experience.html", context)

def show_projects(request):
    # Daftar proyek dimuat lewat AJAX dari api:project-list; view ini cukup mengirim kerangka halaman.
    title_query = request.GET.get("title", "").strip()

    context = {
        "name": "Andy Aulia Akbar",
        "title_query": title_query,
        "form": ProjectForm(),
        "can_create_or_delete": can_create_or_delete(request.user),
        # Projects hanya dikelola pemilik, sama seperti IsPortfolioOwnerOrReadOnly di API.
        "can_update": can_create_or_delete(request.user),
    }
    return render(request, "projects.html", context)

####################################################################
#   projects crud

@login_required(login_url="/login/")
def create_project(request):
    if not can_create_or_delete(request.user):
        raise PermissionDenied

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


@login_required(login_url="/login/")
def update_project(request, project_id):
    if not can_create_or_delete(request.user):
        raise PermissionDenied

    project = get_object_or_404(Project, pk=project_id)
    form = ProjectForm(request.POST or None, instance=project)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek berhasil diperbarui!")
        return redirect("main:show_projects")

    context = {
        "name": "Andy Aulia Akbar",
        "form": form,
        "project": project,
    }
    return render(request, "projects_form.html", context)

####################################################################

####################################################################
# Experience Crud

@login_required(login_url="/login/")
def create_experience(request):
    if not can_create_or_delete(request.user):
        raise PermissionDenied

    form = ExperienceForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pengalaman baru berhasil ditambahkan!")
        return redirect("main:show_experience")

    context = {
        "name": "Andy Aulia Akbar",
        "form": form,
    }
    return render(request, "experience_form.html", context)


@login_required(login_url="/login/")
def update_experience(request, experience_id):
    if not can_update(request.user):
        raise PermissionDenied

    experience = get_object_or_404(Experience, pk=experience_id)
    form = ExperienceForm(request.POST or None, instance=experience)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pengalaman berhasil diperbarui!")
        return redirect("main:show_experience")

    context = {
        "name": "Andy Aulia Akbar",
        "form": form,
        "experience": experience,
    }
    return render(request, "experience_form.html", context)


@login_required(login_url="/login/")
def delete_experience(request, experience_id):
    if not can_create_or_delete(request.user):
        raise PermissionDenied

    experience = get_object_or_404(Experience, pk=experience_id)

    if request.method == "POST":
        experience.delete()
        messages.success(request, "Pengalaman berhasil dihapus!")
        return redirect("main:show_experience")

    return redirect("main:show_experience")

####################################################################