from rest_framework.permissions import SAFE_METHODS, BasePermission

EDITOR_GROUP_NAME = "Editor"


def is_editor(user):
    if not user.is_authenticated:
        return False
    return user.groups.filter(name=EDITOR_GROUP_NAME).exists()


def can_create_or_delete(user):
    """Hanya pemilik portofolio (superuser) yang boleh membuat/menghapus data."""
    return user.is_authenticated and user.is_superuser


def can_update(user):
    """Pemilik portofolio dan Editor boleh mengubah data."""
    return user.is_authenticated and (user.is_superuser or is_editor(user))


class ProjectPermission(BasePermission):
    """Semua orang boleh membaca; aturan tulis mengikuti can_update dan can_create_or_delete."""

    message = "Anda tidak memiliki izin untuk melakukan tindakan ini."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if request.method in ("PUT", "PATCH"):
            return can_update(request.user)
        return can_create_or_delete(request.user)
