const { getHistory, clearHistory, removeHistoryItem } = require('../../utils/history');

Page({
  data: {
    historyList: []
  },

  onShow() {
    this.loadHistory();
  },

  loadHistory() {
    const list = getHistory().map(item => {
      // 格式化时间
      const date = new Date(item.timestamp);
      item.displayTime = `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`;
      return item;
    });
    this.setData({ historyList: list });
  },

  onTapItem(e) {
    const item = e.currentTarget.dataset.item;
    // 获取当前页面栈
    const pages = getCurrentPages();
    const prevPage = pages[pages.length - 2];
    
    // 如果上一页是首页，则设置数据并返回
    if (prevPage && prevPage.route === 'pages/index/index') {
      const isImages = item.images && item.images.length > 0;
      prevPage.setData({
        inputValue: item.video_url, // 注意：这里可能需要原始分享链接，但历史记录存的是解析后的。不过没关系，这里直接展示结果
        result: item,
        isImages: isImages
      });
      wx.navigateBack();
    }
  },

  onDeleteItem(e) {
    const index = e.currentTarget.dataset.index;
    wx.showModal({
        title: '提示',
        content: '确定删除这条记录吗？',
        success: (res) => {
            if (res.confirm) {
                const newList = removeHistoryItem(index);
                this.loadHistory();
            }
        }
    })
  },

  onClearAll() {
    wx.showModal({
      title: '确认清空',
      content: '确定要清空所有历史记录吗？',
      success: (res) => {
        if (res.confirm) {
          clearHistory();
          this.setData({ historyList: [] });
        }
      }
    })
  }
})