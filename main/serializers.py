from django.utils.html import strip_tags
from rest_framework import serializers

from main.models import Project


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
