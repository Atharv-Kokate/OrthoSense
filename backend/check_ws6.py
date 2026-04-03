import asyncio
import websockets

async def test():
    async with websockets.connect('ws://localhost:8000/ws/track/lunge/1') as ws:
        print('Connected!')

asyncio.run(test())