from django.conf.urls import url
from game import consumers

websocket_urlpatterns = [
    url(r'^ws/game/room/(?P<room_id>[^/]+)/$', consumers.GameInfoConsumer, name="info_message"),
]