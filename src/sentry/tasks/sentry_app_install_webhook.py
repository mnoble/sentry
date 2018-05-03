"""
sentry.tasks.sentry_app_install_webhook
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2010-2018 by the Sentry Team, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

from __future__ import absolute_import

import json
import logging
import requests

from sentry.tasks.base import instrumented_task

logger = logging.getLogger(__name__)


@instrumented_task(
    name='sentry.tasks.sentry_app_install_webhook.send_install_webhook',
    queue='sentry_apps.webhook')
def send_install_webhook(install_id, grant_id):
    from sentry.api.serializers import SentryAppInstallationSerializer
    from sentry.models import ApiGrant, SentryAppInstallation

    try:
        install = SentryAppInstallation.objects.get(pk=install_id)
    except SentryAppInstallation.DoesNotExist:
        return

    try:
        grant = ApiGrant.objects.get(pk=grant_id)
    except ApiGrant.DoesNotExist:
        return

    payload = SentryAppInstallationSerializer().serialize(install, grant)
    requests.post(install.sentry_app.webhook_url, data=json.dumps(payload))
