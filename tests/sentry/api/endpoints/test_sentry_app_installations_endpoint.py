from __future__ import absolute_import

from django.core.urlresolvers import reverse

from sentry.mediators.sentry_apps import Creator
from sentry.testutils import APITestCase


class TestSentryAppInstallationsEndpoint(APITestCase):
    def setUp(self):
        self.org = self.create_organization()
        self.sentry_app = Creator.run(
            name='nulldb',
            user=self.create_user(),
            scopes=['project:read'],
        )

        self.url = reverse('sentry-api-0-sentry-app-installations',
                           args=[self.org.id])

        self.login_as(user=self.user)

    def test_simple(self):
        response = self.client.post(self.url, data={'slug': 'nulldb'})

        assert response.status_code == 201
        assert response.data['sentry_app']['slug'] == 'nulldb'

    def test_non_existent_sentry_app(self):
        response = self.client.post(self.url, data={'slug': 'notathing'})

        assert response.status_code == 422
        assert 'The `notathing` Sentry App was not found' in \
            response.data['errors']['slug']

    def test_api_grant(self):
        response = self.client.post(self.url, data={'slug': 'nulldb'})

        assert response.status_code == 201
        assert response.data['grant']['code'] is not None
