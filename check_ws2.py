import asyncio
import websockets
import json

async def test():
    async with websockets.connect('ws://localhost:8000/ws/track/lunge/1') as ws:
        for i in range(10):
            print('Sent', i)
            await ws.send(json.dumps({'raw_landmarks': [{'x': 0, 'y': 0, 'z': 0, 'visibility': 1} for _ in range(33)]}))
            await asyncio.sleep(0.1)
        while True:
            print(await ws.recv())

asyncio.run(test())