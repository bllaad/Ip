import socket
import ssl
import time
import random

PORT = 443
TIMEOUT = 2.0

OUTPUT_TOP = 20


# 🌍 各地区 Cloudflare 常见段（经验段）
REGIONS = {

    "us": [
        "104.16.", "104.17.", "104.18."
    ],

    "jp": [
        "172.64.", "172.65."
    ],

    "kr": [
        "162.158.", "162.159."
    ],

    "sg": [
        "188.114.", "190.93."
    ],

    "hk": [
        "141.101.", "108.162."
    ],

    "tw": [
        "173.245.", "198.41."
    ]

}


def generate_ips(prefixes):

    ips = []

    for prefix in prefixes:

        for _ in range(80):

            ip = (
                prefix
                + str(random.randint(0,255))
                + "."
                + str(random.randint(1,254))
            )

            ips.append(ip)

    return ips


def tcp_latency(ip):

    try:

        start = time.time()

        sock = socket.create_connection(
            (ip, PORT),
            timeout=TIMEOUT
        )

        sock.close()

        return time.time() - start

    except:

        return None


def tls_latency(ip):

    try:

        ctx = ssl.create_default_context()

        start = time.time()

        with socket.create_connection(
            (ip, PORT),
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

    print("Testing region:", region)

    ips = generate_ips(prefixes)

    random.shuffle(ips)

    results = []

    for ip in ips:

        tcp = tcp_latency(ip)

        if tcp is None:
            continue

        tls = tls_latency(ip)

        if tls is None:
            continue

        score = tcp + tls

        results.append((ip, score, tcp, tls))

    results.sort(key=lambda x: x[1])

    return results


print("🌍 Multi-country CF scan start")


for region, prefixes in REGIONS.items():

    results = test_region(region, prefixes)

    filename = f"fastest_{region}.txt"

    with open(filename, "w") as f:

        for ip, score, tcp, tls in results[:OUTPUT_TOP]:

            f.write(
                f"{ip}#"
                f"{score:.3f}#"
                f"{tcp:.3f}#"
                f"{tls:.3f}#cloudflare\n"
            )


print("✅ Multi-country scan done")