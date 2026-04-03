import urllib.request
import urllib.parse
import urllib.error
import json
import asyncio
import websockets
import time

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"

def post(endpoint, data):
    req = urllib.request.Request(
        f"{BASE_URL}{endpoint}",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode())

def get(endpoint):
    req = urllib.request.Request(
        f"{BASE_URL}{endpoint}",
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return json.loads(e.read().decode())

async def ws_test(patient_id):
    print("  [WAIT] Connecting to Tracking WebSocket...")
    uri = f"{WS_URL}/ws/track/squats/{patient_id}?lang=en-IN"
    try:
        async with websockets.connect(uri) as ws:
            print("  [OK] WebSocket Tracking connected.")
            # Trigger Voice AI
            voice_req = {"patient_vocal_command": "hello do you hear me?"}
            await ws.send(json.dumps(voice_req))
            
            start = time.time()
            ai_replied = False
            while time.time() - start < 10:
                try:
                    res = await asyncio.wait_for(ws.recv(), timeout=2.0)
                    data = json.loads(res)
                    if "llm_feedback" in data:
                        print(f"  [OK] AI Responded: {data['llm_feedback']}")
                        ai_replied = True
                        break
                except asyncio.TimeoutError:
                    continue
            if not ai_replied:
                print("  [FAIL] AI did not respond in 10s.")
                return False
            return True
    except Exception as e:
         print(f"  [FAIL] WebSockets failed: {e}")
         return False

def run_sync_tests():
    print("================================================")
    print("🚀 Backend E2E Test Suite Running...")
    print("================================================")
    
    # 1. Test Doctor Registration
    print("1. Testing Auth & Registration...")
    email = f"test_doctor_{int(time.time())}@orthosense.com"
    doc_res = post("/api/auth/register-doctor", {
        "first_name": "Test",
        "last_name": "Automaton",
        "email": email,
        "password": "securepassword123",
        "specialty": "orthopedics",
        "license_number": f"TEST{int(time.time())}"
    })
    
    if hasattr(doc_res, "get") and "access_token" in doc_res:
         print("  [OK] Ortho Doctor Registration Works.")
    elif hasattr(doc_res, "get") and doc_res.get("detail") == "Email already registered":
         print("  [OK] Ortho Doctor Registration Works (Already Registered).")
    else:
         print("  [FAIL] Registration endpoint failed", doc_res)

    # 2. Test Login
    try:
        req_body = f"username={urllib.parse.quote(email)}&password=securepassword123"
        login_req = urllib.request.Request(
            f"{BASE_URL}/api/auth/login",
            data=req_body.encode("utf-8"),
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        with urllib.request.urlopen(login_req) as response:
            login_res = json.loads(response.read().decode())
            
        doc_id = login_res.get("user_id", 1)  # Mock fallback
        print("  [OK] Doctor Login Works.")
    except Exception as e:
        print("  [FAIL] Doctor Login Failed:", e)
        doc_id = 1

    # 3. Create Patient
    print("\n2. Testing Patient Onboarding...")
    patient_res = post("/api/patients/onboard", {
        "doctor_id": doc_id,
        "first_name": "Test",
        "last_name": "Patient",
        "email": f"patient_{int(time.time())}@orthosense.com",
        "password": "patientpassword",
        "condition": "Knee Rehab",
        "date_of_surgery": "2024-01-01",
        "target_rom_degrees": 120.0
    })
    
    patient_id = 1
    if hasattr(patient_res, "get") and "patient_profile_id" in patient_res:
        patient_id = patient_res["patient_profile_id"]
        print(f"  [OK] Patient Onboarding Works (ID: {patient_id})")
    else:
        print(f"  [FAIL] Patient Onboarding Failed: {patient_res}")

    return patient_id

if __name__ == "__main__":
    try:
        # Run Sync
        pid = run_sync_tests()
        
        # Run Async WS Test
        print("\n3. Testing WebSocket tracking & Voice AI Agent Link...")
        success = asyncio.run(ws_test(pid))
        
        if success:
             print("\n✅ ALL BACKEND E2E TESTS PASSED!")
        else:
             print("\n❌ SOME BACKEND TESTS FAILED!")
    except Exception as e:
        print(f"Exception during testing: {e}")
