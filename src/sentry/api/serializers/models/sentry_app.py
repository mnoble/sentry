from __future__ import absolute_import

from sentry.api.serializers import Serializer, register
from sentry.models import SentryApp


@register(SentryApp)
class SentryAppSerializer(Serializer):
    def serialize(self, obj, attrs, user):
        return {
            'application': {
                'id': obj.application.id,
                'client_id': obj.application.client_id,
            },
            'owner': {
                'id': obj.owner.id,
                'username': obj.owner.username,
            },
            'name': obj.name,
            'slug': obj.slug,
            'uuid': obj.uuid,
            'scopes': obj.scope_list,
            'webhook_url': obj.webhook_url,
            'date_added': obj.date_added,
            'date_updated': obj.date_updated,
        }
