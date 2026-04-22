import socket
import time
import random

# 🌍 Cloudflare 全球常见 CDN 高频段
CF_PREFIXES = [
    "104.16.",
    "104.17.",
    "104.18.",
    "104.19.",
    "104.20.",
    "104.21.",
    "172.64.",
    "172.65.",
    "172.66.",
    "172.67.",
    "188.114.",
    "190.93.",
    "162.158.",
    "162.159.",
    "198.41."
]

PORT = 443
TIMEOUT = 1.2

SCAN_PER_PREFIX = 60
OUTPUT_TOP = 30


def generate_candidates():
    ips = []

    for prefix in CF_PREFIXES:

        for _ in range(SCAN_PER_PREFIX):

            ip = (
                prefix
                + str(random.randint(0, 255))
                + "."
                + str(random.randint(1, 254))
            )

            ips.append(ip)

    return ips


def test_latency(ip):

    try:

        start = time.time()

        sock = socket.create_connection(
            (ip, PORT),
            timeout=TIMEOUT
        )

        sock.close()

        latency = time.time() - start

        return latency

    except:

        return None


print("🌍 Generating Cloudflare candidates...")

candidates = generate_candidates()

random.shuffle(candidates)

print("Total candidates:", len(candidates))


results = []

for ip in candidates:

    latency = test_latency(ip)

    if latency:

        print("✅", ip, latency)

        results.append((ip, latency))

    else:

        print("❌", ip)


print("Sorting results...")

results.sort(key=lambda x: x[1])


print("Fastest found:", len(results))


with open("fastest_cf_ips.txt", "w") as f:

    for ip, latency in results[:OUTPUT_TOP]:

        f.write(f"{ip}#{latency:.3f}#cloudflare\n")


print("Saved fastest_cf_ips.txt ✅")