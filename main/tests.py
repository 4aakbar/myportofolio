from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Experience, Project
from main.permissions import EDITOR_GROUP_NAME


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Staff of the Academic Division, BEM Fasilkom UI",
            description=(
                "Managed fundraising initiatives to support the faculty's "
                "competition contingent and coordinated the faculty's internal "
                "competition from planning through execution."
            ),
            category="volunteer",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(
            str(self.experience), "Staff of the Academic Division, BEM Fasilkom UI"
        )
        self.assertEqual(self.experience.category, "volunteer")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        response = self.client.get(reverse("main:show_experience"))

        # Halaman hanya berisi kerangka; data pengalaman dimuat lewat AJAX.
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, reverse("api:experience-list"))
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()

        self.assertFalse(self.experience.is_ongoing)


class ExperienceViewPermissionTest(TestCase):
    """Halaman lama Tugas 3 harus mengikuti aturan peran yang sama dengan API experience."""

    def setUp(self):
        self.experience = Experience.objects.create(
            title="Riset", description="Riset", category="research",
        )
        self.owner = User.objects.create_superuser("owner", password="rahasia-123")
        self.editor = User.objects.create_user("editor", password="rahasia-123")
        self.editor.groups.add(Group.objects.get_or_create(name=EDITOR_GROUP_NAME)[0])
        self.user = User.objects.create_user("pengunjung", password="rahasia-123")
        self.create_url = reverse("main:create_experience")
        self.update_url = reverse("main:update_experience", args=[self.experience.id])
        self.delete_url = reverse("main:delete_experience", args=[self.experience.id])

    def test_regular_user_cannot_manage(self):
        self.client.force_login(self.user)

        self.assertEqual(self.client.get(self.create_url).status_code, 403)
        self.assertEqual(self.client.get(self.update_url).status_code, 403)
        self.assertEqual(self.client.post(self.delete_url).status_code, 403)
        self.assertTrue(Experience.objects.filter(pk=self.experience.pk).exists())

    def test_editor_can_update_but_not_create_or_delete(self):
        self.client.force_login(self.editor)

        self.assertEqual(self.client.get(self.update_url).status_code, 200)
        self.assertEqual(self.client.get(self.create_url).status_code, 403)
        self.assertEqual(self.client.post(self.delete_url).status_code, 403)
        self.assertTrue(Experience.objects.filter(pk=self.experience.pk).exists())

    def test_owner_can_delete(self):
        self.client.force_login(self.owner)

        response = self.client.post(self.delete_url)

        self.assertRedirects(response, reverse("main:show_experience"))
        self.assertFalse(Experience.objects.filter(pk=self.experience.pk).exists())


class ProjectTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title="Veto",
            description=(
                "An AI-assisted logistics compliance system that integrates "
                "with ERP/WMS to automatically validate truck loads against "
                "Indonesian regulations before dispatch."
            ),
            category="ai",
        )

    def test_projects_url_is_accessible(self):
        response = self.client.get(reverse("main:show_projects"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects.html")

    def test_project_model(self):
        self.assertEqual(str(self.project), "Veto")
        self.assertEqual(self.project.category, "ai")

    def test_projects_page_uses_api(self):
        response = self.client.get(reverse("main:show_projects"))

        # Halaman hanya berisi kerangka; data proyek dimuat lewat API.
        self.assertNotContains(response, self.project.title)
        self.assertContains(response, reverse("api:project-list"))

    def test_projects_api_with_link(self):
        self.project.link = "https://github.com/4aakbar/veto"
        self.project.save()
        project = self.client.get(reverse("api:project-list")).json()[0]

        self.assertEqual(project["link"], self.project.link)

    def test_empty_projects_api(self):
        Project.objects.all().delete()
        response = self.client.get(reverse("api:project-list"))

        self.assertEqual(response.json(), [])
