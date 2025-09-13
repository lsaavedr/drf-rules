drf-rules
=========

.. image:: https://img.shields.io/pypi/v/drf-rules.svg
    :target: https://pypi.org/project/drf-rules
    :alt: PyPI - Version

.. image:: https://img.shields.io/pypi/pyversions/drf-rules.svg
    :target: https://pypi.org/project/drf-rules
    :alt: PyPI - Python Version

.. image:: https://coveralls.io/repos/github/lsaavedr/drf-rules/badge.svg
    :target: https://coveralls.io/github/lsaavedr/drf-rules
    :alt: Coverage Status

``drf-rules`` is a **Django REST Framework** extension built on top of
`django-rules`_ that provides **object-level permissions** fully aligned
with DRF actions.

It allows you to **declaratively define** which users or groups can perform
each action (*create, list, retrieve, update, destroy, etc.*) on your models
and API endpoints.

----

.. _django-rules: https://github.com/dfunckt/django-rules


Features
--------

- **Simplicity (KISS)**: minimal setup, easy to understand.
- **Native DRF integration**: rules map directly to DRF actions.
- **Consistent conventions**: follows DRF’s CRUD action names
  (``retrieve`` instead of ``view``, ``destroy`` instead of ``delete``).
- **Well tested and documented**: high test coverage and clear examples.
- **Powered by django-rules**: inherits its flexibility and extensibility.


Table of Contents
-----------------

- `Requirements`_
- `Installation`_
- `Django Setup`_
- `Defining Rules`_
- `Using with DRF`_
  + `Model Permissions`_
  + `View Permissions`_
  + `Custom User Integration`_
- `License`_


Requirements
------------

- Python **3.8+**
- Django **4.2+**

Note: `drf-rules` supports all currently maintained Django versions and drops
end-of-life versions in minor releases. See the Django Project documentation
for timelines.


Installation
------------

Using pip:

.. code-block:: console

    $ pip install drf-rules

Using uv:

.. code-block:: console

    $ uv add drf-rules

Run tests with:

.. code-block:: console

    $ ./runtests.sh


Django Setup
------------

Add ``rules`` to ``INSTALLED_APPS``:

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        "rules",
    ]

Configure authentication backends:

.. code-block:: python

    AUTHENTICATION_BACKENDS = [
        "rules.permissions.ObjectPermissionBackend",
        "django.contrib.auth.backends.ModelBackend",
    ]


Defining Rules
--------------

Example with a ``Book`` model:

.. code-block:: python

    import rules

    @rules.predicate
    def is_librarian(user):
        return user.groups.filter(name="librarians").exists()

    @rules.predicate
    def is_author(user):
        return user.groups.filter(name="authors").exists()


Using with DRF
--------------

Model Permissions
.................

Define object-level rules in ``Meta.rules_permissions``:

.. code-block:: python

    import rules
    from rules.contrib.models import RulesModel

    class Book(RulesModel):
        title = models.CharField(max_length=100)
        author = models.CharField(max_length=100)

        class Meta:
            rules_permissions = {
                "create": rules.is_staff,
                "retrieve": rules.is_authenticated,
            }

CRUD conventions differ slightly:

.. list-table:: CRUD Conventions
   :header-rows: 1

   * - Action
     - django-rules
     - drf-rules
   * - Create
     - add
     - create
   * - Retrieve
     - view
     - retrieve
   * - Update
     - change
     - update / partial_update
   * - Delete
     - delete
     - destroy
   * - List
     - view
     - list


View Permissions
................

Use ``AutoRulesPermission`` with your DRF views:

.. code-block:: python

    from rest_framework.viewsets import ModelViewSet
    from drf_rules.permissions import AutoRulesPermission

    class BookViewSet(ModelViewSet):
        queryset = Book.objects.all()
        serializer_class = BookSerializer
        permission_classes = [AutoRulesPermission]

You can also define rules for **custom actions**:

.. code-block:: python

    class Book(RulesModel):
        title = models.CharField(max_length=100)
        author = models.CharField(max_length=100)

        class Meta:
            rules_permissions = {
                "create": rules.is_staff,
                "retrieve": rules.is_authenticated,
                "custom_nodetail": rules.is_authenticated,
                ":default:": rules.is_authenticated,
            }

- The ``:default:`` rule applies to all **conventional** actions
  (``list``, ``retrieve``, ``create``, ``update``, ``partial_update``,
  ``destroy``) not explicitly defined.
- Non-standard actions (e.g. ``custom_nodetail``) must be defined explicitly.


Custom User Integration
.......................

If you are using a **custom User model** or any other custom model, you can
integrate ``drf-rules`` by combining ``RulesModelMixin`` with the
``RulesModelBase`` metaclass.  This ensures that permissions are automatically
registered on the model.

.. code-block:: python

    from django.contrib.auth.models import AbstractUser
    from rules.contrib.models import RulesModelMixin, RulesModelBase

    class CustomUser(AbstractUser, RulesModelMixin, metaclass=RulesModelBase):
        """
        Example custom user integrated with drf-rules.
        You can define CRUD permissions here via Meta.rules_permissions.
        """
        class Meta:
            rules_permissions = {
                "create": rules.is_staff,
                "retrieve": rules.is_authenticated,
                ":default:": rules.is_authenticated,
            }

If you already use a **custom metaclass** for your user model (or any other
model), make sure it **inherits from ``RulesModelBase``** so that
``drf-rules`` can register permissions correctly.


License
-------

``drf-rules`` is distributed under the terms of the
`BSD-3-Clause <https://spdx.org/licenses/BSD-3-Clause.html>`_ license.
