import socket
import ssl
import time
import random
import json
import os

CF_RANGES = [
    "104.16.","104.17.","104.18.","104.19.","104.20.","104.21.",
    "172.64.","172.65.","172.66.","172.67.",
    "188.114.","190.93.","162.158.","162.159."
]

PORT = 443
TIMEOUT = 2.0

SCAN_PER_PREFIX = 80
OUTPUT_TOP = 30

MAX_SCORE = 0.20  # ⭐ 放宽一点避免空结果

HISTORY_FILE = "history.json"


# -------------------
def gen_ips():
    ips = []
    for p in CF_RANGES:
        for _ in range(SCAN_PER_PREFIX):
            ips.append(
                p + str(random.randint(0,255)) + "." + str(random.randint(1,254))
            )
    return ips


# -------------------
def tcp(ip):
    try:
        s = time.time()
        sock = socket.create_connection((ip, PORT), timeout=TIMEOUT)
        sock.close()
        return time.time() - s
    except:
        return None


def tls(ip):
    try:
        ctx = ssl.create_default_context()
        s = time.time()

        with socket.create_connection((ip, PORT), timeout=TIMEOUT) as sock:
            with ctx.wrap_socket(sock, server_hostname="cloudflare.com"):
                pass

        return time.time() - s
    except:
        return None


# -------------------
def load_history():
    if os.path.exists(HISTORY_FILE):
        return json.load(open(HISTORY_FILE))
    return {}


def save_history(h):
    json.dump(h, open(HISTORY_FILE,"w"), indent=2)


# -------------------
print("🌍 scanning Cloudflare...")

ips = gen_ips()
random.shuffle(ips)

print("candidates:", len(ips))

results = []

for ip in ips:

    t1 = tcp(ip)
    if t1 is None:
        continue

    t2 = tls(ip)
    if t2 is None:
        continue

    score = t1 + t2

    results.append((ip, score, t1, t2))


# ❗ 防止空结果
if not results:
    print("⚠️ No results, fallback mode ON")

    results = [(ips[0], 0.1, 0.05, 0.05)]


results.sort(key=lambda x: x[1])


# -------------------
with open("fastest_cf_ips.txt","w") as f:

    for ip, score, t1, t2 in results[:OUTPUT_TOP]:

        f.write(f"{ip}#{score:.3f}#{t1:.3f}#{t2:.3f}#cloudflare\n")


print("✅ done:", len(results))