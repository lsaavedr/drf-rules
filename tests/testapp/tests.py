# SPDX-FileCopyrightText: 2024-present Luis Saavedra <luis94855510@gmail.com>
#
# SPDX-License-Identifier: BSD-3-Clause
from typing import List

from testapp.models import Cat, Dog, Gender

from django.core.exceptions import ImproperlyConfigured
from django.urls import URLPattern, path
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.routers import SimpleRouter
from rest_framework.serializers import ModelSerializer
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_403_FORBIDDEN,
)
from rest_framework.test import APITestCase, URLPatternsTestCase
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from drf_rules.permissions import AutoRulesPermission


class AutoPermissionRequiredMixinTests(APITestCase, URLPatternsTestCase):
    urlpatterns: List[URLPattern] = []

    @classmethod
    def setUpClass(cls):
        class CatSerializer(ModelSerializer):
            class Meta:
                model = Cat
                fields = "__all__"

        class DogSerializer(ModelSerializer):
            class Meta:
                model = Dog
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

            @action(detail=True)
            def unknown_detail(self, request, pk):
                return Response()

            @action(detail=False)
            def unknown_nodetail(self, request):
                return Response()

        class DogViewSet(ModelViewSet):
            queryset = Dog.objects.all()
            serializer_class = DogSerializer
            permission_classes = [AutoRulesPermission]

        class CustomCatView(APIView):
            queryset = Cat.objects.all()
            permission_classes = [AutoRulesPermission]

            def get(self, request):
                return Response()

            def post(self, request: Request):
                serializer = CatSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response(serializer.data, status=HTTP_201_CREATED)
                return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        class CustomDogView(APIView):
            permission_classes = [AutoRulesPermission]

            def get(self, request):
                return Response()

        router = SimpleRouter()
        router.register("cats", CatViewSet)
        router.register("dogs", DogViewSet)
        cls.urlpatterns = router.get_urls()

        cls.urlpatterns += [
            path(
                "custom/cats/",
                CustomCatView.as_view(),
                name="custom-cats-list",
            ),
            path(
                "custom/dogs/",
                CustomDogView.as_view(),
                name="custom-dogs-list",
            ),
        ]

        return super().setUpClass()

    def test_predefined_cat_actions(self):
        url = reverse("cat-list")
        url_1 = reverse("cat-detail", [1])

        # create
        response = self.client.post(
            url,
            {"name": "michi", "age": 3, "gender": Gender.FEMALE},
            format="json",
        )
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        # update
        response = self.client.put(
            url_1,
            {"name": "michi", "age": 2, "gender": Gender.MALE},
            format="json",
        )
        self.assertEqual(response.status_code, HTTP_200_OK)

        # update
        response = self.client.put(
            url_1,
            {"name": "michi", "age": 4, "gender": Gender.MALE},
            format="json",
        )
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

        # partial_update
        response = self.client.patch(
            url_1,
            {"age": 6},
            format="json",
        )
        self.assertEqual(response.status_code, HTTP_200_OK)

        # list
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)

        # retrieve
        response = self.client.get(url_1, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)

        # destroy
        response = self.client.delete(url_1, format="json")
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_predefined_dog_actions(self):
        url = reverse("dog-list")
        url_1 = reverse("dog-detail", [1])

        # create
        response = self.client.post(
            url,
            {"name": "puppy", "age": 3, "gender": Gender.FEMALE},
            format="json",
        )
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        # update
        with self.assertRaises(ImproperlyConfigured):
            self.client.put(
                url_1,
                {"name": "puppy", "age": 2, "gender": Gender.MALE},
                format="json",
            )

        # partial_update
        with self.assertRaises(ImproperlyConfigured):
            self.client.patch(
                url_1,
                {"age": 6},
                format="json",
            )

        # list
        with self.assertRaises(ImproperlyConfigured):
            self.client.get(url, format="json")

        # retrieve
        response = self.client.get(url_1, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)

        # destroy
        response = self.client.delete(url_1, format="json")
        self.assertEqual(response.status_code, HTTP_403_FORBIDDEN)

    def test_custom_cat_actions(self):
        url = reverse("cat-custom-nodetail")
        url_1 = reverse("cat-custom-detail", [1])

        #  custom_nodetail
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)

        #  custom_detail
        response = self.client.get(url_1, format="json")
        self.assertEqual(response.status_code, HTTP_200_OK)

    def test_unknown_cat_action(self):
        url = reverse("cat-unknown-nodetail")
        url_1 = reverse("cat-unknown-detail", [1])

        # unknow_nodetail
        with self.assertRaises(ImproperlyConfigured):
            self.client.get(url, format="json")

        # unkown_detail
        with self.assertRaises(ImproperlyConfigured):
            self.client.get(url_1, format="json")

    def test_custom_view(self):
        url_cats = reverse("custom-cats-list")
        url_dogs = reverse("custom-dogs-list")

        # get not in rules_permissions
        with self.assertRaises(ImproperlyConfigured):
            self.client.get(url_cats, format="json")

        # post
        response = self.client.post(url_cats, {}, format="json")
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)

        # get not in rules_permissions and queryset not in CustomDogView
        with self.assertRaises(ImproperlyConfigured):
            self.client.get(url_dogs, format="json")
