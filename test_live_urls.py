
import urllib.request, ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

urls = [
    'https://architect-edu.tift.uz/moliya-va-intellektual-texnologiyalar/',
    'https://architect-edu.tift.uz/moliya%20va%20intelektual%20texnologiyalar/',
    'https://architect-edu.tift.uz/moliya%20va%20intellektual%20texnologiyalar/',
]

for url in urls:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as r:
            print(f'{url} -> {r.status} {r.reason}')
    except urllib.error.HTTPError as e:
        print(f'{url} -> HTTP ERROR: {e.code} {e.reason}')
    except Exception as e:
        print(f'{url} -> EXCEPTION: {e}')
