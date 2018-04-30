from __future__ import absolute_import

from rest_framework.serializers import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from sentry.api.base import Endpoint, SessionAuthentication
from sentry.api.exceptions import ResourceDoesNotExist
from sentry.api.serializers import serialize
from sentry.models import SentryApp
from sentry.mediators.sentry_apps import Updater


class SentryAppDetailsEndpoint(Endpoint):
    authentication_classes = (SessionAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request, slug):
        try:
            sentry_app = SentryApp.objects.get(slug=slug)
        except SentryApp.DoesNotExist:
            raise ResourceDoesNotExist

        return Response(serialize(sentry_app))

    def put(self, request, slug):
        try:
            sentry_app = SentryApp.objects.get(slug=slug)
        except SentryApp.DoesNotExist:
            raise ResourceDoesNotExist

        try:
            sentry_app = Updater.run(
                sentry_app=sentry_app,
                name=request.DATA.get('name'),
                scopes=request.DATA.get('scopes'),
                webhook_url=request.DATA.get('webhook_url'),
            )
        except ValidationError as e:
            return Response({'error': e.message}, status=422)

        return Response(serialize(sentry_app))
