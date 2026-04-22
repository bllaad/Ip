import requests
import time
import random

# 🌐 多IP来源（带来源名称）
SOURCES = {
    "zip": "https://zip.cm.edu.kg/all.txt",
    "speedx": "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "shifty": "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "clarketm": "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt"
}

TEST_URL = "http://httpbin.org/get"


def load_ips():
    ip_map = {}

    for source_name, url in SOURCES.items():
        print("Loading:", source_name)

        try:
            text = requests.get(url, timeout=15).text

            for line in text.splitlines():
                line = line.strip()

                if ":" in line:
                    ip = line.split()[0]

                    # 去重（优先保留第一次出现的来源）
                    if ip not in ip_map:
                        ip_map[ip] = source_name

        except Exception as e:
            print("Load failed:", source_name)

    return ip_map


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

        if r.status_code == 200 and "origin" in r.text:
            return True, latency

        return False, None

    except:
        return False, None


print("Loading proxy sources...")

ip_map = load_ips()

ips = list(ip_map.keys())

random.shuffle(ips)

print("TOTAL IPS:", len(ips))

good = []

# 🔥 GitHub Actions 推荐测试数量
TEST_LIMIT = 300

for ip in ips[:TEST_LIMIT]:

    ok, latency = test_ip(ip)

    if ok:
        source = ip_map[ip]

        print("OK:", ip, latency, source)

        good.append((ip, latency, source))

    else:
        print("FAIL:", ip)


# 📊 按延迟排序
good.sort(key=lambda x: x[1])


print("GOOD IPS:", len(good))


# 💾 输出最终格式
with open("good_ips.txt", "w") as f:

    for ip, lat, source in good:

        f.write(f"{ip}#{lat:.2f}#{source}\n")


print("Saved good_ips.txt successfully")