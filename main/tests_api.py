from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Project
from main.permissions import EDITOR_GROUP_NAME


class ProjectApiTest(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_superuser("owner", password="rahasia-123")
        self.editor = User.objects.create_user("editor", password="rahasia-123")
        self.editor.groups.add(Group.objects.get_or_create(name=EDITOR_GROUP_NAME)[0])
        self.visitor = User.objects.create_user("pengunjung", password="rahasia-123")

        self.project = Project.objects.create(
            title="Veto",
            description="Sistem kepatuhan logistik",
            category="ai",
        )
        self.list_url = reverse("main:project_list_api")
        self.detail_url = reverse("main:project_detail_api", args=[self.project.id])
        self.star_url = reverse("main:project_star_api", args=[self.project.id])
        self.valid_data = {
            "title": "Portofolio",
            "description": "Situs portofolio",
            "category": "web",
            "link": "https://github.com/4aakbar/myportofolio",
        }

    def test_list_is_public(self):
        self.project.starred_by.add(self.visitor)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Veto")
        self.assertEqual(response.data[0]["category_display"], "AI/ML")
        self.assertEqual(response.data[0]["star_count"], 1)
        self.assertFalse(response.data[0]["is_starred"])
        self.assertNotIn("starred_by", response.data[0])

    def test_list_search_by_title(self):
        Project.objects.create(title="Chatbot", description="Bot", category="ai")

        response = self.client.get(self.list_url, {"title": "chat"})

        self.assertEqual([project["title"] for project in response.data], ["Chatbot"])

    def test_detail(self):
        response = self.client.get(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.project.id))

    def test_detail_not_found(self):
        url = reverse("main:project_detail_api", args=["00000000-0000-0000-0000-000000000000"])

        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)

    def test_create_requires_owner(self):
        anonymous = self.client.post(self.list_url, self.valid_data, format="json")
        self.client.force_login(self.visitor)
        visitor = self.client.post(self.list_url, self.valid_data, format="json")
        self.client.force_login(self.editor)
        editor = self.client.post(self.list_url, self.valid_data, format="json")

        self.assertEqual(anonymous.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(visitor.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(editor.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Project.objects.count(), 1)

    def test_create_valid(self):
        self.client.force_login(self.owner)

        response = self.client.post(self.list_url, self.valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Project.objects.filter(pk=response.data["id"], title="Portofolio").exists())

    def test_create_invalid(self):
        self.client.force_login(self.owner)
        invalid_data = {"title": "", "description": "", "category": "tidak-ada", "link": "bukan-url"}

        response = self.client.post(self.list_url, invalid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(set(response.data), {"title", "description", "category", "link"})
        self.assertEqual(Project.objects.count(), 1)

    def test_create_strips_html_tags(self):
        self.client.force_login(self.owner)
        xss = "<img src=\"x\" onerror=\"alert('XSS!')\">"

        rejected = self.client.post(self.list_url, {**self.valid_data, "title": xss}, format="json")
        accepted = self.client.post(
            self.list_url, {**self.valid_data, "title": f"Portofolio {xss}<b>Keren</b>"}, format="json"
        )

        self.assertEqual(rejected.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(accepted.status_code, status.HTTP_201_CREATED)
        self.assertEqual(accepted.data["title"], "Portofolio Keren")

    def test_session_request_requires_csrf_token(self):
        client = APIClient(enforce_csrf_checks=True)
        client.force_login(self.owner)

        response = client.post(self.list_url, self.valid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Project.objects.count(), 1)

    def test_update_forbidden_for_visitor(self):
        anonymous = self.client.patch(self.detail_url, {"title": "Diretas"}, format="json")
        self.client.force_login(self.visitor)
        visitor = self.client.patch(self.detail_url, {"title": "Diretas"}, format="json")

        self.project.refresh_from_db()
        self.assertEqual(anonymous.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(visitor.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.project.title, "Veto")

    def test_editor_can_update_but_not_delete(self):
        self.client.force_login(self.editor)

        patched = self.client.patch(self.detail_url, {"title": "Veto v2"}, format="json")
        replaced = self.client.put(self.detail_url, self.valid_data, format="json")
        deleted = self.client.delete(self.detail_url)

        self.project.refresh_from_db()
        self.assertEqual(patched.status_code, status.HTTP_200_OK)
        self.assertEqual(patched.data["title"], "Veto v2")
        self.assertEqual(replaced.status_code, status.HTTP_200_OK)
        self.assertEqual(self.project.title, "Portofolio")
        self.assertEqual(deleted.status_code, status.HTTP_403_FORBIDDEN)

    def test_owner_can_delete(self):
        self.client.force_login(self.owner)

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Project.objects.filter(pk=self.project.pk).exists())

    def test_star_toggle(self):
        anonymous = self.client.post(self.star_url)
        self.client.force_login(self.visitor)

        starred = self.client.post(self.star_url)
        listed = self.client.get(self.list_url)
        unstarred = self.client.post(self.star_url)

        self.assertEqual(anonymous.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(starred.data, {"is_starred": True, "star_count": 1})
        self.assertTrue(listed.data[0]["is_starred"])
        self.assertEqual(unstarred.data, {"is_starred": False, "star_count": 0})
