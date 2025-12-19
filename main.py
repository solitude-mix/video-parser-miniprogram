import os
import re
import secrets
from video_parsers import VideoSource, parse_video_id, parse_video_share_url

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
import requests
# from fastapi_mcp import FastApiMCP

app = FastAPI()

# mcp = FastApiMCP(app)

# mcp.mount_http()

templates = Jinja2Templates(directory="templates")


def get_auth_dependency() -> list[Depends]:
    """
    根据环境变量动态返回 Basic Auth 依赖项
    - 如果设置了 USERNAME 和 PASSWORD，返回验证函数
    - 如果未设置，返回一个直接返回 None 的 Depends
    """
    basic_auth_username = os.getenv("PARSE_VIDEO_USERNAME")
    basic_auth_password = os.getenv("PARSE_VIDEO_PASSWORD")

    if not (basic_auth_username and basic_auth_password):
        return []  # 返回包含Depends实例的列表

    security = HTTPBasic()

    def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
        # 验证凭据
        correct_username = secrets.compare_digest(
            credentials.username, basic_auth_username
        )
        correct_password = secrets.compare_digest(
            credentials.password, basic_auth_password
        )
        if not (correct_username and correct_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Basic"},
            )
        return credentials

    return [Depends(verify_credentials)]  # 返回封装好的 Depends


@app.get("/", response_class=HTMLResponse, dependencies=get_auth_dependency())
async def read_item(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "title": "github.com/wujunwei928/parse-video-py Demo",
        },
    )


@app.get("/video/share/url/parse", dependencies=get_auth_dependency())
async def share_url_parse(url: str):
    url_reg = re.compile(r"http[s]?:\/\/[\w.-]+[\w\/-]*[\w.-]*\??[\w=&:\-\+\%]*[/]*")
    video_share_url = url_reg.search(url).group()

    try:
        video_info = await parse_video_share_url(video_share_url)
        return {"code": 200, "msg": "解析成功", "data": video_info.__dict__}
    except Exception as err:
        return {
            "code": 500,
            "msg": str(err),
        }


@app.get("/video/id/parse", dependencies=get_auth_dependency())
async def video_id_parse(source: VideoSource, video_id: str):
    try:
        video_info = await parse_video_id(source, video_id)
        return {"code": 200, "msg": "解析成功", "data": video_info.__dict__}
    except Exception as err:
        return {
            "code": 500,
            "msg": str(err),
        }


@app.get("/video/proxy")
async def video_proxy(url: str):
    """
    代理下载视频，绕过防盗链
    """
    if not url:
        raise HTTPException(status_code=400, detail="Missing url parameter")

    # 使用与 base.py 一致的 Android UA，这在解析时已被证明能绕过反爬
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36",
        "Accept": "*/*",
        "Accept-Encoding": "identity;q=1, *;q=0",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Range": "bytes=0-", # 模拟播放器请求
        "Referer": "https://www.douyin.com/", # 尝试带回 Referer，部分 CDN 需要
    }

    try:
        # stream=True 开启流式传输
        # verify=False 忽略 SSL 验证
        r = requests.get(url, headers=headers, stream=True, timeout=30, verify=False)
        
        # 如果上游返回 403，手动抛出异常以便调试
        if r.status_code == 403:
             raise HTTPException(status_code=403, detail="Upstream server forbidden (Hotlinking)")

        # 过滤并重组响应头
        # 强制设置为附件下载，并指定文件名（虽然小程序不看文件名，但对浏览器友好）
        response_headers = {
            "Content-Disposition": 'attachment; filename="video.mp4"',
            "Content-Type": r.headers.get("Content-Type", "video/mp4")
        }
        
        return StreamingResponse(
            r.iter_content(chunk_size=1024*1024), 
            headers=response_headers,
            media_type=response_headers["Content-Type"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proxy failed: {str(e)}")


# mcp.setup_server()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
