import { ref } from 'vue'
import { defineStore } from 'pinia'
import { articleApi, type ArticleSearchItem } from '../api/article'

export const useRecentArticlesStore = defineStore('recentArticles', () => {
  const recentCreated = ref<ArticleSearchItem[]>([])
  const recentUpdated = ref<ArticleSearchItem[]>([])
  const loading = ref(false)
  const loaded = ref(false)

  const fetchRecentArticles = async (force = false) => {
    if (loaded.value && !force) return
    if (loading.value) return

    loading.value = true
    try {
      const [created, updated] = await Promise.all([
        articleApi.getRecentCreatedArticles(),
        articleApi.getRecentUpdatedArticles()
      ])
      recentCreated.value = created || []
      recentUpdated.value = updated || []
      loaded.value = true
    } catch (e) {
      // 出错时保持现有数据，避免影响页面
      // console.error('fetchRecentArticles failed', e)
    } finally {
      loading.value = false
    }
  }

  return {
    recentCreated,
    recentUpdated,
    loading,
    loaded,
    fetchRecentArticles
  }
})

