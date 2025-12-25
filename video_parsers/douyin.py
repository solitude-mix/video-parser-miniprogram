import json
import re
import secrets
import string
from urllib.parse import parse_qs, urlparse

import httpx

from .base import BaseParser, ImgInfo, VideoAuthor, VideoInfo


class DouYin(BaseParser):
    """
    抖音 / 抖音火山版
    """

    async def parse_share_url(self, share_url: str) -> VideoInfo:
        # 解析URL获取域名
        parsed_url = urlparse(share_url)
        host = parsed_url.netloc

        if host in ["www.iesdouyin.com", "www.douyin.com"]:
            # 支持电脑网页端链接
            video_id = self._parse_video_id_from_path(share_url)
            if not video_id:
                raise ValueError("Failed to parse video ID from PC share URL")
            share_url = self._get_request_url_by_video_id(video_id)
        elif host == "v.douyin.com":
            # 支持app分享链接 https://v.douyin.com/xxxxxx
            video_id = await self._parse_app_share_url(share_url)
            if not video_id:
                raise ValueError("Failed to parse video ID from app share URL")
            share_url = self._get_request_url_by_video_id(video_id)
        else:
            raise ValueError(f"Douyin not support this host: {host}")

        async with httpx.AsyncClient(follow_redirects=True, verify=False, trust_env=False) as client:
            response = await client.get(share_url, headers=self.get_default_headers())
            response.raise_for_status()

        # 检查是否是图集内容
        is_note = self._is_note_content(response.text, share_url)

        json_data = None
        if is_note:
            # 如果是图集，使用专门的API获取数据
            json_data = await self._get_slides_info(video_id)

        if not json_data:
            # 如果专用API失败或者不是图集，使用标准解析方式
            # 尝试匹配多种可能的 JSON 变量名
            patterns = [
                re.compile(r"window\._ROUTER_DATA\s*=\s*(.*?)</script>", re.DOTALL),
                re.compile(r"window\._SSR_HYDRATED_DATA\s*=\s*(.*?)</script>", re.DOTALL),
                re.compile(r"window\.RENDER_DATA\s*=\s*(.*?)</script>", re.DOTALL),
                re.compile(r'<script id="RENDER_DATA" type="application/json">(.*?)</script>', re.DOTALL),
            ]
            
            find_res = None
            for pattern in patterns:
                find_res = pattern.search(response.text)
                if find_res and find_res.group(1):
                     # 如果是 url encoded 的 json (RENDER_DATA 经常是这样)，需要解码
                    try:
                        raw_json = find_res.group(1).strip()
                        # 尝试直接解析
                        json_data = json.loads(raw_json)
                        break
                    except json.JSONDecodeError:
                        try:
                            # 尝试先 unquote 再解析
                            from urllib.parse import unquote
                            json_data = json.loads(unquote(raw_json))
                            break
                        except:
                            continue

            if not json_data:
                # 记录一下失败时的 HTML 片段，方便调试（仅打印前500字符）
                # print(f"Parse failed. HTML start: {response.text[:500]}")
                raise ValueError("parse video json info from html fail")

        # 处理不同的数据结构
        data = None
        # ... (后续代码处理逻辑需要兼容不同的 json 结构)
        
        # 针对 RENDER_DATA / _SSR_HYDRATED_DATA 结构的适配
        if isinstance(json_data, dict):
            # 1. 尝试匹配 aweme_details (API 返回)
            if "aweme_details" in json_data:
                if len(json_data["aweme_details"]) > 0:
                    data = json_data["aweme_details"][0]
            
            # 2. 尝试匹配 loaderData (旧版 Router Data)
            elif "loaderData" in json_data:
                 # ... (原有的 loaderData 处理逻辑)
                 VIDEO_ID_PAGE_KEY = "video_(id)/page"
                 NOTE_ID_PAGE_KEY = "note_(id)/page"

                 original_video_info = None
                 if VIDEO_ID_PAGE_KEY in json_data["loaderData"]:
                     original_video_info = json_data["loaderData"][VIDEO_ID_PAGE_KEY]["videoInfoRes"]
                 elif NOTE_ID_PAGE_KEY in json_data["loaderData"]:
                     original_video_info = json_data["loaderData"][NOTE_ID_PAGE_KEY]["videoInfoRes"]
                 
                 if original_video_info and "item_list" in original_video_info and len(original_video_info["item_list"]) > 0:
                     data = original_video_info["item_list"][0]

            # 3. 尝试匹配 app.videoDetail (新版 RENDER_DATA 常见结构)
            elif "app" in json_data and "videoDetail" in json_data["app"]:
                 data = json_data["app"]["videoDetail"]
            
            # 4. 尝试直接在根节点找 aweme_detail (部分 SSR 数据)
            elif "aweme_detail" in json_data:
                data = json_data["aweme_detail"]

        if not data:
             # 如果上述都没匹配到，尝试在 loaderData 里做最后的挣扎（防止 key 变了）
             if isinstance(json_data, dict) and "loaderData" in json_data:
                  pass # 已经在上面 loaderData 分支处理过了，这里只是占位
             
             raise Exception("Unknown data structure or failed to extract data")

        # 获取图集图片地址
        images = []
        # 如果data含有 images，并且 images 是一个列表
        if "images" in data and isinstance(data["images"], list):
            # 获取每个图片的url_list中的第一个元素，优先获取非 .webp 格式的图片 url
            for img in data["images"]:
                if (
                    "url_list" in img
                    and isinstance(img["url_list"], list)
                    and len(img["url_list"]) > 0
                ):
                    image_url = self._get_no_webp_url(img["url_list"])
                    if image_url:
                        live_photo_url = ""
                        if (
                            "video" in img
                            and "play_addr" in img["video"]
                            and "url_list" in img["video"]["play_addr"]
                        ):
                            live_photo_url = (
                                img["video"]["play_addr"]["url_list"][0]
                                if img["video"]["play_addr"]["url_list"]
                                else ""
                            )
                        images.append(
                            ImgInfo(url=image_url, live_photo_url=live_photo_url)
                        )

        # 获取视频播放地址
        video_url = ""
        if (
            "video" in data
            and "play_addr" in data["video"]
            and "url_list" in data["video"]["play_addr"]
        ):
            video_url = data["video"]["play_addr"]["url_list"][0].replace(
                "playwm", "play"
            )

        # 如果图集地址不为空时，因为没有视频，上面抖音返回的视频地址无法访问，置空处理
        if len(images) > 0:
            video_url = ""

        # 获取重定向后的mp4视频地址
        # 图集时，视频地址为空，不处理
        video_mp4_url = ""
        if len(video_url) > 0:
            # 修改：直接返回原始地址，让客户端（浏览器）自己去重定向
            # 这样抖音会根据用户(浏览器)的IP分配最近的CDN节点，解决服务器在海外导致国内下载慢的问题
            # video_mp4_url = await self.get_video_redirect_url(video_url)
            video_mp4_url = video_url

        # 获取封面图片，优先获取非 .webp 格式的图片 url
        cover_url = ""
        if (
            "video" in data
            and "cover" in data["video"]
            and "url_list" in data["video"]["cover"]
        ):
            cover_url = self._get_no_webp_url(data["video"]["cover"]["url_list"])

        video_info = VideoInfo(
            video_url=video_mp4_url,
            cover_url=cover_url,
            title=data.get("desc", ""),
            images=images,
            author=VideoAuthor(
                uid=data.get("author", {}).get("sec_uid", ""),
                name=data.get("author", {}).get("nickname", ""),
                avatar=(
                    data.get("author", {})
                    .get("avatar_thumb", {})
                    .get("url_list", [""])[0]
                    if data.get("author", {}).get("avatar_thumb", {}).get("url_list")
                    else ""
                ),
            ),
        )
        return video_info

    async def get_video_redirect_url(self, video_url: str) -> str:
        async with httpx.AsyncClient(follow_redirects=False, verify=False, trust_env=False) as client:
            response = await client.get(video_url, headers=self.get_default_headers())
        # 返回重定向后的地址，如果没有重定向则返回原地址(抖音中的西瓜视频,重定向地址为空)
        return response.headers.get("location") or video_url

    async def parse_video_id(self, video_id: str) -> VideoInfo:
        req_url = self._get_request_url_by_video_id(video_id)
        return await self.parse_share_url(req_url)

    def _get_request_url_by_video_id(self, video_id) -> str:
        return f"https://www.iesdouyin.com/share/video/{video_id}/"

    async def _parse_app_share_url(self, share_url: str) -> str:
        """解析app分享链接 https://v.douyin.com/xxxxxx"""
        async with httpx.AsyncClient(follow_redirects=False, verify=False, trust_env=False) as client:
            response = await client.get(share_url, headers=self.get_default_headers())

        location = response.headers.get("location")
        if not location:
            return ""

        # 检查是否是西瓜视频链接
        if "ixigua.com" in location:
            # 如果是西瓜视频，这里应该返回特殊处理，暂时返回空
            # 在实际应用中可能需要调用西瓜视频解析器
            return ""

        return self._parse_video_id_from_path(location)

    def _parse_video_id_from_path(self, url_path: str) -> str:
        """从URL路径中解析视频ID"""
        if not url_path:
            return ""

        try:
            parsed_url = urlparse(url_path)

            # 判断网页精选页面的视频
            # https://www.douyin.com/jingxuan?modal_id=7555093909760789812
            query_params = parse_qs(parsed_url.query)
            if "modal_id" in query_params:
                return query_params["modal_id"][0]

            # 判断其他页面的视频
            # https://www.iesdouyin.com/share/video/7424432820954598707/?region=CN&mid=7424432976273869622&u_code=0
            # https://www.douyin.com/video/xxxxxx
            path = parsed_url.path.strip("/")
            if path:
                path_parts = path.split("/")
                if len(path_parts) > 0:
                    return path_parts[-1]
        except Exception:
            pass

        return ""

    def _get_no_webp_url(self, url_list: list) -> str:
        """优先获取非 .webp 格式的图片 url"""
        if not url_list:
            return ""

        # 优先获取非 .webp 格式的图片 url
        for url in url_list:
            if url and not url.endswith(".webp"):
                return url

        # 如果没找到，使用第一项
        return url_list[0] if url_list and url_list[0] else ""

    def _is_note_content(self, html_content: str, share_url: str) -> bool:
        """检查是否是图集内容"""
        try:
            # 方法1: 检查canonical URL是否包含/note/
            pattern = re.compile(
                r'<link[^>]*rel=["\']canonical["\'][^>]*href=["\']([^' r'"\']+)["\']',
                re.IGNORECASE,
            )
            match = pattern.search(html_content)
            if match:
                canonical_url = match.group(1)
                if "/note/" in canonical_url:
                    return True

            # 方法2: 检查URL路径是否包含note相关路径
            parsed_url = urlparse(share_url)
            if "/note/" in parsed_url.path:
                return True

            # 方法3: 检查HTML中是否有图集相关的标识
            if "note_" in html_content or "图文" in html_content:
                return True

        except Exception:
            pass

        return False

    async def _get_slides_info(self, video_id: str) -> dict:
        """获取图集的详细信息，包括Live Photo"""
        try:
            # 生成web_id和a_bogus参数
            web_id = "75" + self._generate_fixed_length_numeric_id(15)
            a_bogus = self._rand_seq(64)

            api_url = (
                f"https://www.iesdouyin.com/web/api/v2/aweme/slidesinfo/"
                f"?reflow_source=reflow_page"
                f"&web_id={web_id}"
                f"&device_id={web_id}"
                f"&aweme_ids=%5B{video_id}%5D"
                f"&request_source=200"
                f"&a_bogus={a_bogus}"
            )

            async with httpx.AsyncClient(verify=False, trust_env=False) as client:
                response = await client.get(api_url, headers=self.get_default_headers())
                response.raise_for_status()

            data = response.json()
            return data if data.get("aweme_details") else None

        except Exception:
            return None

    def _generate_fixed_length_numeric_id(self, length: int) -> str:
        """生成固定位数的随机数字ID"""
        return "".join(secrets.choice(string.digits) for _ in range(length))

    def _rand_seq(self, n: int) -> str:
        """生成随机字符串"""
        chars = string.ascii_letters + string.digits
        return "".join(secrets.choice(chars) for _ in range(n))
