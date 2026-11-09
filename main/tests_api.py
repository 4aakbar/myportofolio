import uuid

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from main.models import Experience, Project
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



class ExperienceAPITest(APITestCase):
    """API Experience (Tugas 6): empat peran, validasi, star, dan CSRF."""

    def setUp(self):
        self.owner = User.objects.create_superuser(
            username="owner", password="test-password", email="owner@example.com",
        )
        self.editor = User.objects.create_user(username="editor", password="test-password")
        # Database test selalu kosong kecuali data migration; get_or_create aman untuk keduanya.
        self.editor.groups.add(Group.objects.get_or_create(name=EDITOR_GROUP_NAME)[0])
        self.user = User.objects.create_user(
            username="user", password="test-password", email="user@example.com",
        )
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membimbing tutorial Django",
            category="part-time",
            started_at="2026-01-01T00:00:00Z",
        )
        self.list_url = reverse("api:experience-list")
        self.detail_url = reverse("api:experience-detail", args=[self.experience.id])
        self.star_url = reverse("api:experience-star", args=[self.experience.id])
        self.payload = {
            "title": "Magang Backend",
            "description": "Membangun REST API",
            "category": "internship",
            "thumbnail": "",
            "started_at": "2025-06-01",
            "ended_at": "2025-08-31",
        }

    def assertExperienceUnchanged(self):
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Asisten Dosen PBP")
        self.assertEqual(self.experience.description, "Membimbing tutorial Django")

    # ---------- Membaca (semua pengunjung) ----------

    def test_public_list_and_detail(self):
        self.experience.starred_by.add(self.user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item = response.data[0]
        self.assertEqual(item["id"], str(self.experience.id))
        self.assertEqual(item["category_display"], "Part-Time")
        self.assertTrue(item["is_ongoing"])
        self.assertEqual(item["star_count"], 1)
        self.assertFalse(item["is_starred"])
        self.assertEqual(self.client.get(self.detail_url).status_code, status.HTTP_200_OK)

    def test_sensitive_account_data_not_exposed(self):
        self.experience.starred_by.add(self.user)

        item = self.client.get(self.detail_url).data
        body = self.client.get(self.list_url).content.decode()

        self.assertNotIn("starred_by", item)
        self.assertNotIn("user@example.com", body)
        self.assertNotIn("pbkdf2", body)

    def test_search_by_query_param_and_empty_result(self):
        Experience.objects.create(title="Riset AI", description="Riset", category="research")

        response = self.client.get(self.list_url, {"title": "RISET"})
        self.assertEqual([item["title"] for item in response.data], ["Riset AI"])

        response = self.client.get(self.list_url, {"title": "tidak-ada"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])

    def test_missing_experience_returns_404(self):
        url = reverse("api:experience-detail", args=[uuid.uuid4()])
        star_url = reverse("api:experience-star", args=[uuid.uuid4()])

        self.assertEqual(self.client.get(url).status_code, status.HTTP_404_NOT_FOUND)
        self.client.force_authenticate(user=self.owner)
        self.assertEqual(self.client.delete(url).status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.post(star_url).status_code, status.HTTP_404_NOT_FOUND)

    # ---------- Hak akses empat peran ----------

    def test_visitor_and_regular_user_cannot_write(self):
        for account in (None, self.user):
            self.client.force_authenticate(user=account)

            created = self.client.post(self.list_url, self.payload, format="json")
            patched = self.client.patch(self.detail_url, {"title": "Diretas"}, format="json")
            replaced = self.client.put(self.detail_url, self.payload, format="json")
            deleted = self.client.delete(self.detail_url)

            for response in (created, patched, replaced, deleted):
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Pastikan database benar-benar tidak berubah, bukan hanya status HTTP-nya.
        self.assertEqual(Experience.objects.count(), 1)
        self.assertExperienceUnchanged()

    def test_editor_can_patch_and_put(self):
        self.client.force_authenticate(user=self.editor)

        patched = self.client.patch(self.detail_url, {"title": "Asdos PBP"}, format="json")
        self.assertEqual(patched.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Asdos PBP")
        # PATCH tidak mengubah field yang tidak dikirim.
        self.assertEqual(self.experience.description, "Membimbing tutorial Django")

        replaced = self.client.put(self.detail_url, self.payload, format="json")
        self.assertEqual(replaced.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Magang Backend")

    def test_editor_cannot_create_or_delete(self):
        self.client.force_authenticate(user=self.editor)

        created = self.client.post(self.list_url, self.payload, format="json")
        deleted = self.client.delete(self.detail_url)

        self.assertEqual(created.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(deleted.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Experience.objects.count(), 1)
        self.assertTrue(Experience.objects.filter(pk=self.experience.pk).exists())

    def test_owner_can_create_update_and_delete(self):
        self.client.force_authenticate(user=self.owner)

        created = self.client.post(self.list_url, self.payload, format="json")
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Experience.objects.filter(pk=created.data["id"], title="Magang Backend").exists())

        patched = self.client.patch(self.detail_url, {"ended_at": "2026-06-30"}, format="json")
        self.assertEqual(patched.status_code, status.HTTP_200_OK)
        self.assertFalse(patched.data["is_ongoing"])

        deleted = self.client.delete(self.detail_url)
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(deleted.content, b"")
        self.assertFalse(Experience.objects.filter(pk=self.experience.pk).exists())

    def test_wrong_method_returns_405(self):
        self.client.force_authenticate(user=self.owner)

        self.assertEqual(self.client.delete(self.list_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(self.client.get(self.star_url).status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # ---------- Validasi input ----------

    def test_invalid_input_returns_400(self):
        self.client.force_authenticate(user=self.owner)

        for changes, field in [
            ({"title": "   "}, "title"),
            ({"title": '<img src="x" onerror="alert(1)">'}, "title"),
            ({"description": "<script></script>"}, "description"),
            ({"category": "tidak-ada"}, "category"),
            ({"thumbnail": "javascript:alert(1)"}, "thumbnail"),
            ({"started_at": "bukan-tanggal"}, "started_at"),
            ({"ended_at": "2025-01-01"}, "ended_at"),
        ]:
            response = self.client.post(self.list_url, {**self.payload, **changes}, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, field)
            self.assertIn(field, response.data)

        self.assertEqual(Experience.objects.count(), 1)

    def test_html_tags_are_stripped(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(self.list_url, {
            **self.payload,
            "title": 'Magang <img src="x" onerror="alert(1)"><b>Backend</b>',
            "description": "<script>alert(1)</script>Membangun API",
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        experience = Experience.objects.get(pk=response.data["id"])
        self.assertEqual(experience.title, "Magang Backend")
        self.assertEqual(experience.description, "alert(1)Membangun API")

    def test_patch_date_range_uses_saved_start_date(self):
        # started_at tidak dikirim, jadi validasi harus membandingkan dengan nilai di database.
        self.client.force_authenticate(user=self.editor)

        response = self.client.patch(self.detail_url, {"ended_at": "2025-12-31"}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("ended_at", response.data)
        self.experience.refresh_from_db()
        self.assertIsNone(self.experience.ended_at)

    def test_computed_fields_are_read_only(self):
        self.client.force_authenticate(user=self.owner)

        response = self.client.post(self.list_url, {
            **self.payload, "star_count": 99, "is_starred": True, "is_ongoing": True,
            "category_display": "Palsu", "starred_by": [self.user.id],
        }, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["star_count"], 0)
        self.assertFalse(response.data["is_starred"])
        self.assertFalse(response.data["is_ongoing"])
        self.assertEqual(response.data["category_display"], "Internship")
        self.assertFalse(Experience.objects.get(pk=response.data["id"]).starred_by.exists())

    # ---------- Star ----------

    def test_star_rejected_for_visitor(self):
        response = self.client.post(self.star_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(self.experience.starred_by.exists())

    def test_star_toggles_for_logged_in_user(self):
        self.client.force_authenticate(user=self.user)

        starred = self.client.post(self.star_url)
        self.assertEqual(starred.status_code, status.HTTP_200_OK)
        self.assertTrue(starred.data["is_starred"])
        self.assertEqual(starred.data["star_count"], 1)
        self.assertTrue(self.experience.starred_by.filter(pk=self.user.pk).exists())

        unstarred = self.client.post(self.star_url)
        self.assertFalse(unstarred.data["is_starred"])
        self.assertEqual(unstarred.data["star_count"], 0)
        self.assertFalse(self.experience.starred_by.exists())

    def test_star_always_uses_request_user(self):
        self.client.force_authenticate(user=self.user)

        self.client.post(self.star_url, {"user": self.owner.id, "user_id": self.owner.id}, format="json")

        self.assertEqual(list(self.experience.starred_by.all()), [self.user])

    def test_editor_and_owner_can_star(self):
        for account in (self.editor, self.owner):
            self.client.force_authenticate(user=account)
            self.assertEqual(self.client.post(self.star_url).status_code, status.HTTP_200_OK)

        self.assertEqual(self.experience.starred_by.count(), 2)

    # ---------- CSRF dengan session login sungguhan ----------

    def test_session_write_without_csrf_is_rejected(self):
        # force_authenticate melewati CSRF, jadi test ini memakai .login() dan session asli.
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="owner", password="test-password"))

        created = client.post(self.list_url, self.payload, format="json")
        deleted = client.delete(self.detail_url)

        self.assertEqual(created.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(deleted.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Experience.objects.count(), 1)

    def test_star_without_csrf_is_rejected(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="user", password="test-password"))

        response = client.post(self.star_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(self.experience.starred_by.exists())

    def test_session_write_with_csrf_from_page_succeeds(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(username="editor", password="test-password"))
        # Halaman Experience harus memasang cookie csrftoken supaya fetch() bisa mengirim X-CSRFToken.
        client.get(reverse("main:show_experience"))
        token = client.cookies["csrftoken"].value

        response = client.patch(
            self.detail_url, {"title": "Asdos PBP"}, format="json", HTTP_X_CSRFTOKEN=token,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Asdos PBP")
