import requests
import time

SOURCE_URL = "https://zip.cm.edu.kg/all.txt"

def load_ips():
    text = requests.get(SOURCE_URL, timeout=10).text
    return [x.strip() for x in text.splitlines() if ":" in x]

def test_ip(ip):
    proxies = {
        "http": f"http://{ip}",
        "https": f"http://{ip}",
    }
    try:
        start = time.time()
        r = requests.get("https://api.ipify.org", proxies=proxies, timeout=5)
        latency = time.time() - start
        return True, latency
    except:
        return False, None

def main():
    ips = load_ips()
    good = []

    print(f"Total IPs: {len(ips)}")

    for ip in ips[:200]:  # 防止GitHub跑太慢（可改）
        ok, latency = test_ip(ip)
        if ok:
            print(f"[OK] {ip} {latency:.2f}s")
            good.append((ip, latency))
        else:
            print(f"[FAIL] {ip}")

    # 排序：延迟优先
    good.sort(key=lambda x: x[1])

    with open("good_ips.txt", "w") as f:
        for ip, lat in good:
            f.write(f"{ip}|{lat:.2f}\n")

    print(f"Good IPs: {len(good)}")

if __name__ == "__main__":
    main()