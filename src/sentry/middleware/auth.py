from __future__ import absolute_import

import json

from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user as auth_get_user
from django.utils.functional import SimpleLazyObject

from sentry.models import ApiApplication, UserIP
from sentry.utils.linksign import process_signature
from sentry.utils.auth import AuthUserPasswordExpired, logger


def get_user(request):
    if not hasattr(request, '_cached_user'):
        user = auth_get_user(request)

        if isinstance(user, AnonymousUser) and is_sentry_app_request(request):
            user = get_sentry_app_user(request)

        # If the user bound to this request matches a real user,
        # we need to validate the session's nonce. This nonce is
        # to make sure that the session is valid for effectively the
        # current "version" of the user. When security related
        # actions take place, this nonce will rotate causing a
        # mismatch here forcing the session to be logged out and
        # requiring re-validation.
        if user.is_authenticated() and not user.is_sentry_app:
            # We only need to check the nonce if there is a nonce
            # currently set on the User. By default, the value will
            # be None until the first action has been taken, at
            # which point, a nonce will always be required.
            if user.session_nonce and request.session.get('_nonce', '') != user.session_nonce:
                # If the nonces don't match, this session is anonymous.
                logger.info(
                    'user.auth.invalid-nonce',
                    extra={
                        'ip_address': request.META['REMOTE_ADDR'],
                        'user_id': user.id,
                    }
                )
                user = AnonymousUser()
            else:
                UserIP.log(user, request.META['REMOTE_ADDR'])
        request._cached_user = user
    return request._cached_user


def is_sentry_app_request(request):
    """
    The token exchange Sentry Apps must go through require them to include
    their Client ID and Secret in the request. When they're present, look up
    and authenticate the proxy User using them.
    """
    return 'client_id' in request.body and 'client_secret' in request.body


def get_sentry_app_user(request):
    body = json.loads(request.body)
    client_id = body.get('client_id')
    client_secret = body.get('client_secret')

    if client_id is None or client_secret is None:
        return AnonymousUser()

    application = ApiApplication.objects.get(client_id=client_id)

    if not hasattr(application, 'sentry_app'):
        return AnonymousUser()

    if not application.client_secret == client_secret:
        return AnonymousUser()

    return application.sentry_app.proxy_user


class AuthenticationMiddleware(object):
    def process_request(self, request):
        request.user_from_signed_request = False

        # If there is a valid signature on the request we override the
        # user with the user contained within the signature.
        user = process_signature(request)
        if user is not None:
            request.user = user
            request.user_from_signed_request = True
        else:
            request.user = SimpleLazyObject(lambda: get_user(request))

    def process_exception(self, request, exception):
        if isinstance(exception, AuthUserPasswordExpired):
            from sentry.web.frontend.accounts import expired
            return expired(request, exception.user)
