const { login, logout, isLoggedIn, getUserInfo } = require('../../utils/auth');

Page({
  data: {
    isLoggedIn: false,
    userInfo: null
  },

  onShow() {
    this.checkLoginStatus();
  },

  checkLoginStatus() {
    this.setData({
      isLoggedIn: isLoggedIn(),
      userInfo: getUserInfo()
    })
  },

  onLogin() {
    wx.getUserProfile({
      desc: '用于完善会员资料',
      success: (res) => {
        login(res.userInfo);
        this.checkLoginStatus();
        wx.showToast({
          title: '登录成功',
          icon: 'success'
        })
      },
      fail: (err) => {
        console.log(err);
        wx.showToast({
          title: '登录失败',
          icon: 'none'
        })
      }
    })
  },

  onLogout() {
    wx.showModal({
      title: '提示',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          logout();
          this.checkLoginStatus();
          wx.showToast({
            title: '已退出',
            icon: 'none'
          })
        }
      }
    })
  },

  onAbout() {
    wx.navigateTo({
      url: '/pages/about/about',
    })
  },

  onContact() {
    wx.setClipboardData({
      data: 'ztscsgo0921@163.com',
      success: () => {
        wx.showToast({
          title: '邮箱已复制',
          icon: 'success'
        })
      }
    })
  }
})