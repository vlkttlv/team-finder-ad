from django.contrib.auth.hashers import make_password
from django.db import migrations


TEST_USERS = [
    {
        "email": "alex@example.com",
        "name": "Алексей",
        "surname": "Иванов",
        "phone": "+79999999999",
        "password": "password",
    },
    {
        "email": "maria@example.com",
        "name": "Мария",
        "surname": "Петрова",
        "phone": "+79990000002",
        "password": "password",
    },
    {
        "email": "oleg@example.com",
        "name": "Олег",
        "surname": "Сидоров",
        "phone": "+79990000003",
        "password": "password",
    },
]


TEST_PROJECTS = [
    {
        "owner_email": "alex@example.com",
        "name": "API трекера тренировок",
        "description": "Пример реализации проекта трекера-тренировок с сайта roadmap.sh",
        "status": "open",
        "github_url": "https://github.com/vlkttlv/workout_tracker",
    },
    {
        "owner_email": "maria@example.com",
        "name": "Лабораторные работы по Ассемблеру",
        "description": "После выполнения данных лаб требовался поход к психологу.....",
        "status": "open",
        "github_url": "https://github.com/vlkttlv/labs_assembler",
    },
    {
        "owner_email": "oleg@example.com",
        "name": "Сервис для онлайн бронирования отелей",
        "description": "Этот проект представляет собой веб-приложение, предназначенное для онлайн-бронирования номеров в отелях. Сервис позволяет пользователям искать доступные отели, просматривать информацию о номерах, а также бронировать их на определенные даты.",
        "status": "closed",
        "github_url": "https://github.com/vlkttlv/booking_service",
    },
]


def create_test_data(apps, schema_editor):
    User = apps.get_model("users", "User")
    Project = apps.get_model("projects", "Project")

    users_by_email = {}
    for user_data in TEST_USERS:
        user, _ = User.objects.get_or_create(
            email=user_data["email"],
            defaults={
                "name": user_data["name"],
                "surname": user_data["surname"],
                "phone": user_data["phone"],
                "password": make_password(user_data["password"]),
                "is_active": True,
            },
        )
        users_by_email[user.email] = user

    for project_data in TEST_PROJECTS:
        owner = users_by_email[project_data["owner_email"]]
        project, created = Project.objects.get_or_create(
            name=project_data["name"],
            owner=owner,
            defaults={
                "description": project_data["description"],
                "status": project_data["status"],
                "github_url": project_data["github_url"],
            },
        )

        project.participants.add(owner)


def delete_test_data(apps, schema_editor):
    User = apps.get_model("users", "User")
    Project = apps.get_model("projects", "Project")

    project_names = [project["name"] for project in TEST_PROJECTS]
    user_emails = [user["email"] for user in TEST_USERS]

    Project.objects.filter(name__in=project_names).delete()
    User.objects.filter(email__in=user_emails).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_alter_user_phone"),
        ("projects", "0003_alter_project_status"),
    ]

    operations = [
        migrations.RunPython(create_test_data, delete_test_data),
    ]