App({
  onLaunch() {
    console.log('App Launch')
  },
  globalData: {
    // Local development URL. 
    // In production, this must be an HTTPS URL and configured in WeChat Admin Console.
    baseUrl: 'http://127.0.0.1:8000' 
  }
})