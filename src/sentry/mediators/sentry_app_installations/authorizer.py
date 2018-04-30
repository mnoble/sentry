from __future__ import absolute_import

import six

from django.db import transaction

from sentry.coreapi import APIUnauthorized
from sentry.mediators import Mediator, Param
from sentry.models import ApiGrant, ApiApplication, ApiToken, SentryApp
from sentry.utils.cache import memoize


class Authorizer(Mediator):
    grant_type = Param(six.string_types)
    code = Param(six.string_types)
    client_id = Param(six.string_types)
    user = Param('sentry.models.user.User')
    install = Param('sentry.models.sentryappinstallation.SentryAppInstallation')

    def call(self):
        with self.log():
            with transaction.atomic():
                self._validate_grant_type()
                self._validate_install()
                self._validate_sentry_app()
                self._validate_grant()

                return self.exchange()

    def exchange(self):
        return ApiToken.objects.create(
            user=self.user,
            application=self.application,
            scope_list=self.sentry_app.scope_list,
            refresh_token=None,
            expires_at=None,
        )

    def _validate_grant_type(self):
        if not self.grant_type == 'authorization_code':
            raise APIUnauthorized

    def _validate_install(self):
        if not self.install.sentry_app.proxy_user == self.user:
            raise APIUnauthorized

    def _validate_sentry_app(self):
        if not self.user.is_sentry_app:
            raise APIUnauthorized

    def _validate_grant(self):
        if (
            self.grant.application.owner != self.user or
            self.grant.application.client_id != self.client_id
        ):
            raise APIUnauthorized

        if self.grant.is_expired():
            raise APIUnauthorized

    @memoize
    def sentry_app(self):
        try:
            return self.application.sentry_app
        except SentryApp.DoesNotExist:
            raise APIUnauthorized

    @memoize
    def application(self):
        try:
            return self.grant.application
        except ApiApplication.DoesNotExist:
            raise APIUnauthorized

    @memoize
    def grant(self):
        try:
            return ApiGrant.objects.get(code=self.code)
        except ApiGrant.DoesNotExist:
            raise APIUnauthorized
