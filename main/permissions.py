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
