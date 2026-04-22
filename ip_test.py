import requests
import time
import random

# 🌐 多源IP（关键升级点）
SOURCES = [
    "https://zip.cm.edu.kg/all.txt",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt"
]

def load_ips():
    ips = set()

    for url in SOURCES:
        try:
            text = requests.get(url, timeout=15).text
            for line in text.splitlines():
                line = line.strip()
                if ":" in line:
                    # 清洗非法字符
                    ip = line.split()[0]
                    ips.add(ip)
        except:
            pass

    return list(ips)

# 🔥 更稳定测试目标（比 ipify 稳）
TEST_URL = "http://httpbin.org/get"

def test_ip(ip):
    proxies = {
        "http": f"http://{ip}",
        "https": f"http://{ip}",
    }

    try:
        start = time.time()

        r = requests.get(
            TEST_URL,
            proxies=proxies,
            timeout=8
        )

        latency = time.time() - start

        # 二次验证（防假成功）
        if r.status_code == 200 and "origin" in r.text:
            return True, latency

        return False, None

    except:
        return False, None


ips = load_ips()
random.shuffle(ips)

print("TOTAL IPS:", len(ips))

good = []

# 🔥 稳定关键：多一点测试数量
for ip in ips[:300]:

    ok, latency = test_ip(ip)

    if ok:
        print("[OK]", ip, round(latency, 2))
        good.append((ip, latency))
    else:
        print("[FAIL]", ip)

# 📊 排序（延迟优先）
good.sort(key=lambda x: x[1])

# 💾 输出结果
with open("good_ips.txt", "w") as f:
    for ip, lat in good:
        f.write(f"{ip}|{lat:.2f}\n")

print("\nFINAL GOOD IPS:", len(good))