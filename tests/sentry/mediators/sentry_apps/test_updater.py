from __future__ import absolute_import

from rest_framework.serializers import ValidationError

from sentry.mediators.sentry_apps import Creator, Updater
from sentry.models import SentryApp
from sentry.testutils import TestCase


class TestSentryAppUpdater(TestCase):
    def setUp(self):
        self.user = self.create_user()
        self.sentry_app = Creator.run(
            name='nulldb',
            user=self.user,
            scopes=(),
            webhook_url='http://example.com',
        )

        self.creator = Updater(sentry_app=self.sentry_app)

    def update(self, **kwargs):
        data = {
            'sentry_app': self.sentry_app,
        }
        data.update(**kwargs)
        Updater.run(**data)
        return SentryApp.objects.get(pk=self.sentry_app.id)

    def test_updates_name(self):
        app = self.update(name='slowdb')
        assert app.name == 'slowdb'

    def test_updates_scopes(self):
        app = self.update(scopes=('org:read', ))
        assert 'org:read' in app.get_scopes()

    def test_does_not_remove_scopes(self):
        self.update(scopes=('org:read', ))

        with self.assertRaises(ValidationError):
            self.update(scopes=())

    def test_updates_webhook_url(self):
        app = self.update(webhook_url='http://example.com/hook')
        assert app.webhook_url == 'http://example.com/hook'
