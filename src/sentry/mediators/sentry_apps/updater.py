from __future__ import absolute_import

import six

from collections import Iterable
from django.db import transaction
from rest_framework.serializers import ValidationError

from sentry.mediators import Mediator, Param


class Updater(Mediator):
    sentry_app = Param('sentry.models.sentryapp.SentryApp')
    name = Param(six.string_types, required=False)
    scopes = Param(Iterable, required=False)
    webhook_url = Param(six.string_types, required=False)

    @transaction.atomic
    def call(self):
        with self.log():
            self._validate_only_added_scopes()
            self._update_sentry_app()
            return self.sentry_app

    def _validate_only_added_scopes(self):
        if any(self._scopes_removed):
            raise ValidationError('Cannot remove `scopes` already in use.')

    def _update_sentry_app(self):
        if hasattr(self, 'name') and self.name is not None:
            self.sentry_app.name = self.name

        if hasattr(self, 'scopes') and self.scopes is not None:
            self.sentry_app.scope_list = self.scopes

        if hasattr(self, 'webhook_url') and self.webhook_url is not None:
            self.sentry_app.webhook_url = self.webhook_url

        self.sentry_app.save()

    @property
    def _scopes_removed(self):
        return [s for s in self.sentry_app.scope_list if s not in self.scopes]
