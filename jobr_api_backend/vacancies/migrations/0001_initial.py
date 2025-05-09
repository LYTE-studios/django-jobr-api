# Generated by Django 5.1.3 on 2025-01-24 14:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ContractType",
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
                ("contract_type", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Function",
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
                ("function", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Language",
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
                ("language", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Location",
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
                ("location", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Question",
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
                ("question", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Skill",
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
                ("skill", models.CharField(max_length=255)),
                (
                    "category",
                    models.CharField(
                        choices=[("hard", "Hard"), ("soft", "Soft")],
                        default="hard",
                        max_length=10,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="VacancyQuestion",
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
                ("question", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Weekday",
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
                ("name", models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name="Vacancy",
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
                (
                    "expected_mastery",
                    models.CharField(
                        choices=[
                            ("None", "None"),
                            ("Beginner", "Beginner"),
                            ("Intermediate", "Intermediate"),
                            ("Advanced", "Advanced"),
                            ("Expert", "Expert"),
                        ],
                        max_length=255,
                        null=True,
                    ),
                ),
                ("job_date", models.DateField(null=True)),
                (
                    "salary",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                (
                    "contract_type",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="vacancies.contracttype",
                    ),
                ),
                (
                    "employer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "function",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="vacancies.function",
                    ),
                ),
                (
                    "location",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="vacancies.location",
                    ),
                ),
                ("skill", models.ManyToManyField(to="vacancies.skill")),
            ],
        ),
        migrations.CreateModel(
            name="ApplyVacancy",
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
                (
                    "employee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "vacancy",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="vacancies.vacancy",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="VacancyDescription",
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
                ("description", models.TextField()),
                (
                    "question",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="vacancies.question",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="vacancy",
            name="descriptions",
            field=models.ManyToManyField(to="vacancies.vacancydescription"),
        ),
        migrations.CreateModel(
            name="VacancyLanguage",
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
                (
                    "mastery",
                    models.CharField(
                        choices=[
                            ("None", "None"),
                            ("Beginner", "Beginner"),
                            ("Intermediate", "Intermediate"),
                            ("Advanced", "Advanced"),
                            ("Expert", "Expert"),
                        ],
                        max_length=255,
                    ),
                ),
                (
                    "language",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="vacancies.language",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="vacancy",
            name="languages",
            field=models.ManyToManyField(
                related_name="vacancy_languages", to="vacancies.vacancylanguage"
            ),
        ),
        migrations.AddField(
            model_name="vacancy",
            name="questions",
            field=models.ManyToManyField(to="vacancies.vacancyquestion"),
        ),
        migrations.AddField(
            model_name="vacancy",
            name="week_day",
            field=models.ManyToManyField(null=True, to="vacancies.weekday"),
        ),
    ]
