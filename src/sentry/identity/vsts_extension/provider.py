from __future__ import absolute_import

from sentry.identity.vsts.provider import VSTSIdentityProvider


class VstsExtensionIdentityProvider(VSTSIdentityProvider):
    key = 'vsts-extension'
