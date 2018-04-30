from __future__ import absolute_import

from django.db import transaction

from sentry.mediators import Mediator, Param


class Destroyer(Mediator):
    install = Param(
        'sentry.models.sentryappinstallation.SentryAppInstallation'
    )

    def call(self):
        with self.log():
            with transaction.atomic():
                self._destroy_installation()
                self._destroy_authorization()
                self._destroy_grant()

            return self.install

    def _destroy_authorization(self):
        self.install.authorization.delete()

    def _destroy_grant(self):
        self.install.api_grant.delete()

    def _destroy_installation(self):
        self.install.delete()
