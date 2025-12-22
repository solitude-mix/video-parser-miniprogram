import os
import re
import secrets
import logging
from video_parsers import VideoSource, parse_video_id, parse_video_share_url

import uvicorn
import httpx
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
# from fastapi_mcp import FastApiMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
            logger.warning(f"Failed login attempt with username: {credentials.username}")
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
    logger.info(f"Parsing share URL: {url}")
    url_reg = re.compile(r"http[s]?:\/\/[\w.-]+[\w\/-]*[\w.-]*\??[\w=&:\-\+\%]*[/]*")
    search_res = url_reg.search(url)
    if not search_res:
        logger.error(f"Invalid URL format: {url}")
        return {
            "code": 400,
            "msg": "Invalid URL",
        }
    video_share_url = search_res.group()

    try:
        video_info = await parse_video_share_url(video_share_url)
        logger.info(f"Successfully parsed URL: {video_share_url}")
        return {"code": 200, "msg": "解析成功", "data": video_info.__dict__}
    except Exception as err:
        logger.error(f"Error parsing URL {video_share_url}: {err}", exc_info=True)
        return {
            "code": 500,
            "msg": str(err),
        }


@app.get("/video/id/parse", dependencies=get_auth_dependency())
async def video_id_parse(source: VideoSource, video_id: str):
    logger.info(f"Parsing video ID: {video_id} from source: {source}")
    try:
        video_info = await parse_video_id(source, video_id)
        logger.info(f"Successfully parsed ID: {video_id}")
        return {"code": 200, "msg": "解析成功", "data": video_info.__dict__}
    except Exception as err:
        logger.error(f"Error parsing ID {video_id}: {err}", exc_info=True)
        return {
            "code": 500,
            "msg": str(err),
        }


@app.get("/video/proxy", dependencies=get_auth_dependency())
async def video_proxy(url: str):
    """
    Proxy video download to bypass 403 Forbidden (anti-hotlinking).
    """
    if not url:
        raise HTTPException(status_code=400, detail="Missing url parameter")

    logger.info(f"Proxy request for URL: {url}")

    # Use robust headers to mimic a real mobile request and bypass hotlinking protection
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "Accept": "*/*",
        "Accept-Encoding": "identity;q=1, *;q=0",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Range": "bytes=0-",
    }

    async def iter_file():
        try:
            # Increase timeout to 60s (connect=10.0, read=60.0, write=10.0, pool=10.0)
            timeout = httpx.Timeout(60.0, connect=10.0)
            async with httpx.AsyncClient(verify=False, trust_env=False, follow_redirects=True, timeout=timeout) as client:
                async with client.stream("GET", url, headers=headers) as response:
                    if response.status_code >= 400:
                        logger.error(f"Upstream server returned {response.status_code} for URL: {url}")
                        # Consume response to avoid hanging connection
                        await response.aread() 
                        raise HTTPException(status_code=response.status_code, detail=f"Upstream error {response.status_code}")
                    
                    async for chunk in response.aiter_bytes():
                        yield chunk
        except httpx.RequestError as exc:
            logger.error(f"An error occurred while requesting {exc.request.url!r}: {exc}")
            raise HTTPException(status_code=500, detail=f"Proxy request error: {exc}")
        except Exception as e:
            logger.error(f"Unexpected error in proxy: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")

    return StreamingResponse(iter_file(), media_type="video/mp4")


# mcp.setup_server()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
