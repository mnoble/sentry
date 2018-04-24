from __future__ import absolute_import

from bitfield import BitField
from django.db import models
from django.utils import timezone
from uuid import uuid4

from sentry.db.models import (ArrayField, Model, FlexibleForeignKey)
from sentry.models import ApiScopes
from sentry.utils.strings import dasherize


class SentryApp(Model):
    __core__ = True

    application = FlexibleForeignKey('sentry.ApiApplication')

    # Much of the OAuth system in place currently depends on a User existing.
    # This "proxy user" represents the SentryApp in those cases.
    proxy_user = FlexibleForeignKey('sentry.User',
                                    related_name='proxy_user_set')

    # The owner is an actual Sentry User who created the SentryApp. Used to
    # determine who can manage the SentryApp itself.
    owner = FlexibleForeignKey('sentry.User', related_name='owner_set')

    # The set of OAuth scopes necessary for this integration to function.
    scopes = BitField(flags=ApiScopes().to_bitfield())
    scope_list = ArrayField(of=models.TextField())

    name = models.TextField()
    slug = models.TextField()
    uuid = models.CharField(max_length=64, default=lambda: uuid4().hex)

    webhook_url = models.TextField()

    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'sentry'
        db_table = 'sentry_sentryapp'

    def save(self, *args, **kwargs):
        self._set_slug()
        return super(SentryApp, self).save(*args, **kwargs)

    def _set_slug(self):
        """
        Matches ``name``, but in lowercase, dash form.

        >>> self._set_slug('My Cool App')
        >>> self.slug
        my-cool-app
        """
        if not self.slug:
            self.slug = dasherize(self.name)
