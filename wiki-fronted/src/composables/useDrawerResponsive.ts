import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

export const DRAWER_LAYOUT_COMPACT_MAX = 1024
export const DRAWER_LAYOUT_MOBILE_MAX = 768
/** 高于文章页移动端 TOC/附件层 (500) 与底部工具栏 (430) */
export const DRAWER_Z_INDEX_COMPACT = 2600

/** 平板/手机评论、反馈等侧栏使用的精简富文本工具栏 */
export const COMPACT_RICH_TEXT_TOOLBAR = [
  ['bold', 'italic', 'underline', 'strike'],
  [{ list: 'ordered' }, { list: 'bullet' }],
  [{ color: [] }, { background: [] }],
  ['link', 'blockquote', 'code'],
  ['image', 'file']
] as const

export function useDrawerResponsive() {
  const isCompactLayout = ref(false)
  const isMobileLayout = ref(false)

  const updateLayout = () => {
    isCompactLayout.value = window.matchMedia(`(max-width: ${DRAWER_LAYOUT_COMPACT_MAX}px)`).matches
    isMobileLayout.value = window.matchMedia(`(max-width: ${DRAWER_LAYOUT_MOBILE_MAX}px)`).matches
  }

  onMounted(() => {
    updateLayout()
    window.addEventListener('resize', updateLayout)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('resize', updateLayout)
  })

  const drawerWidth = computed(() => {
    if (isMobileLayout.value) return '100%'
    if (isCompactLayout.value) return 'min(520px, 100%)'
    return '70%'
  })

  const drawerZIndex = computed(() =>
    isCompactLayout.value ? DRAWER_Z_INDEX_COMPACT : 2000
  )

  const drawerBodyClass = (base: string) =>
    computed(() => [
      base,
      { [`${base}--compact`]: isCompactLayout.value },
      { [`${base}--mobile`]: isMobileLayout.value }
    ])

  return {
    isCompactLayout,
    isMobileLayout,
    drawerWidth,
    drawerZIndex,
    drawerBodyClass
  }
}
