import { ref, watch, onMounted, onBeforeUnmount } from 'vue'

const LAYOUT_COMPACT_MAX = 1024
const LAYOUT_MOBILE_MAX = 768

/** 平板/手机紧凑布局：侧栏抽屉、顶栏留白等 */
export function useResponsiveLayout() {
  const isCompactLayout = ref(false)
  const isMobileLayout = ref(false)
  const mobileDrawerOpen = ref(false)

  const updateLayout = () => {
    isCompactLayout.value = window.matchMedia(`(max-width: ${LAYOUT_COMPACT_MAX}px)`).matches
    isMobileLayout.value = window.matchMedia(`(max-width: ${LAYOUT_MOBILE_MAX}px)`).matches
    if (!isCompactLayout.value) {
      mobileDrawerOpen.value = false
      document.body.style.overflow = ''
    }
  }

  const toggleMobileDrawer = () => {
    mobileDrawerOpen.value = !mobileDrawerOpen.value
  }

  const closeMobileDrawer = () => {
    mobileDrawerOpen.value = false
  }

  watch(mobileDrawerOpen, (open) => {
    if (isCompactLayout.value) {
      document.body.style.overflow = open ? 'hidden' : ''
    }
  })

  onMounted(() => {
    updateLayout()
    window.addEventListener('resize', updateLayout)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('resize', updateLayout)
    document.body.style.overflow = ''
  })

  return {
    isCompactLayout,
    isMobileLayout,
    mobileDrawerOpen,
    toggleMobileDrawer,
    closeMobileDrawer,
    updateLayout
  }
}
