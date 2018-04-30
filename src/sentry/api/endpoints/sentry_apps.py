from __future__ import absolute_import

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from sentry.api.base import Endpoint, SessionAuthentication
from sentry.api.paginator import OffsetPaginator
from sentry.api.serializers import serialize
from sentry.api.serializers.rest_framework import SentryAppSerializer
from sentry.mediators.sentry_apps import Creator
from sentry.models import SentryApp


class SentryAppsEndpoint(Endpoint):
    authentication_classes = (SessionAuthentication, )
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        sentry_apps = SentryApp.objects.filter(owner=request.user)

        return self.paginate(
            request=request,
            queryset=sentry_apps,
            order_by='name',
            paginator_cls=OffsetPaginator,
            on_results=lambda s: serialize(s))

    def post(self, request):
        serializer = SentryAppSerializer(data=request.DATA)

        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=422)

        sentry_app = Creator.run(
            name=request.DATA.get('name'),
            user=request.user,
            scopes=request.DATA.get('scopes'),
            webhook_url=request.DATA.get('webhook_url'),
        )

        return Response(serialize(sentry_app), status=201)
