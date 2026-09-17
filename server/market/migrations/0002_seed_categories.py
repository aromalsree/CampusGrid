from django.db import migrations


CATEGORIES = [
    {
        "name": "Laptops & Electronics",
        "slug": "laptops",
        "description": "Laptops, tablets, phones, calculators, and other electronics.",
    },
    {
        "name": "Textbooks & Study Guides",
        "slug": "books",
        "description": "Course textbooks, reference books, and study guides.",
    },
    {
        "name": "Academic Notes & PDFs",
        "slug": "notes",
        "description": "Handwritten notes, revision sheets, and digital study resources.",
    },
    {
        "name": "Lab Gear & Instruments",
        "slug": "lab-gear",
        "description": "Lab equipment, instruments, kits, and practical supplies.",
    },
    {
        "name": "Hostel & Room Essentials",
        "slug": "hostel",
        "description": "Furniture, appliances, and useful hostel room essentials.",
    },
    {
        "name": "Bicycles & Mobility",
        "slug": "mobility",
        "description": "Bicycles, safety gear, and campus mobility items.",
    },
]


def seed_categories(apps, schema_editor):
    Category = apps.get_model("market", "Category")
    for category in CATEGORIES:
        Category.objects.update_or_create(
            slug=category["slug"],
            defaults={
                "name": category["name"],
                "description": category["description"],
                "is_active": True,
            },
        )


def remove_categories(apps, schema_editor):
    Category = apps.get_model("market", "Category")
    Category.objects.filter(slug__in=[category["slug"] for category in CATEGORIES]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("market", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_categories, remove_categories),
    ]
