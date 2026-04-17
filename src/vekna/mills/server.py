import asyncio

from pydantic import ValidationError

from vekna.pacts.bus import EventBusProtocol
from vekna.pacts.notify import ERROR_RESPONSE_INVALID, OK_RESPONSE, Event
from vekna.pacts.socket import SocketServerLinkProtocol
from vekna.pacts.tmux import TmuxLinkProtocol


class ServerMill:
    def __init__(
        self,
        tmux: TmuxLinkProtocol,
        socket_server: SocketServerLinkProtocol,
        bus: EventBusProtocol,
    ) -> None:
        self._tmux = tmux
        self._socket_server = socket_server
        self._bus = bus

    async def run(self) -> None:
        self._tmux.ensure_session()
        await self._socket_server.start(self._handle)
        try:
            await asyncio.to_thread(self._tmux.attach)
        finally:
            await self._socket_server.stop()

    async def _handle(self, message: str) -> str:
        try:
            event = Event.model_validate_json(message)
        except ValidationError:
            return ERROR_RESPONSE_INVALID
        self._bus.publish(event)
        return OK_RESPONSE
