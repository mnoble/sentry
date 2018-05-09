from __future__ import absolute_import

from rest_framework.response import Response

from sentry.api.base import Endpoint
from sentry.api.serializers import serialize
from sentry.api.serializers.rest_framework import (
    SentryAppInstallationSerializer
)
from sentry.mediators.sentry_app_installations import Creator
from sentry.models import Organization


class SentryAppInstallationsEndpoint(Endpoint):
    def post(self, request, organization_id):
        serializer = SentryAppInstallationSerializer(data=request.DATA)

        # TODO(mn): Move validation logic into the mediator once the API has
        # a more rich exception handling setup.
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=422)

        org = Organization.objects.get(id=organization_id)

        install, grant = Creator.run(
            organization=org,
            slug=request.DATA['slug'],
        )

        return Response(serialize(install, grant), status=201)
