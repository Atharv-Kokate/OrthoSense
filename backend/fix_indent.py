import sys

def fix_main_py():
    with open('backend/app/main.py', 'r') as f:
        content = f.read()

    # The buggy string that we need to replace
    # From "await asyncio.sleep(3)" to the end of the while loop before WebSocketDisconnect exception
    bad_part = """                await asyncio.sleep(3)
                continue

                is_in_rep = True
                if current_knee_angle < lowest_knee_angle:
                    lowest_knee_angle = current_knee_angle

            # Squat coming back up -> Rep Completed!
            elif current_knee_angle > 160 and is_in_rep:"""

    good_part = """                await asyncio.sleep(3)
                continue

            # 4. Mathematical Buffering
            try:
                current_knee_angle = (features["angles"]["left_knee"] + features["angles"]["right_knee"]) / 2.0
            except KeyError:
                continue
            
            buffer.add(features)
            seq = buffer.get_lstm_sequence()

            if len(seq) == buffer.maxlen:
                errors, lstm_confidence = expert_lstm.analyze(seq)

                # Squat going down -> Started a Rep!
                if current_knee_angle < engagement_threshold:
                    is_in_rep = True
                    if current_knee_angle < lowest_knee_angle:
                        lowest_knee_angle = current_knee_angle

                # Squat coming back up -> Rep Completed!
                elif current_knee_angle > 160 and is_in_rep:"""

    if bad_part in content:
        content = content.replace(bad_part, good_part)
        print("Replaced chunk 1")
    else:
        print("Chunk 1 not found!")
        
    # We must also indent everything from `rep_count += 1` to `break # Terminate session loop cleanly`
    # Let's do it line by line inside the `if len(seq) == buffer.maxlen:` block.
    
    lines = content.split('\n')
    new_lines = []
    in_block = False
    
    for i, line in enumerate(lines):
        if line.endswith("elif current_knee_angle > 160 and is_in_rep:"):
            in_block = True
            new_lines.append(line)
            continue
            
        if in_block:
            if line.startswith("            else:"):
                in_block = False
                new_lines.append("            else:")
                continue
            
            # If the line is already indented 16 spaces properly (like `rep_count += 1`), it should be 20 spaces?
            # Wait, `elif current_knee_angle > 160 and is_in_rep:` is indented 16 spaces.
            # So its contents should be 20 spaces.
            # Let's just indent everything that starts with 16 spaces by +4 spaces until `else:`
            if line.startswith("                "):
                pass
                # wait, let's just add 4 spaces
                # line = "    " + line
                
        new_lines.append(line)

    with open('backend/app/main.py', 'w') as f:
        f.write("\n".join(new_lines))
        print("Done writing main.py")

if __name__ == "__main__":
    fix_main_py()