from __future__ import absolute_import

from rest_framework.permissions import IsAuthenticated

from sentry.api.base import Endpoint
from sentry.api.exceptions import ResourceDoesNotExist
from sentry.api.permissions import ScopedPermission
from sentry.app import raven
from sentry.models import SentryApp, SentryAppInstallation


class SentryAppPermission(ScopedPermission):
    def has_object_permission(self, request, view, sentry_app):
        return sentry_app.owner == request.user


class SentryAppEndpoint(Endpoint):
    permission_classes = (SentryAppPermission, )
    authentication_classes = (IsAuthenticated, )

    def convert_args(self, request, slug, *args, **kwargs):
        try:
            sentry_app = SentryApp.objects.get_from_cache(slug=slug)
        except SentryApp.DoesNotExist:
            raise ResourceDoesNotExist

        self.check_object_permissions(request, sentry_app)

        raven.tags_context({
            'sentry_app': sentry_app.id,
        })

        request.sentry_app = sentry_app

        kwargs['sentry_app'] = sentry_app
        return (args, kwargs)


class SentryAppInstallationPermission(ScopedPermission):
    def has_object_permission(self, request, view, install):
        if not request.user:
            return False
        return install.organization in request.user.get_orgs()


class SentryAppInstallationEndpoint(Endpoint):
    permission_classes = (SentryAppInstallationPermission, )
    authentication_classes = (IsAuthenticated, )

    def convert_args(self, request, uuid, *args, **kwargs):
        try:
            install = SentryAppInstallation.objects.get_from_cache(uuid=uuid)
        except SentryAppInstallation.DoesNotExist:
            raise ResourceDoesNotExist

        self.check_object_permissions(request, install)

        raven.tags_context({
            'sentry_app_installation': install.id,
        })

        request.sentry_app_installation = install

        kwargs['install'] = install
        return (args, kwargs)


class SentryAppInstallationAuthorizationPermission(ScopedPermission):
    def has_object_permission(self, request, view, install):
        if not request.user.is_sentry_app:
            return False
        return request.user == install.sentry_app.proxy_user


class SentryAppInstallationAuthorizationEndpoint(SentryAppInstallationEndpoint):
    permission_classes = (SentryAppInstallationAuthorizationPermission, )
