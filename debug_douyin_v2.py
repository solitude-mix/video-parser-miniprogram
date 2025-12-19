import asyncio
import re
import httpx
import requests
from video_parsers import parse_video_share_url

async def test_httpx_no_proxy():
    url = "https://v.douyin.com/YYpUwvatgmA/"
    print(f"\n--- Testing httpx with verify=False and no proxies: {url} ---")
    try:
        async with httpx.AsyncClient(verify=False, proxies={{}}) as client:
            resp = await client.get(url)
            print(f"Status: {resp.status_code}")
            print(f"Headers: {resp.headers}")
    except Exception as e:
        print(f"httpx failed: {e}")

def test_requests():
    url = "https://v.douyin.com/YYpUwvatgmA/"
    print(f"\n--- Testing requests with verify=False: {url} ---")
    try:
        resp = requests.get(url, verify=False)
        print(f"Status: {resp.status_code}")
        print(f"History: {resp.history}")
        print(f"Final URL: {resp.url}")
    except Exception as e:
        print(f"requests failed: {e}")

async def run_original_logic():
    text = "0.53 复制打开抖音，看看【超人强.的作品】我不知道什么人会需要快应用这种东西# 手机使用技巧... https://v.douyin.com/YYpUwvatgmA/ 11/13 icn:/ Z@m.QK"
    print(f"\n--- Running Original Logic for: {text} ---")
    
    url_reg = re.compile(r"http[s]?://[\w.-]+[\w\/-]*[\w.-]*\??[\w=&:\-\+\%]*[/]*")
    match = url_reg.search(text)
    if not match:
        print("Regex failed to match URL")
        return
    
    video_share_url = match.group()
    print(f"Extracted URL: {video_share_url}")

    try:
        video_info = await parse_video_share_url(video_share_url)
        print("Parsing successful!")
        print(video_info.__dict__)
    except Exception as e:
        print(f"Parsing failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(test_httpx_no_proxy())
    test_requests()
    # asyncio.run(run_original_logic())
