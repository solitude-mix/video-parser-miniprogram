# Universal Video Parser (WeChat Mini Program Edition)
# 万能视频解析 - 微信小程序版

[中文](README.md) | [English](README_EN.md)

本项目是一个基于 Python 后端和微信小程序前端的视频去水印解析工具，支持 抖音、快手、B站、微博 等主流短视频平台。

> **⚠️ 特别致谢 / Acknowledgements**
>
> 本项目是在 **[parse-video-py](https://github.com/wujunwei928/parse-video-py)** 的基础上进行二次开发和扩展的。
>
> 核心解析逻辑源自原作者 **wujunwei928**，在此表示由衷感谢！
> This project is developed based on [parse-video-py](https://github.com/wujunwei928/parse-video-py).

---

## ✨ 项目亮点 (Features)

### 🎨 微信小程序前端
*   **酷炫 UI**：采用暗黑科技风设计，带动态氛围背景与玻璃拟态效果。
*   **用户系统**：
    *   👤 **会员中心**：包含用户登录、个人资料展示及退出功能。
    *   🔒 **权限控制**：查看历史记录需先登录，保护隐私。
    *   ℹ️ **关于/联系**：内置产品介绍、使用教程、免责声明及客服联系方式。
*   **智能交互**：
    *   🔥 **自动检测剪贴板**：打开小程序自动识别并提示解析链接。
    *   📜 **历史记录**：自动保存解析历史，支持回看、一键回填、清空。
    *   🖼️ **图集支持**：完美支持抖音/小红书图集模式，提供轮播预览。
*   **便捷工具**：
    *   📹 **视频直下**：一键保存无水印视频到相册。
    *   📸 **封面保存**：提取高清封面图。
    *   📝 **文案提取**：一键复制视频描述文案。

### 🚀 Python Backend (FastAPI)
*   **高性能**：基于 FastAPI + uvicorn 异步框架。
*   **多平台**：支持 20+ 主流视频平台解析。
*   **修复优化**：
    *   解决了原项目与 Python 标准库 `parser` 的命名冲突 (重命名为 `video_parsers`)。
    *   优化了部分平台 (如抖音) 在特定网络环境下的 SSL/代理连接问题。

---

## 📺 支持平台 (Supported Platforms)

包括但不限于：
- **抖音 (Douyin)** / 抖音火山版
- **快手 (Kuaishou)**
- **哔哩哔哩 (Bilibili)**
- **微博 (Weibo)** / 绿洲
- **小红书 (RedBook)**
- **西瓜视频 (XiGua)**
- **皮皮虾 (PiPiXia)**
- **微视 (WeiShi)**
- ... 以及更多 (详见 `video_parsers/base.py`)

---

## 📂 项目结构 (Structure)

```text
.
├── main.py                  # 后端启动入口
├── requirements.txt         # Python 依赖列表
├── video_parsers/           # [核心] 视频解析逻辑 (原 parser 目录)
│   ├── base.py
│   ├── douyin.py
│   └── ...
└── wechat_miniprogram/      # [前端] 微信小程序源码
    ├── app.json
    ├── app.js
    ├── images/              # 图标资源
    ├── pages/
    │   ├── index/           # 首页 (解析页)
    │   ├── history/         # 历史记录页
    │   ├── me/              # 个人中心 (登录/关于)
    │   └── about/           # 关于页面
    └── utils/
```

---

## 🛠️ 快速开始 (Quick Start)

### 1. 后端环境搭建 (Backend)

确保已安装 Python 3.9+。

```bash
# 1. 安装依赖 (推荐使用国内镜像源)
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 2. 启动服务
python main.py
```
启动成功后，终端会显示：`Uvicorn running on http://0.0.0.0:8000`

### 2. 小程序前端运行 (Frontend)

1.  下载并安装 [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)。
2.  打开工具，选择 **"导入项目"**。
3.  **目录**选择本项目下的 `wechat_miniprogram` 文件夹。
4.  **AppID**：使用测试号（点击注册/登录界面的"测试号"）或你自己的 AppID。
5.  **关键设置**：
    *   点击右上角 **"详情"** -> **"本地设置"**。
    *   ✅ **勾选 "不校验合法域名、web-view（业务域名）、TLS版本以及HTTPS证书"**。
    *   *(原因：本地开发使用的是 http://127.0.0.1，非 https)*

### 3. 真机调试说明

如果你想在手机上预览：
1.  确保手机和电脑连接同一个 WiFi。
2.  获取电脑的局域网 IP (如 `192.168.1.5`)。
3.  修改 `wechat_miniprogram/app.js`：
    ```javascript
    globalData: {
      // 将 127.0.0.1 修改为你电脑的 IP
      baseUrl: 'http://192.168.1.5:8000' 
    }
    ```
4.  在开发者工具中点击 "预览"，使用微信扫码。

---

## ❓ 常见问题 (FAQ)

**Q: 解析失败，提示 SSL 或连接错误？**
A: 本版本已针对部分网络环境优化了 SSL 验证逻辑。如果仍然报错，请检查是否开启了全局代理软件，尝试关闭代理或在代码中强制指定 `trust_env=False`。

**Q: 为什么生成的视频还是有水印？**
A: 部分视频如果是平台自带的硬字幕水印（直接压制在画面里的），是无法通过解析接口去除的。本工具主要去除平台自动添加的片尾水印和右下角 ID 水印。

**Q: 依赖安装失败？**
A: 请尝试使用国内镜像源：`pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com`

---

## ⚖️ 免责声明 (Disclaimer)

*   本项目仅供学习和技术研究使用，**严禁用于任何商业用途**。
*   使用者应遵守各视频平台的服务条款（ToS）。
*   请尊重版权，不要下载、传播受版权保护的视频内容。
*   原项目协议：[LICENSE](LICENSE) (遵循原项目协议)

---

**Developed with ❤️ by Gemini & You**
Based on [parse-video-py](https://github.com/wujunwei928/parse-video-py)