import os
import requests
import sys

print("--- Network Diagnostic ---")
print("Current Environment Variables:")
for k in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy", "all_proxy", "ALL_PROXY", "NO_PROXY", "no_proxy"]:
    print(f"{k}: {os.environ.get(k)}")

# EastMoney API URL from the error log
url = "https://82.push2.eastmoney.com/api/qt/clist/get?pn=1&pz=100&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f12&fs=m%3A0+t%3A6%2Cm%3A0+t%3A80%2Cm%3A1+t%3A2%2Cm%3A1+t%3A23%2Cm%3A0+t%3A81+s%3A2048&fields=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6%2Cf7%2Cf8%2Cf9%2Cf10%2Cf12%2Cf13%2Cf14%2Cf15%2Cf16%2Cf17%2Cf18%2Cf20%2Cf21%2Cf23%2Cf24%2Cf25%2Cf22%2Cf11%2Cf62%2Cf128%2Cf136%2Cf115%2Cf152"

print(f"\nTesting connection to EastMoney API...")
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    resp = requests.get(url, headers=headers, timeout=10)
    print(f"Direct Request Status Code: {resp.status_code}")
    print(f"Content length: {len(resp.content)}")
except Exception as e:
    print(f"Direct Request Error: {e}")

print("\nTesting connection to Baidu (Connectivity Check)...")
try:
    resp = requests.get("https://www.baidu.com", timeout=5)
    print(f"Baidu Status Code: {resp.status_code}")
except Exception as e:
    print(f"Baidu Error: {e}")

print("\nChecking detected proxies...")
try:
    from requests.utils import get_environ_proxies
    print(f"Detected proxies for url: {get_environ_proxies(url)}")
except Exception as e:
    print(f"Error checking proxies: {e}")

print("\nTesting Sina API (HTTP) with Headers...")
try:
    # Sina uses HTTP, which avoids SSL/TLS issues
    sina_url = "http://hq.sinajs.cn/list=sh600519"
    sina_headers = {
        "Referer": "https://finance.sina.com.cn/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    resp = requests.get(sina_url, headers=sina_headers, timeout=10, proxies={"http": None, "https": None})
    print(f"Sina Status Code: {resp.status_code}")
    # Sina returns GBK encoding usually
    print(f"Sina Content: {resp.content.decode('gbk')[:100]}...")
except Exception as e:
    print(f"Sina Error: {e}")

print("\nTesting EastMoney with verify=False AND proxies=None...")
try:
    resp = requests.get(url, headers=headers, timeout=10, verify=False, proxies={"http": None, "https": None})
    print(f"EastMoney (No SSL) Status Code: {resp.status_code}")
except Exception as e:
    print(f"EastMoney (No SSL) Error: {e}")
