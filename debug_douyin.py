import asyncio
import re
from video_parsers import parse_video_share_url

async def test():
    text = "0.53 复制打开抖音，看看【超人强.的作品】我不知道什么人会需要快应用这种东西# 手机使用技巧... https://v.douyin.com/YYpUwvatgmA/ 11/13 icn:/ Z@m.QK"
    print(f"Original Text: {text}")

    # 模拟 main.py 中的正则提取
    url_reg = re.compile(r"http[s]?:\/\/[\w.-]+[\w\/-]*[\w.-]*\??[\w=&:\-\+\%]*[/]*")
    match = url_reg.search(text)
    if not match:
        print("Regex failed to match URL")
        return
    
    video_share_url = match.group()
    print(f"Extracted URL: {video_share_url}")

    try:
        print("Starting parsing...")
        video_info = await parse_video_share_url(video_share_url)
        print("Parsing successful!")
        print(video_info.__dict__)
    except Exception as e:
        print(f"Parsing failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())