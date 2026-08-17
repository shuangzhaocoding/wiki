// Algolia 搜索配置
export const algoliaConfig = {
  // 这些值应该从环境变量中读取，或者从后端 API 获取
  appId: import.meta.env.VITE_ALGOLIA_APP_ID || '',
  apiKey: import.meta.env.VITE_ALGOLIA_SEARCH_API_KEY || '',
  indexName: import.meta.env.VITE_ALGOLIA_INDEX_NAME || 'wiki_docs'
}

// 检查配置是否完整
export const isAlgoliaConfigured = () => {
  return !!(algoliaConfig.appId && algoliaConfig.apiKey && algoliaConfig.indexName)
}
