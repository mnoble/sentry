from __future__ import absolute_import

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from sentry.api.base import Endpoint
from sentry.api.authentication import ClientIdSecretAuthentication
from sentry.coreapi import APIUnauthorized
from sentry.models import SentryAppInstallation
from sentry.mediators.sentry_app_installations import Authorizer
from sentry.api.serializers.models.apitoken import ApiTokenSerializer


class SentryAppInstallationAuthorizationsEndpoint(Endpoint):
    authentication_classes = (ClientIdSecretAuthentication, )
    permission_classes = (IsAuthenticated, )

    def post(self, request, uuid):
        try:
            install = SentryAppInstallation.objects.get(uuid=uuid)
        except SentryAppInstallation.DoesNotExist:
            return Response({'error': 'Unauthorized'}, status=403)

        try:
            token = Authorizer.run(
                grant_type=request.DATA.get('grant_type'),
                code=request.DATA.get('code'),
                client_id=request.DATA.get('client_id'),
                user=request.user,
                install=install,
            )
        except APIUnauthorized:
            return Response({'error': 'Unauthorized'}, status=403)

        token = ApiTokenSerializer().serialize(
            token,
            {'application': None},
            request.user,
        )
        return Response(token, status=201)
