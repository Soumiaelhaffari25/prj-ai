"""Gestionnaire des connexions WebSocket pour le temps réel du dashboard."""
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active:
            self.active.remove(websocket)

    async def broadcast(self, message: dict):
        """Envoie un message à tous les dashboards connectés."""
        dead = []
        for ws in self.active:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        # Nettoie les connexions mortes
        for ws in dead:
            self.disconnect(ws)


# Instance unique partagée dans toute l'application
manager = ConnectionManager()