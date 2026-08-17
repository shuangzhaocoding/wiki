import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Locale } from '../i18n'
import { getLocale as getStoredLocale, setLocale as setStoredLocale } from '../i18n'

export const useLocaleStore = defineStore('locale', () => {
  const localeMap: Record<string, string> = {
    zh: 'zh-CN',
    en: 'en-US',
    ko: 'ko-KR',
    de: 'de-DE',
    ja: 'ja-JP',
    fr: 'fr-FR'
  }
  // 当前语言
  const currentLocale = ref<Locale>(getStoredLocale())
  
  // 响应式更新标识
  const localeKey = ref(0)
  
  // 设置语言
  const setLocale = (locale: Locale) => {
    currentLocale.value = locale
    setStoredLocale(locale)
    localeKey.value++ // 触发响应式更新
  }
  
  // 获取当前语言
  const getLocale = computed(() => currentLocale.value)
  
  return {
    currentLocale,
    localeKey,
    setLocale,
    getLocale,
    localeMap
  }
})
