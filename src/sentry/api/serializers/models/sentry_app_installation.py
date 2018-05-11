from __future__ import absolute_import

import six

from sentry.api.serializers import Serializer, register
from sentry.models import SentryAppInstallation


@register(SentryAppInstallation)
class SentryAppInstallationSerializer(Serializer):
    def serialize(self, install, attrs, _, grant=None):
        data = {
            'sentry_app': {
                'uuid': install.sentry_app.uuid,
                'slug': install.sentry_app.slug,
            },
            'organization': {
                'id': install.organization.id,
                'name': install.organization.name,
            },
            'uuid': install.uuid,
            'date_added': six.binary_type(install.date_added),
            'date_updated': six.binary_type(install.date_updated),
        }

        if grant:
            data['grant'] = {
                'code': grant.code,
                'expires_at': six.binary_type(grant.expires_at),
            }

        return data
