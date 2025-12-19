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

    # 简单的防盗链处理 
    # 许多视频 CDN 如果检测到 Referer 不对会拒绝，不传 Referer 反而能通过
    # 使用手机 UA 模拟移动端访问
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        # "Referer": "https://www.douyin.com/"  <-- 移除硬编码的 Referer
    }

    try:
        # stream=True 开启流式传输，避免大文件占满内存
        # verify=False 忽略 SSL 验证（部分 CDN 证书可能有问题）
        r = requests.get(url, headers=headers, stream=True, timeout=30, verify=False)
        
        # 如果上游返回 403，手动抛出异常以便调试
        if r.status_code == 403:
             raise HTTPException(status_code=403, detail="Upstream server forbidden (Hotlinking)")

        # 转发 Content-Type
        content_type = r.headers.get("Content-Type", "video/mp4")
        
        return StreamingResponse(
            r.iter_content(chunk_size=1024*1024), 
            media_type=content_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proxy failed: {str(e)}")


# mcp.setup_server()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
