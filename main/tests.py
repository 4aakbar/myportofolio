from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Experience, Project


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
        self.assertContains(response, reverse("main:get_experience_json"))
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_experience_json(self):
        response = self.client.get(reverse("main:get_experience_json"))
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data), 1)
        fields = data[0]["fields"]
        self.assertEqual(fields["title"], self.experience.title)
        self.assertEqual(fields["category_display"], "Volunteer")
        self.assertTrue(fields["is_ongoing"])
        self.assertEqual(fields["star_count"], 0)
        self.assertFalse(fields["is_starred"])

    def test_experience_json_search(self):
        Experience.objects.create(title="Riset AI", description="Riset", category="research")

        data = self.client.get(reverse("main:get_experience_json"), {"title": "riset"}).json()

        self.assertEqual([item["fields"]["title"] for item in data], ["Riset AI"])

    def test_empty_experience_json(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:get_experience_json"))

        self.assertEqual(response.json(), [])

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        fields = self.client.get(reverse("main:get_experience_json")).json()[0]["fields"]

        self.assertFalse(self.experience.is_ongoing)
        self.assertFalse(fields["is_ongoing"])
        self.assertIsNotNone(fields["ended_at"])


class ExperienceAjaxTest(TestCase):
    def setUp(self):
        self.url = reverse("main:create_experience_ajax")
        self.valid_data = {
            "title": "Magang Backend",
            "description": "Membangun API",
            "category": "internship",
            "started_at": "2025-01-01",
        }
        self.owner = User.objects.create_superuser("owner", password="rahasia-123")
        self.user = User.objects.create_user("pengunjung", password="rahasia-123")

    def test_create_requires_owner(self):
        self.assertEqual(self.client.post(self.url, self.valid_data).status_code, 403)

        self.client.login(username="pengunjung", password="rahasia-123")
        self.assertEqual(self.client.post(self.url, self.valid_data).status_code, 403)
        self.assertFalse(Experience.objects.exists())

    def test_create_valid(self):
        self.client.login(username="owner", password="rahasia-123")
        response = self.client.post(self.url, self.valid_data)

        self.assertEqual(response.status_code, 201)
        self.assertTrue(Experience.objects.filter(pk=response.json()["pk"]).exists())

    def test_create_invalid(self):
        self.client.login(username="owner", password="rahasia-123")
        response = self.client.post(self.url, {**self.valid_data, "title": ""})

        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.json()["errors"])

    def test_create_strips_html_tags(self):
        self.client.login(username="owner", password="rahasia-123")
        xss = "<img src=\"x\" onerror=\"alert('XSS!')\">"

        rejected = self.client.post(self.url, {**self.valid_data, "title": xss})
        accepted = self.client.post(self.url, {**self.valid_data, "title": f"Magang {xss}<b>Keren</b>"})

        self.assertEqual(rejected.status_code, 400)
        self.assertEqual(accepted.status_code, 201)
        self.assertEqual(Experience.objects.get(pk=accepted.json()["pk"]).title, "Magang Keren")

    def test_toggle_star(self):
        experience = Experience.objects.create(title="Riset", description="Riset", category="research")
        star_url = reverse("main:toggle_star_experience", args=[experience.id])
        self.client.login(username="pengunjung", password="rahasia-123")

        self.client.post(star_url)
        fields = self.client.get(reverse("main:get_experience_json")).json()[0]["fields"]
        self.assertEqual(fields["star_count"], 1)
        self.assertTrue(fields["is_starred"])

        self.client.post(star_url)
        self.assertEqual(experience.starred_by.count(), 0)


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

    def test_projects_json_shows_data(self):
        fields = self.client.get(reverse("main:get_projects_json")).json()[0]["fields"]

        self.assertEqual(fields["title"], self.project.title)
        self.assertEqual(fields["description"], self.project.description)
        self.assertEqual(fields["category_display"], "AI/ML")

    def test_projects_json_with_link(self):
        self.project.link = "https://github.com/4aakbar/veto"
        self.project.save()
        fields = self.client.get(reverse("main:get_projects_json")).json()[0]["fields"]

        self.assertEqual(fields["link"], self.project.link)

    def test_empty_projects_json(self):
        Project.objects.all().delete()
        response = self.client.get(reverse("main:get_projects_json"))

        self.assertEqual(response.json(), [])
