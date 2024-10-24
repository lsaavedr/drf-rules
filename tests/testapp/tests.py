# SPDX-FileCopyrightText: 2024-present Luis Saavedra <luis94855510@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from django.core.exceptions import ImproperlyConfigured
from django.urls import URLPattern
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.routers import SimpleRouter
from rest_framework.serializers import ModelSerializer
from rest_framework.test import APITestCase, URLPatternsTestCase
from rest_framework.viewsets import ModelViewSet
from testapp.models import Cat

from drf_rules.permissions import AutoRulesPermission


class AutoPermissionRequiredMixinTests(APITestCase, URLPatternsTestCase):
    urlpatterns: list[URLPattern] = []

    @classmethod
    def setUpClass(cls):
        class CatSerializer(ModelSerializer):
            class Meta:
                model = Cat
                fields = "__all__"

        class CatViewSet(ModelViewSet):
            queryset = Cat.objects.all()
            serializer_class = CatSerializer
            permission_classes = [AutoRulesPermission]

            @action(detail=True)
            def custom_detail(self, request, pk):
                return Response()

            @action(detail=False)
            def custom_nodetail(self, request):
                return Response()

            @action(detail=False)
            def unknown(self, request):
                return Response()

        router = SimpleRouter()
        router.register("cats", CatViewSet)
        cls.urlpatterns = router.get_urls()

        return super().setUpClass()

    def test_predefined_actions(self):
        url = reverse("cat-list")
        url_1 = reverse("cat-detail", [1])

        # Create should be allowed due to the create permission
        response = self.client.post(
            url,
            {"name": "michi", "age": 3, "gender": "femenino"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)

        # List should be forbidden due to missing list permission
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 403)

        # Retrieve should be allowed due to the view permission
        response = self.client.get(url_1, format="json")
        self.assertEqual(response.status_code, 200)

        # Destroy should be forbidden due to the destroy permission
        response = self.client.delete(url_1, format="json")
        self.assertEqual(response.status_code, 403)

    def test_custom_actions(self):
        url = reverse("cat-custom-nodetail")
        url_1 = reverse("cat-custom-detail", [1])

        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, 200)

        response = self.client.get(url_1, format="json")
        self.assertEqual(response.status_code, 200)

    def test_unknown_action(self):
        url = reverse("cat-unknown")
        with self.assertRaises(ImproperlyConfigured):
            self.client.get(url, format="json")
