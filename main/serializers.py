from django.utils.html import strip_tags
from rest_framework import serializers

from main.models import Experience, Project


class ProjectSerializer(serializers.ModelSerializer):
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()

    class Meta:
        model = Project
        # starred_by sengaja tidak disertakan supaya username pemberi star tidak terekspos ke publik.
        fields = [
            "id",
            "title",
            "description",
            "category",
            "category_display",
            "link",
            "created_at",
            "star_count",
            "is_starred",
        ]
        read_only_fields = ["id", "created_at"]

    def get_star_count(self, obj):
        return len(obj.starred_by.all())

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.starred_by.all()

    def validate_title(self, value):
        title = strip_tags(value).strip()
        if not title:
            raise serializers.ValidationError("Nama proyek tidak boleh hanya berisi tag HTML.")
        return title

    def validate_description(self, value):
        description = strip_tags(value).strip()
        if not description:
            raise serializers.ValidationError("Deskripsi tidak boleh kosong atau hanya berisi tag HTML.")
        return description


class ExperienceSerializer(serializers.ModelSerializer):
    """Representasi dan validasi Experience untuk API /api/v1/experience/.

    Aturan validasinya mengikuti ExperienceForm (Tugas 3-5), karena input lewat API
    tidak melewati clean_<field> milik form.
    """

    category_display = serializers.CharField(source="get_category_display", read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()

    class Meta:
        model = Experience
        # starred_by sengaja tidak disertakan supaya data akun pemberi star tidak terekspos.
        fields = [
            "id",
            "title",
            "description",
            "category",
            "category_display",
            "thumbnail",
            "started_at",
            "ended_at",
            "is_ongoing",
            "star_count",
            "is_starred",
        ]
        read_only_fields = ["id"]

    def get_star_count(self, obj):
        # len() memakai hasil prefetch_related("starred_by") sehingga tidak ada query tambahan per item.
        return len(obj.starred_by.all())

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.starred_by.all()

    def validate_title(self, value):
        title = strip_tags(value).strip()
        if not title:
            raise serializers.ValidationError("Nama pengalaman tidak boleh hanya berisi tag HTML.")
        return title

    def validate_description(self, value):
        description = strip_tags(value).strip()
        if not description:
            raise serializers.ValidationError("Deskripsi tidak boleh kosong atau hanya berisi tag HTML.")
        return description

    def validate(self, attrs):
        # Saat PATCH, field yang tidak dikirim diambil dari data yang sudah tersimpan.
        started_at = attrs.get("started_at", getattr(self.instance, "started_at", None))
        ended_at = attrs.get("ended_at", getattr(self.instance, "ended_at", None))

        if started_at and ended_at and ended_at < started_at:
            raise serializers.ValidationError(
                {"ended_at": "Tanggal berakhir tidak boleh sebelum tanggal mulai."}
            )
        return attrs
