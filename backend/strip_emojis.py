import re
with open('app/main.py', 'r', encoding='utf-8') as f:
    content = f.read()
content = re.sub(r'[^\x00-\x7F]', '', content)
with open('app/main.py', 'w', encoding='utf-8') as f:
    f.write(content)