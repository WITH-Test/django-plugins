# -*- coding: utf-8 -*-
import dirtyfields.dirtyfields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Plugin",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        verbose_name="ID",
                        serialize=False,
                        primary_key=True,
                        auto_created=True,
                    ),
                ),
                ("import_string", models.CharField(unique=True, max_length=255)),
                ("name", models.CharField(max_length=255, blank=True, null=True)),
                ("title", models.CharField(max_length=255, blank=True, default="")),
                ("index", models.IntegerField(default=0)),
                (
                    "status",
                    models.SmallIntegerField(
                        choices=[(0, "Enabled"), (1, "Disabled"), (2, "Removed")],
                        default=0,
                    ),
                ),
            ],
            options={
                "ordering": ("index", "id"),
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name="PluginPoint",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        verbose_name="ID",
                        serialize=False,
                        primary_key=True,
                        auto_created=True,
                    ),
                ),
                ("import_string", models.CharField(max_length=255)),
                ("title", models.CharField(max_length=255)),
                (
                    "status",
                    models.SmallIntegerField(
                        choices=[(0, "Enabled"), (1, "Disabled"), (2, "Removed")],
                        default=0,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="plugin",
            name="point",
            field=models.ForeignKey(
                to="django_plugins.PluginPoint", on_delete=models.CASCADE
            ),
        ),
        migrations.AlterUniqueTogether(
            name="plugin",
            unique_together=(("point", "name"),),
        ),
    ]
