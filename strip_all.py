import os, re
for root, dirs, files in os.walk('backend/app'):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as file:
                c = file.read()
            c = re.sub(r'[^\x00-\x7F]', '', c)
            with open(path, 'w', encoding='utf-8') as file:
                file.write(c)