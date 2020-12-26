from urllib.parse import parse_qs

from channels.auth import AuthMiddlewareStack
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from django.http import parse_cookie
from rest_framework.exceptions import AuthenticationFailed


class TokenAuthMiddleware:

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        if "headers" not in scope:
            raise ValueError(
                "CookieMiddleware was passed a scope that did not have a headers key "
                + "(make sure it is only passed HTTP or WebSocket connections)"
            )

        for name, value in scope.get('headers', []):
            if name == b'cookie':
                cookies = parse_cookie(value.decode('ascii'))
                print(cookies)
                break
        else:
            cookies = {}

        try:
            user_id = cookies.get('user_id', '')

            if user_id == '':
                raise AuthenticationFailed

            scope['user'] = user_id
            print(user_id)

        except AuthenticationFailed:
            scope['user'] = AnonymousUser()

        return self.inner(scope)


def token_auth_middleware_stack(inner):
    return TokenAuthMiddleware(AuthMiddlewareStack(inner))