from django.urls import path

from main.api_views import ProjectDetailAPIView, ProjectListCreateAPIView, ProjectStarAPIView
from main.views import (
    show_main,
    show_experience,
    show_projects,
    create_project,
    update_project,
    create_experience,
    create_experience_ajax,
    update_experience,
    delete_experience,
    toggle_star_experience,
    get_experience_json,
    register,
    login_user,
    logout_user,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("experience/add/", create_experience, name="create_experience"),
    path("experience/add-ajax/", create_experience_ajax, name="create_experience_ajax"),
    path("experience/<uuid:experience_id>/edit/", update_experience, name="update_experience"),
    path("experience/<uuid:experience_id>/delete/", delete_experience, name="delete_experience"),
    path("experience/<uuid:experience_id>/star/", toggle_star_experience, name="toggle_star_experience"),
    path("api/experience/", get_experience_json, name="get_experience_json"),
    path("projects/", show_projects, name="show_projects"),
    path("projects/add/", create_project, name="create_project"),
    path("projects/<uuid:project_id>/edit/", update_project, name="update_project"),
    path("api/projects/", ProjectListCreateAPIView.as_view(), name="project_list_api"),
    path("api/projects/<uuid:pk>/", ProjectDetailAPIView.as_view(), name="project_detail_api"),
    path("api/projects/<uuid:pk>/star/", ProjectStarAPIView.as_view(), name="project_star_api"),
    path("register/", register, name="register"),
    path("login/", login_user, name="login"),
    path("logout/", logout_user, name="logout"),
]
