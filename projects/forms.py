from django import forms

from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "github_url", "status"]
        labels = {
            "name": "Название проекта",
            "description": "Описание проекта",
            "github_url": "GitHub",
            "status": "Статус",
        }

    def clean_github_url(self):
        url = (self.cleaned_data.get("github_url") or "").strip()
        if not url:
            return ""
        if "github.com" not in url.lower():
            raise forms.ValidationError("Ссылка должна вести на GitHub")
        return url
