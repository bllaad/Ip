import socket
import ssl
import time
import random

TIMEOUT = 2.0
OUTPUT_TOP = 20

# 常见 Cloudflare 端口
PORTS = [443, 2053, 2083, 2087, 2096, 8443]

# 国家模拟段（经验优选段）
REGIONS = {

    "US": ["104.16.", "104.17."],

    "JP": ["172.64.", "172.65."],

    "KR": ["162.158.", "162.159."],

    "SG": ["188.114.", "190.93."],

    "HK": ["141.101.", "108.162."],

    "TW": ["173.245.", "198.41."],

    "NL": ["103.102.228."]

}


def generate_ips(prefixes):

    ips = []

    for prefix in prefixes:

        for _ in range(50):

            ip = (
                prefix
                + str(random.randint(0,255))
                + "."
                + str(random.randint(1,254))
            )

            ips.append(ip)

    return ips


def tcp_latency(ip, port):

    try:

        start = time.time()

        sock = socket.create_connection(
            (ip, port),
            timeout=TIMEOUT
        )

        sock.close()

        return time.time() - start

    except:

        return None


def tls_latency(ip, port):

    try:

        ctx = ssl.create_default_context()

        start = time.time()

        with socket.create_connection(
            (ip, port),
            timeout=TIMEOUT
        ) as sock:

            with ctx.wrap_socket(
                sock,
                server_hostname="cloudflare.com"
            ):

                pass

        return time.time() - start

    except:

        return None


def test_region(region, prefixes):

    print("Testing:", region)

    ips = generate_ips(prefixes)

    random.shuffle(ips)

    results = []

    for ip in ips:

        for port in PORTS:

            tcp = tcp_latency(ip, port)

            if tcp is None:
                continue

            tls = tls_latency(ip, port)

            if tls is None:
                continue

            score = tcp + tls

            results.append((ip, port, score))

    results.sort(key=lambda x: x[2])

    return results


print("🌍 Multi-country scan start")

all_results = []

for region, prefixes in REGIONS.items():

    results = test_region(region, prefixes)

    filename = f"fastest_{region}.txt"

    with open(filename, "w") as f:

        for ip, port, score in results[:OUTPUT_TOP]:

            line = f"{ip}:{port}#{region}\n"

            f.write(line)

            all_results.append(line)


# 合并输出总列表

with open("fastest_all.txt", "w") as f:

    for line in all_results:

        f.write(line)


print("✅ Done")