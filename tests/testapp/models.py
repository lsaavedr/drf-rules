from __future__ import absolute_import

from django.db import models
from rules.contrib.models import RulesModel
from rules.predicates import always_true, is_staff

from .rules import is_adult_cat


class Gender(models.TextChoices):
    MALE = "MALE", "Male"
    FEMALE = "FEMALE", "Female"


class Cat(RulesModel):
    name = models.CharField(max_length=64)
    age = models.IntegerField()
    gender = models.CharField(max_length=6, choices=Gender.choices)

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        rules_permissions = {
            "post": always_true,
            "create": always_true,
            "retrieve": always_true,
            "destroy": is_staff,
            "partial_update": always_true,
            "custom_detail": always_true,
            "custom_nodetail": always_true,
            ":default:": is_adult_cat,
        }

    def __str__(self) -> str:
        return self.name


class Dog(RulesModel):
    name = models.CharField(max_length=64)
    age = models.IntegerField()
    gender = models.CharField(max_length=6, choices=Gender.choices)

    class Meta:  # pyright: ignore[reportIncompatibleVariableOverride]
        rules_permissions = {
            "create": always_true,
            "retrieve": always_true,
            "destroy": is_staff,
        }

    def __str__(self) -> str:
        return self.name
