import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

const TABLET_MAX = 1024
const MOBILE_MAX = 768

export function useAuthFormLayout() {
  const isTablet = ref(false)
  const isMobile = ref(false)

  const updateLayout = () => {
    isTablet.value = window.matchMedia(`(max-width: ${TABLET_MAX}px)`).matches
    isMobile.value = window.matchMedia(`(max-width: ${MOBILE_MAX}px)`).matches
  }

  onMounted(() => {
    updateLayout()
    window.addEventListener('resize', updateLayout)
  })

  onBeforeUnmount(() => {
    window.removeEventListener('resize', updateLayout)
  })

  const formLabelPosition = computed(() => (isMobile.value ? 'top' : 'right'))
  const formLabelWidth = computed(() => (isMobile.value ? '' : '80px'))

  return {
    isTablet,
    isMobile,
    formLabelPosition,
    formLabelWidth
  }
}
