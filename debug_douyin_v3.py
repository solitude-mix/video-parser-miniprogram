import asyncio
import httpx
import requests

async def test_httpx_trust_env_false():
    url = "https://v.douyin.com/YYpUwvatgmA/"
    print(f"\n--- Testing httpx with verify=False, trust_env=False: {url} ---")
    try:
        # httpx 0.23+ 使用 trust_env=False 来忽略系统代理
        async with httpx.AsyncClient(verify=False, trust_env=False) as client:
            resp = await client.get(url)
            print(f"Status: {resp.status_code}")
            print(f"Location Header: {resp.headers.get('location')}")
    except Exception as e:
        print(f"httpx failed: {e}")

def test_requests_trust_env_false():
    url = "https://v.douyin.com/YYpUwvatgmA/"
    print(f"\n--- Testing requests with verify=False, trust_env=False: {url} ---")
    try:
        s = requests.Session()
        s.trust_env = False
        s.verify = False
        resp = s.get(url)
        print(f"Status: {resp.status_code}")
        print(f"Final URL: {resp.url}")
    except Exception as e:
        print(f"requests failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_httpx_trust_env_false())
    test_requests_trust_env_false()