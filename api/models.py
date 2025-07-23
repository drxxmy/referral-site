import secrets
import string

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Необходимо указать номер телефона")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone_number, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser):
    phone_number = models.CharField(max_length=11, unique=True)
    invite_code = models.CharField(max_length=6, unique=True, blank=True)
    activated_invite = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Генерация 6-значного инвайт кода
        alphabet = string.ascii_letters + string.digits
        self.invite_code = "".join(secrets.choice(alphabet) for _ in range(6))
        return super().save(*args, **kwargs)


class AuthCode(models.Model):
    phone_number = models.CharField(max_length=11)
    code = models.CharField(max_length=4)
    created_at = models.DateField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
