import socket
import ssl
import time
import random
import http.client
import json
import os

# 🌍 Cloudflare ASN常见公网段（动态扫描基础）
CF_RANGES = [
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
    "162.158.",
    "162.159.",
    "188.114.",
    "190.93.",
    "198.41.",
    "141.101.",
    "108.162.",
    "173.245."
]

PORT = 443
TIMEOUT = 1.5

SCAN_PER_PREFIX = 60
OUTPUT_TOP = 30

MAX_SCORE = 0.12  # ⭐ 自动过滤阈值

HISTORY_FILE = "history.json"


# ---------------------------
# 生成候选IP（ASN动态扫描）
# ---------------------------
def generate_candidates():
    ips = []
    for prefix in CF_RANGES:
        for _ in range(SCAN_PER_PREFIX):
            ip = (
                prefix
                + str(random.randint(0, 255))
                + "."
                + str(random.randint(1, 254))
            )
            ips.append(ip)
    return ips


# ---------------------------
# TCP测速
# ---------------------------
def tcp_latency(ip):
    try:
        start = time.time()
        sock = socket.create_connection((ip, PORT), timeout=TIMEOUT)
        sock.close()
        return time.time() - start
    except:
        return None


# ---------------------------
# TLS测速
# ---------------------------
def tls_latency(ip):
    try:
        context = ssl.create_default_context()
        start = time.time()

        with socket.create_connection((ip, PORT), timeout=TIMEOUT) as sock:
            with context.wrap_socket(sock, server_hostname="cloudflare.com"):
                pass

        return time.time() - start
    except:
        return None


# ---------------------------
# HTTP测速
# ---------------------------
def http_latency(ip):
    try:
        start = time.time()
        conn = http.client.HTTPSConnection(ip, timeout=TIMEOUT)
        conn.request("HEAD", "/")
        conn.getresponse()
        conn.close()
        return time.time() - start
    except:
        return None


# ---------------------------
# 读取历史数据
# ---------------------------
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {}


# ---------------------------
# 保存历史数据
# ---------------------------
def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


# ---------------------------
# 主程序
# ---------------------------
print("🌍 Cloudflare ASN scan start...")

candidates = generate_candidates()
random.shuffle(candidates)

print("Candidates:", len(candidates))

history = load_history()

results = []


for ip in candidates:

    tcp = tcp_latency(ip)
    if tcp is None:
        continue

    tls = tls_latency(ip)
    if tls is None:
        continue

    http = http_latency(ip)
    if http is None:
        continue

    score = tcp + tls + http

    results.append((ip, score, tcp, tls, http))


# 排序
results.sort(key=lambda x: x[1])


# ---------------------------
# 写 fastest（本次最快）
# ---------------------------
with open("fastest_cf_ips.txt", "w") as f:

    for ip, score, tcp, tls, http in results[:OUTPUT_TOP]:

        f.write(
            f"{ip}#"
            f"{score:.3f}#"
            f"{tcp:.3f}#"
            f"{tls:.3f}#"
            f"{http:.3f}#cloudflare\n"
        )


# ---------------------------
# 写 stable + 更新历史
# ---------------------------
stable = []

for ip, score, tcp, tls, http in results:

    if score > MAX_SCORE:
        continue

    # 更新历史
    if ip not in history:
        history[ip] = {
            "count": 0,
            "total": 0.0
        }

    history[ip]["count"] += 1
    history[ip]["total"] += score

    avg = history[ip]["total"] / history[ip]["count"]

    stable.append((ip, avg, history[ip]["count"]))


# 排序：稳定性优先 + 平均延迟
stable.sort(key=lambda x: x[1])


with open("stable_cf_ips.txt", "w") as f:

    for ip, avg, count in stable[:OUTPUT_TOP]:

        f.write(
            f"{ip}#"
            f"{avg:.3f}#"
            f"count={count}#cloudflare\n"
        )


# 保存历史
save_history(history)


print("✅ Done")
print("Fast:", len(results))
print("Stable:", len(stable))