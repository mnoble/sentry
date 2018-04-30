from __future__ import absolute_import

from rest_framework import serializers
from rest_framework.serializers import Serializer, ValidationError

from sentry.models import SentryApp


class SentryAppInstallationSerializer(Serializer):
    slug = serializers.CharField()

    def validate_slug(self, attrs, source):
        if not SentryApp.objects.filter(slug=attrs['slug']).exists():
            raise ValidationError('The `{}` Sentry App was not found'.format(
                attrs['slug']))
