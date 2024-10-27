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

``drf-rules`` is a Django Rest Framework library that provides object-level
permissions based on rules. It allows you to define fine-grained access
control for your API endpoints, enabling you to specify which users or groups
can perform certain actions on specific objects.

----

.. _django-rules: https://github.com/dfunckt/django-rules


Features
--------

- **KISS Principle**: The library follows the KISS principle, providing a
  simple and easy-to-understand how it works.
- **Documented**: The library is well-documented, with clear examples and
  explanations of how to use its features.
- **Tested**: The library is thoroughly tested, with a high test coverage to
  ensure its reliability and correctness.
- **DRF Integration**: Seamlessly integrates with Django Rest Framework to
  provide object-level permissions.
- **Based on django-rules**: Built on top of the `django-rules`_ library,
  which provides a flexible and extensible rule system.


Table of Contents
-----------------

- `Requirements`_
- `Installation`_
- `Configuring Django`_
- `Defining Rules`_
- `Using Rules with DRF`_

  + `Permissions in models`_
  + `Permissions in views`_
- `License`_


Requirements
------------

``drf-rules`` requires Python 3.8 or newer and Django 3.2 or newer.

Note: At any given moment in time, `drf-rules` will maintain support for all
currently supported Django versions, while dropping support for those versions
that reached end-of-life in minor releases. See the Supported Versions section
on Django Project website for the current state and timeline.


Installation
------------

Using pip:

.. code-block:: console

    $ pip install drf-rules

Run test with:

.. code-block:: console

    $ ./runtests.sh


.. _`Configuring Django`:

Configuring Django (see `django-rules`_)
----------------------------------------

Add ``rules`` to ``INSTALLED_APPS``:

.. code-block:: python
   :emphasize-lines: 3

    INSTALLED_APPS = (
        # ...
        'rules',
    )

Add the authentication backend:

.. code-block:: python
   :emphasize-lines: 2

    AUTHENTICATION_BACKENDS = (
        'rules.permissions.ObjectPermissionBackend',
        'django.contrib.auth.backends.ModelBackend',
    )


.. _`Defining Rules`:

Defining Rules (see `django-rules`_)
------------------------------------

For a comprehensive guide on using `django-rules`_, please refer to the
detailed documentation.

We will suppose that you have a ``Book`` model and you want to restrict access
to it based on the user's group.

First, define the rule in a ``rules.py`` file:


.. code-block:: python

    import rules

    # Define a rule that checks if the user's group is 'librarians'
    @rules.predicate
    def is_librarian(user):
        return user.groups.filter(name='librarians').exists()

    # Define a rule that checks if the user's group is 'authors'
    @rules.predicate
    def is_author(user):
        return user.groups.filter(name='authors').exists()

    # Define a rule that checks if the user's group is 'managers'
    @rules.predicate
    def is_manager(user):
        return user.groups.filter(name='managers').exists()

    # Define a rule that checks if the user is the author of the book
    @rules.predicate
    def is_book_author(user, book):
        return book.author == user


.. _`Using Rules with DRF`:

Using Rules with DRF (see `django-rules`_)
------------------------------------------

We will assume that you have already defined all the necessary rules to
restrict access to your API.

The ``rules`` library is capable of providing object-level permissions in
Django. It includes an authorization backend and several template tags for use
in your templates. You will need to utilize this library to implement all the
required rules.


Permissions in models
+++++++++++++++++++++

It is common to have a set of permissions for a model, similar to what Django
provides with its default model permissions (such as *add*, *change*, etc.).
When using ``rules`` as the permission checking backend, you can declare
object-level permissions for any model in a similar manner, using a new
``Meta`` option.

To integrate the rules library with your Django models, you'll need to switch
your model's base class and metaclass to the extended versions provided in
``rules.contrib.models``. The extensions are lightweight and only augment the
models by registering permissions. They do not create any migrations for your
models.

The approach you take depends on whether you're using a custom base class
and/or metaclass for your models. Here are the steps:

* If you're using the stock ``django.db.models.Model`` as base for your models,
  simply switch over to ``RulesModel`` and you're good to go.
* If you're currently using the default ``django.db.models.Model`` as the base
  for your models, simply switch to using ``RulesModel`` instead, and you're
  all set.
* If you already have a custom base class that adds common functionality to
  your models, you can integrate ``RulesModelMixin`` and set ``RulesModelBase``
  as the metaclass. Here's how you can do it:

    .. code-block:: python
       :emphasize-lines: 4

        from django.db.models import Model
        from rules.contrib.models import RulesModelBase, RulesModelMixin

        class MyModel(RulesModelMixin, Model, metaclass=RulesModelBase):
            ...

* If you're using a custom metaclass for your models, you'll know how to
  ensure it inherits from ``RulesModelBaseMixin``.

  To create your models, assuming you are using ``RulesModel`` as the base
  class directly, follow this example:

    .. code-block:: python
       :emphasize-lines: 4, 6-10

        import rules
        from rules.contrib.models import RulesModel

        class Book(RulesModel):
            class Meta:
                rules_permissions = {
                    "create": rules.is_staff,
                    "retrieve": rules.is_authenticated,
                }

  The ``RulesModelMixin`` includes methods that you can override to customize
  how a model's permissions are registered. For more details, refer to the
  `django-rules <https://github.com/dfunckt/django-rules>`_ documentation.


**NOTE:** The keys of ``rules_permissions`` differ from Django's default name
conventions (which are also used by ``django-rules``). Instead, we adopt the
Django Rest Framework (DRF) conventions. Below is a table showing the default
CRUD keys for both conventions:

.. list-table:: CRUD key Conventions
   :header-rows: 1

   * - action
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
     - update/partial_update
   * - Delete
     - delete
     - destroy
   * - List
     - view
     - list

As demonstrated, the keys in `drf-rules` can distinguish directly between
various types of update actions, such as `update` and `partial_update`.
Additionally, they can differentiate between `list` and `retrieve` actions.
This is because `drf-rules` is designed to align with Django Rest Framework
(DRF) conventions, enabling it to operate seamlessly with DRF actions.

Another advantage of using this approach is that it facilitates an automatic
association between rules and Django Rest Framework (DRF) actions. As we will
see later, this allows for the seamless integration of `drf-rules` as
permissions in views.


Permissions in views
++++++++++++++++++++

This marks the first instance where we utilize ``drf-rules``. You can
configure the ``permission_classes`` attribute for a view or viewset by using
the ``ModelViewSet`` class-based views:

.. code-block:: python
  :emphasize-lines: 4, 10

  from rest_framework.decorators import action
  from rest_framework.viewsets import ModelViewSet

  from drf_rules.permissions import AutoRulesPermission


  class BookViewSet(ModelViewSet):
      queryset = Book.objects.all()
      serializer_class = BookSerializer
      permission_classes = [AutoRulesPermission]

      @action(detail=False)
      def custom_nodetail(self, request):
          return Response({'status': 'request was permitted'})

This defines permissions based on ``rules_permissions`` specified in the model.
To set permissions for custom actions, you can modify ``rules_permissions``.
For example, you can do this:


.. code-block:: python
  :emphasize-lines: 4, 6-11

  import rules
  from rules.contrib.models import RulesModel

  class Book(RulesModel):
      class Meta:
          rules_permissions = {
              "create": rules.is_staff,
              "retrieve": rules.is_authenticated,
              "custom_nodetail": rules.is_authenticated,
          }

With this configuration, the ``custom_nodetail`` action will be allowed only
to authenticated users. Note that the ``list``, ``update``, ``partial_update``
and ``destroy`` actions are not explicitly defined. Therefore, the
``:default:`` rule will be applied. However, since the ``:default:`` rule is
not defined, these actions will not be allowed at all. The ``:default:`` rule
is applicable only to conventional actions, such as ``list``, ``retrieve``,
``create``, ``update``, ``partial_update``, and ``destroy``. To ensure that
the ``:default:`` rule applies to all conventional actions that are not
explicitly defined, you can define it accordingly:

.. code-block:: python
  :emphasize-lines: 4, 6-10

  import rules
  from rules.contrib.models import RulesModel

  class Book(RulesModel):
      class Meta:
          rules_permissions = {
              "create": rules.is_staff,
              "retrieve": rules.is_authenticated,
              ":default:": rules.is_authenticated,
          }

In this case, if ``custom_nodetail`` rule is not explicitly defined,
``custom_nodetail`` action will not be allowed, even if the ``:default:`` is
specified. This is because ``custom_nodetail`` is not a conventional action.
However, the ``:default:`` rule will apply to the ``list``, ``update``,
``partial_update``, and ``destroy`` actions.


License
-------

``drf-rules`` is distributed under the terms of the
`BSD-3-Clause <https://spdx.org/licenses/BSD-3-Clause.html>`_ license.
