# SPDX-FileCopyrightText: 2024-present Luis Saavedra <luis94855510@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
import logging

from typing import TYPE_CHECKING, List, Union, cast

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Manager, QuerySet
from django.http import HttpRequest
from rest_framework.permissions import BasePermission
from rest_framework.views import APIView
from rules.contrib.models import RulesModel
from rules.permissions import perm_exists

logger: logging.Logger = logging.getLogger("drf-rules")

crud_method_names: List[str] = [
    "list",
    "create",
    "retrieve",
    "update",
    "partial_update",
    "destroy",
]
error_message: str = (
    "Permission {} not found, please add it to rules_permissions!"
)


class AutoRulesPermission(BasePermission):
    """
    This permission class enforces object-level permissions in
    ``rest_framework.views.APIView``, determining the permission type
    based on the specific Django Rest Framework (DRF) action to be performed.

    Similar to ``rules.contrib.views.AutoPermissionRequiredMixin``, this
    functionality is effective only when model permissions are registered
    using ``rules.contrib.models.RulesModelMixin`` or
    ``rules.contrib.models.RulesModel``.

    ``AutoRulesPermission`` maps Django Rest Framework (DRF) actions to rules
    without converting or adjusting for naming convention differences between
    default Django permissions and DRF actions. This means that the mapping
    does not adhere to Django's default permission names.

    For example, for a `rest_framework.viewsets.ViewSet`, the default actions
    are as follows:

    - list
    - create
    - retrieve
    - update
    - partial_update
    - destroy

    then a ``Meta`` class of the ``Model`` specifying the permissions might
    look like this:

    ```python
    class Meta:
        rules_permissions = {
            "create": rules.is_staff,
            "retrieve": rules.is_authenticated,
            "list": rules.is_authenticated,
            "get_from_name": rules.auhtenticated,
        }
    ```

    regardles of the actual names diffier from the
    ``AutoPermissionViewSetMixin``. But this enables that all actions can be
    maped to a rule in this form. In this example a simple custom action
    ``get_from_name`` is added.
    """

    def _queryset(self, view: APIView) -> Union[QuerySet, Manager]:
        queryset_from_get = getattr(view, "get_queryset", lambda: None)()
        queryset = getattr(view, "queryset", None)

        if queryset_from_get is not None or queryset is not None:
            if queryset_from_get is not None:
                return cast(Union[QuerySet, Manager], queryset_from_get)

            return cast(Union[QuerySet, Manager], queryset)

        message = (
            f"Cannot apply {self.__class__.__name__} on a view that does"
            "not set `.queryset` and not have a `.get_queryset()` method."
        )
        logger.warning(message)
        raise ImproperlyConfigured(message)

    def _method_name(self, request: HttpRequest, view: APIView) -> str:
        method = request.method.lower() if request.method else ""
        return getattr(view, "action", method)

    def _permission(self, method_name: str, view: APIView):
        """
        Get permission from action method name
        """

        queryset = self._queryset(view)
        model_cls: RulesModel = cast(RulesModel, queryset.model)

        return model_cls.get_perm(method_name)

    def has_permission(self, request: HttpRequest, view: APIView):
        user = request.user
        if TYPE_CHECKING:
            user = cast(AbstractUser, user)

        method_name = self._method_name(request, view)
        perm = self._permission(method_name, view)

        if not perm_exists(name=perm):
            logger.warning(error_message.format(perm))

            if method_name not in crud_method_names:
                raise ImproperlyConfigured(error_message.format(perm))

            perm = self._permission(":default:", view)
            if not perm_exists(name=perm):
                raise ImproperlyConfigured(error_message.format(perm))

        return user.has_perm(perm)

    def has_object_permission(self, request: HttpRequest, view: APIView, obj):
        user = request.user
        if TYPE_CHECKING:
            user = cast(AbstractUser, user)

        method_name = self._method_name(request, view)
        perm = self._permission(method_name, view)

        if not perm_exists(name=perm):
            logger.warning(error_message.format(perm))

            # already evaluated in has_permission
            # if method_name not in crud_method_names:
            #     raise ImproperlyConfigured(error_message.format(perm))
            assert method_name in crud_method_names

            perm = self._permission(":default:", view)
            # already evaluated in has_permission
            # if not perm_exists(name=perm):
            #     raise ImproperlyConfigured(error_message.format(perm))
            assert perm_exists(name=perm)

        return user.has_perm(perm, obj)
