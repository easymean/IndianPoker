from django.conf.urls import url
from django.urls import re_path, path
from channels.routing import URLRouter

from game import consumers

# websocket_urlpatterns = [
#     re_path(r'ws/game/(?P<room_id>\w+)/$', consumers.GameConsumer),
# ]

websocket_urlpatterns = [
    url(r'^ws/game/room/(?P<room_id>[^/]+)/$', consumers.GameInfoConsumer, name="info_message"),
]