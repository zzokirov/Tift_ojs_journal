import glob

# Windows cp1252 → Unicode: to'liq reverse mapping
# cp1252 ning har bir bayti uchun Unicode codepoint → cp1252 bayt
reverse_cp1252 = {}
for byte_val in range(256):
    try:
        char = bytes([byte_val]).decode('cp1252')
        reverse_cp1252[ord(char)] = byte_val
    except Exception:
        pass  # Undefined cp1252 bytes (0x81, 0x8D, 0x8F, 0x90, 0x9D)

# Undefined cp1252 baytlari uchun: PowerShell ularni U+xx (xuddi shu byte) sifatida saqlaydi
for undefined_byte in [0x81, 0x8D, 0x8F, 0x90, 0x9D]:
    reverse_cp1252[undefined_byte] = undefined_byte


def fix_double_encoding_v3(content_bytes):
    """
    PowerShell UTF-8 faylni cp1252 sifatida o'qib, UTF-8 sifatida saqlagan.
    Bu funksiya shu jarayonni to'liq teskari bajaradi.
    """
    try:
        text = content_bytes.decode('utf-8')
    except UnicodeDecodeError:
        return content_bytes

    raw_bytes = bytearray()
    for char in text:
        cp = ord(char)
        if cp in reverse_cp1252:
            # Bu character cp1252 da mavjud — original baytga qaytarish
            raw_bytes.append(reverse_cp1252[cp])
        else:
            # cp1252 da yo'q — original UTF-8 bayt sifatida saqlash
            raw_bytes.extend(char.encode('utf-8'))

    try:
        result = raw_bytes.decode('utf-8')
        return result.encode('utf-8')
    except UnicodeDecodeError:
        result = raw_bytes.decode('utf-8', errors='replace')
        return result.encode('utf-8')


po_files = glob.glob('locale/**/*.po', recursive=True)
for path in po_files:
    with open(path, 'rb') as f:
        original = f.read()

    fixed = fix_double_encoding_v3(original)

    with open(path, 'wb') as f:
        f.write(fixed)
    print(f'Fixed: {path}')

# Tekshirish - to'g'ri baytlarmi?
print('\nVerification (locale/ru/LC_MESSAGES/django.po):')
with open('locale/ru/LC_MESSAGES/django.po', 'rb') as f:
    lines = f.read().split(b'\n')

for line in lines[9:25]:
    if line.startswith(b'msgstr') and len(line) > 12:
        try:
            decoded = line.decode('utf-8')
            print('  OK:', decoded[:60])
        except Exception as e:
            print('  ERR:', line[:40], e)

print('\nDone!')
