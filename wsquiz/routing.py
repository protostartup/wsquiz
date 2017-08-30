from channels.routing import route

from quiz.consumers import (
    ws_connect,
    ws_message,
    ws_disconnect,
    top_players_connect,
    top_players_disconnect,
)

channel_routing = [
    route('websocket.connect', top_players_connect, path=r'^/top_players/$'),
    route('websocket.disconnect', top_players_disconnect, path=r'^/top_players/$'),
    route('websocket.connect', ws_connect),
    route('websocket.receive', ws_message),
    route('websocket.disconnect', ws_disconnect),
]
