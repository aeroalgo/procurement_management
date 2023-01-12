import datetime
from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser


class Direction(models.Model):
    DIRECTION_VTMP = 0
    DIRECTION_GFG = 1
    DIRECTION_OPR = 2
    DIRECTION_KITCHEN = 3
    DIRECTIONS = (
        (DIRECTION_VTMP, "ВТМП"),
        (DIRECTION_GFG, "ГФГ"),
        (DIRECTION_OPR, "ОПР"),
        (DIRECTION_KITCHEN, "Кухня"),
    )

    title = models.CharField(
        verbose_name="Название направления", blank=False, max_length=255, null=True
    )
    key = models.CharField(
        verbose_name="Ключ направления", blank=False, max_length=255, null=True
    )


class UserProfile(AbstractBaseUser, PermissionsMixin):
    login = models.CharField(
        "Логин", max_length=255, blank=True, null=True, unique=True
    )
    last_name = models.CharField("Фамилия", max_length=255, blank=False, null=True)
    first_name = models.CharField("Имя", max_length=255, blank=False, null=True)
    middle_name = models.CharField("Отчество", max_length=255, blank=True, null=True)
    full_name = models.CharField("ФИО", max_length=255, blank=True, null=True)
    email = models.EmailField("Email", blank=False, null=True)
    source_modified = models.DateField(
        "Дата изменения в источнике", blank=False, default=datetime.date(1970, 1, 1)
    )
    direction = models.ManyToManyField(
        Direction, verbose_name="Направление", related_name="user_direction", blank=False
    )

    USERNAME_FIELD = "login"