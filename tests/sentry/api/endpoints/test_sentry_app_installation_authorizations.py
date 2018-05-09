from __future__ import absolute_import

import six

from datetime import timedelta
from django.core.urlresolvers import reverse
from django.utils import timezone

from sentry.mediators.sentry_apps import Creator as SentryAppCreator
from sentry.mediators.sentry_app_installations import Creator as \
    SentryAppInstallationCreator
from sentry.models import ApiApplication
from sentry.testutils import APITestCase


class TestSentryAppInstallationAuthorizationsEndpoint(APITestCase):
    def setUp(self):
        self.user = self.create_user()
        self.org = self.create_organization()

        self.sentry_app = SentryAppCreator.run(
            name='nulldb',
            user=self.user,
            scopes=('org:read', ),
            webhook_url='http://example.com',
        )

        self.other_sentry_app = SentryAppCreator.run(
            name='slowdb',
            user=self.user,
            scopes=(),
            webhook_url='http://example.com',
        )

        self.install, self.grant = SentryAppInstallationCreator.run(
            organization=self.org,
            slug='nulldb',
        )

    @property
    def url(self):
        return reverse(
            'sentry-api-0-sentry-app-installation-authorizations',
            args=[self.install.uuid],
        )

    def run_request(self, *args, **kwargs):
        data = {
            'client_id': self.sentry_app.application.client_id,
            'client_secret': self.sentry_app.application.client_secret,
            'grant_type': 'authorization_code',
            'code': self.grant.code,
            'installation': self.install.uuid,
        }
        data.update(**kwargs)
        return self.client.post(self.url, data=data)

    def test_simple(self):
        response = self.run_request()
        assert response.status_code == 201
        assert response.data['token'] is not None

    def test_incorrect_grant_type(self):
        response = self.run_request(grant_type='notit')
        assert response.status_code == 403

    def test_invalid_installation(self):
        self.install, _ = SentryAppInstallationCreator.run(
            organization=self.org,
            slug='slowdb',
        )

        response = self.run_request()
        assert response.status_code == 403

    def test_non_sentry_app_user(self):
        app = ApiApplication.objects.create(
            owner=self.create_user()
        )
        response = self.run_request(
            client_id=app.client_id,
            client_secret=app.client_secret,
        )
        assert response.status_code == 401

    def test_invalid_grant(self):
        response = self.run_request(code='123')
        assert response.status_code == 403

    def test_expired_grant(self):
        self.grant.update(expires_at=timezone.now() - timedelta(minutes=2))
        response = self.run_request()
        assert response.status_code == 403

    def test_access_token_request(self):
        response = self.run_request()
        token = response.data['token']

        url = reverse('sentry-api-0-organization-details',
                      args=[self.org.slug])

        response = self.client.get(
            url,
            HTTP_AUTHORIZATION='Bearer {}'.format(token),
        )

        assert response.status_code == 200
        assert response.data['id'] == six.binary_type(self.org.id)
