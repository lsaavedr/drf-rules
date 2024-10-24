# Generated by Django 5.1.2 on 2024-10-24 01:30

import rules.contrib.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Cat",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=64)),
                ("age", models.IntegerField()),
                ("gender", models.CharField(max_length=32)),
            ],
            bases=(rules.contrib.models.RulesModelMixin, models.Model),
        ),
    ]