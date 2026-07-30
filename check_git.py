import subprocess

for commit in ['b4d13a3', 'cdfb2a3', '25e3e6d', '478516a', '08b8901', 'HEAD']:
    print(f"--- Commit: {commit} ---")
    res = subprocess.run(['git', 'cat-file', '-p', f'{commit}:locale/ru/LC_MESSAGES/django.po'], capture_output=True)
    if res.returncode != 0:
        print("Not found or error")
        continue
    data = res.stdout
    lines = data.split(b'\n')
    count = 0
    for line in lines:
        if line.startswith(b'msgstr ') and len(line) > 12:
            print(f'Bytes: {line[:50]}')
            try:
                print(f'Decoded: {line.decode("utf-8")[:30]}')
            except Exception as e:
                print(f'Decode error: {e}')
            count += 1
            if count >= 2:
                break
