const KEY = 'parse_history';
const MAX_COUNT = 20;

const getHistory = () => {
  return wx.getStorageSync(KEY) || [];
};

const addHistory = (item) => {
  let history = getHistory();
  // 去重：如果已存在相同的 video_url，先删除旧的
  history = history.filter(h => h.video_url !== item.video_url);
  // 添加到头部
  history.unshift({
    ...item,
    timestamp: new Date().getTime()
  });
  // 限制数量
  if (history.length > MAX_COUNT) {
    history = history.slice(0, MAX_COUNT);
  }
  wx.setStorageSync(KEY, history);
};

const clearHistory = () => {
  wx.removeStorageSync(KEY);
};

const removeHistoryItem = (index) => {
    let history = getHistory();
    history.splice(index, 1);
    wx.setStorageSync(KEY, history);
    return history;
}

module.exports = {
  getHistory,
  addHistory,
  clearHistory,
  removeHistoryItem
};