from __future__ import absolute_import

import rules
from django.db import models
from rules.contrib.models import RulesModel


class Cat(RulesModel):
    name = models.CharField(max_length=64)
    age = models.IntegerField()
    gender = models.CharField(max_length=32)

    class Meta:
        rules_permissions = {
            "create": rules.always_true,
            "retrieve": rules.always_true,
            "destroy": rules.is_staff,
            "custom_detail": rules.always_true,
            "custom_nodetail": rules.always_true,
            ":default:": rules.is_staff,
        }

    def __str__(self) -> str:
        return self.name
