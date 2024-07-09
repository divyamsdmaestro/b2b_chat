# Generated by Django 4.2.3 on 2023-12-18 10:22

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0003_user_is_expert"),
    ]

    operations = [
        migrations.AddField(
            model_name="room",
            name="is_course_group",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="Course",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("modified_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=512)),
                ("course_uuid", models.UUIDField(editable=False)),
                ("image", models.URLField(default=None, null=True)),
                ("is_ccms", models.BooleanField(default=False)),
                ("tenant", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="chat.tenant")),
            ],
            options={
                "ordering": ["-created_at"],
                "abstract": False,
                "default_related_name": "related_courses",
            },
        ),
    ]