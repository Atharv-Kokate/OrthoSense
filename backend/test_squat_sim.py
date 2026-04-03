import asyncio
import websockets
import json
import time
import sys

async def send_and_recv(ws, payload):
    await ws.send(json.dumps(payload))
    res = await ws.recv()
    data = json.loads(res)
    
    if data.get("llm_feedback"):
         msg = data["llm_feedback"]
         print(f"\n=================================\n🤖 ORTHO AI: {msg}\n=================================\n")
    elif data.get("status") == "tracking":
         reps = data.get("rep_count", 0)
         errs = len(data.get("errors", []))
         print(f"Tracking   | Reps: {reps} | Errors: {errs} | Data: {data}")
async def run():
    uri = "ws://localhost:8001/ws/track/1"
    async with websockets.connect(uri) as ws:
        print("?? Phase 0: 40 frames Standing (Filling AI baseline buffer)")
        for _ in range(40):
            await send_and_recv(ws, {"left_knee_angle": 175.0, "right_knee_angle": 175.0, "back_angle": 10.0, "symmetry_score": 0.0, "timestamp": time.time()})
            await asyncio.sleep(0.05)

        print("\n?? Phase 1: Perfect Squat (Rep 1)")
        for i in range(20):
             await send_and_recv(ws, {"left_knee_angle": 175.0 - i*4, "right_knee_angle": 175.0 - i*4, "back_angle": 10.0, "symmetry_score": 0.0, "timestamp": time.time()})
             await asyncio.sleep(0.05)
        for i in range(20):
             await send_and_recv(ws, {"left_knee_angle": 95.0 + i*4, "right_knee_angle": 95.0 + i*4, "back_angle": 10.0, "symmetry_score": 0.0, "timestamp": time.time()})
             await asyncio.sleep(0.05)
             
        print("\n?? Phase 2: Shallow Squat & Bad Posture (Rep 2 - Triggering LLM...)")
        for i in range(15):
             await send_and_recv(ws, {"left_knee_angle": 175.0 - i*6, "right_knee_angle": 175.0 - i*6, "back_angle": 55.0, "symmetry_score": 0.0, "timestamp": time.time()})
             await asyncio.sleep(0.05)
        for i in range(15):
             await send_and_recv(ws, {"left_knee_angle": 91.0 + i*6, "right_knee_angle": 91.0 + i*6, "back_angle": 55.0, "symmetry_score": 0.0, "timestamp": time.time()})
             await asyncio.sleep(0.05)
             
        print("\n? Patient standing, waiting for LLM feedback based on Rep 2...")
        for _ in range(60):
            await send_and_recv(ws, {"left_knee_angle": 175.0, "right_knee_angle": 175.0, "back_angle": 10.0, "symmetry_score": 0.0, "timestamp": time.time()})
            await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(run())
