from django.forms import DateInput, ModelForm, Select, TextInput, Textarea, URLInput

from main.models import Project
from main.models import Experience


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "category",
            "link",
        ]

        labels = {
            "title": "Nama Proyek",
            "description": "Deskripsi Proyek",
            "category": "Kategori Proyek",
            "link": "URL Proyek",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Portfolio Website",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan Proyekmu",
                    "rows": 3,
                }
            ),
            "category": Select(),
            "link": URLInput(
                attrs={
                    "placeholder": "https://github.com/4aakbar/myportofolio",
                }
            ),
        }

class ExperienceForm(ModelForm):
    class Meta:
        model = Experience
        fields = [
            "title",
            "description",
            "category",
            "thumbnail",
            "ended_at",
        ]

        labels = {
            "title": "Experience",
            "description": "Deskripsi Experience",
            "category": "Kategori Experience",
            "thumbnail": "Thumbnail Experience",
            "ended_at": "Berakhir pada Tanggal",
        }

        widgets = {
            "title": TextInput(
                attrs={
                    "placeholder": "Experience",
                    "maxlength": 255,
                }
            ),
            "description": Textarea(
                attrs={
                    "placeholder": "Ceritakan Pengalamanmu",
                    "rows": 3,
                }
            ),
            "category": Select(),
            "thumbnail": URLInput(
                attrs={
                    "placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000",
                }
            ),
            "ended_at": DateInput(attrs={"type": "date"}),
        }