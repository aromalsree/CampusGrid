from django.db import migrations


def seed_services_category(apps, schema_editor):
    Category = apps.get_model("market", "Category")
    Category.objects.update_or_create(
        slug="services",
        defaults={
            "name": "Peer Tutoring & Services",
            "description": "Peer tutoring, academic coaching, and student services.",
            "is_active": True,
        },
    )


def remove_services_category(apps, schema_editor):
    Category = apps.get_model("market", "Category")
    Category.objects.filter(slug="services").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("market", "0002_seed_categories"),
    ]

    operations = [
        migrations.RunPython(seed_services_category, remove_services_category),
    ]
