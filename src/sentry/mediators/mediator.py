from __future__ import absolute_import

import datetime
import logging
import six

from contextlib import contextmanager

from sentry.utils.cache import memoize
from .param import Param


class MediatorMetaClass(type):
    def __init__(cls, *args, **kwargs):
        """
        Mediators declare their parameters in the class scope. Because of this,
        when you try to access one on an instance, you will receive the
        ``Param`` object itself, instead of the value you'd expect.

        We don't want that. Instead, we want to either expose the value passed
        in on Mediator instantiation (via ``**kwargs``) or evaluate the default
        value of the ``Param``.

        To do that, we hide each declared Param in a ``_<attr>`` variable. Then
        when ``__getattr__`` in invoked for ``<attr>`` we can return that value
        from instantiation or lookup the default value via ``_<attr>``.

        This is intended to work similarly to model fields. If you declare:

            >>> class Person(Model):
            >>>     name = models.TextField()

        you don't expect to get an instance of ``models.TextField`` when you
        call ``person.name``. You expect to receive the string value of
        ``name``.
        """
        if 'Mediator' in [c.__name__ for c in cls.__bases__]:
            cls._prepare_params()

        super(MediatorMetaClass, cls).__init__(*args, **kwargs)

    def _prepare_params(cls):
        params = [(k, v) for k, v in six.iteritems(cls.__dict__)
                  if isinstance(v, Param)]

        for name, param in params:
            param.setup(cls, name)


@six.add_metaclass(MediatorMetaClass)
class Mediator(object):
    """
    Objects that encapsulte domain logic.

    Mediators provide a layer between User accessible components like Endpoints
    and the database. They encapsulate the logic necessary to create domain
    objects, including all dependant objects, cross-object validations, etc.

    Mediators are intended to be composable and make it obvious where a piece
    of domain logic resides.

    Naming & Organization Conventions
        Mediators are organized by domain object and describe some domain
        process relevant to that object. For example:

            sentry.mediators.sentry_apps.Creator
            sentry.mediators.sentry_apps.Deactivator

    Params:
        Mediators declare the params they need similarly to Models. On
        instantiation, the Mediator will validate using the ``**kwargs``
        passed in.

        >>> from sentry.mediators import Mediator, Param
        >>>
        >>> class Creator(Mediator):
        >>>     name = Param(str, default='example')
        >>>     user = Param('sentry.models.user.User', none=True)

        See ``sentry.mediators.param`` for more in-depth docs.

    Interface:
        Mediators have two main functions you should be aware of.

        ``run``:
            Convenience function for __init__(**kwargs).call()

        ``call``:
            Instance method where you should implement your logic.

        >>> class Creator(Mediator):
        >>>     name = Param(str, default='example')
        >>>
        >>>     def call(self):
        >>>         Thing.objects.create(name=self.name)

    Logging:
        Mediators have a ``log`` function available to them that will write to
        a logger with a standardized name. The name will be the full module
        path and class of the Mediator.

        >>> class Creator(Mediator):
        >>>     def call(self):
        >>>         self.log(at='step')
        >>>
        >>> Creator.run()
        18:14:26 [INFO] sentry.mediators.sentry_apps.creator.Creator:  (at=u'step')  # NOQA

    Measuring:
        When ``log`` is used as a generator it will automatically log the
        start and end of the Mediator's invocation as well as the elapsed time
        in milliseconds.

        It will also log when an exception is raised. You should use Sentry to
        actually learn about what happened (who would have thought), but
        sometimes it's useful to see an error as part of the overall path taken
        through the codebase.

        >>> class Creator(Mediator):
        >>>     def call(self):
        >>>         with self.log():
        >>>             print('Doing stuff!')
        >>>
        >>> Creator.run()
        18:14:26 [INFO] sentry.mediators.sentry_apps.creator.Creator:  (at=u'start')  # NOQA
        Doing stuff!
        18:14:27 [INFO] sentry.mediators.sentry_apps.creator.Creator:  (at=u'finish', elapsed=1634)  # NOQA

        >>> class Creator(Mediator):
        >>>     def call(self):
        >>>         with self.log():
        >>>             raise TypeError
        >>>
        >>> Creator.run()
        >>>
        18:14:26 [INFO] sentry.mediators.sentry_apps.creator.Creator:  (at=u'start')  # NOQA
        18:14:27 [INFO] sentry.mediators.sentry_apps.creator.Creator:  (at=u'exception', elapsed=1634)  # NOQA
        Traceback (most recent call last):
            ...
        TypeError:
    """

    @classmethod
    def run(cls, *args, **kwargs):
        return cls(*args, **kwargs).call()

    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        self.logger = kwargs.get('logger',
                                 logging.getLogger(self._logging_name))
        self._validate_params(**kwargs)

    def call(self):
        raise NotImplementedError

    def log(self, **kwargs):
        if any(kwargs):
            self.logger.info(None, extra=kwargs)
        else:
            return self._measured(self)

    def _validate_params(self, **kwargs):
        for name, param in six.iteritems(self._params):
            if param.is_required:
                param.validate(self, name, self.__getattr__(name))

    def __getattr__(self, key):
        if key in self.kwargs:
            return self.kwargs.get(key)

        param = self._params.get(key)

        if param and param.has_default:
            return param.default(self)

        return self.__getattribute__(key)

    @property
    def _params(self):
        # These will be named ``_<name>`` on the class, so remove the ``_`` so
        # that it matches the name we'll be invoking on the Mediator instance.
        return dict(
            (k[1:], v) for k, v in six.iteritems(self.__class__.__dict__)
            if isinstance(v, Param)
        )

    @memoize
    def _logging_name(self):
        return '.'.join([
            self.__class__.__module__,
            self.__class__.__name__
        ])

    @contextmanager
    def _measured(self, context):
        start = datetime.datetime.now()
        context.log(at='start')

        try:
            yield
        except Exception as e:
            context.log(at='exception',
                        elapsed=self._milliseconds_since(start))
            raise e

        context.log(at='finish', elapsed=self._milliseconds_since(start))

    def _milliseconds_since(self, start):
        now = datetime.datetime.now()
        elapsed = now - start
        return (elapsed.seconds * 1000) + (elapsed.microseconds / 1000)
