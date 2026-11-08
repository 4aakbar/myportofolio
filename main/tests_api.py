import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Project
from main.permissions import EDITOR_GROUP_NAME


class ProjectAPITest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        self.visitor = User.objects.create_user(username="visitor", password="test-password")
        self.project = Project.objects.create(
            title="Veto", description="Sistem kepatuhan logistik", category="ai",
        )
        self.list_url = reverse("api:project-list")
        self.detail_url = reverse("api:project-detail", args=[self.project.id])
        self.star_url = reverse("api:project-star", args=[self.project.id])
        self.payload = {
            "title": "Portofolio",
            "description": "Situs portofolio",
            "category": "web",
            "link": "https://example.com/",
        }

    def test_public_list_and_detail(self):
        self.project.starred_by.add(self.visitor)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], str(self.project.id))
        self.assertEqual(response.data[0]["category_display"], "AI/ML")
        self.assertEqual(response.data[0]["star_count"], 1)
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("fields", response.data[0])
        self.assertNotIn("starred_by", response.data[0])
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_search_and_empty_results(self):
        response = self.client.get(self.list_url, {"title": "VET"})
        self.assertEqual(len(response.data), 1)

        response = self.client.get(self.list_url, {"title": "tidak-ada"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_missing_project(self):
        url = reverse("api:project-detail", args=[uuid.uuid4()])

        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_guest_and_visitor_cannot_write(self):
        for user in (None, self.visitor):
            self.client.force_authenticate(user=user)
            created = self.client.post(self.list_url, self.payload, format="json")
            patched = self.client.patch(self.detail_url, {"title": "Diretas"}, format="json")
            deleted = self.client.delete(self.detail_url)

            self.assertEqual(created.status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(patched.status_code, status.HTTP_403_FORBIDDEN)
            self.assertEqual(deleted.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(Project.objects.count(), 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Veto")

    def test_owner_can_create(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(self.list_url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Project.objects.filter(pk=response.data["id"], title="Portofolio").exists())

    def test_validation(self):
        self.client.force_authenticate(user=self.owner)

        for changes, field in [
            ({"title": "   "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"description": "<script></script>"}, "description"),
            ({"category": "tidak-ada"}, "category"),
            ({"link": "javascript:alert(1)"}, "link"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn(field, response.data)

        self.assertEqual(Project.objects.count(), 1)

    def test_html_tags_are_stripped(self):
        self.client.force_authenticate(user=self.owner)
        title = 'Portofolio <img src="x" onerror="alert(1)"><b>Keren</b>'

        response = self.client.post(self.list_url, {**self.payload, "title": title}, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Portofolio Keren")

    def test_patch_put_and_delete(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.patch(self.detail_url, {"title": "Veto v2"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Veto v2")
        self.assertEqual(self.project.description, "Sistem kepatuhan logistik")

        response = self.client.put(self.detail_url, {"title": "Tidak lengkap"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.content, b"")
        self.assertFalse(Project.objects.filter(pk=self.project.id).exists())

    def test_star_requires_login_and_toggles(self):
        self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.project.starred_by.count(), 0)

        self.client.force_authenticate(user=self.visitor)
        response = self.client.post(self.star_url)
        self.assertTrue(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 1)

        response = self.client.post(self.star_url)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["star_count"], 0)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "is_starred": True,
            "category_display": "Palsu", "starred_by": [self.visitor.id],
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertEqual(response.data["category_display"], "Web Application")

    def test_staff_and_editor_cannot_manage_tutorial_projects(self):
        self.visitor.is_staff = True
        self.visitor.save()
        # Grup Editor sudah dibuat oleh data migration Tugas 4, jadi cukup diambil.
        self.visitor.groups.add(Group.objects.get_or_create(name=EDITOR_GROUP_NAME)[0])
        self.client.force_authenticate(user=self.visitor)

        patched = self.client.patch(self.detail_url, {"title": "Diretas"}, format="json")
        created = self.client.post(self.list_url, self.payload, format="json")
        deleted = self.client.delete(self.detail_url)

        self.assertEqual(patched.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(created.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(deleted.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Project.objects.count(), 1)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Veto")

    def test_wrong_method(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.delete(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_session_write_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))

        response = client.post(self.list_url, self.payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Project.objects.count(), 1)

    def test_session_write_with_csrf_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))
        # Browsable API merender form dengan token CSRF asli sehingga cookie csrftoken terbentuk.
        page = client.get(self.list_url, HTTP_ACCEPT="text/html")
        self.assertEqual(page.status_code, status.HTTP_200_OK)
        token = client.cookies["csrftoken"].value

        response = client.post(self.list_url, self.payload, format="json", HTTP_X_CSRFTOKEN=token)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
