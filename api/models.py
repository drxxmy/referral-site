import secrets
import string

from django.contrib.auth.models import AbstractBaseUser
from django.db import models


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
