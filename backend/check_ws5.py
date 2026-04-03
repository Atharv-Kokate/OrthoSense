import asyncio
import websockets

async def test():
    async with websockets.connect('ws://localhost:8000/ws/track/lunge/undefined') as ws:
        pass

asyncio.run(test())