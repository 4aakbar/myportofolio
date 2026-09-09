from datetime import datetime, timezone as dt_timezone

from django.core.management.base import BaseCommand

from main.models import Experience

EXPERIENCES = [
    {
        "title": "Staff of the Academic Division, BEM Fasilkom UI",
        "description": (
            "Managed fundraising initiatives to support the faculty's "
            "competition contingent, coordinating promotional and financial "
            "activities worth up to Rp40.000.000. Developed and executed "
            "fundraising strategies involving multiple stakeholders within "
            "the faculty, and managed the faculty's internal competition "
            "from planning through execution, including coordination, "
            "logistics, and participant management."
        ),
        "category": "volunteer",
        "ended_at": None,
    },
    {
        "title": "Digital Marketing Staff, Computer Science Festival UI",
        "description": (
            "Developed social media content to promote Computer Science "
            "Festival UI activities and competitions, reaching 150,000+ "
            "views. Assisted in developing digital marketing campaigns "
            "across Instagram and other social media platforms, and "
            "collaborated with other divisions to ensure consistent "
            "branding and communication."
        ),
        "category": "volunteer",
        "ended_at": None,
    },
    {
        "title": "Mentor, BETIS Fasilkom UI",
        "description": (
            "Mentored underprivileged high-school students in preparation "
            "for university entrance examinations, providing academic "
            "guidance and learning support tailored to students' individual "
            "needs, and assisting them in developing effective study "
            "strategies and maintaining academic progress."
        ),
        "category": "volunteer",
        "ended_at": datetime(2025, 12, 31, tzinfo=dt_timezone.utc),
    },
    {
        "title": "Exhibition Coordinator, DelArt (SMAN 8 Yogyakarta Art Exhibit)",
        "description": (
            "Coordinated artwork placement, exhibition layout, and "
            "installation activities to ensure the exhibition was completed "
            "within the event timeline."
        ),
        "category": "volunteer",
        "ended_at": datetime(2024, 12, 31, tzinfo=dt_timezone.utc),
    },
]


class Command(BaseCommand):
    help = "Seed the database with Andy Aulia Akbar's real Experience entries."

    def handle(self, *args, **options):
        created_count = 0
        for data in EXPERIENCES:
            _, created = Experience.objects.get_or_create(
                title=data["title"],
                defaults={
                    "description": data["description"],
                    "category": data["category"],
                    "ended_at": data["ended_at"],
                },
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {created_count} new experience(s), "
                f"{Experience.objects.count()} total in database."
            )
        )
