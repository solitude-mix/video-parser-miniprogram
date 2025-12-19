// utils/auth.js
const KEY_USER_INFO = 'user_info';

const login = (userInfo) => {
  wx.setStorageSync(KEY_USER_INFO, userInfo);
}

const logout = () => {
  wx.removeStorageSync(KEY_USER_INFO);
}

const getUserInfo = () => {
  return wx.getStorageSync(KEY_USER_INFO);
}

const isLoggedIn = () => {
  return !!getUserInfo();
}

module.exports = {
  login,
  logout,
  getUserInfo,
  isLoggedIn
}