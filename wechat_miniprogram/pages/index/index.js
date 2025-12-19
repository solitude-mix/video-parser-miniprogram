const app = getApp()
const { addHistory } = require('../../utils/history');
const { isLoggedIn } = require('../../utils/auth');

Page({
  data: {
    inputValue: '',
    loading: false,
    result: null,
    error: '',
    isImages: false
  },

  onShow() {
    // 自动检测剪贴板
    this.checkClipboard();
  },

  checkClipboard() {
    wx.getClipboardData({
      success: (res) => {
        const text = res.data;
        // 简单正则判断是否包含链接
        if (text && (text.includes('http://') || text.includes('https://'))) {
           // 避免重复弹窗，可以判断是否和当前输入框内容一致
           if (text !== this.data.inputValue) {
             wx.showModal({
               title: '检测到链接',
               content: '是否粘贴并解析剪贴板中的链接？',
               confirmText: '解析',
               success: (modalRes) => {
                 if (modalRes.confirm) {
                   this.setData({ inputValue: text });
                   this.onParse();
                 }
               }
             })
           }
        }
      },
      fail: () => {} // 忽略错误，避免静默失败提示干扰
    })
  },

  onInput(e) {
    this.setData({
      inputValue: e.detail.value,
      error: '' // 输入时清除错误
    })
  },

  onClear() {
    this.setData({
      inputValue: '',
      result: null,
      error: '',
      isImages: false
    })
  },

  onPaste() {
    wx.getClipboardData({
      success: (res) => {
        if (res.data) {
          this.setData({ inputValue: res.data });
          wx.showToast({ title: '已粘贴', icon: 'none' });
        }
      }
    })
  },

  goToHistory() {
    if (!isLoggedIn()) {
      wx.showModal({
        title: '提示',
        content: '请先登录后查看历史记录',
        confirmText: '去登录',
        success: (res) => {
          if (res.confirm) {
            wx.switchTab({
              url: '/pages/me/me'
            })
          }
        }
      })
      return;
    }

    wx.navigateTo({
      url: '/pages/history/history',
    })
  },

  onParse() {
    const url = this.data.inputValue.trim();
    if (!url) {
      wx.showToast({
        title: '请输入链接',
        icon: 'none'
      })
      return;
    }

    if (this.data.loading) return;

    this.setData({
      loading: true,
      result: null,
      error: '',
      isImages: false
    });

    wx.request({
      url: `${app.globalData.baseUrl}/video/share/url/parse`,
      method: 'GET',
      data: {
        url: url
      },
      success: (res) => {
        if (res.data && res.data.code === 200) {
          const videoData = res.data.data;
          
          // 判断是视频还是图集
          const isImages = videoData.images && videoData.images.length > 0;
          
          // 生成代理地址，用于绕过防盗链 (预览和下载都用这个)
          if (videoData.video_url) {
            videoData.proxy_url = `${app.globalData.baseUrl}/video/proxy?url=${encodeURIComponent(videoData.video_url)}`;
          }

          this.setData({
            result: videoData,
            isImages: isImages
          });

          // 添加到历史记录
          addHistory(videoData);

        } else {
          this.showError(res.data.msg || '解析失败');
        }
      },
      fail: (err) => {
        console.error(err);
        this.showError('请求失败，请检查网络');
      },
      complete: () => {
        this.setData({
          loading: false
        });
      }
    });
  },

  showError(msg) {
    this.setData({ error: msg });
    // 3秒后自动隐藏
    setTimeout(() => {
      this.setData({ error: '' });
    }, 3000);
  },

  previewImage(e) {
    const current = e.currentTarget.dataset.current;
    if (this.data.result && this.data.result.images) {
      const urls = this.data.result.images.map(item => item.url);
      wx.previewImage({
        current: current,
        urls: urls
      })
    } else if (this.data.result && this.data.result.cover_url) {
        wx.previewImage({
            urls: [this.data.result.cover_url]
        })
    }
  },

  copyUrl(e) {
    // 复制时依然复制原始链接 (result.video_url)，方便用户分享
    const url = e.currentTarget.dataset.url;
    wx.setClipboardData({
      data: url,
      success: () => {
        wx.showToast({
          title: '链接已复制',
          icon: 'success'
        })
      }
    })
  },

  copyTitle() {
    if (this.data.result && this.data.result.title) {
        wx.setClipboardData({
            data: this.data.result.title,
            success: () => {
              wx.showToast({ title: '文案已复制', icon: 'success' })
            }
        })
    }
  },

  downloadCover() {
      if (this.data.result && this.data.result.cover_url) {
          this.saveImage(this.data.result.cover_url);
      }
  },

  saveImage(url) {
    wx.showLoading({ title: '下载中...' });
    wx.downloadFile({
        url: url,
        success: (res) => {
            if (res.statusCode === 200) {
                wx.saveImageToPhotosAlbum({
                    filePath: res.tempFilePath,
                    success: () => wx.showToast({ title: '已保存', icon: 'success' }),
                    fail: (err) => this.handleSaveFail(err)
                })
            }
        },
        fail: () => wx.showToast({ title: '下载失败', icon: 'none' }),
        complete: () => wx.hideLoading()
    })
  },
  
  downloadVideo() {
    // 优先使用代理地址下载
    const url = this.data.result.proxy_url || this.data.result.video_url;
    if (!url) return;

    console.log("正在下载视频:", url);

    wx.showLoading({ title: '下载中...' });
    wx.downloadFile({
      url: url,
      success: (res) => {
        if (res.statusCode === 200) {
          wx.saveVideoToPhotosAlbum({
            filePath: res.tempFilePath,
            success: () => {
              wx.showToast({ title: '已保存到相册', icon: 'success' });
            },
            fail: (err) => this.handleSaveFail(err)
          })
        } else {
            wx.showToast({ title: '下载失败:' + res.statusCode, icon: 'none' });
        }
      },
      fail: (err) => {
        console.log('Download failed:', err);
        wx.showToast({ title: '下载请求失败', icon: 'none' });
      },
      complete: () => {
        wx.hideLoading();
      }
    })
  },

  handleSaveFail(err) {
    if (err.errMsg && err.errMsg.indexOf('auth deny') >= 0) {
        wx.showModal({
            title: '权限不足',
            content: '需要访问相册权限才能保存，请在设置中开启',
            confirmText: '去设置',
            success: (res) => {
                if (res.confirm) wx.openSetting()
            }
        })
    } else {
        wx.showToast({ title: '保存失败', icon: 'none' });
    }
  }
})