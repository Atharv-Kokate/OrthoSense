import json

def fix():
    with open("backend/app/main.py", "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    skip = False
    for i, line in enumerate(lines):
        if "raw_data = await websocket.receive_text()" in line:
            new_lines.append(line)
            correct_logic = """            features = json.loads(raw_data)
            
            # --- 2-WAY PATIENT VOICE COMMUNICATION TRAP ---
            if "patient_vocal_command" in features:
                patient_quote = features["patient_vocal_command"]
                accumulated_errors.append({
                    "type": "Patient Verbal Intervention",
                    "severity": 1.0,
                    "clinical_target": "Listen to Patient",
                    "achieved": f"Patient said: '{patient_quote}'"
                })
                
                # Generate an immediate, empathetic AI response based on what they said
                vocal_response = await generate_patient_feedback(
                    patient_first_name=patient_name,
                    exercise=exercise,
                    current_rep=rep_count,
                    target_reps=target_reps,
                    errors=accumulated_errors,
                    is_fatigued=False,
                    fatigue_metrics=None
                )
                
                await websocket.send_json({
                    "status": "tracking",
                    "lstm_confidence": 1.0,
                    "errors": accumulated_errors,
                    "llm_feedback": vocal_response,
                    "rep_count": rep_count
                })
                
                # Pause briefly so AI can speak without tracking overlap
                await asyncio.sleep(3)
                continue

            # 4. Math extraction and ML Buffering
            if "angles" not in features:
                continue
                
            current_knee_angle = (features["angles"]["left_knee"] + features["angles"]["right_knee"]) / 2.0
            buffer.add(features)
            seq = buffer.get_lstm_sequence()
            
            if len(seq) == buffer.maxlen:
                # 5. Continuous AI monitoring
                errors, lstm_confidence = expert_lstm.analyze(seq)
                
                # Squat going down -> Started a Rep!
                if current_knee_angle < engagement_threshold:
                    is_in_rep = True
                    if current_knee_angle < lowest_knee_angle:
                        lowest_knee_angle = current_knee_angle

                # Squat coming back up -> Rep Completed!
                elif current_knee_angle > 160 and is_in_rep:
                    rep_count += 1
                    
                    # Check if they failed to reach their Doctor's prescribed Golden Rep target depth
                    if lowest_knee_angle > target_rom_degrees:
                        accumulated_errors.append({
                            "type": "Insufficient Depth",
                            "severity": round((lowest_knee_angle - target_rom_degrees) / 10.0, 2),
                            "clinical_target": target_rom_degrees,
                            "achieved": round(lowest_knee_angle, 2)
                        })

                    # Compute Rep Form Score for fatigue tracking
                    rep_penalty = sum([err.get("severity", 0.5) * 5 for err in accumulated_errors])
                    rep_form_score = max(0.0, 100.0 - rep_penalty * 4)
                    buffer.add_rep_metric(lowest_knee_angle, rep_form_score)
                    
                    # Check Fatigue (Mid-Session Intervention)
                    is_fatigued, fatigue_metrics = buffer.check_fatigue_degradation(window=3, threshold=15.0)
                    if is_fatigued and rep_count < target_reps:
                        target_reps = rep_count  # End session early
                        accumulated_errors.append({
                            "type": "Session Interrupted: Muscular Fatigue Detected",
                            "severity": 1.0,
                            "clinical_target": "Safe Continuation",
                            "achieved": "Degraded Form"
                        })
                        last_llm_response_for_rep = await generate_patient_feedback(
                            patient_first_name=patient_name,
                            exercise=exercise,
                            current_rep=rep_count,
                            target_reps=target_reps,
                            errors=accumulated_errors,
                            is_fatigued=True,
                            fatigue_metrics=fatigue_metrics
                        )

                    # Write to Medical Record Database!
                    log_repetition(
                        db=db,
                        session_id=telemetry_session.id,
                        rep_number=rep_count,
                        max_rom_achieved=lowest_knee_angle,
                        errors=accumulated_errors,
                        ai_feedback=last_llm_response_for_rep
                    )

                    # Reset rep state
                    is_in_rep = False
                    lowest_knee_angle = 180.0
                    accumulated_errors = []
                    # Keep final intervention message if we stopped, else clear
                    if not is_fatigued:
                        last_llm_response_for_rep = ""
                    
                if errors:
                    # Append new distinct errors to the current rep tracking
                    for err in errors:
                        if not any(e["type"] == err["type"] for e in accumulated_errors):
                            accumulated_errors.append(err)
                
                response_payload = {
                    "status": "tracking",
                    "lstm_confidence": lstm_confidence,
                    "errors": errors,
                    "llm_feedback": last_llm_response_for_rep if last_llm_response_for_rep else None,
                    "rep_count": rep_count
                }

                # 7. Only generate conversational LLM feedback if there are errors and outside cooldown
                current_time = time.time()
                if last_llm_response_for_rep:
                    last_llm_time = current_time # Reset cooldown to prioritize the fatigue/rep completion message
                elif errors and (current_time - last_llm_time > feedback_cooldown):
                    natural_response = await generate_patient_feedback(
                        patient_first_name=patient_name,
                        exercise=exercise,
                        current_rep=rep_count,
                        target_reps=target_reps,
                        errors=errors,
                        is_fatigued=False,
                        fatigue_metrics=None
                    )
                    response_payload["llm_feedback"] = natural_response
                    last_llm_response_for_rep = natural_response # save to log in DB at end of rep
                    last_llm_time = current_time

                await websocket.send_json(response_payload)

                # Check for session completion
                if rep_count >= target_reps:
                    try:
                        new_rx = evaluate_patient_adaptation(db, patient_id, exercise)
                        await websocket.send_json({
                            "status": "completed",
                            "message": "Workout finished.",
                            "llm_feedback": "Workout complete. Saving your clinical progress."
                        })
                    except Exception as e:
                        print(f"Error completing session: {e}")

                    await asyncio.sleep(2) # Give frontend enough time to read the message and speak BEFORE closing
                    await websocket.close()
                    break # Terminate session loop cleanly
            else:
                # Buffer is still filling up (first 1 second)
                await websocket.send_json({"status": "buffering", "message": "Gathering AI baseline..."})
"""
            new_lines.append(correct_logic + "\n")
            skip = True
        elif skip and "except WebSocketDisconnect:" in line:
            skip = False
            new_lines.append(line)
        elif not skip:
            new_lines.append(line)

    with open("backend/app/main.py", "w", encoding="utf-8") as f:
        f.writelines(new_lines)
    print("Reconstructed main.py successfully!")

if __name__ == "__main__":
    fix()
