from django.shortcuts import render

from main.models import Experience


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
