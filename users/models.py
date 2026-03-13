import io
import os
import random
import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.files.base import ContentFile
from django.core.validators import MaxLengthValidator
from django.db import models
from django.utils import timezone

from PIL import Image, ImageDraw, ImageFont


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=124)
    surname = models.CharField(max_length=124)
    avatar = models.ImageField(upload_to="avatars/")
    phone = models.CharField(max_length=12, unique=True, blank=True, null=True)
    github_url = models.URLField(blank=True)
    about = models.TextField(blank=True, validators=[MaxLengthValidator(256)])
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    def __str__(self):
        return f"{self.name} {self.surname}"

    def save(self, *args, **kwargs):
        if not self.pk and not self.avatar:
            self._generate_default_avatar()
        super().save(*args, **kwargs)

    def _generate_default_avatar(self):
        letter = (self.name or "U").strip()[:1].upper()
        bg_colors = [
            (76, 110, 219),
            (45, 156, 219),
            (39, 174, 96),
            (111, 66, 193),
            (240, 138, 93),
            (52, 73, 94),
        ]
        bg_color = random.choice(bg_colors)

        size = 256
        image = Image.new("RGB", (size, size), color=bg_color)
        draw = ImageDraw.Draw(image)

        font = None
        font_path = settings.BASE_DIR / "static" / "fonts" / "Neue_Haas_Grotesk_Display_Pro_75_Bold.otf"
        if os.path.exists(font_path):
            try:
                font = ImageFont.truetype(str(font_path), 140)
            except OSError:
                font = None
        if font is None:
            font = ImageFont.load_default()

        text_bbox = draw.textbbox((0, 0), letter, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = (size - text_width) / 2
        text_y = (size - text_height) / 2 - 8

        draw.text((text_x, text_y), letter, font=font, fill=(255, 255, 255))

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        file_name = f"avatar_{uuid.uuid4().hex}.png"
        self.avatar.save(file_name, ContentFile(buffer.read()), save=False)
