from __future__ import absolute_import

from rest_framework.response import Response

from sentry.api.bases import SentryAppInstallationAuthorizationEndpoint
from sentry.api.authentication import ClientIdSecretAuthentication
from sentry.coreapi import APIUnauthorized
from sentry.mediators.sentry_app_installations import Authorizer
from sentry.api.serializers.models.apitoken import ApiTokenSerializer


class SentryAppInstallationAuthorizationsEndpoint(
    SentryAppInstallationAuthorizationEndpoint
):
    authentication_classes = (ClientIdSecretAuthentication, )

    def post(self, request, install):
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
