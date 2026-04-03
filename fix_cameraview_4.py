import sys

with open('frontend/src/components/CameraView.jsx', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Remove import
text = text.replace("import VideoConsultation from './VideoConsultation';\n", "")
# 2. Remove isTeleRehab declaration
text = text.replace("const isTeleRehab = location.state?.isTeleRehab || false;\n", "")
# 3. Remove muteVoice
text = text.replace(", { muteVoice: isTeleRehab }", "")
# 4. Fix speech synthesis
text = text.replace("if (!isTeleRehab && 'speechSynthesis' in window)", "if ('speechSynthesis' in window)")

start_idx = text.find('{isTeleRehab && (')
if start_idx != -1:
    paren_count = 0
    end_idx = -1
    for i in range(start_idx, len(text)):
        if text[i] == '{':
            paren_count += 1
        elif text[i] == '}':
            paren_count -= 1
            if paren_count == 0:
                end_idx = i
                break
    if end_idx != -1:
        text = text[:start_idx] + text[end_idx+1:]
        
with open('frontend/src/components/CameraView.jsx', 'w', encoding='utf-8') as f:
    f.write(text)
print("Done")