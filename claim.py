import requests
import json
import time
import random
from itertools import cycle
import os

url = 'https://mbscan.io/airdrop'
headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',  # Example User-Agent, replace with yours if needed
    'Referer': 'https://mbscan.io/'
}

address_file = 'address.txt'
proxy_file = 'proxies.txt'
wait_time_between_claims = 2  # Fixed wait time between individual claims
min_wait_before_cycle = 5  # Minimum wait before the next cycle (seconds)
max_wait_before_cycle = 10  # Maximum wait before the next cycle (seconds)

def get_proxies(file_path):
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        try:
            with open(file_path, 'r') as f:
                proxies = [line.strip() for line in f if line.strip()]
            return cycle(proxies)
        except FileNotFoundError:
            print(f"Warning: The file '{file_path}' was not found, not using proxies.")
            return None
    else:
        print(f"Warning: The file '{file_path}' is empty or does not exist, not using proxies.")
        return None

proxy_pool = get_proxies(proxy_file)
use_proxies = proxy_pool is not None

while True:
    try:
        with open(address_file, 'r') as f:
            for line in f:
                address = line.strip()
                if address:
                    request_kwargs = {}
                    proxy_used = "No proxy"

                    if use_proxies:
                        proxy = next(proxy_pool)
                        proxies = {'http': proxy, 'https': proxy}
                        request_kwargs['proxies'] = proxies
                        proxy_used = proxy

                    payload = json.dumps({'address': address})
                    try:
                        response = requests.post(url, headers=headers, data=payload, **request_kwargs)
                        response.raise_for_status()
                        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Claim sent for address: {address} using proxy: {proxy_used}")
                        print(response.text)
                    except requests.exceptions.RequestException as e:
                        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error for address {address} using proxy {proxy_used}: {e}")
                        if 'response' in locals() and response is not None:
                            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}]   Status code: {response.status_code}")
                            print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}]   Response: {response.text}")

                    time.sleep(wait_time_between_claims)  # Fixed wait time between claims

        # Introduce random waiting time before the next cycle
        wait_before_cycle = random.uniform(min_wait_before_cycle, max_wait_before_cycle)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] All addresses in '{address_file}' processed. Waiting for {wait_before_cycle:.2f} seconds before next cycle...")
        time.sleep(wait_before_cycle)

    except FileNotFoundError:
        print(f"Error: The file '{address_file}' was not found.")
        break
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        break
