from django.core.management.base import BaseCommand

from main.models import Project

PROJECTS = [
    {
        "title": "Veto",
        "description": (
            "An AI-powered logistics compliance solution. Built an "
            "AI-assisted logistics compliance system that integrates with "
            "ERP/WMS to automatically validate truck loads against "
            "Indonesian regulations before dispatch."
        ),
        "category": "ai",
        "link": "https://veto-gold.vercel.app",
    },
]


class Command(BaseCommand):
    help = "Seed the database with Andy Aulia Akbar's real Project entries."

    def handle(self, *args, **options):
        created_count = 0
        for data in PROJECTS:
            _, created = Project.objects.get_or_create(
                title=data["title"],
                defaults={
                    "description": data["description"],
                    "category": data["category"],
                    "link": data["link"],
                },
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {created_count} new project(s), "
                f"{Project.objects.count()} total in database."
            )
        )
