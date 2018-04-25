from __future__ import absolute_import

import logging
import six
import types

from mock import patch

from sentry.mediators import Mediator, Param
from sentry.testutils import TestCase


class MockMediator(Mediator):
    user = Param(dict)
    name = Param(six.string_types, default=lambda self: self.user['name'])
    age = Param(int, required=False)

    def call(self):
        with self.log():
            pass


class TestMediator(TestCase):
    def setUp(self):
        super(TestCase, self).setUp()

        self.logger = logging.getLogger('test-mediator')
        self.mediator = MockMediator(
            user={'name': 'Example'},
            age=30,
            logger=self.logger,
        )

    def test_must_implement_call(self):
        del MockMediator.call

        with self.assertRaises(NotImplementedError):
            MockMediator.run(user={'name': 'Example'})

    def test_validate_params(self):
        with self.assertRaises(TypeError):
            MockMediator.run(user=False)

    def test_param_access(self):
        assert self.mediator.user == {'name': 'Example'}
        assert self.mediator.age == 30

    def test_param_default_access(self):
        assert self.mediator.name == 'Example'

    def test_log(self):
        with patch.object(self.logger, 'info') as mock:
            self.mediator.log(at='test')

        mock.assert_any_called(None, extra={'at': 'test'})

    def test_log_start(self):
        with patch.object(self.logger, 'info') as mock:
            self.mediator.call()

        mock.assert_any_call(None, extra={'at': 'start'})

    def test_log_finish(self):
        with patch.object(self.logger, 'info') as mock:
            self.mediator.call()

        mock.assert_any_call(None, extra={'at': 'finish', 'elapsed': 0})

    def test_log_exception(self):
        def call(self):
            with self.log():
                raise TypeError

        setattr(self.mediator, 'call', types.MethodType(call, self.mediator))

        with patch.object(self.logger, 'info') as mock:
            try:
                self.mediator.call()
            except Exception:
                pass

        mock.assert_any_call(None, extra={'at': 'exception', 'elapsed': 0})
