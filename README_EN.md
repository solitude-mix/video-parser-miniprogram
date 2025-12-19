# Universal Video Parser (WeChat Mini Program Edition)

[中文](README.md) | [English](README_EN.md)

This project is a video watermark removal and parsing tool based on a Python backend and a WeChat Mini Program frontend. It supports major short video platforms such as Douyin (TikTok China), Kuaishou, Bilibili, Weibo, and more.

> **⚠️ Acknowledgements**
>
> This project is developed based on **[parse-video-py](https://github.com/wujunwei928/parse-video-py)**.
>
> The core parsing logic is derived from the original author **wujunwei928**. We extend our sincere gratitude for their work!

---

## ✨ Features

### 🎨 WeChat Mini Program Frontend
*   **Cool UI**: Designed with a dark tech style, featuring dynamic ambient backgrounds and glassmorphism effects.
*   **Smart Interaction**:
    *   🔥 **Auto Clipboard Detection**: Automatically detects links in the clipboard upon opening the app and prompts for parsing.
    *   📜 **History**: Automatically saves parsing history, supporting review, one-click refill, and deletion.
    *   🖼️ **Gallery Support**: Perfectly supports Douyin/RedBook image galleries with a carousel preview.
*   **Handy Tools**:
    *   📹 **Video Download**: One-click save watermark-free videos to your album.
    *   📸 **Save Cover**: Extract high-definition cover images.
    *   📝 **Copy Description**: One-click copy of the video description text.

### 🚀 Python Backend (FastAPI)
*   **High Performance**: Built on the FastAPI + uvicorn asynchronous framework.
*   **Multi-Platform**: Supports 20+ mainstream video platforms.
*   **Fixes & Optimizations**:
    *   Resolved naming conflicts with the Python standard library `parser` (renamed to `video_parsers`).
    *   Optimized SSL/Proxy connection issues for certain platforms (e.g., Douyin) in specific network environments.

---

## 📺 Supported Platforms

Includes but not limited to:
- **Douyin (TikTok CN)** / Douyin Volcano
- **Kuaishou**
- **Bilibili**
- **Weibo** / LvZhou
- **RedBook (Xiaohongshu)**
- **XiGua Video**
- **PiPiXia**
- **WeiShi**
- ... and more (see `video_parsers/base.py`)

---

## 📂 Project Structure

```text
.
├── main.py                  # Backend entry point
├── requirements.txt         # Python dependencies
├── video_parsers/           # [Core] Video parsing logic (originally 'parser')
│   ├── base.py
│   ├── douyin.py
│   └── ...
└── wechat_miniprogram/      # [Frontend] WeChat Mini Program source code
    ├── app.json
    ├── app.js
    ├── pages/
    │   ├── index/           # Home page (Parsing)
    │   └── history/         # History page
    └── utils/
```

---

## 🛠️ Quick Start

### 1. Backend Setup

Ensure Python 3.9+ is installed.

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the server
python main.py
```
Upon success, the terminal will show: `Uvicorn running on http://0.0.0.0:8000`

### 2. Frontend Setup (WeChat Mini Program)

1.  Download and install [WeChat DevTools](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html).
2.  Open the tool and select **"Import Project"**.
3.  **Directory**: Select the `wechat_miniprogram` folder in this project.
4.  **AppID**: Use a Test ID (click "Test ID" on the login/register screen) or your own AppID.
5.  **Crucial Settings**:
    *   Click **"Details" (详情)** -> **"Local Settings" (本地设置)** in the top right corner.
    *   ✅ **Check "Does not verify valid domain names, web-view (business domain names), TLS versions, and HTTPS certificates"**.
    *   *(Reason: Local development uses http://127.0.0.1, not https)*

### 3. Real Device Debugging

If you want to preview on your phone:
1.  Ensure your phone and computer are on the same WiFi network.
2.  Get your computer's local IP address (e.g., `192.168.1.5`).
3.  Modify `wechat_miniprogram/app.js`:
    ```javascript
    globalData: {
      // Change 127.0.0.1 to your computer's IP
      baseUrl: 'http://192.168.1.5:8000' 
    }
    ```
4.  Click "Preview" in WeChat DevTools and scan the QR code with WeChat.

---

## ❓ FAQ

**Q: Parsing failed with SSL or connection errors?**
A: This version has optimized SSL verification logic for some network environments. If errors persist, check if global proxy software is enabled, try disabling it, or enforce `trust_env=False` in the code.

**Q: Why does the generated video still have a watermark?**
A: Some videos have "hard subtitles" or watermarks embedded directly into the video stream by the platform. This tool primarily removes the auto-generated ending credits and the bottom-right ID watermark.

---

## ⚖️ Disclaimer

*   This project is for learning and technical research purposes only. **Commercial use is strictly prohibited.**
*   Users must comply with the Terms of Service (ToS) of the respective video platforms.
*   Please respect copyright; do not download or distribute copyrighted content.
*   Original License: [LICENSE](LICENSE) (Follows the original project's license)

---

**Developed with ❤️ by Gemini & You**
Based on [parse-video-py](https://github.com/wujunwei928/parse-video-py)