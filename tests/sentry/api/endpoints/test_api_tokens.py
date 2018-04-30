from __future__ import absolute_import

import uuid

from django.core.urlresolvers import reverse

from sentry.mediators.sentry_apps import Creator as SentryAppCreator
from sentry.models import ApiGrant, ApiToken
from sentry.testutils import APITestCase


class ApiTokensListTest(APITestCase):
    def test_simple(self):
        ApiToken.objects.create(user=self.user)
        ApiToken.objects.create(user=self.user)

        self.login_as(self.user)
        url = reverse('sentry-api-0-api-tokens')
        response = self.client.get(url)
        assert response.status_code == 200, response.content
        assert len(response.data) == 2


class ApiTokensCreateTest(APITestCase):
    def test_no_scopes(self):
        self.login_as(self.user)
        url = reverse('sentry-api-0-api-tokens')
        response = self.client.post(url)
        assert response.status_code == 400

    def test_simple(self):
        self.login_as(self.user)
        url = reverse('sentry-api-0-api-tokens')
        response = self.client.post(url, data={'scopes': ['event:read']})
        assert response.status_code == 201
        token = ApiToken.objects.get(
            user=self.user,
        )
        assert not token.expires_at
        assert not token.refresh_token
        assert token.get_scopes() == ['event:read']


class ApiTokenExchangeTest(APITestCase):
    """
    When exchanging an ApiGrant for an ApiToken
    """

    def setUp(self):
        self.user = self.create_user()
        self.sentry_app = SentryAppCreator.run(
            name='nulldb',
            user=self.user,
            scopes=['project:read'],
        )
        self.grant = ApiGrant.objects.create(
            user=self.sentry_app.proxy_user,
            application=self.sentry_app.application,
        )

    def _make_request(self, **kwargs):
        url = reverse('sentry-api-0-api-tokens')
        data = {
            'grant_type': 'authorization_code',
            'code': self.grant.code,
            'client_id': self.sentry_app.application.client_id,
        }
        data.update(kwargs)
        return self.client.post(url, data=data)

    def test_simple(self):
        self.login_as(self.sentry_app.proxy_user)
        response = self._make_request()
        assert response.status_code == 201
        assert ApiToken.objects.get(id=response.data['id'])

    def test_not_as_sentry_app(self):
        self.login_as(self.user)
        response = self._make_request()
        assert response.status_code == 403

    def test_invalid_grant_code(self):
        self.login_as(self.sentry_app.proxy_user)
        response = self._make_request(code=uuid.uuid4().hex)
        assert response.status_code == 403

    def test_mismatching_owner(self):
        self.login_as(self.create_user())
        response = self._make_request()
        assert response.status_code == 403

    def test_mismatching_client_id(self):
        self.login_as(self.sentry_app.proxy_user)
        response = self._make_request(client_id=uuid.uuid4().hex)
        assert response.status_code == 403


class ApiTokensDeleteTest(APITestCase):
    def test_simple(self):
        token = ApiToken.objects.create(user=self.user)
        self.login_as(self.user)
        url = reverse('sentry-api-0-api-tokens')
        response = self.client.delete(url, data={'token': token.token})
        assert response.status_code == 204
        assert not ApiToken.objects.filter(id=token.id).exists()
