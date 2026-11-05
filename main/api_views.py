from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from main.models import Project
from main.permissions import ProjectPermission
from main.serializers import ProjectSerializer


class ProjectListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [ProjectPermission]

    def get_queryset(self):
        projects = Project.objects.prefetch_related("starred_by").order_by("-created_at")
        title_query = self.request.query_params.get("title", "").strip()

        if title_query:
            projects = projects.filter(title__icontains=title_query)

        return projects


class ProjectDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.prefetch_related("starred_by")
    serializer_class = ProjectSerializer
    permission_classes = [ProjectPermission]


class ProjectStarAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)

        is_starred = project.starred_by.filter(pk=request.user.pk).exists()
        if is_starred:
            project.starred_by.remove(request.user)
        else:
            project.starred_by.add(request.user)

        return Response({"is_starred": not is_starred, "star_count": project.starred_by.count()})
