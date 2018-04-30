from __future__ import absolute_import

from django.db import models
from django.utils import timezone
from uuid import uuid4

from sentry.db.models import (Model, FlexibleForeignKey)
from sentry.models import HasApiScopes, Organization
from sentry.utils.strings import dasherize


class SentryApp(Model, HasApiScopes):
    __core__ = True

    application = models.OneToOneField('sentry.ApiApplication',
                                       related_name='sentry_app')

    # Much of the OAuth system in place currently depends on a User existing.
    # This "proxy user" represents the SentryApp in those cases.
    proxy_user = FlexibleForeignKey('sentry.User',
                                    related_name='proxy_user_set')

    # The owner is an actual Sentry User who created the SentryApp. Used to
    # determine who can manage the SentryApp itself.
    owner = FlexibleForeignKey('sentry.User', related_name='owner_set')

    name = models.TextField()
    slug = models.TextField()
    uuid = models.CharField(max_length=64, default=lambda: uuid4().hex)

    webhook_url = models.TextField()

    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'sentry'
        db_table = 'sentry_sentryapp'

    @property
    def organizations(self):
        if not self.id:
            return Organization.objects.none()

        return Organization \
            .objects \
            .select_related('sentryappinstallation') \
            .filter(sentryappinstallation__sentry_app_id=self.id)

    @property
    def teams(self):
        # (mn): for some reason this can't be loaded up top
        from sentry.models import Team

        if not self.id:
            return Team.objects.none()

        return Team.objects.filter(organization__in=self.organizations)

    def save(self, *args, **kwargs):
        self._set_slug()
        return super(SentryApp, self).save(*args, **kwargs)

    def installed_to(self, organization=None, team=None):
        if organization and team:
            raise TypeError('Must only pass organization OR team')

        if organization:
            return self.organizations.filter(id=organization.id).exists()

        if team:
            return self.teams.filter(id=team.id).exists()

        return False

    def _set_slug(self):
        """
        Matches ``name``, but in lowercase, dash form.

        >>> self._set_slug('My Cool App')
        >>> self.slug
        my-cool-app
        """
        if not self.slug:
            self.slug = dasherize(self.name)
