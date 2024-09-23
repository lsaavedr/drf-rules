# SPDX-FileCopyrightText: 2024-present Luis Saavedra <luis94855510@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
import logging

from django.db.models import QuerySet
from django.http import HttpRequest
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import BasePermission
from rules.contrib.models import RulesModel
from rules.permissions import perm_exists

logger = logging.getLogger("drf-rules")


class AutoRulesPermissions(BasePermission):
    """
    automatic permissions on drf-actions with django-rules
     - lists
     - create
     - retrieve
     - update
     - partial_update
     - destroy
    """

    def _queryset(self, view: GenericAPIView) -> QuerySet:
        assert (
            hasattr(view, "get_queryset") or getattr(view, "queryset", None) is not None
        ), (
            f"Cannot apply {self.__class__.__name__} on a view that does"
            "not set `.queryset` or have a `.get_queryset()` method."
        )

        if hasattr(view, "get_queryset"):
            queryset = view.get_queryset()
            assert queryset is not None, "{}.get_queryset() returned None".format(
                view.__class__.__name__
            )
            return queryset
        return view.queryset

    def _permission(self, request: HttpRequest, view: GenericAPIView):
        """
        Get permission from action method name
        """

        method_name = getattr(view, "action", request.method.lower())
        queryset = self._queryset(view)

        model_cls: RulesModel = queryset.model

        return model_cls.get_perm(method_name)

    def has_permission(self, request: HttpRequest, view: GenericAPIView):
        user = request.user
        perm = self._permission(request, view)

        if not perm_exists(name=perm):
            logger.warning(
                f"Permission {perm} not found, please add it to rules_permissions!"
            )
            return False

        return user.has_perm(perm)

    def has_object_permission(self, request: HttpRequest, view: GenericAPIView, obj):
        user = request.user
        perm = self._permission(request, view)

        if not perm_exists(name=perm):
            logger.warning(
                f"Permission {perm} not found, please add it to rules_permissions!"
            )
            return False

        return user.has_perm(perm, obj)
