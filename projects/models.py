from django.conf import settings
from django.db import models


class Project(models.Model):
    STATUS_CHOICES = [
        ("open", "Открыт"),
        ("closed", "Закрыт"),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="owned_projects",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    github_url = models.URLField(blank=True)
    status = models.CharField(max_length=6, choices=STATUS_CHOICES)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participated_projects",
        blank=True,
    )
    interested_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="favorites",
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def title(self):
        return self.name
