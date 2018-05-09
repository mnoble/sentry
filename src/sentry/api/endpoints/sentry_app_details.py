from __future__ import absolute_import

from rest_framework.serializers import ValidationError
from rest_framework.response import Response

from sentry.api.bases import SentryAppEndpoint
from sentry.api.serializers import serialize
from sentry.mediators.sentry_apps import Updater


class SentryAppDetailsEndpoint(SentryAppEndpoint):
    def get(self, request, sentry_app):
        return Response(serialize(sentry_app))

    def put(self, request, sentry_app):
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
