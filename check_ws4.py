import asyncio
import websockets
import json

async def test():
    async with websockets.connect('ws://localhost:8000/ws/track/lunge/1') as ws:
        for i in range(35):
            print('Sent', i)
            await ws.send(json.dumps({'left_knee_angle': 90, 'right_knee_angle': 90, 'back_angle': 90, 'symmetry_score': 0, 'lower_body_visible': True}))
            try:
                reply = await asyncio.wait_for(ws.recv(), timeout=0.1)
                print('Reply:', reply)
            except asyncio.TimeoutError:
                pass
        print('Done. Listening forever...')
        while True:
            print(await ws.recv())

asyncio.run(test())