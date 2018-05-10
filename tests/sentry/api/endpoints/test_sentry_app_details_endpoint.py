from __future__ import absolute_import

from django.core.urlresolvers import reverse

from sentry.mediators.sentry_apps import Creator
from sentry.testutils import APITestCase


class TestSentryAppDetailsEndpoint(APITestCase):
    def setUp(self):
        self.user = self.create_user()
        self.sentry_app = Creator.run(
            name='nulldb',
            user=self.user,
            scopes=(),
            webhook_url='http://example.com',
        )

        self.url = reverse('sentry-api-0-sentry-app-details',
                           args=[self.sentry_app.slug])

        self.login_as(user=self.user)

    def test_get(self):
        response = self.client.get(self.url)
        assert response.status_code == 200
        assert response.data['name'] == 'nulldb'

    def test_put(self):
        response = self.client.put(self.url, data={'name': 'slowdb'})
        assert response.status_code == 200
        assert response.data['name'] == 'slowdb'

    def test_get_as_non_owner(self):
        self.login_as(self.create_user())
        response = self.client.get(self.url)
        assert not response.status_code == 200

    def test_put_as_non_owner(self):
        self.login_as(self.create_user())
        response = self.client.put(self.url, data={'name': 'hax'})
        assert not response.status_code == 200
