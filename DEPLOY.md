# 🚀 微信小程序部署上线指南 (Deployment Guide)

这份文档仅供开发者内部参考，详细记录了将本项目部署到线上的完整流程。

---

## 方案一：微信云托管 (WeChat CloudRun) - **[推荐 🔥]**

> **优势**：免运维、免备案、自带 HTTPS、无缝集成微信生态。
> **成本**：按量付费（有免费额度），适合个人开发者。

### 1. 开通环境
1.  登录 [微信公众平台](https://mp.weixin.qq.com/) -> **云托管**。
2.  开通服务并创建一个环境（Env）。

### 2. 部署后端 (Python)
1.  进入 **服务管理** -> **新建服务**。
2.  **服务名称**：`video-parser-api`。
3.  **部署方式**：选择 **GitHub 仓库**。
    *   授权您的 GitHub 账号。
    *   选择仓库：`video-parser-miniprogram`。
    *   分支：`main`。
    *   **构建配置**：
        *   构建目录：`/`
        *   Dockerfile 地址：`Dockerfile` (默认即可)
4.  点击 **发布**。系统会自动拉取代码、构建 Docker 镜像并启动容器。
5.  部署成功后，在服务详情页找到 **“公网访问”**，开启它，您会获得一个默认域名（如 `https://xxx.app.tcloudbase.com`）。

### 3. 配置小程序前端
1.  打开本地代码 `wechat_miniprogram/app.js`。
2.  修改 `baseUrl`：
    ```javascript
    globalData: {
      baseUrl: 'https://xxx.app.tcloudbase.com' // 填入刚才获得的云托管域名
    }
    ```
3.  **重要**：云托管的域名自动加入白名单，通常无需手动配置 request 合法域名，但建议检查一下。

---

## 方案二：传统云服务器 (ECS/CVM)

> **优势**：完全自主控制，可部署多个应用。
> **成本**：固定包年包月，需要域名备案（国内）。

### 1. 准备工作
*   **服务器**：购买 Ubuntu/CentOS 服务器。
*   **域名**：购买并备案（香港服务器可免备案）。
*   **SSL 证书**：申请免费 SSL 证书（阿里云/腾讯云控制台可申请）。

### 2. 服务器环境部署
登录服务器终端，执行：

```bash
# 1. 安装 Docker
curl -fsSL https://get.docker.com | bash

# 2. 拉取代码
git clone https://github.com/solitude-mix/video-parser-miniprogram.git
cd video-parser-miniprogram

# 3. 构建并启动容器
docker build -t video-parser .
docker run -d --name video-parser -p 8000:8000 --restart always video-parser
```

### 3. 配置 HTTPS (Nginx)
安装 Nginx 并配置反向代理，将 8000 端口转发到 HTTPS 443。

```nginx
server {
    listen 443 ssl;
    server_name api.your-domain.com; # 您的域名

    ssl_certificate /path/to/cert.pem;     # 证书路径
    ssl_certificate_key /path/to/key.pem;  # 私钥路径

    location / {
        proxy_pass http://127.0.0.1:8000; # 转发给 Python 后端
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. 微信后台配置
1.  登录微信公众平台。
2.  **开发 -> 开发管理 -> 开发设置 -> 服务器域名**。
3.  将 `https://api.your-domain.com` 填入 `request合法域名` 和 `downloadFile合法域名`。

---

## 方案三：前端发布 (通用步骤)

无论后端使用哪种方案，前端发布步骤一致：

1.  **修改代码**：确保 `app.js` 中的 `baseUrl` 是正式环境的 HTTPS 地址。
2.  **上传版本**：
    *   在微信开发者工具中点击 **“上传”**。
    *   版本号建议：`1.0.0`。
    *   备注：`首发版本，支持多平台视频解析`。
3.  **提交审核**：
    *   进入微信公众平台 -> **版本管理**。
    *   选择刚才上传的版本，点击 **“提交审核”**。
    *   **隐私协议**：需并在后台更新用户隐私保护指引（涉及“相册/存储”权限）。
    *   **服务类目**：推荐选择 `工具 > 效率` 或 `工具 > 信息查询`。
4.  **发布**：审核通过后，点击发布上线。

---

## ⚠️ 审核避坑指南
*   **功能说明**：提交审核时，建议说明是“个人视频资料整理工具”，避免强调“去水印”、“下载他人视频”等敏感词汇。
*   **演示视频**：最好录制一个简单的操作视频传给审核员，展示功能是正常的。
*   **空状态**：确保如果没有输入链接，界面有友好的提示，不要留白或报错。
