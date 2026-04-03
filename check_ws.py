import asyncio
import websockets
import json

async def test():
    async with websockets.connect('ws://localhost:8000/ws/track/lunge/1') as ws:
        await ws.send(json.dumps({'raw_landmarks': [{'x': 0, 'y': 0, 'z': 0, 'visibility': 1} for _ in range(33)]}))
        print(await ws.recv())

asyncio.run(test())