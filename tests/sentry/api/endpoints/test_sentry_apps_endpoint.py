from __future__ import absolute_import

from django.core.urlresolvers import reverse

from sentry.mediators.sentry_apps import Creator
from sentry.testutils import APITestCase


class TestSentryAppsEndpoint(APITestCase):
    def setUp(self):
        self.url = reverse('sentry-api-0-sentry-apps')
        self.login_as(user=self.user)

    def test_get(self):
        app = Creator.run(
            name='nulldb',
            user=self.user,
            scopes=(),
            webhook_url='http://example.com',
        )
        response = self.client.get(self.url)
        assert response.status_code == 200
        assert response.data[0]['name'] == app.name

    def test_post(self):
        response = self.client.post(self.url, data={
            'name': 'nulldb',
            'scopes': ['project:read'],
            'webhook_url': 'http://example.com',
        })

        assert response.status_code == 201
        assert response.data['name'] == 'nulldb'

    def test_invalid_scope(self):
        response = self.client.post(self.url, data={
            'name': 'nulldb',
            'scopes': ['not:ascope'],
            'webhook_url': 'http://example.com',
        })

        assert response.status_code == 422
        assert 'not:ascope not a valid scope' in \
            response.data['errors']['scopes']

    def test_missing_name(self):
        response = self.client.post(self.url, data={
            'scopes': ['project:read'],
            'webhook_url': 'http://example.com',
        })

        assert response.status_code == 422
        assert 'This field is required.' in response.data['errors']['name']

    def test_missing_webhook_url(self):
        response = self.client.post(self.url, data={
            'name': 'nulldb',
            'scopes': ['project:read'],
        })

        assert response.status_code == 422
        assert 'This field is required.' in response.data['errors']['webhook_url']
