<template>
  <Teleport to="body">
    <Transition name="image-viewer-fade">
      <div
        v-if="visible"
        class="custom-image-viewer"
        :style="{ zIndex: zIndex }"
        @click.self="handleMaskClick"
        @wheel.prevent="handleWheel"
        @mousedown="handleMouseDown"
        @mousemove="handleMouseMove"
        @mouseup="handleMouseUp"
        @mouseleave="handleMouseUp"
      >
        <!-- 关闭按钮 -->
        <tiny-button
          v-if="closeShow"
          class="custom-image-viewer__close"
          :icon="TinyIconClose"
          :reset-time="0"
          circle
          @click="handleClose"
          :aria-label="t('imageViewer.close')"
        />

        <!-- 上一张/下一张按钮（工具栏隐藏时显示在两侧） -->
        <tiny-button
          v-if="arrowShow && urlList.length > 1 && !toolShow"
          class="custom-image-viewer__arrow custom-image-viewer__arrow--prev"
          :icon="TinyIconChevronLeft"
          :reset-time="0"
          circle
          @click="handlePrev"
          :disabled="!canPrev"
          :aria-label="t('imageViewer.prev')"
        />
        <tiny-button
          v-if="arrowShow && urlList.length > 1 && !toolShow"
          class="custom-image-viewer__arrow custom-image-viewer__arrow--next"
          :icon="TinyIconChevronRight"
          :reset-time="0"
          circle
          @click="handleNext"
          :disabled="!canNext"
          :aria-label="t('imageViewer.next')"
        />

        <!-- 工具栏 -->
        <div v-if="toolShow" class="custom-image-viewer__toolbar">
          <tiny-button
            v-if="arrowShow && urlList.length > 1"
            class="custom-image-viewer__tool"
            :icon="TinyIconChevronLeft"
            circle
            :reset-time="0"
            @click="handlePrev"
            :disabled="!canPrev"
            :aria-label="t('imageViewer.prev')"
          />
          <tiny-button
            v-if="arrowShow && urlList.length > 1"
            class="custom-image-viewer__tool"
            :icon="TinyIconChevronRight"
            circle
            :reset-time="0"
            @click="handleNext"
            :disabled="!canNext"
            :aria-label="t('imageViewer.next')"
          />
          <div v-if="arrowShow && urlList.length > 1" class="custom-image-viewer__divider"></div>
          <tiny-button
            class="custom-image-viewer__tool"
            :icon="TinyIconZoomOut"
            circle
            :reset-time="0"
            @click="handleZoomOut"
            :disabled="scale <= minScale"
            :aria-label="t('imageViewer.zoomOut')"
          />
          <tiny-button
            class="custom-image-viewer__tool"
            :icon="TinyIconZoomIn"
            circle
            :reset-time="0"
            @click="handleZoomIn"
            :disabled="scale >= maxScale"
            :aria-label="t('imageViewer.zoomIn')"
          />
          <tiny-button
            class="custom-image-viewer__tool"
            :icon="TinyIconConmentRefresh"
            circle
            :reset-time="0"
            @click="handleReset"
            :aria-label="t('imageViewer.reset')"
          />
          <div class="custom-image-viewer__divider"></div>
          <tiny-button
            class="custom-image-viewer__tool"
            circle
            :reset-time="0"
            :icon="TinyIconRepeat"
            @click="handleRotateLeft"
            :aria-label="t('imageViewer.rotateLeft')"
          >
          </tiny-button>
          <tiny-button
            class="custom-image-viewer__tool"
            circle
            :icon="TinyIconRefres"
            :reset-time="0"
            @click="handleRotateRight"
            :aria-label="t('imageViewer.rotateRight')"
          >
          </tiny-button>
          <span v-if="showIndex && urlList.length > 1" class="custom-image-viewer__index-inline">{{ currentIndex + 1 }}/{{ urlList.length }}</span>
          <template v-if="closeShow">
            <div class="custom-image-viewer__divider"></div>
            <tiny-button
              class="custom-image-viewer__tool"
              :icon="TinyIconClose"
              circle
              :reset-time="0"
              @click="handleClose"
              :aria-label="t('imageViewer.close')"
            />
          </template>
        </div>

        <!-- 图片容器 -->
        <div class="custom-image-viewer__wrapper">
          <div
            class="custom-image-viewer__content"
            :style="contentStyle"
            @wheel.prevent="handleWheel"
            @mousedown="handleMouseDown"
            @mousemove="handleMouseMove"
            @mouseup="handleMouseUp"
            @mouseleave="handleMouseUp"
          >
            <img
              v-if="currentImageUrl"
              :src="currentImageUrl"
              :alt="`${t('imageViewer.image')} ${currentIndex + 1}`"
              class="custom-image-viewer__image"
              :style="imageStyle"
              draggable="false"
              @load="handleImageLoad"
              @error="handleImageError"
            />
            <div v-else class="custom-image-viewer__loading">
              <div class="custom-image-viewer__spinner"></div>
              <p>{{ t('imageViewer.loading') }}</p>
            </div>
          </div>
        </div>

        <!-- 索引显示（工具栏隐藏时独立显示） -->
        <div v-if="showIndex && urlList.length > 1 && !toolShow" class="custom-image-viewer__index">
          {{ currentIndex + 1 }} / {{ urlList.length }}
        </div>
        
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { Button as TinyButton } from '@opentiny/vue'
import { IconClose, IconChevronLeft, IconChevronRight, IconZoomIn, IconZoomOut, 
  IconRefresh, IconRefres, IconRepeat, IconConmentRefresh} from '@opentiny/vue-icon'
import { t } from '../i18n'

const TinyIconClose = IconClose()
const TinyIconChevronLeft = IconChevronLeft()
const TinyIconChevronRight = IconChevronRight()
const TinyIconZoomIn = IconZoomIn()
const TinyIconZoomOut = IconZoomOut()
const TinyIconRefresh = IconRefresh()
const TinyIconConmentRefresh = IconConmentRefresh()
const TinyIconRefres = IconRefres()
const TinyIconRepeat = IconRepeat()


interface Props {
  urlList: string[]
  visible?: boolean
  startPosition?: number
  zIndex?: number
  closeShow?: boolean
  arrowShow?: boolean
  toolShow?: boolean
  showIndex?: boolean
  maskClosable?: boolean
  minScale?: number
  maxScale?: number
  scaleStep?: number
}

const props = withDefaults(defineProps<Props>(), {
  urlList: () => [],
  visible: false,
  startPosition: 0,
  zIndex: 2000,
  closeShow: true,
  arrowShow: true,
  toolShow: true,
  showIndex: true,
  maskClosable: true,
  minScale: 0.5,
  maxScale: 3,
  scaleStep: 0.1
})

const emit = defineEmits<{
  close: []
  switch: [index: number]
}>()

// 当前索引
const currentIndex = ref(props.startPosition)
// 缩放比例
const scale = ref(1)
// 旋转角度（度）
const rotation = ref(0)
// 偏移量
const offsetX = ref(0)
const offsetY = ref(0)
// 拖拽状态
const isDragging = ref(false)
const dragStartX = ref(0)
const dragStartY = ref(0)
const dragStartOffsetX = ref(0)
const dragStartOffsetY = ref(0)
// 图片加载状态
const imageLoaded = ref(false)

// 当前图片URL
const currentImageUrl = computed(() => {
  if (props.urlList.length === 0 || currentIndex.value < 0 || currentIndex.value >= props.urlList.length) {
    return ''
  }
  return props.urlList[currentIndex.value]
})

// 是否可以上一张
const canPrev = computed(() => currentIndex.value > 0)
// 是否可以下一张
const canNext = computed(() => currentIndex.value < props.urlList.length - 1)

// 内容样式
const contentStyle = computed(() => ({
  transform: `translate(${offsetX.value}px, ${offsetY.value}px) scale(${scale.value}) rotate(${rotation.value}deg)`,
  transition: isDragging.value ? 'none' : 'transform 0.3s ease'
}))

// 图片样式
const imageStyle = computed(() => ({
  maxWidth: '100vw',
  maxHeight: '100vh',
  objectFit: 'contain' as const
}))

// 监听 visible 变化，重置状态
watch(() => props.visible, (newVal) => {
  if (newVal) {
    currentIndex.value = Math.max(0, Math.min(props.startPosition, props.urlList.length - 1))
    resetTransform()
    imageLoaded.value = false
  }
})

// 监听 startPosition 变化
watch(() => props.startPosition, (newVal) => {
  if (props.visible) {
    currentIndex.value = Math.max(0, Math.min(newVal, props.urlList.length - 1))
    resetTransform()
  }
})

// 重置变换
const resetTransform = () => {
  scale.value = 1
  rotation.value = 0
  offsetX.value = 0
  offsetY.value = 0
}

// 左旋转（逆时针）
const handleRotateLeft = () => {
  rotation.value = rotation.value - 90
}

// 右旋转（顺时针）
const handleRotateRight = () => {
  rotation.value = rotation.value + 90
}

// 关闭
const handleClose = () => {
  emit('close')
}

// 遮罩点击
const handleMaskClick = () => {
  if (props.maskClosable) {
    handleClose()
  }
}

// 上一张
const handlePrev = () => {
  if (canPrev.value) {
    currentIndex.value--
    resetTransform()
    emit('switch', currentIndex.value)
  }
}

// 下一张
const handleNext = () => {
  if (canNext.value) {
    currentIndex.value++
    resetTransform()
    emit('switch', currentIndex.value)
  }
}

// 放大
const handleZoomIn = () => {
  scale.value = Math.min(scale.value + props.scaleStep, props.maxScale)
}

// 缩小
const handleZoomOut = () => {
  scale.value = Math.max(scale.value - props.scaleStep, props.minScale)
}

// 重置
const handleReset = () => {
  resetTransform()
}

// 鼠标滚轮缩放
const handleWheel = (e: WheelEvent) => {
  e.preventDefault()
  const delta = e.deltaY > 0 ? -props.scaleStep : props.scaleStep
  scale.value = Math.max(props.minScale, Math.min(scale.value + delta, props.maxScale))
}

// 鼠标按下（仅左键，点击按钮/工具栏不触发拖拽；图片上点击也可拖拽）
const handleMouseDown = (e: MouseEvent) => {
  if (e.button !== 0) return // 只响应左键
  const target = e.target as HTMLElement
  if (target.closest('button') || target.closest('.custom-image-viewer__toolbar') || target.closest('.custom-image-viewer__close') || target.closest('.custom-image-viewer__arrow')) {
    return
  }
  e.preventDefault() // 禁止图片默认拖拽等，确保在图片上也能拖拽视图
  isDragging.value = true
  dragStartX.value = e.clientX
  dragStartY.value = e.clientY
  dragStartOffsetX.value = offsetX.value
  dragStartOffsetY.value = offsetY.value
}

// 鼠标移动（仅左键按下时更新位置）
const handleMouseMove = (e: MouseEvent) => {
  if (!isDragging.value) return
  if ((e.buttons & 1) !== 1) {
    // 左键已松开（例如在窗口外松开后移回）
    isDragging.value = false
    return
  }
  offsetX.value = dragStartOffsetX.value + (e.clientX - dragStartX.value)
  offsetY.value = dragStartOffsetY.value + (e.clientY - dragStartY.value)
}

// 鼠标释放（仅左键松开时结束拖拽）
const handleMouseUp = (e: MouseEvent) => {
  if (e.button === 0) {
    isDragging.value = false
  }
}

// 图片加载完成
const handleImageLoad = () => {
  imageLoaded.value = true
}

// 图片加载错误
const handleImageError = () => {
  imageLoaded.value = false
  console.error('图片加载失败:', currentImageUrl.value)
}

// 键盘事件处理
const handleKeyDown = (e: KeyboardEvent) => {
  if (!props.visible) return

  switch (e.key) {
    case 'Escape':
      handleClose()
      break
    case 'ArrowLeft':
      handlePrev()
      break
    case 'ArrowRight':
      handleNext()
      break
    case 'ArrowUp':
      handleZoomIn()
      break
    case 'ArrowDown':
      handleZoomOut()
      break
    case '+':
    case '=':
      handleZoomIn()
      break
    case '-':
      handleZoomOut()
      break
    case '0':
      handleReset()
      break
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown)
})
</script>

<style lang="less" scoped>
:deep(.tiny-button) {
  width: 60px;
  height: 60px;
  background: #c2c2c2;
  border: none;
  outline: none;
  &:focus {
    outline: none;
  }
}
.custom-image-viewer {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0,0,0,.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  user-select: none;
  cursor: grab;

  &.is-dragging {
    cursor: grabbing;
  }

  &__close {
    position: absolute;
    top: 20px;
    right: 20px;
    z-index: 10;
    
    :deep(.tiny-button) {
      width: 48px;
      height: 48px;
      background: rgba(255, 255, 255, 0.1);
      border: none;
      color: #fff;
      transition: all 0.3s ease;
      outline: none;

      &:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: scale(1.1);
      }

      &:active {
        transform: scale(0.95);
      }

      &:focus,
      &:focus-visible {
        outline: none;
        box-shadow: none;
      }
    }
  }

  &__arrow {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    z-index: 10;

    :deep(.tiny-button) {
      width: 48px;
      height: 48px;
      background: rgba(255, 255, 255, 0.1);
      border: none;
      color: #fff;

      &:hover:not(:disabled) {
        background: rgba(255, 255, 255, 0.2);
        transform: scale(1.1);
      }

      &:active:not(:disabled) {
        transform: scale(0.95);
      }

      &:disabled {
        opacity: 0.3;
        cursor: not-allowed;
      }

      &:focus {
        outline: none;
        box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.5);
      }
    }

    &--prev {
      left: 20px;
    }

    &--next {
      right: 20px;
    }
  }

  &__toolbar {
    position: absolute;
    bottom: 30px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    align-items: center;
    gap: 8px;
    background: #c2c2c2;
    backdrop-filter: blur(10px);
    padding: 10px 16px;
    border-radius: 32px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(255, 255, 255, 0.2);
    z-index: 10;
  }

  &__divider {
    width: 1px;
    height: 24px;
    background: rgba(0, 0, 0, 0.2);
    margin: 0 4px;
  }

  &__index-inline {
    margin-left: 8px;
    padding: 0 4px;
    color: #fff;
    font-size: 14px;
    font-weight: 500;
    letter-spacing: 0.5px;
    text-shadow: 0 0 4px rgba(255, 255, 255, 0.9), 0 1px 2px rgba(255, 255, 255, 0.5);
    flex-shrink: 0;
  }

  &__tool {
    :deep(.tiny-button) {
      width: 44px;
      height: 44px;
      background: #c2c2c2;
      border: none;
      color: #fff;
      transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
      position: relative;
      overflow: visible;
      outline: none;

      svg {
        width: 26px;
        height: 26px;
        position: relative;
        z-index: 1;
        filter: drop-shadow(0 0 3px rgba(255, 255, 255, 0.9)) drop-shadow(0 1px 2px rgba(255, 255, 255, 0.4));
      }

      &:hover:not(:disabled) {
        transform: scale(1.08);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
      }

      &:active:not(:disabled) {
        transform: scale(0.96);
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
      }

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
        background: #a8a8a8;
      }

      &:focus,
      &:focus-visible {
        outline: none;
        box-shadow: none;
      }
    }
  }

  &__wrapper {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
  }

  &__content {
    position: relative;
    transform-origin: center center;
    cursor: grab;

    &:active {
      cursor: grabbing;
    }
  }

  &__image {
    display: block;
    transform-origin: center center;
  }

  &__image {
    display: block;
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
  }

  &__loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #fff;
    gap: 16px;

    p {
      margin: 0;
      font-size: 14px;
    }
  }

  &__spinner {
    width: 40px;
    height: 40px;
    border: 3px solid rgba(255, 255, 255, 0.3);
    border-top-color: #8b5cf6;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  &__index {
    position: absolute;
    bottom: 30px;
    left: 50%;
    transform: translateX(-50%);
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.95) 0%, rgba(124, 58, 237, 0.95) 100%);
    backdrop-filter: blur(10px);
    color: #fff;
    padding: 10px 20px;
    border-radius: 20px;
    font-size: 14px;
    font-weight: 500;
    z-index: 10;
    margin-bottom: 70px; // 避免与工具栏重叠
    box-shadow: 0 4px 16px rgba(139, 92, 246, 0.3), 0 0 0 1px rgba(255, 255, 255, 0.1);
    letter-spacing: 0.5px;
  }
}

// 过渡动画
.image-viewer-fade-enter-active,
.image-viewer-fade-leave-active {
  transition: opacity 0.3s ease;
}

.image-viewer-fade-enter-from,
.image-viewer-fade-leave-to {
  opacity: 0;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

// 响应式设计
@media (max-width: 768px) {
  .custom-image-viewer {
    &__close,
    &__arrow {
      :deep(.tiny-button) {
        width: 40px;
        height: 40px;

        svg {
          width: 20px;
          height: 20px;
        }
      }
    }

    &__arrow {
      &--prev {
        left: 10px;
      }

      &--next {
        right: 10px;
      }
    }

    &__toolbar {
      bottom: 20px;
      padding: 8px;
      gap: 8px;
    }

    &__tool {
      :deep(.tiny-button) {
        width: 40px;
        height: 40px;

        svg {
          width: 22px;
          height: 22px;
        }
      }
    }

    &__index {
      bottom: 20px;
      margin-bottom: 50px;
      font-size: 12px;
      padding: 6px 12px;
    }
  }
}
</style>
