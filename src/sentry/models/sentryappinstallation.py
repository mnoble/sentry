from __future__ import absolute_import

from django.db import models
from django.db.models import Manager
from django.db.models.query import QuerySet
from django.utils import timezone
from uuid import uuid4

from sentry.db.models import (Model, FlexibleForeignKey)


class ParanoidQuerySet(QuerySet):
    def delete(self):
        self.update(date_deleted=timezone.now())


class ParanoidManager(Manager):
    def get_queryset(self):
        return ParanoidQuerySet(self.model, using=self._db).filter(
            date_deleted__isnull=True)


class SentryAppInstallation(Model):
    __core__ = True

    sentry_app = FlexibleForeignKey('sentry.SentryApp')

    # SentryApp's are installed and scoped to an Organization. They will have
    # access, defined by their scopes, to Teams, Projects, etc. under that
    # Organization, implicitly.
    organization = FlexibleForeignKey('sentry.Organization')

    # Each installation gets associated with an instance of ApiAuthorization.
    authorization = FlexibleForeignKey('sentry.ApiAuthorization',
                                       null=True,
                                       on_delete=models.SET_NULL)

    # Each installation has a Grant that the integration can exchange for an
    # Access Token.
    api_grant = FlexibleForeignKey('sentry.ApiGrant',
                                   null=True,
                                   on_delete=models.SET_NULL)

    uuid = models.CharField(max_length=64, default=lambda: uuid4().hex)

    date_added = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(default=timezone.now)
    date_deleted = models.DateTimeField(default=None, blank=True, null=True)

    objects = ParanoidManager()

    class Meta:
        app_label = 'sentry'
        db_table = 'sentry_sentryappinstallation'

    def delete(self):
        self.date_deleted = timezone.now()
        self.save()
