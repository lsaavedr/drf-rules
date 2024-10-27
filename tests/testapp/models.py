from __future__ import absolute_import

import rules
from rules.contrib.models import RulesModel

from django.db import models

from .rules import is_adult_cat


class Gender(models.TextChoices):
    MALE = "MALE", "Male"
    FEMALE = "FEMALE", "Female"


class Cat(RulesModel):
    name = models.CharField(max_length=64)
    age = models.IntegerField()
    gender = models.CharField(max_length=6, choices=Gender.choices)

    class Meta:
        rules_permissions = {
            "post": rules.always_true,
            "create": rules.always_true,
            "retrieve": rules.always_true,
            "destroy": rules.is_staff,
            "partial_update": rules.always_true,
            "custom_detail": rules.always_true,
            "custom_nodetail": rules.always_true,
            ":default:": is_adult_cat,
        }

    def __str__(self) -> str:
        return self.name


class Dog(RulesModel):
    name = models.CharField(max_length=64)
    age = models.IntegerField()
    gender = models.CharField(max_length=6, choices=Gender.choices)

    class Meta:
        rules_permissions = {
            "create": rules.always_true,
            "retrieve": rules.always_true,
            "destroy": rules.is_staff,
        }

    def __str__(self) -> str:
        return self.name
