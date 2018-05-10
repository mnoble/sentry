from __future__ import absolute_import

import six

from django.db import transaction

from sentry.mediators import Mediator, Param
from sentry.models import (
    ApiAuthorization, ApiGrant, SentryApp, SentryAppInstallation
)
from sentry.utils.cache import memoize
from sentry.tasks.sentry_app_install_webhook import send_install_webhook


class Creator(Mediator):
    organization = Param('sentry.models.organization.Organization')
    slug = Param(six.string_types)

    @transaction.atomic
    def call(self):
        with self.log():
            self._create_authorization()
            self._create_api_grant()
            self._create_install()
            self._enqueue_webhook()

            return (self.install, self.api_grant)

    def _create_authorization(self):
        self.authorization = ApiAuthorization.objects.create(
            application=self.api_application,
            user=self.sentry_app.proxy_user,
            scope_list=self.sentry_app.scope_list,
        )

    def _create_install(self):
        self.install = SentryAppInstallation.objects.create(
            organization=self.organization,
            sentry_app=self.sentry_app,
            authorization=self.authorization,
            api_grant=self.api_grant,
        )

    def _create_api_grant(self):
        self.api_grant = ApiGrant.objects.create(
            user=self.sentry_app.proxy_user,
            application=self.api_application,
        )

    def _enqueue_webhook(self):
        send_install_webhook.delay(self.install.id, self.api_grant.id)

    @memoize
    def api_application(self):
        return self.sentry_app.application

    @memoize
    def sentry_app(self):
        return SentryApp.objects.get(slug=self.slug)
