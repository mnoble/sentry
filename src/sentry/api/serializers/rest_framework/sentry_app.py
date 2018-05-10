from __future__ import absolute_import

from rest_framework import serializers
from rest_framework.serializers import Serializer, ValidationError

from sentry.models import ApiScopes


class ApiScopesField(serializers.WritableField):
    def from_native(self, data):
        for scope in data:
            if scope not in ApiScopes():
                raise ValidationError('{} not a valid scope'.format(scope))
        return data


class SentryAppSerializer(Serializer):
    name = serializers.CharField()
    scopes = ApiScopesField()
    webhook_url = serializers.CharField()
