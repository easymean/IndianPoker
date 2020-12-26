from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

import game.routing
from game.middleware import TokenAuthMiddleware

application = ProtocolTypeRouter({
    # ProtocolTypeRouter will inspect the type of connection
    # if the type is ws or wss, the connection will be given to AuthMiddlewareStack
    'websocket': TokenAuthMiddleware(
        # it will populate the request obj of view func with currently authenticated user
        URLRouter(
            # it will examine http path of the connection to route
            #
            game.routing.websocket_urlpatterns
        )
    )
})