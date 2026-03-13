from django import forms
from django.contrib.auth import authenticate

from .models import User


class RegisterForm(forms.Form):
    """Форма регистрации нового пользователя"""
    name = forms.CharField(max_length=124, label="Имя")
    surname = forms.CharField(max_length=124, label="Фамилия")
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    def clean_email(self):
        """Валидирует email, проверяя, что пользователь с таким email не существует"""
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует")
        return email

    def save(self):
        """Создает нового пользователя на основе данных формы"""
        return User.objects.create_user(
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            name=self.cleaned_data["name"],
            surname=self.cleaned_data["surname"],
        )


class LoginForm(forms.Form):
    """Форма входа пользователя"""
    email = forms.EmailField(label="Email")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    def clean(self):
        """Валидирует форму, аутентифицируя пользователя"""
        cleaned = super().clean()
        email = cleaned.get("email")
        password = cleaned.get("password")
        if email and password:
            user = authenticate(email=email.lower(), password=password)
            if not user:
                raise forms.ValidationError("Неверный email или пароль")
            cleaned["user"] = user
        return cleaned


class UserProfileForm(forms.ModelForm):
    """Форма редактирования профиля пользователя"""
    avatar = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={"accept": "image/*"}),
    )

    class Meta:
        model = User
        fields = ["avatar", "name", "surname", "about", "phone", "github_url"]
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "about": "О себе",
            "phone": "Телефон",
            "github_url": "GitHub",
            "avatar": "Аватар",
        }

    def clean_phone(self):
        """Валидирует телефонный номер пользователя, нормализует формат в +7XXXXXXXXXX"""
        phone = (self.cleaned_data.get("phone") or "").strip()
        if not phone:
            return None
        if phone.startswith("8"):
            phone = "+7" + phone[1:]
        if not (phone.startswith("+7") and len(phone) == 12 and phone[1:].isdigit()):
            raise forms.ValidationError("Номер должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX")
        qs = User.objects.filter(phone=phone)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Этот номер телефона уже используется")
        return phone

    def clean_github_url(self):
        """Валидирует ссылку на GitHub пользователя"""
        url = (self.cleaned_data.get("github_url") or "").strip()
        if not url:
            return ""
        if "github.com" not in url.lower():
            raise forms.ValidationError("Ссылка должна вести на GitHub")
        return url
