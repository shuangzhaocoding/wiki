<template>
  <div
    class="editor-container"
    :class="{
      'editor-preview': isReadOnlyLike,
      'editor-container--with-edit-toc': showEditToc,
    }"
  >
    <div class="fluent-editor-v4-layout">
      <div class="fluent-editor-v4-main">
        <!-- 目录相对编辑区容器定位：叠在正文区域右侧（非与整列并排抢宽） -->
        <div
          ref="editorSurfaceEl"
          class="fluent-editor-v4-editor-surface"
          :class="{
            'fluent-editor-v4-editor-surface--toc-open':
              showEditToc && !editTocCollapsed && showFloatingScrollActions,
          }"
          :style="editTocSurfaceStyle"
        >
          <!-- 复用 v3 组件的 class，尽量不改现有样式选择器 -->
          <div ref="hostEl" class="tiny-fluent-editor" />
          <!-- 代码块复制按钮层：不可插入 .ql-code-block-container（仅允许子 blot），只能叠在编辑区外 -->
          <div ref="codeBlockCopyLayerEl" class="fe-code-block-copy-layer" aria-hidden="true" />
          <!-- 无右侧目录、或目录折叠时：浮动回到顶部/底部（滚动 .ql-editor） -->
          <Transition name="edit-scroll-float-reveal">
            <div
              v-if="!isReadOnlyLike && showFloatingScrollActions && (!showEditToc || editTocCollapsed)"
              key="fluent-scroll-float"
              class="fluent-editor-v4-scroll-actions"
              role="toolbar"
              :aria-label="scrollToolbarAria"
            >
              <button
                type="button"
                class="fluent-editor-v4-scroll-actions__btn"
                :title="backToTopTitle"
                :aria-label="backToTopTitle"
                @click="scrollEditEditorToTop"
              >
                <svg class="fluent-editor-v4-scroll-actions__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                  <polyline points="18 15 12 9 6 15" />
                </svg>
              </button>
              <button
                type="button"
                class="fluent-editor-v4-scroll-actions__btn"
                :title="backToBottomTitle"
                :aria-label="backToBottomTitle"
                @click="scrollEditEditorToBottom"
              >
                <svg class="fluent-editor-v4-scroll-actions__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                  <polyline points="6 9 12 15 18 9" />
                </svg>
              </button>
              <!-- 目录折叠时：展开目录，放在滚动按钮下方 -->
              <button
                v-if="showEditToc && editTocCollapsed"
                type="button"
                class="fluent-editor-v4-scroll-actions__btn fluent-editor-v4-scroll-actions__btn--toc-expand"
                :title="editTocShowTitle"
                :aria-label="editTocShowTitle"
                @click="editTocCollapsed = false"
              >
                <svg class="fluent-editor-v4-scroll-actions__toc-expand-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                  <polyline points="11 17 6 12 11 7" />
                  <polyline points="18 17 13 12 18 7" />
                </svg>
              </button>
            </div>
          </Transition>
          <!-- 编辑态目录：相对 .fluent-editor-v4-editor-surface 绝对定位在右侧 -->
          <aside
            v-if="showEditToc && !editTocCollapsed && showFloatingScrollActions"
            key="fluent-edit-toc"
            class="fluent-editor-v4-toc"
            :style="{ width: editTocWidth + 'px' }"
            :aria-label="tocTitleText"
          >
        <div
          class="fluent-editor-v4-toc__resize-handle"
          role="separator"
          aria-orientation="vertical"
          :aria-label="editTocResizeAria"
          :class="{ 'is-dragging': editTocResizing }"
          @mousedown.prevent="onEditTocResizeStart"
        >
          <svg
            class="fluent-editor-v4-toc__resize-handle-icon"
            viewBox="0 0 12 24"
            aria-hidden="true"
            focusable="false"
          >
            <circle cx="3" cy="6" r="1.5" fill="currentColor" />
            <circle cx="9" cy="6" r="1.5" fill="currentColor" />
            <circle cx="3" cy="12" r="1.5" fill="currentColor" />
            <circle cx="9" cy="12" r="1.5" fill="currentColor" />
            <circle cx="3" cy="18" r="1.5" fill="currentColor" />
            <circle cx="9" cy="18" r="1.5" fill="currentColor" />
          </svg>
        </div>
        <div class="fluent-editor-v4-toc__inner">
          <div class="fluent-editor-v4-toc__header">
            <h3 class="fluent-editor-v4-toc__title">{{ tocTitleText }}</h3>
          </div>
          <div class="fluent-editor-v4-toc__body">
            <p v-if="editTocItems.length === 0" class="fluent-editor-v4-toc__empty">{{ emptyTocHint }}</p>
            <div v-else ref="editTocTreeWrapRef" class="fluent-editor-v4-toc__tree-wrap">
              <tiny-tree
                :data="editTocTreeData"
                :expand-on-click-node="false"
                :props="{ children: 'children', label: 'label' }"
                node-key="id"
                :default-expand-all="true"
                :highlight-current="false"
                @node-click="handleEditTocTreeNodeClick"
              >
                <template #default="{ node, data }">
                  <span
                    class="fluent-editor-v4-toc__node-label"
                    :class="{ 'is-edit-toc-active': editTocActiveHeadingId === data.id }"
                    :data-edit-toc-id="data.id"
                    :title="String(node.label ?? '')"
                  >
                    {{ node.label }}
                  </span>
                </template>
              </tiny-tree>
            </div>
          </div>
          <div class="fluent-editor-v4-toc__footer">
            <button
              type="button"
              class="fluent-editor-v4-toc__scroll-btn"
              :title="backToTopTitle"
              :aria-label="backToTopTitle"
              @click="scrollEditEditorToTop"
            >
              <svg class="fluent-editor-v4-toc__scroll-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <polyline points="18 15 12 9 6 15" />
              </svg>
              <span class="fluent-editor-v4-toc__scroll-text">{{ backToTopTitle }}</span>
            </button>
            <button
              type="button"
              class="fluent-editor-v4-toc__scroll-btn"
              :title="backToBottomTitle"
              :aria-label="backToBottomTitle"
              @click="scrollEditEditorToBottom"
            >
              <svg class="fluent-editor-v4-toc__scroll-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <polyline points="6 9 12 15 18 9" />
              </svg>
              <span class="fluent-editor-v4-toc__scroll-text">{{ backToBottomTitle }}</span>
            </button>
            <button
              type="button"
              class="fluent-editor-v4-toc__toggle fluent-editor-v4-toc__toggle--footer"
              :title="editTocHideTitle"
              :aria-label="editTocHideTitle"
              @click="editTocCollapsed = true"
            >
              <svg class="fluent-editor-v4-toc__toggle-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <polyline points="13 17 18 12 13 7" />
                <polyline points="6 17 11 12 6 7" />
              </svg>
            </button>
          </div>
        </div>
      </aside>
        </div>
      </div>
    </div>
    <div v-if="uploadPendingCount > 0 && !readonly" class="editor-upload-overlay">
      <div class="editor-upload-overlay__card">
        <span class="editor-upload-overlay__spinner" />
        <span class="editor-upload-overlay__text">文件上传中...</span>
      </div>
    </div>
    <div v-if="previewVisible" class="editor-preview-modal" @click.self="closeAttachmentPreview">
      <div class="editor-preview-modal__panel">
        <div class="editor-preview-modal__header">
          <div class="editor-preview-modal__title" :title="previewFileName">{{ previewFileName }}</div>
          <button type="button" class="editor-preview-modal__close" @click="closeAttachmentPreview">
            <span class="editor-preview-modal__close-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">
                <path d="M6 6l12 12" />
                <path d="M18 6L6 18" />
              </svg>
            </span>
            <span>关闭</span>
          </button>
        </div>
        <div class="editor-preview-modal__body">
          <img
            v-if="previewFileUrl && isImageFile(previewFileName)"
            :src="previewFileUrl"
            :alt="previewFileName"
            class="editor-preview-modal__image"
          />

          <video
            v-else-if="previewFileUrl && isVideoFile(previewFileName)"
            :src="previewFileUrl"
            controls
            class="editor-preview-modal__video"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, h, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { Tree as TinyTree, Modal, Button as TinyButton } from '@opentiny/vue'
import FluentEditor, {
  FULL_TOOLBAR,
  I18N,
  generateToolbarTip,
  generateTableUp,
  CollaborationModule,
  ImagePreviewModal,
} from '@opentiny/fluent-editor'

// fluent-editor 双击图片预览：关闭按钮单独挂在 body 上，库内 hide() 未隐藏该节点，关闭后仍残留在右上角
{
  const proto = ImagePreviewModal.prototype
  const origHide = proto.hide
  const origShow = proto.show
  proto.hide = function (this: ImagePreviewModal) {
    origHide.call(this)
    document.querySelectorAll('.tiny-editor-image-preview-close').forEach((el) => {
      ;(el as HTMLElement).style.display = 'none'
    })
  }
  proto.show = function (this: ImagePreviewModal, imageUrl: string) {
    origShow.call(this, imageUrl)
    document.querySelectorAll('.tiny-editor-image-preview-close').forEach((el) => {
      ;(el as HTMLElement).style.removeProperty('display')
    })
  }
}
import { useLocaleStore } from '../stores/locale'
import { fileApi } from '../api/file'
import { userManagementApi } from '../api/userManagement'
import type { User } from '../api/userManagement'
// emoji 表情
import data from '@emoji-mart/data';
import { computePosition } from '@floating-ui/dom';
import type { EmojiMartData } from '@emoji-mart/data';
import { Picker } from 'emoji-mart';
import { t } from '../i18n'
import { marked } from 'marked'
// table 表格
import {
  defaultCustomSelect,
  TableMenuContextmenu,
  TableSelection,
  TableResizeBox, TableResizeLine, TableResizeScale,
  TableMenuSelect,
  TableUp,
} from 'quill-table-up';
import 'quill-table-up/index.css';
import 'quill-table-up/table-creator.css';

// toolbar-tip 工具栏提示
import QuillToolbarTip from 'quill-toolbar-tip';
import 'quill-toolbar-tip/dist/index.css';

// formula 可编辑公式
import type { MathliveModule } from '@opentiny/fluent-editor';
import 'mathlive';
import 'mathlive/static.css';
import 'mathlive/fonts.css';

// markdown 操作
import MarkdownShortcuts from 'quill-markdown-shortcuts';

// mind-map 思维导图
import SimpleMindMap from 'simple-mind-map';
import Drag from 'simple-mind-map/src/plugins/Drag.js';
import Export from 'simple-mind-map/src/plugins/Export.js';
import Themes from 'simple-mind-map-plugin-themes';
import nodeIconList from 'simple-mind-map/src/svg/icons';

// flow-chart 流程图
import LogicFlow from '@logicflow/core';
import { DndPanel, SelectionSelect, Snapshot } from '@logicflow/extension';

// syntax 语法高亮
import hljs from 'highlight.js';
import go from 'highlight.js/lib/languages/go'
import 'highlight.js/styles/atom-one-dark.css';
hljs.registerLanguage('go', go)

// screenshot 截屏
import Html2Canvas from 'html2canvas';
window.Html2Canvas = Html2Canvas;
// mention @提醒
const searchKey = 'name';

// mention 用户搜索（后端分页搜索 + 结果缓存）
const mentionSearchSeq = { value: 0 }
const mentionSearchCache = new Map<string, { expiresAt: number; items: any[] }>()
const MENTION_SEARCH_CACHE_TTL_MS = 30_000
const mentionSearchPageSize = 10
const normalizeMentionKeyword = (term: string) => term?.trim?.() ?? ''
const mapUserToMentionItem = (u: User) => {
  const name = u.username || String(u.id)
  return {
    id: u.id,
    name, // mention-link 的数据集会用 searchKey=name 取该字段
    cn: u.username || String(u.id), // itemKey=cn：下拉展示内容
    email: u.email,
  }
}
// 公式
import katex from 'katex';
import 'katex/dist/katex.min.css';
window.katex = katex;
import { openOfficeOnlinePreview } from '../utils/officePreview'
type FluentEditorOptions = Record<string, any>

const props = withDefaults(
  defineProps<{
    modelValue?: string
    options?: FluentEditorOptions
    modules?: Record<string, any>
    toolbar?: any
    disabled?: boolean
    readonly?: boolean
    placeholder?: string
    articleId?: number
    /** 为 true 时在编辑器右侧显示标题目录（如文章编辑页传入 isEditing） */
    showEditToc?: boolean
    /** 为 false 时不显示右下角顶/底浮动与目录展开（评论、回复、反馈等内嵌场景） */
    showFloatingScrollActions?: boolean
  }>(),
  {
    showEditToc: false,
    showFloatingScrollActions: true,
  }
)
const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
}>()

/** 只读 / 禁用：不展示右下角顶底浮动按钮（与 Quill readOnly 语义对齐） */
const isReadOnlyLike = computed(() => !!(props.readonly || props.disabled))

const localeStore = useLocaleStore()
const hostEl = ref<HTMLDivElement | null>(null)
/** 代码块复制按钮叠层（与 .ql-editor 内 DOM 分离，避免 Quill 剔除） */
const codeBlockCopyLayerEl = ref<HTMLElement | null>(null)
/** 包裹工具栏+正文+目录，目录 absolute 相对此节点定位 */
const editorSurfaceEl = ref<HTMLDivElement | null>(null)
const uploadPendingCount = ref(0)
const previewVisible = ref(false)
const previewFileUrl = ref('')
const previewFileName = ref('')
const previewFileType = ref('')

let editor: FluentEditor | null = null
const quillRef = ref<FluentEditor | null>(null)
let isSyncingFromModel = false
let isModelUpdateFromEditor = false
let modelIsDeltaJson = true

/** 代码块「复制」按钮叠层（Quill CodeBlockContainer 仅允许 .ql-code-block 子节点，不能往容器内插 DOM） */
let codeBlockCopyMountTimer: ReturnType<typeof setTimeout> | null = null
let codeBlockCopyPositionRaf = 0
const copyButtonToCodeContainer = new WeakMap<HTMLElement, Element>()
let codeBlockCopyScrollHandler: (() => void) | null = null
let codeBlockCopyResizeObserver: ResizeObserver | null = null

function getCodeBlockPlainText(container: Element): string {
  const lines = container.querySelectorAll<HTMLElement>('.ql-code-block')
  if (!lines.length) {
    return (container.textContent ?? '').replace(/\u00a0/g, ' ')
  }
  return Array.from(lines)
    .map((el) => (el.textContent ?? '').replace(/\u00a0/g, ' '))
    .join('\n')
}

async function copyTextToClipboard(text: string): Promise<boolean> {
  try {
    if (typeof navigator !== 'undefined' && navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text)
      return true
    }
  } catch {
    /* 降级 */
  }
  try {
    const ta = document.createElement('textarea')
    ta.value = text
    ta.setAttribute('readonly', '')
    ta.style.position = 'fixed'
    ta.style.left = '-9999px'
    ta.style.top = '0'
    document.body.appendChild(ta)
    ta.focus()
    ta.select()
    const ok = document.execCommand('copy')
    document.body.removeChild(ta)
    return ok
  } catch {
    return false
  }
}

/** 与 .ql-ui 左侧对齐的间距（px）；按钮为正方形，边长取 .ql-ui 的 height */
const CODE_COPY_GAP_TO_QL_UI = 6
const CODE_COPY_FALLBACK_SIDE = 22

function applyCopyButtonSquareSize(btn: HTMLElement, sidePx: number) {
  const s = `${sidePx}px`
  btn.style.width = s
  btn.style.height = s
  btn.style.minWidth = s
  btn.style.minHeight = s
}

function positionCodeBlockCopyButton(btn: HTMLElement, container: Element, surface: HTMLElement) {
  const cr = container.getBoundingClientRect()
  const sr = surface.getBoundingClientRect()
  const ui = container.querySelector('.ql-ui') as HTMLElement | null
  let top: number
  let left: number
  if (ui) {
    const ur = ui.getBoundingClientRect()
    const raw = ur.height > 0 ? ur.height : ur.width > 0 ? ur.width : CODE_COPY_FALLBACK_SIDE
    const side = Math.max(12, Math.round(raw))
    applyCopyButtonSquareSize(btn, side)
    left = ur.left - sr.left - side - CODE_COPY_GAP_TO_QL_UI
    top = ur.top - sr.top
  } else {
    applyCopyButtonSquareSize(btn, Math.max(12, CODE_COPY_FALLBACK_SIDE))
    const pad = 8
    top = cr.top - sr.top + 6
    left = cr.right - sr.left - CODE_COPY_FALLBACK_SIDE - pad
  }
  const intersects =
    cr.width > 0 &&
    cr.height > 0 &&
    cr.bottom > sr.top &&
    cr.top < sr.bottom &&
    cr.right > sr.left &&
    cr.left < sr.right
  btn.style.position = 'absolute'
  btn.style.top = `${Math.round(top)}px`
  btn.style.left = `${Math.round(left)}px`
  btn.style.visibility = intersects ? 'visible' : 'hidden'
  btn.style.pointerEvents = intersects ? 'auto' : 'none'
}

function positionAllCodeBlockCopyButtons() {
  const layer = codeBlockCopyLayerEl.value
  const surface = editorSurfaceEl.value
  if (!layer || !surface || !editor?.root) return
  layer.querySelectorAll<HTMLElement>('.fe-code-block-copy').forEach((btn) => {
    const container = copyButtonToCodeContainer.get(btn)
    if (container && document.contains(container)) {
      positionCodeBlockCopyButton(btn, container, surface)
    }
  })
}

function schedulePositionCodeBlockCopyButtons() {
  cancelAnimationFrame(codeBlockCopyPositionRaf)
  codeBlockCopyPositionRaf = requestAnimationFrame(() => {
    codeBlockCopyPositionRaf = 0
    positionAllCodeBlockCopyButtons()
  })
}

function mountCodeBlockCopyButtons(root: HTMLElement) {
  const layer = codeBlockCopyLayerEl.value
  const surface = editorSurfaceEl.value
  if (!layer || !surface) return
  layer.innerHTML = ''
  const copyLabel = t('article.copyCode')
  root.querySelectorAll('.ql-code-block-container').forEach((container) => {
    const btn = document.createElement('div')
    btn.className = 'fe-code-block-copy'
    btn.setAttribute('aria-label', copyLabel)
    btn.setAttribute('title', copyLabel)
    btn.innerHTML =
      '<div class="fe-code-block-copy__icon-wrap" aria-hidden="true"><svg class="fe-code-block-copy__icon" viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="13" height="13" rx="2" ry="2" fill="none" stroke="#ffffff"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" fill="none" stroke="#ffffff"/></svg></div>'
    copyButtonToCodeContainer.set(btn, container)
    layer.appendChild(btn)
    positionCodeBlockCopyButton(btn, container, surface)
  })
}

function scheduleCodeBlockCopyMount() {
  if (!editor?.root) return
  if (codeBlockCopyMountTimer) clearTimeout(codeBlockCopyMountTimer)
  codeBlockCopyMountTimer = setTimeout(() => {
    codeBlockCopyMountTimer = null
    if (!editor?.root) return
    mountCodeBlockCopyButtons(editor.root)
  }, 120)
}

function refreshCodeBlockCopyButtonLabels() {
  const copyLabel = t('article.copyCode')
  codeBlockCopyLayerEl.value?.querySelectorAll('.fe-code-block-copy').forEach((el) => {
    el.setAttribute('aria-label', copyLabel)
    el.setAttribute('title', copyLabel)
  })
}

function bindCodeBlockCopyLayoutSync() {
  teardownCodeBlockCopyLayoutSync()
  if (!editor?.root) return
  codeBlockCopyScrollHandler = () => {
    schedulePositionCodeBlockCopyButtons()
  }
  editor.root.addEventListener('scroll', codeBlockCopyScrollHandler, { passive: true })
  window.addEventListener('scroll', codeBlockCopyScrollHandler, { passive: true })
  const surface = editorSurfaceEl.value
  if (surface) {
    codeBlockCopyResizeObserver = new ResizeObserver(() => {
      schedulePositionCodeBlockCopyButtons()
    })
    codeBlockCopyResizeObserver.observe(surface)
  }
}

function teardownCodeBlockCopyLayoutSync() {
  if (editor?.root && codeBlockCopyScrollHandler) {
    editor.root.removeEventListener('scroll', codeBlockCopyScrollHandler)
  }
  if (codeBlockCopyScrollHandler) {
    window.removeEventListener('scroll', codeBlockCopyScrollHandler)
  }
  codeBlockCopyScrollHandler = null
  if (codeBlockCopyResizeObserver) {
    codeBlockCopyResizeObserver.disconnect()
    codeBlockCopyResizeObserver = null
  }
  cancelAnimationFrame(codeBlockCopyPositionRaf)
  codeBlockCopyPositionRaf = 0
}

function handleCodeBlockCopyClickCapture(e: Event) {
  const ev = e as MouseEvent
  const target = ev.target as HTMLElement | null
  const btn = target?.closest?.('.fe-code-block-copy') as HTMLElement | null
  const layer = codeBlockCopyLayerEl.value
  if (!btn || !layer?.contains(btn)) return
  const container = copyButtonToCodeContainer.get(btn)
  if (!container) return
  ev.preventDefault()
  ev.stopPropagation()
  const text = getCodeBlockPlainText(container)
  void (async () => {
    const ok = await copyTextToClipboard(text)
    if (ok) {
      Modal.message({ message: t('article.copyCodeSuccess'), status: 'success' })
    } else {
      Modal.message({ message: t('article.copyCodeFailed'), status: 'error' })
    }
  })()
}

/** 编辑态右侧目录 */
interface EditTocItem {
  id: string
  text: string
  level: number
}

const editTocItems = ref<EditTocItem[]>([])
let editTocTimer: ReturnType<typeof setTimeout> | null = null

/** 目录树滚动容器（用于「跟随滚动」时把当前项滚进可视区） */
const editTocTreeWrapRef = ref<HTMLElement | null>(null)
/** 与正文滚动同步的当前标题 id */
const editTocActiveHeadingId = ref<string | null>(null)
let editTocScrollSpyRaf = 0
let editTocScrollBound = false
const EDIT_TOC_SCROLL_OPTS: AddEventListenerOptions = { passive: true }

/** 扁平标题 → Tiny Tree 数据（与文章阅读态目录相同的层级规则） */
function buildEditTocTreeFromFlat(items: EditTocItem[]): { id: string; label: string; children?: any[] }[] {
  if (items.length === 0) return []
  const tree: any[] = []
  const stack: any[] = []
  items.forEach((item) => {
    const node: any = {
      id: item.id,
      label: item.text,
      level: item.level,
    }
    while (stack.length > 0 && stack[stack.length - 1].level >= item.level) {
      stack.pop()
    }
    if (stack.length === 0) {
      tree.push(node)
    } else {
      const parent = stack[stack.length - 1]
      if (!parent.children) parent.children = []
      parent.children.push(node)
    }
    stack.push(node)
  })
  const prune = (nodes: any[]): { id: string; label: string; children?: any[] }[] =>
    nodes.map((n) => {
      const out: { id: string; label: string; children?: any[] } = { id: n.id, label: n.label }
      if (n.children?.length) {
        out.children = prune(n.children)
      }
      return out
    })
  return prune(tree)
}

const editTocTreeData = computed(() => buildEditTocTreeFromFlat(editTocItems.value))

function handleEditTocTreeNodeClick(data: { id?: string }) {
  if (data?.id) scrollToEditTocHeading(data.id)
}

const tocTitleText = computed(() => {
  void localeStore.localeKey
  return t('article.tableOfContents')
})

const emptyTocHint = computed(() => {
  void localeStore.localeKey
  return t('article.emptyContent')
})

/** 编辑目录折叠（仅右侧栏，不持久化） */
const editTocCollapsed = ref(false)

const EDIT_TOC_WIDTH_STORAGE_KEY = 'fluentEditorV4_editTocWidth'
const MIN_EDIT_TOC_WIDTH = 180
const MAX_EDIT_TOC_WIDTH = 720
const DEFAULT_EDIT_TOC_WIDTH = 300

function readStoredEditTocWidth(): number {
  try {
    const raw = localStorage.getItem(EDIT_TOC_WIDTH_STORAGE_KEY)
    if (!raw) return DEFAULT_EDIT_TOC_WIDTH
    const n = parseInt(raw, 10)
    if (!Number.isFinite(n)) return DEFAULT_EDIT_TOC_WIDTH
    return Math.min(MAX_EDIT_TOC_WIDTH, Math.max(MIN_EDIT_TOC_WIDTH, n))
  } catch {
    return DEFAULT_EDIT_TOC_WIDTH
  }
}

const editTocWidth = ref(readStoredEditTocWidth())
const editTocResizing = ref(false)

/** 目录叠在编辑区右侧时注入宽度，供正文 padding 避让 */
const editTocSurfaceStyle = computed(() => {
  if (!props.showEditToc || editTocCollapsed.value || !props.showFloatingScrollActions) {
    return {}
  }
  return {
    '--fe-edit-toc-width': `${editTocWidth.value}px`,
  }
})

/** 监听工具栏 + 编辑区容器尺寸；浏览器缩放时 offsetHeight 与百分比高度易不同步，需配合 getBoundingClientRect 与 visualViewport */
let editTocDockResizeObserver: ResizeObserver | null = null
let editTocVisualViewportCleanup: (() => void) | null = null

function syncEditTocDockTop() {
  const surface = editorSurfaceEl.value
  const host = hostEl.value
  if (!surface || !host) return
  const tb = host.querySelector('.ql-toolbar') as HTMLElement | null
  if (!tb) return
  const s = surface.getBoundingClientRect()
  const tr = tb.getBoundingClientRect()
  // 目录 top = 工具栏下沿相对 surface 上沿；缩放/子像素下比单用 offsetHeight 稳
  const delta = tr.bottom - s.top
  const oh = tb.offsetHeight
  const topPx = Math.max(0, Math.ceil(Math.max(delta, oh)))
  surface.style.setProperty('--fe-edit-toc-top', `${topPx}px`)
}

/** 布局稳定后再量一次（缩放、目录 v-if 显示、flex 重排后） */
function scheduleSyncEditTocDockTop() {
  syncEditTocDockTop()
  requestAnimationFrame(() => {
    syncEditTocDockTop()
    requestAnimationFrame(() => {
      syncEditTocDockTop()
    })
  })
}

function teardownEditTocDockTopObserver() {
  if (editTocDockResizeObserver) {
    editTocDockResizeObserver.disconnect()
    editTocDockResizeObserver = null
  }
  if (editTocVisualViewportCleanup) {
    editTocVisualViewportCleanup()
    editTocVisualViewportCleanup = null
  }
}

function bindEditTocVisualViewport() {
  if (editTocVisualViewportCleanup) {
    editTocVisualViewportCleanup()
    editTocVisualViewportCleanup = null
  }
  const vv = window.visualViewport
  if (!vv) return
  const handler = () => scheduleSyncEditTocDockTop()
  vv.addEventListener('resize', handler)
  vv.addEventListener('scroll', handler)
  editTocVisualViewportCleanup = () => {
    vv.removeEventListener('resize', handler)
    vv.removeEventListener('scroll', handler)
  }
}

function bindEditTocDockTopObserver() {
  teardownEditTocDockTopObserver()
  const host = hostEl.value
  const surface = editorSurfaceEl.value
  if (!host || !surface) return
  const tb = host.querySelector('.ql-toolbar')
  if (!tb) return
  editTocDockResizeObserver = new ResizeObserver(() => {
    scheduleSyncEditTocDockTop()
  })
  editTocDockResizeObserver.observe(tb)
  editTocDockResizeObserver.observe(surface)
  bindEditTocVisualViewport()
  scheduleSyncEditTocDockTop()
}

function onWindowResizeEditTocDock() {
  scheduleSyncEditTocDockTop()
}

const editTocResizeAria = computed(() => {
  void localeStore.localeKey
  return t('article.editTocResizeWidth')
})

let editTocResizeMoveHandler: ((ev: MouseEvent) => void) | null = null
let editTocResizeUpHandler: (() => void) | null = null

function onEditTocResizeStart(e: MouseEvent) {
  e.preventDefault()
  const startX = e.clientX
  const startWidth = editTocWidth.value
  editTocResizing.value = true
  editTocResizeMoveHandler = (ev: MouseEvent) => {
    const next = startWidth - (ev.clientX - startX)
    editTocWidth.value = Math.min(MAX_EDIT_TOC_WIDTH, Math.max(MIN_EDIT_TOC_WIDTH, next))
  }
  editTocResizeUpHandler = () => {
    editTocResizing.value = false
    const move = editTocResizeMoveHandler
    const up = editTocResizeUpHandler
    editTocResizeMoveHandler = null
    editTocResizeUpHandler = null
    if (move) document.removeEventListener('mousemove', move)
    if (up) document.removeEventListener('mouseup', up)
    document.body.style.cursor = ''
    document.body.style.userSelect = ''
    try {
      localStorage.setItem(EDIT_TOC_WIDTH_STORAGE_KEY, String(editTocWidth.value))
    } catch {
      /* ignore */
    }
  }
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
  document.addEventListener('mousemove', editTocResizeMoveHandler)
  document.addEventListener('mouseup', editTocResizeUpHandler)
}

function teardownEditTocResize() {
  if (editTocResizeMoveHandler) {
    document.removeEventListener('mousemove', editTocResizeMoveHandler)
    editTocResizeMoveHandler = null
  }
  if (editTocResizeUpHandler) {
    document.removeEventListener('mouseup', editTocResizeUpHandler)
    editTocResizeUpHandler = null
  }
  editTocResizing.value = false
  document.body.style.cursor = ''
  document.body.style.userSelect = ''
}

const editTocHideTitle = computed(() => {
  void localeStore.localeKey
  return t('article.editTocHide')
})

const editTocShowTitle = computed(() => {
  void localeStore.localeKey
  return t('article.editTocShow')
})

const backToTopTitle = computed(() => {
  void localeStore.localeKey
  return t('article.backToTop')
})

const backToBottomTitle = computed(() => {
  void localeStore.localeKey
  return t('article.backToBottom')
})

const scrollToolbarAria = computed(() => {
  void localeStore.localeKey
  const parts = [t('article.backToTop'), t('article.backToBottom')]
  if (props.showEditToc && editTocCollapsed.value) {
    parts.push(t('article.editTocShow'))
  }
  return parts.join(' · ')
})

watch(
  () => props.showEditToc,
  (v) => {
    if (!v) editTocCollapsed.value = false
  }
)

function scheduleGenerateEditToc() {
  if (!props.showEditToc || !editor?.root) return
  if (editTocTimer) clearTimeout(editTocTimer)
  editTocTimer = setTimeout(() => {
    editTocTimer = null
    generateEditToc()
  }, 280)
}

function generateEditToc() {
  if (!props.showEditToc || !editor?.root) return
  const root = editor.root
  const headings = root.querySelectorAll('h1, h2, h3, h4, h5, h6')
  const items: EditTocItem[] = []
  const base = `fe-toc-${props.articleId ?? '0'}`
  headings.forEach((node, index) => {
    const el = node as HTMLElement
    const level = parseInt(el.tagName.charAt(1), 10)
    const text = el.textContent?.trim() || ''
    if (!text) return
    let id = el.id
    if (!id) {
      id = `${base}-${index}`
      el.id = id
    }
    items.push({ id, text, level })
  })
  editTocItems.value = items
  nextTick(() => updateEditTocActiveFromScroll())
}

function scrollToEditTocHeading(id: string) {
  const el = document.getElementById(id)
  if (!el || !editor?.root?.contains(el) || !hostEl.value) return
  editTocActiveHeadingId.value = id
  // 仅在 .tiny-fluent-editor 内 .ql-editor 滚动，把标题对齐到编辑器内容区顶部，不带动外层页面
  const scrollRoot = editor.root as HTMLElement
  const elRect = el.getBoundingClientRect()
  const rootRect = scrollRoot.getBoundingClientRect()
  const nextTop = scrollRoot.scrollTop + (elRect.top - rootRect.top)
  scrollRoot.scrollTo({ top: Math.max(0, nextTop), behavior: 'smooth' })
  el.classList.add('fe-toc-flash')
  window.setTimeout(() => el.classList.remove('fe-toc-flash'), 2000)
}

function scrollEditEditorToTop() {
  const root = editor?.root as HTMLElement | undefined
  if (!root) return
  root.scrollTo({ top: 0, behavior: 'smooth' })
}

function scrollEditEditorToBottom() {
  const root = editor?.root as HTMLElement | undefined
  if (!root) return
  const max = Math.max(0, root.scrollHeight - root.clientHeight)
  root.scrollTo({ top: max, behavior: 'smooth' })
}

/** 仅在目录树容器内滚动，避免 scrollIntoView 带动外层 */
function scrollEditTocPanelToActive(id: string) {
  const container = editTocTreeWrapRef.value
  if (!container) return
  const nodes = container.querySelectorAll('[data-edit-toc-id]')
  for (const n of nodes) {
    const el = n as HTMLElement
    if (el.dataset.editTocId !== id) continue
    const c = container.getBoundingClientRect()
    const e = el.getBoundingClientRect()
    if (e.top < c.top) {
      container.scrollTop -= c.top - e.top + 6
    } else if (e.bottom > c.bottom) {
      container.scrollTop += e.bottom - c.bottom + 6
    }
    break
  }
}

/** 根据 .ql-editor 滚动位置高亮「越过」参考线的最后一个标题（与阅读页目录逻辑一致） */
function updateEditTocActiveFromScroll() {
  if (!props.showEditToc || props.readonly || !editor?.root) return
  const scrollRoot = editor.root as HTMLElement
  const items = editTocItems.value
  if (items.length === 0) {
    editTocActiveHeadingId.value = null
    return
  }
  const rootRect = scrollRoot.getBoundingClientRect()
  const offset = Math.min(100, Math.max(48, rootRect.height * 0.08))
  const lineY = rootRect.top + offset
  let active: string | null = null
  for (const item of items) {
    const el = document.getElementById(item.id)
    if (!el || !scrollRoot.contains(el)) continue
    const top = el.getBoundingClientRect().top
    if (top <= lineY) active = item.id
  }
  if (active === null && scrollRoot.scrollTop < 32 && items[0]) {
    active = items[0].id
  }
  const prev = editTocActiveHeadingId.value
  editTocActiveHeadingId.value = active
  if (active && active !== prev && !editTocCollapsed.value) {
    nextTick(() => scrollEditTocPanelToActive(active!))
  }
}

function onEditTocEditorScroll() {
  if (editTocScrollSpyRaf) return
  editTocScrollSpyRaf = requestAnimationFrame(() => {
    editTocScrollSpyRaf = 0
    updateEditTocActiveFromScroll()
  })
}

function teardownEditTocScrollSpy() {
  const root = editor?.root as HTMLElement | undefined
  if (root && editTocScrollBound) {
    root.removeEventListener('scroll', onEditTocEditorScroll, EDIT_TOC_SCROLL_OPTS)
    editTocScrollBound = false
  }
  if (editTocScrollSpyRaf) {
    cancelAnimationFrame(editTocScrollSpyRaf)
    editTocScrollSpyRaf = 0
  }
}

function syncEditTocScrollSpy() {
  teardownEditTocScrollSpy()
  if (!props.showEditToc || props.readonly || !editor?.root) {
    editTocActiveHeadingId.value = null
    return
  }
  const root = editor.root as HTMLElement
  root.addEventListener('scroll', onEditTocEditorScroll, EDIT_TOC_SCROLL_OPTS)
  editTocScrollBound = true
  updateEditTocActiveFromScroll()
}

watch(editTocCollapsed, (collapsed) => {
  if (!collapsed) {
    nextTick(() => {
      const id = editTocActiveHeadingId.value
      if (id) scrollEditTocPanelToActive(id)
    })
  }
})

marked.setOptions({
  gfm: true,
  breaks: true,
})

function detectModelIsDeltaJson(modelValue: string | undefined) {
  if (!modelValue) return modelIsDeltaJson
  try {
    const parsed = JSON.parse(modelValue) as any
    return !!(parsed && typeof parsed === 'object' && 'ops' in parsed)
  } catch {
    return false
  }
}

async function renderMarkdownToHtml(markdown: string) {
  const rendered = await marked.parse(markdown ?? '')
  return typeof rendered === 'string' ? rendered : String(rendered ?? '')
}

function patchAiModule(aiModule: any) {
  if (!aiModule || aiModule.__markdownPatched) return

  aiModule.__markdownPatched = true
  aiModule.__markdownContent = ''

  aiModule.showAIResponse = async function(response: string) {
    if (!this.resultPopupEl) return
    if (this._charCount <= this.textNumber) {
      this.__markdownContent = response || ''
      const html = await renderMarkdownToHtml(this.__markdownContent)
      if (!this.resultPopupContentEl) return
      this.resultPopupContentEl.innerHTML = html
      this.charCount = (this.resultPopupContentEl.textContent || '').replace(/\s+/g, '').length
    } else {
      this.isBreak = true
      this.charCount = 0
    }
    this.showResultPopupEl = true
  }

  aiModule.replaceSelectText = async function() {
    if (!this.resultPopupContentEl) return
    const range = this.quill.getSelection(true)
    if (range && range.length > 0) {
      this.quill.deleteText(range.index, range.length)
      const html = await renderMarkdownToHtml(this.__markdownContent || this.resultPopupContentEl.textContent || '')
      this.quill.clipboard.dangerouslyPasteHTML(range.index, html)
    }
    this.closeAIPanel()
  }

  aiModule.insertAIResponse = async function() {
    if (!this.resultPopupContentEl) return
    const range = this.quill.getSelection(true)
    if (range) {
      const html = await renderMarkdownToHtml(this.__markdownContent || this.resultPopupContentEl.textContent || '')
      this.quill.clipboard.dangerouslyPasteHTML(range.index + range.length, html)
    }
    this.closeAIPanel()
  }
}

function isImageFile(filename: string) {
  const ext = filename.toLowerCase().split('.').pop() || ''
  return ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg'].includes(ext)
}

function isImageUrl(text: string) {
  const value = text.trim()
  if (!value) return false

  try {
    const url = new URL(value)
    const pathname = url.pathname.toLowerCase()
    return /\.(jpg|jpeg|png|gif|bmp|webp|svg)$/.test(pathname)
  } catch {
    return false
  }
}

function getUrlFilename(text: string) {
  const value = text.trim()
  if (!value) return ''

  try {
    const url = new URL(value)
    const pathname = decodeURIComponent(url.pathname || '')
    const segments = pathname.split('/').filter(Boolean)
    return segments[segments.length - 1] || ''
  } catch {
    return ''
  }
}

function isSingleHttpUrl(text: string) {
  const value = text.trim()
  if (!value || /\s/.test(value)) return false

  try {
    const url = new URL(value)
    return /^https?:$/.test(url.protocol)
  } catch {
    return false
  }
}

/** 判断粘贴内容是否像 Markdown 源码（从 .md 或编辑器复制的正文） */
function looksLikeMarkdown(text: string): boolean {
  const raw = text.replace(/^\uFEFF/, '')
  const t = raw.trim()
  if (!t) return false
  // 整段是单个 URL 的交给后续链接/附件逻辑
  if (!/\s/.test(t) && isSingleHttpUrl(t)) return false

  if (/^#{1,6}\s/m.test(raw)) return true
  if (/```[\s\S]*?```/.test(raw)) return true
  if (/^>\s/m.test(raw)) return true
  if (/^\s*[-*+]\s/m.test(raw) || /^\s*\d+\.\s/m.test(raw)) return true
  if (/\[[^\]]+\]\([^)]+\)/.test(raw)) return true
  if (/\*\*[^*\n]+\*\*|__[^_\n]+__/.test(raw)) return true
  if (/^(\s*\|[^\n]+\|\s*\r?\n\|\s*[-:| ]+\|)/m.test(raw)) return true
  if (/\n-{3,}\s*\n|\n\*{3,}\s*\n/.test(raw)) return true

  if (t.length < 24) return false
  let score = 0
  if (/^#{1,6}\s/m.test(raw)) score += 2
  if (/^\s*[-*+]\s/m.test(raw) || /^\s*\d+\.\s/m.test(raw)) score += 1
  if (/\[[^\]]+\]\([^)]+\)/.test(raw)) score += 1
  if (/\*\*[^*]+\*\*/.test(raw)) score += 1
  return score >= 2
}

function stopClipboardEvent(event: ClipboardEvent) {
  event.preventDefault()
  event.stopPropagation()
  event.stopImmediatePropagation?.()
}

/** 光标是否在代码块或行内 code 内：自定义 Markdown/链接粘贴会破坏结构，需走 Quill 默认纯文本 */
function isSelectionInCodeOrCodeBlock(quill: any): boolean {
  const range = quill.getSelection?.(true)
  if (!range || typeof range.index !== 'number') return false
  const fmt = quill.getFormat?.(range.index) ?? {}
  if (fmt['code-block']) return true
  if (fmt.code) return true
  return false
}

/** 清空编辑器并将整篇内容替换为 Markdown 渲染后的 HTML（用户确认「立即转换」后调用） */
async function replaceEditorWithMarkdownFromString(markdown: string) {
  if (!editor) return
  const quill = editor as any
  const normalized = markdown.replace(/^\uFEFF/, '')
  const html = await renderMarkdownToHtml(normalized)
  quill.setContents([], 'user')
  quill.clipboard?.dangerouslyPasteHTML?.(0, html)
  const len = quill.getLength?.() ?? 0
  const end = Math.max(0, len - 1)
  quill.setSelection?.(end, 0, 'silent')
}

let markdownPasteMsgVm: { close?: (type?: string) => void } | null = null

function openMarkdownPasteConvertPrompt(markdown: string) {
  const md = markdown.replace(/^\uFEFF/, '')
  void Modal.message({
    status: 'info',
    duration: 45000,
    messageClosable: true,
    top: 16,
    message: ((render: typeof h) =>
      render(
        'div',
        { class: 'fluent-editor-md-paste-msg' },
        [
          render('span', { class: 'fluent-editor-md-paste-msg__text' }, t('article.pasteMarkdownConvertMessage')),
          render(
            TinyButton,
            {
              type: 'primary',
              size: 'small',
              onClick: async (e: Event) => {
                e?.stopPropagation?.()
                await replaceEditorWithMarkdownFromString(md)
                const vm = markdownPasteMsgVm
                markdownPasteMsgVm = null
                vm?.close?.('close')
              },
            },
            { default: () => t('article.pasteMarkdownConvertNow') }
          ),
        ]
      )) as any,
    events: {
      show: function (this: { close?: (type?: string) => void }) {
        markdownPasteMsgVm = this
      },
      hide: function () {
        markdownPasteMsgVm = null
      },
    },
  })
}

/** 先走默认粘贴，再在下一帧弹出是否整篇转换的提示 */
function scheduleMarkdownPastePrompt(plainRaw: string) {
  void nextTick(() => {
    queueMicrotask(() => {
      if (!editor || props.readonly) return
      if (!plainRaw || !looksLikeMarkdown(plainRaw)) return
      openMarkdownPasteConvertPrompt(plainRaw)
    })
  })
}

function escapeHtml(value: string) {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function createFileLinkHtml(fileUrl: string, fileName: string) {
  const safeUrl = escapeHtml(fileUrl)
  const safeName = escapeHtml(fileName)
  return `<a class="ql-file-item icon-file" href="${safeUrl}" target="_blank" rel="noopener noreferrer" data-title="${safeName}">${safeName}</a>`
}

function createPlainLinkHtml(linkUrl: string) {
  const safeUrl = escapeHtml(linkUrl)
  return `<a href="${safeUrl}" target="_blank" rel="noopener noreferrer">${safeUrl}</a>`
}

function createVideoHtml(videoUrl: string) {
  const safeUrl = escapeHtml(videoUrl)
  return `<p><video class="my-video" controls preload="metadata" src="${safeUrl}"></video></p>`
}

function isVideoFile(filename: string) {
  const ext = filename.toLowerCase().split('.').pop() || ''
  return ['mp4', 'webm', 'ogg', 'mov', 'avi', 'wmv', 'flv', 'mkv'].includes(ext)
}

function isGenericFileType(filename: string) {
  const ext = filename.toLowerCase().split('.').pop() || ''
  return [
    'zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'xz',
    'txt', 'md', 'csv',
    'apk', 'ipa', 'exe', 'dmg', 'pkg', 'msi',
    'psd', 'ai', 'sketch', 'fig',
    'json', 'xml', 'yml', 'yaml',
  ].includes(ext)
}

function getPreviewFileType(filename: string) {
  const ext = filename.toLowerCase().split('.').pop() || ''
  if (['ppt', 'pptx'].includes(ext)) return 'pptx'
  if (['xls', 'xlsx'].includes(ext)) return 'xlsx'
  if (['doc', 'docx'].includes(ext)) return 'docx'
  if (ext === 'pdf') return 'pdf'
  if (isImageFile(filename)) return 'image'
  if (isVideoFile(filename)) return 'video'
  return ext
}

function isOfficePreviewType(fileType: string) {
  return ['pptx', 'xlsx', 'docx', 'pdf'].includes(fileType)
}

function isPreviewableFileType(fileType: string) {
  return ['pptx', 'xlsx', 'docx', 'pdf', 'image', 'video'].includes(fileType)
}

function closeAttachmentPreview() {
  previewVisible.value = false
}

function openAttachmentPreview(fileUrl: string, fileName: string) {
  if (openOfficeOnlinePreview(fileUrl, fileName)) return
  previewFileUrl.value = fileUrl
  previewFileName.value = fileName
  previewFileType.value = getPreviewFileType(fileName)
  previewVisible.value = true
}

function handleWindowKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape' && previewVisible.value) {
    event.preventDefault()
    closeAttachmentPreview()
  }
}

function handleEditorClick(event: Event) {
  const target = event.target as HTMLElement | null
  const fileLink = target?.closest?.('a.ql-file-item') as HTMLAnchorElement | null
  if (!fileLink) return

  const fileUrl = fileLink.href
  const fileName = fileLink.dataset.title || fileLink.textContent?.trim() || '附件'
  if (!fileUrl) return

  const fileType = getPreviewFileType(fileName)

  if (!isPreviewableFileType(fileType)) {
    const link = document.createElement('a')
    link.href = fileUrl
    link.download = fileName
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    event.preventDefault()
    event.stopPropagation()
    return
  }

  event.preventDefault()
  event.stopPropagation()
  ;(event as MouseEvent).stopImmediatePropagation?.()
  openAttachmentPreview(fileUrl, fileName)
}

function handleEditorPaste(event: ClipboardEvent) {
  if (!editor || props.readonly) return

  const quill = editor as any
  if (isSelectionInCodeOrCodeBlock(quill)) {
    return
  }

  const clipboardData = event.clipboardData
  if (!clipboardData) return

  const hasFiles = !!clipboardData.files?.length
  if (hasFiles) return

  const plainRaw = clipboardData.getData('text/plain') ?? ''

  // Markdown 可能：先默认粘贴，再异步提示是否整篇转为富文本（避免误判直接转换导致错乱）
  if (plainRaw && looksLikeMarkdown(plainRaw)) {
    const trimmed = plainRaw.trim()
    if (!isSingleHttpUrl(trimmed)) {
      scheduleMarkdownPastePrompt(plainRaw)
      return
    }
  }

  const pastedText = plainRaw.trim()
  if (!pastedText || !isSingleHttpUrl(pastedText)) {
    return
  }

  const range = quill.getSelection?.(true)
  const insertIndex = typeof range?.index === 'number' ? range.index : quill.getLength?.() ?? 0
  const filename = getUrlFilename(pastedText) || pastedText
  const fileType = getPreviewFileType(filename)
  const stopHandledPaste = () => stopClipboardEvent(event)

  if (fileType === 'image') {
    stopHandledPaste()
    quill.insertEmbed?.(insertIndex, 'image', pastedText, 'user')
    quill.setSelection?.(insertIndex + 1, 0, 'silent')
    return
  }

  if (fileType === 'video') {
    stopHandledPaste()
    quill.clipboard?.dangerouslyPasteHTML?.(insertIndex, createVideoHtml(pastedText))
    quill.setSelection?.(insertIndex + 1, 0, 'silent')
    return
  }

  if (isOfficePreviewType(fileType) || isGenericFileType(filename)) {
    stopHandledPaste()
    quill.clipboard?.dangerouslyPasteHTML?.(insertIndex, createFileLinkHtml(pastedText, filename))
    quill.setSelection?.(insertIndex + filename.length, 0, 'silent')
    return
  }

  stopHandledPaste()
  quill.clipboard?.dangerouslyPasteHTML?.(insertIndex, createPlainLinkHtml(pastedText))
  quill.setSelection?.(insertIndex + pastedText.length, 0, 'silent')
}

const fluentEditorLang = computed(() => {
  // 基础内置 i18n 只有 zh-CN / en-US，其他语言回退即可。
  const cur = localeStore.currentLocale
  if (cur === 'zh') return 'zh-CN'
  return 'en-US'
})


function safeSetContentsFromModel(modelValue: string | undefined) {
  if (!editor) return
  const safeValue = modelValue ?? ''

  modelIsDeltaJson = detectModelIsDeltaJson(modelValue)

  if (!safeValue) {
    editor.setContents([])
    return
  }

  // 优先当成 delta JSON
  try {
    const parsed = JSON.parse(safeValue) as any
    if (parsed && typeof parsed === 'object' && 'ops' in parsed) {
      editor.setContents(parsed as any)
      return
    }
  } catch {
    // 不是 JSON，按 HTML 渲染
  }

  editor.clipboard.dangerouslyPasteHTML(safeValue)
}

onMounted(() => {
  if (!hostEl.value) return
  window.addEventListener('keydown', handleWindowKeydown)
  // 注册 Quill 模块
  FluentEditor.register(
    { 'modules/toolbar-tip': generateToolbarTip(QuillToolbarTip) },
    true
  );
  FluentEditor.register({ 'modules/table-up': generateTableUp(TableUp) }, true);
  FluentEditor.register('modules/markdownShortcuts', MarkdownShortcuts);
  FluentEditor.register(
    'modules/collaborative-editing',
    CollaborationModule,
    true
  );
  let modules = {
    'shortcut-key': true,
      toolbar: {
        container: [...FULL_TOOLBAR, ['mind-map', 'flow-chart']],
        handlers: {
          formula(this: any) {
            const mathlive = this.quill.getModule('mathlive') as MathliveModule;
            mathlive.createDialog('e=mc^2');
          },
        },
      },
      
      file: true,
      'uploader': {
        mimetypes: [
          'image/*',
          'video/*',
          '.pptx',
          '.xlsx',
          '.docx',
          '.pdf',
          '.zip',
          'application/zip',
          'application/x-zip-compressed',
          'application/vnd.openxmlformats-officedocument.presentationml.presentation',
          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
          'application/pdf',
        ],
        maxSize: 500 * 1024 * 1024, // 500MB
        async handler(range: any, files: File[]) {
          const results: (string | false)[] = []
          uploadPendingCount.value += files.length
          
          // 处理每个文件
          await Promise.all(files.map(async (file, index) => {
            try {
              // 上传文件，携带当前文章ID
              const articleId = props.articleId
              const response = await fileApi.uploadFile(file, articleId)
              let fileUrl = response.file_url
              // 构建完整的文件 URL
              if (!fileUrl.startsWith('http://') && !fileUrl.startsWith('https://')) {
                // 如果是相对路径，拼接完整的 URL
                const baseUrl = window.location.origin
                fileUrl = fileUrl.startsWith('/') ? `${baseUrl}${fileUrl}` : `${baseUrl}/${fileUrl}`
              }
              results[index] = fileUrl
            } catch (error) {
              console.error('文件上传失败:', error)
              results[index] = false
            } finally {
              uploadPendingCount.value = Math.max(0, uploadPendingCount.value - 1)
            }
          }))
          
          return results
        },
        success(file: File, _range: any) {
          console.log('文件上传成功:', file)
        },
        fail(file: File, _range: any) {
          console.error('文件上传失败:', file)
        },
      },
      markdownShortcuts: false,
      syntax: {
        hljs,
        languages: [
          { key: 'go', label: 'Golang' },
        ],
      },
      counter: false,
      mathlive: true,
      emoji: {
        emojiData: data as EmojiMartData,
        EmojiPicker: Picker,
        emojiPickerPosition: computePosition,
      },
      i18n: {
        lang: fluentEditorLang.value,
      },
      'toolbar-tip': {
        defaultTooltipOptions: {
          tipHoverable: true,
        },
      },
      'table-up': {
        customSelect: defaultCustomSelect,
        modules: [
            { module: TableSelection },
            { module: TableResizeLine },
            { module: TableResizeScale },
            // { module: TableMenuContextmenu },
            { module: TableResizeBox },
            { module: TableMenuSelect },
          ],
      },
      'mind-map': {
        deps: {
          SimpleMindMap,
          Themes,
          Drag,
          Export,
          nodeIconList,
        },
      },
      'flow-chart': {
        deps: {
          LogicFlow,
          DndPanel,
          SelectionSelect,
          Snapshot,
        },
      },
      // mention: {
      //   containerClass: 'ql-mention-list-container__custom-list',
      //   itemKey: 'cn',
      //   searchKey,
      //   async search(term: string) {
      //     const keyword = normalizeMentionKeyword(term)
      //     if (!keyword) return []

      //     const now = Date.now()
      //     const cache = mentionSearchCache.get(keyword)
      //     if (cache && cache.expiresAt > now) {
      //       return cache.items
      //     }

      //     // 避免并发请求造成“旧结果覆盖新结果”
      //     const seq = ++mentionSearchSeq.value

      //     try {
      //       const res = await userManagementApi.getUsers({
      //         page: 1,
      //         page_size: mentionSearchPageSize,
      //         // mention 一般只展示正常用户；如果你想改成全量，可把 status 这里移除或改成从外部传参
      //         status: 1,
      //         keyword,
      //       })

      //       if (seq !== mentionSearchSeq.value) return []

      //       const items = res.items.map(mapUserToMentionItem)
      //       mentionSearchCache.set(keyword, { expiresAt: now + MENTION_SEARCH_CACHE_TTL_MS, items })
      //       return items
      //     } catch (e) {
      //       // 接口失败时返回空，避免 mention 卡死或抛错影响编辑器输入
      //       console.error('[FluentEditorV4] mention.search error', e)
      //       return []
      //     }
      //   },
      //   renderMentionItem(item: any) {
      //     return `
      //       <div class="item-avatar">
      //         <span class="item-email">${item.email}</span>
      //       </div>
      //     `;
      //   },
      // },
    }
  editor = new FluentEditor(hostEl.value, {
    theme: 'snow',
    readOnly: props.readonly,
    placeholder: props.placeholder,
    modules: modules
  } as any)
  quillRef.value = editor
  editor.root?.addEventListener('click', handleEditorClick, true)
  editor.root?.addEventListener('paste', handleEditorPaste, true)
  patchAiModule(editor.getModule('ai'))
  if (props.readonly) {
    editor.enable(false)
  }
  safeSetContentsFromModel(props.modelValue)
  nextTick(() => {
    codeBlockCopyLayerEl.value?.addEventListener('click', handleCodeBlockCopyClickCapture, true)
    scheduleCodeBlockCopyMount()
    bindCodeBlockCopyLayoutSync()
    syncEditTocScrollSpy()
    bindEditTocDockTopObserver()
    window.addEventListener('resize', onWindowResizeEditTocDock)
    if (props.showEditToc) {
      scheduleGenerateEditToc()
      setTimeout(() => {
        scheduleGenerateEditToc()
        syncEditTocScrollSpy()
      }, 400)
    }
  })

  editor.on('text-change', () => {
    if (!editor) return
    if (isSyncingFromModel) return
    isModelUpdateFromEditor = true
    if (modelIsDeltaJson) {
      const contents = editor.getContents()
      emit('update:modelValue', JSON.stringify(contents))
    } else {
      // 输出为 HTML 字符串（兼容 CommentDrawer 等按 innerHTML 计算文本）
      emit('update:modelValue', editor.root?.innerHTML ?? '')
    }
    scheduleGenerateEditToc()
    // 等待父组件把值回灌，再解除同步标记
    nextTick(() => {
      isModelUpdateFromEditor = false
      scheduleGenerateEditToc()
      scheduleCodeBlockCopyMount()
    })
  })
})

// 当切换可编辑性时，不重建编辑器（重建会触发更多副作用）
watch(
  () => props.readonly,
  (readonly) => {
    if (!editor) return
    editor.enable(!readonly)
  }
)

watch(
  () => props.modelValue,
  (val) => {
    if (!editor) return
    if (isModelUpdateFromEditor) return
    isSyncingFromModel = true
    try {
      safeSetContentsFromModel(val)
    } finally {
      // 下一帧再放开，避免触发 text-change 回写造成抖动
      nextTick(() => {
        isSyncingFromModel = false
        if (props.showEditToc) {
          scheduleGenerateEditToc()
        }
        scheduleCodeBlockCopyMount()
      })
    }
  }
)

watch(
  () => props.showEditToc,
  (on) => {
    if (on) {
      nextTick(() => {
        bindEditTocDockTopObserver()
        scheduleGenerateEditToc()
        setTimeout(() => scheduleGenerateEditToc(), 300)
      })
    } else {
      teardownEditTocScrollSpy()
      teardownEditTocDockTopObserver()
      editTocItems.value = []
      editTocActiveHeadingId.value = null
    }
  }
)

watch(editTocCollapsed, () => {
  nextTick(() => {
    // 目录从折叠到展开时 aside 重新挂载，需重绑观察并在布局稳定后再量一次
    if (!editTocCollapsed.value && props.showEditToc) {
      bindEditTocDockTopObserver()
    }
    scheduleSyncEditTocDockTop()
    setTimeout(() => scheduleSyncEditTocDockTop(), 80)
  })
})

watch(
  () => [props.showEditToc, props.readonly] as const,
  () => {
    nextTick(() => syncEditTocScrollSpy())
  }
)

// 监听语言切换：v4 的 i18n module 支持 changeLanguage
watch(
  () => localeStore.localeKey,
  () => {
    if (!editor) return
    const i18nModule = editor.getModule('i18n') as any
    if (i18nModule && typeof i18nModule.changeLanguage === 'function') {
      i18nModule.changeLanguage({ lang: fluentEditorLang.value }, true)
    }
    nextTick(() => {
      refreshCodeBlockCopyButtonLabels()
    })
  }
)

onBeforeUnmount(() => {
  if (codeBlockCopyMountTimer) {
    clearTimeout(codeBlockCopyMountTimer)
    codeBlockCopyMountTimer = null
  }
  teardownEditTocResize()
  teardownEditTocScrollSpy()
  teardownEditTocDockTopObserver()
  window.removeEventListener('resize', onWindowResizeEditTocDock)
  try {
    if (editTocTimer) clearTimeout(editTocTimer)
    editTocTimer = null
    window.removeEventListener('keydown', handleWindowKeydown)
    codeBlockCopyLayerEl.value?.removeEventListener?.('click', handleCodeBlockCopyClickCapture, true)
    teardownCodeBlockCopyLayoutSync()
    if (codeBlockCopyLayerEl.value) codeBlockCopyLayerEl.value.innerHTML = ''
    editor?.root?.removeEventListener?.('click', handleEditorClick, true)
    editor?.root?.removeEventListener?.('paste', handleEditorPaste, true)
    editor?.off?.('text-change')
  } finally {
    editor = null
    quillRef.value = null
  }
})

defineExpose({
  // 让外部可以通过 `ref.value.quill.enable(...)` 获取实例
  get quill() {
    return quillRef.value
  },
  focus: () => editor?.focus?.()
})
</script>

<style scoped lang="less">

:deep(.ql-ai-dialog) {
  width: 100% !important;
  overflow: auto;
}

:deep(.ql-ai-dialog .ql-ai-wrapper) {
  width: calc(100% - var(--fe-edit-toc-width, 0px) - 30px) !important;
}

/* 中文字体对 italic 支持较弱，补一个轻微倾斜增强可见性 */
:deep(.ql-editor em),
:deep(.ql-editor i) {
  display: inline-block;
  font-style: italic;
  transform: skewX(-10deg);
  transform-origin: center;
}

:deep(.ql-editor em > *),
:deep(.ql-editor i > *) {
  transform: skewX(10deg);
}

/* 段落外边距（覆盖 fluent-editor 默认 margin: 0） */
:deep(.ql-editor p) {
  margin: 16px 0;
}

/* 编辑态：主区域 + 右侧目录 */
.fluent-editor-v4-layout {
  display: flex;
  flex-direction: row;
  align-items: stretch;
  width: 100%;
  min-height: 0;
  flex: 1;
  overflow: hidden;
}

/* 折叠时右下角浮动条 */
.edit-scroll-float-reveal-enter-active,
.edit-scroll-float-reveal-leave-active {
  transition:
    opacity 0.16s cubic-bezier(0.25, 0.46, 0.45, 0.94),
    transform 0.2s cubic-bezier(0.25, 0.46, 0.45, 0.94);
}

.edit-scroll-float-reveal-enter-from,
.edit-scroll-float-reveal-leave-to {
  opacity: 0;
  transform: translateY(6px) scale(0.985);
}

.edit-scroll-float-reveal-enter-to,
.edit-scroll-float-reveal-leave-from {
  opacity: 1;
  transform: translateY(0) scale(1);
}

.fluent-editor-v4-main {
  position: relative;
  flex: 1;
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 工具栏+正文+目录叠层；目录 position:absolute 相对此盒右侧 */
.fluent-editor-v4-editor-surface {
  position: relative;
  flex: 1;
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  .tiny-fluent-editor {
    flex: 1;
    min-height: 0;
    min-width: 0;
    width: 100%;
    box-sizing: border-box;
  }
}

/* 编辑态：无目录或目录折叠时，在编辑区右下角浮动 */
.fluent-editor-v4-scroll-actions {
  position: absolute;
  right: 10px;
  bottom: 14px;
  z-index: 6;
  display: flex;
  flex-direction: column;
  gap: 8px;
  pointer-events: none;

  > * {
    pointer-events: auto;
  }
}

.fluent-editor-v4-scroll-actions__btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  padding: 0;
  margin: 0;
  border: 1px solid rgba(124, 58, 237, 0.22);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.94);
  color: #5b21b6;
  box-shadow:
    0 4px 14px rgba(124, 58, 237, 0.12),
    0 1px 4px rgba(15, 23, 42, 0.06);
  cursor: pointer;
  transition:
    background 0.18s ease,
    color 0.18s ease,
    border-color 0.18s ease,
    transform 0.18s ease;

  &:hover {
    background: rgba(245, 243, 255, 0.98);
    border-color: rgba(124, 58, 237, 0.38);
    color: #4c1d95;
  }

  &:active {
    transform: scale(0.96);
  }

  &:focus-visible {
    outline: 2px solid rgba(124, 58, 237, 0.45);
    outline-offset: 2px;
  }
}

.fluent-editor-v4-scroll-actions__icon {
  width: 20px;
  height: 20px;
  display: block;
}

.fluent-editor-v4-scroll-actions__btn--toc-expand {
  margin-top: 2px;
  padding-top: 1px;
  border-color: rgba(124, 58, 237, 0.28);
  background: linear-gradient(145deg, rgba(245, 243, 255, 0.98), rgba(255, 255, 255, 0.94));

  &:hover {
    background: linear-gradient(145deg, rgba(237, 233, 254, 0.99), rgba(255, 255, 255, 0.98));
    border-color: rgba(124, 58, 237, 0.42);
  }
}

.fluent-editor-v4-scroll-actions__toc-expand-icon {
  width: 18px;
  height: 18px;
  display: block;
}

.editor-container--with-edit-toc {
  :deep(.ql-editor h1),
  :deep(.ql-editor h2),
  :deep(.ql-editor h3),
  :deep(.ql-editor h4),
  :deep(.ql-editor h5),
  :deep(.ql-editor h6) {
    scroll-margin-top: 12px;
  }

  .fluent-editor-v4-toc {
    position: absolute;
    /* 低于 sticky 工具栏 (父页 z-index:5)，避免测量误差时挡住工具栏点击 */
    z-index: 4;
    /* 高度 = 编辑区容器高度 − 工具栏高度（与 --fe-edit-toc-top 一致） */
    top: var(--fe-edit-toc-top, 48px);
    right: 10px;
    bottom: auto;
    height: calc(100% - var(--fe-edit-toc-top, 48px));
    max-height: calc(100% - var(--fe-edit-toc-top, 48px));
    display: flex;
    flex-direction: row;
    align-items: stretch;
    min-width: 0;
    min-height: 0;
    overflow: hidden;
    box-sizing: border-box;
    border-left: 1px solid rgba(139, 92, 246, 0.16);
    background: linear-gradient(165deg, rgba(245, 243, 255, 0.92), rgba(255, 255, 255, 0.98));
    border-radius: 0 0 6px 0;
    box-shadow: -6px 0 18px rgba(91, 33, 182, 0.06);
  }

  /* 正文区全宽；目录叠在右侧，滚动内容在 .ql-editor 右侧留白 */
  .fluent-editor-v4-editor-surface--toc-open :deep(.ql-container) {
    flex: 1 1 auto !important;
    align-self: stretch;
    width: 100% !important;
    max-width: none !important;
    box-sizing: border-box;
    min-width: 0;
  }

  .fluent-editor-v4-editor-surface--toc-open :deep(.ql-editor) {
    padding-right: calc(var(--fe-edit-toc-width, 260px) + 10px) !important;
    box-sizing: border-box;
    transition: padding-right 0.2s ease;
  }

  .fluent-editor-v4-toc__resize-handle {
    flex: 0 0 6px;
    width: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: col-resize;
    align-self: stretch;
    background: transparent;
    position: relative;
    z-index: 2;
    touch-action: none;
    user-select: none;
  }

  .fluent-editor-v4-toc__resize-handle-icon {
    flex-shrink: 0;
    width: 10px;
    height: 16px;
    pointer-events: none;
    color: rgba(91, 33, 182, 0.45);
    transition: color 0.15s ease;
  }

  .fluent-editor-v4-toc__resize-handle:hover .fluent-editor-v4-toc__resize-handle-icon,
  .fluent-editor-v4-toc__resize-handle.is-dragging .fluent-editor-v4-toc__resize-handle-icon {
    color: rgba(91, 33, 182, 0.75);
  }

  .fluent-editor-v4-toc__inner {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    min-height: 0;
    overflow: hidden;
  }

  .fluent-editor-v4-toc__header {
    flex-shrink: 0;
    padding: 10px 12px;
    border-bottom: 1px solid rgba(139, 92, 246, 0.1);
  }

  .fluent-editor-v4-toc__title {
    margin: 0;
    font-size: 14px;
    font-weight: 600;
    color: #4c1d95;
    letter-spacing: 0.02em;
    line-height: 1.35;
  }

  .fluent-editor-v4-toc__toggle {
    flex-shrink: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 34px;
    height: 34px;
    padding: 0;
    margin: 0;
    border: none;
    border-radius: 10px;
    box-sizing: border-box;
    background: rgba(124, 58, 237, 0.08);
    color: #5b21b6;
    cursor: pointer;
    transition:
      background 0.18s ease,
      color 0.18s ease,
      transform 0.18s ease;

    &:hover {
      background: rgba(124, 58, 237, 0.16);
      color: #4c1d95;
    }

    &:active {
      transform: scale(0.96);
    }

    &:focus-visible {
      outline: 2px solid rgba(124, 58, 237, 0.45);
      outline-offset: 2px;
    }
  }

  .fluent-editor-v4-toc__toggle-icon {
    width: 18px;
    height: 18px;
    display: block;
  }

  /* 紧挨在「回到底部」右侧，不拉伸 */
  .fluent-editor-v4-toc__toggle--footer {
    flex: 0 0 auto;
    align-self: center;
  }

  .fluent-editor-v4-toc__footer {
    flex-shrink: 0;
    display: flex;
    flex-direction: row;
    flex-wrap: nowrap;
    align-items: center;
    justify-content: stretch;
    gap: 6px;
    padding: 8px 10px 10px;
    border-top: 1px solid rgba(139, 92, 246, 0.1);
    background: linear-gradient(180deg, rgba(252, 251, 255, 0.98), rgba(255, 255, 255, 0.99));
  }

  .fluent-editor-v4-toc__scroll-btn {
    flex: 1;
    min-width: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    padding: 6px 8px;
    margin: 0;
    border: 1px solid rgba(124, 58, 237, 0.18);
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.85);
    color: #5b21b6;
    font-size: 14px;
    font-weight: 600;
    line-height: 1.2;
    cursor: pointer;
    transition:
      background 0.18s ease,
      border-color 0.18s ease,
      color 0.18s ease,
      transform 0.18s ease;

    &:hover {
      background: rgba(124, 58, 237, 0.1);
      border-color: rgba(124, 58, 237, 0.32);
      color: #4c1d95;
    }

    &:active {
      transform: scale(0.98);
    }

    &:focus-visible {
      outline: 2px solid rgba(124, 58, 237, 0.45);
      outline-offset: 2px;
    }
  }

  .fluent-editor-v4-toc__scroll-icon {
    flex-shrink: 0;
    width: 14px;
    height: 14px;
    display: block;
  }

  .fluent-editor-v4-toc__scroll-text {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .fluent-editor-v4-toc__body {
    flex: 1;
    min-height: 0;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  .fluent-editor-v4-toc__empty {
    margin: 0;
    padding: 16px 12px;
    font-size: 14px;
    color: #94a3b8;
    line-height: 1.5;
  }

  .fluent-editor-v4-toc__tree-wrap {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    overflow-x: hidden;
    padding: 4px 0 8px;
    /* 隐藏滚动条，仍可滚动 */
    scrollbar-width: none;
    -ms-overflow-style: none;

    &::-webkit-scrollbar {
      width: 0;
      height: 0;
      display: none;
    }

    :deep(.tiny-tree) {
      background: transparent;
      border: none;
    }

    :deep(.tiny-tree-node) {
      padding: 2px 0;
    }

    :deep(.tiny-tree-node__content) {
      height: auto;
      min-height: 26px;
      padding: 2px 8px 2px 0;
      align-items: center;
      justify-content: flex-start;
      text-align: left;
      border-radius: 0 8px 8px 0;
      background: transparent !important;
      transition: color 0.15s ease;
    }

    :deep(.tiny-tree-node__content:hover),
    :deep(.tiny-tree-node__content:focus) {
      background: transparent !important;
      box-shadow: none;
    }

    :deep(.tiny-tree-node__label) {
      flex: 1;
      min-width: 0;
      text-align: left;
      font-size: 14px;
      line-height: 1.35;
      color: #475569;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    :deep(.tiny-tree-node__content:hover .tiny-tree-node__label) {
      color: #5b21b6;
    }
  }

  /* 覆盖 Tiny Tree 节点默认 hover 灰底 */
  .fluent-editor-v4-toc__tree-wrap :deep(.tiny-tree-node__content.is-hover),
  .fluent-editor-v4-toc__tree-wrap :deep(.tiny-tree-node__content.is-drop-inner) {
    background: transparent !important;
  }

  .fluent-editor-v4-toc__node-label {
    display: block;
    width: 100%;
    min-width: 0;
    font-size: 14px;
    line-height: 1.35;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    cursor: pointer;
    border-radius: 0 8px 8px 0;
    transition:
      color 0.18s ease,
      font-weight 0.15s ease;

    &.is-edit-toc-active {
      color: #7c3aed;
      font-weight: 600;
      background: rgba(139, 92, 246, 0.1);
    }
  }
}

@media (max-width: 768px) {
  .editor-container--with-edit-toc .fluent-editor-v4-toc {
    position: relative !important;
    top: auto !important;
    right: auto !important;
    bottom: auto !important;
    height: auto !important;
    max-height: 200px !important;
    z-index: auto;
    width: 100% !important;
    border-left: none;
    border-top: 1px solid rgba(139, 92, 246, 0.16);
    border-radius: 0 0 6px 6px;
    box-shadow: none;
  }

  .editor-container--with-edit-toc .fluent-editor-v4-editor-surface--toc-open :deep(.ql-editor) {
    padding-right: 0 !important;
  }

  .editor-container--with-edit-toc .fluent-editor-v4-toc__resize-handle {
    display: none;
  }
}

:deep(.ql-editor .fe-toc-flash) {
  animation: fe-toc-flash 1.8s ease;
}

@keyframes fe-toc-flash {
  0%,
  40% {
    background-color: rgba(124, 58, 237, 0.14);
    box-shadow: 0 0 0 2px rgba(124, 58, 237, 0.2);
  }
  100% {
    background-color: transparent;
    box-shadow: none;
  }
}

.editor-container {
  border-radius: 4px;
  // 全屏/浮层下 mention 下拉可能会超出编辑器自身尺寸；
  // 这里改为 visible，避免被裁剪后“看起来不渲染”
  overflow: visible;
  position: relative;

  &:not(.editor-preview) {
    display: flex;
    flex-direction: column;
    min-height: 0;
  }

  .editor-upload-overlay {
    position: absolute;
    inset: 0;
    z-index: 20;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(2px);
    pointer-events: all;
  }

  .editor-upload-overlay__card {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 12px 18px;
    border-radius: 999px;
    background: rgba(91, 33, 182, 0.94);
    color: #fff;
    box-shadow: 0 12px 28px rgba(91, 33, 182, 0.24);
  }

  .editor-upload-overlay__spinner {
    width: 16px;
    height: 16px;
    border: 2px solid rgba(255, 255, 255, 0.35);
    border-top-color: #fff;
    border-radius: 50%;
    animation: fe-upload-spin 0.8s linear infinite;
    flex-shrink: 0;
  }

  .editor-upload-overlay__text {
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.02em;
    white-space: nowrap;
  }
  
  // 预览模式：隐藏边框和工具栏
  &.editor-preview {
    /* 勿用 overflow:hidden：会裁切任务列表 .ql-ui 负 margin 区域，复选框/选择框看不见 */
    overflow: visible;
    border: none !important;
    border-radius: 0;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 !important;
    
    // 隐藏工具栏 - 使用多种选择器确保覆盖
    :deep(.ql-toolbar),
    :deep(.ql-toolbar.ql-snow),
    :deep([class*="toolbar"]),
    :deep([class*="Toolbar"]) {
      display: none !important;
      visibility: hidden !important;
      height: 0 !important;
      min-height: 0 !important;
      padding: 0 !important;
      margin: 0 !important;
      border: none !important;
      overflow: hidden !important;
    }
    
    // 隐藏编辑器边框 - 覆盖所有可能的边框样式
    :deep(.ql-container),
    :deep(.ql-container.ql-snow),
    :deep([class*="container"]),
    :deep([class*="Container"]) {
      border: none !important;
      border-top: none !important;
      border-bottom: none !important;
      border-left: none !important;
      border-right: none !important;
      box-shadow: none !important;
      outline: none !important;
    }
    
    // 隐藏整个编辑器的边框容器
    :deep(.tiny-fluent-editor),
    :deep(.tiny-fluent-editor > div),
    :deep(.tiny-fluent-editor > .ql-container),
    :deep([class*="fluent-editor"]),
    :deep([class*="FluentEditor"]) {
      border: none !important;
      box-shadow: none !important;
      outline: none !important;
    }
    
    // 确保编辑器内容区域无边框
    :deep(.ql-editor),
    :deep([class*="editor"]) {
      padding: 0 !important;
      border: none !important;
      outline: none !important;
    }
    
    // 隐藏 Quill 编辑器的所有边框相关元素
    :deep(.ql-snow),
    :deep(.ql-snow .ql-toolbar),
    :deep(.ql-snow .ql-container),
    :deep([class*="snow"]) {
      border: none !important;
      outline: none !important;
    }
    
    // 确保编辑器外层容器也无边框 - 使用通配符选择器
    :deep(> *),
    :deep(> * > *) {
      border: none !important;
      outline: none !important;
    }
    
    // 移除所有可能的边框样式（包括内联样式）
    :deep(*) {
      &[style*="border"] {
        border: none !important;
      }
      &[style*="Border"] {
        border: none !important;
      }
    }
    
    // 强制移除所有边框 - 使用更通用的选择器覆盖所有子元素
    :deep(div),
    :deep(span),
    :deep(section),
    :deep(article) {
      border: none !important;
      outline: none !important;
      box-shadow: none !important;
    }

    // 恢复正文任务列表复选框（上面 div/span 通配会去掉 .ql-ui 边框，预览模式下像「没有选框」）
    :deep(.ql-editor li[data-list='checked'] > .ql-ui),
    :deep(.ql-editor li[data-list='unchecked'] > .ql-ui),
    :deep(.ql-editor li.checked > .ql-ui),
    :deep(.ql-editor li.unchecked > .ql-ui) {
      display: inline-block !important;
      width: 16px !important;
      height: 16px !important;
      min-width: 16px !important;
      min-height: 16px !important;
      line-height: 14px !important;
      text-align: center !important;
      border: 1px solid #adb0b8 !important;
      color: #777 !important;
      visibility: visible !important;
      opacity: 1 !important;
      box-shadow: none !important;
    }
    :deep(.ql-editor li[data-list='checked'] > .ql-ui),
    :deep(.ql-editor li.checked > .ql-ui) {
      border-color: #5e7ce0 !important;
    }
    /* Quill2 默认 data-list=checked 的 ::before 为 Unicode ☑，会盖住背景 SVG 的白勾；与 li.checked 一致清空后由背景图显示 */
    :deep(.ql-editor li[data-list='checked'] > .ql-ui::before),
    :deep(.ql-editor li.checked > .ql-ui::before) {
      content: '' !important;
    }

    :deep(.ql-container),
    :deep(.ql-editor) {
      color: #303133 !important;
      background-color: #fff !important;
      color-scheme: light;
      -webkit-text-fill-color: currentColor;
    }

    :deep(.ql-editor a) {
      color: var(--primary-color, #8b5cf6);
    }

    :deep(.ql-editor pre),
    :deep(.ql-editor .ql-code-block-container),
    :deep(.ql-editor .hljs),
    :deep(.ql-editor .hljs *) {
      -webkit-text-fill-color: unset;
      color-scheme: dark;
    }
  }
}

/* 代码块行号：Syntax 模块下每行对应一个 .ql-code-block，用计数器生成左侧行号 */
:deep(.ql-editor .ql-code-block-container) {
  counter-reset: fe-code-line;
  position: relative;
  /* 便于 .ql-ui 靠右；语言条 sticky 不随长代码块一起滚出视口 */
  display: flex;
  flex-direction: column;
  align-items: stretch;
}

/* 代码块复制：按钮在 .fe-code-block-copy-layer。
   勿用 inset:0 铺满：全屏透明层在部分环境下仍会影响下层 .ql-ui（任务列表勾选、代码块语言条）点击。
   改为 0×0 锚点 + overflow:visible，仅子节点 .fe-code-block-copy 可点。 */
.fluent-editor-v4-editor-surface .fe-code-block-copy-layer {
  position: absolute;
  left: 0;
  top: 0;
  width: 0;
  height: 0;
  z-index: 5;
  pointer-events: none;
  overflow: visible;
}

/* Quill 列表/代码块上的 .ql-ui 需明确可点，并略高于行内内容，避免被兄弟节点盖住 */
:deep(.ql-editor .ql-ui) {
  pointer-events: auto;
  z-index: 1;
}

.fluent-editor-v4-editor-surface .fe-code-block-copy-layer .fe-code-block-copy {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  margin: 0;
  border: 1px solid rgba(196, 181, 253, 0.35);
  border-radius: 999px;
  background: linear-gradient(145deg, rgba(124, 58, 237, 0.22), rgba(15, 23, 42, 0.5));
  color: #fff;
  cursor: pointer;
  pointer-events: auto;
  box-sizing: border-box;
  box-shadow:
    0 1px 2px rgba(15, 23, 42, 0.35),
    inset 0 1px 0 rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(6px);
  transition:
    background 0.18s ease,
    border-color 0.18s ease,
    box-shadow 0.18s ease,
    color 0.18s ease,
    transform 0.14s ease;
}

/* 尺寸由 JS 按 .ql-ui 高度设置；图标区用 div 包裹，在正方形内居中 */
.fluent-editor-v4-editor-surface .fe-code-block-copy-layer .fe-code-block-copy .fe-code-block-copy__icon-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 52%;
  height: 52%;
  flex-shrink: 0;
  color: #fff;
}

.fluent-editor-v4-editor-surface .fe-code-block-copy-layer .fe-code-block-copy .fe-code-block-copy__icon {
  display: block;
  width: 100%;
  height: 100%;
  flex-shrink: 0;
  color: #fff;
}

/* 与 Quill Snow / 全局 svg 规则隔离，保证描边为白 */
.fluent-editor-v4-editor-surface .fe-code-block-copy-layer .fe-code-block-copy .fe-code-block-copy__icon rect,
.fluent-editor-v4-editor-surface .fe-code-block-copy-layer .fe-code-block-copy .fe-code-block-copy__icon path {
  fill: none !important;
  stroke: #fff !important;
  stroke-width: 2 !important;
}

.fluent-editor-v4-editor-surface .fe-code-block-copy-layer .fe-code-block-copy:hover {
  background: linear-gradient(145deg, rgba(124, 58, 237, 0.42), rgba(91, 33, 182, 0.35));
  border-color: rgba(216, 180, 254, 0.55);
  color: #fff;
  box-shadow:
    0 2px 8px rgba(124, 58, 237, 0.28),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.fluent-editor-v4-editor-surface .fe-code-block-copy-layer .fe-code-block-copy:active {
  transform: scale(0.92);
}

.fluent-editor-v4-editor-surface .fe-code-block-copy-layer .fe-code-block-copy:focus-visible {
  outline: 2px solid rgba(167, 139, 250, 0.65);
  outline-offset: 2px;
}


:deep(.ql-editor .ql-code-block-container > .ql-code-block) {
  counter-increment: fe-code-line;
  position: relative;
  z-index: 0;
  padding-left: 3.5rem;
  box-sizing: border-box;
}

:deep(.ql-editor .ql-code-block-container > .ql-code-block::before) {
  content: counter(fe-code-line);
  position: absolute;
  left: 0;
  top: 0;
  width: 2.75rem;
  padding-right: 0.65rem;
  text-align: right;
  box-sizing: border-box;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace;
  font-size: 0.85em;
  line-height: inherit;
  font-variant-numeric: tabular-nums;
  user-select: none;
  pointer-events: none;
  color: #fff;
  border-right: 1px solid rgba(255, 255, 255, 0.15);
}

@media (max-width: 600px) {
  :deep(.ql-editor .ql-code-block-container > .ql-code-block) {
    padding-left: 2.85rem;
  }

  :deep(.ql-editor .ql-code-block-container > .ql-code-block::before) {
    width: 2.35rem;
    padding-right: 0.45rem;
    font-size: 0.78em;
  }
}

.editor-preview-modal {
  position: fixed;
  inset: 0;
  z-index: 1200;
  display: flex;
  align-items: stretch;
  justify-content: stretch;
  padding: 0;
  background: rgba(15, 23, 42, 0.42);
  backdrop-filter: blur(6px);
}

.editor-preview-modal__panel {
  display: flex;
  flex-direction: column;
  width: 100vw;
  height: 100vh;
  background: #fff;
  border-radius: 0;
  box-shadow: none;
  overflow: hidden;
}

.editor-preview-modal__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 0;
  border-bottom: 1px solid rgba(139, 92, 246, 0.12);
  background: linear-gradient(135deg, rgba(245, 243, 255, 0.95), #fff);
}

.editor-preview-modal__title {
  flex: 1;
  min-width: 0;
  color: #1f1147;
  font-size: 15px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.editor-preview-modal__close {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border: none;
  border-radius: 12px;
  padding: 0;
  background: linear-gradient(135deg, rgba(124, 58, 237, 0.12), rgba(139, 92, 246, 0.08));
  color: #5b21b6;
  cursor: pointer;
  font-size: 13px;
  font-weight: 600;
  transition:
    background 0.2s ease,
    color 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.2s ease;
  box-shadow: inset 0 0 0 1px rgba(124, 58, 237, 0.08);
}

.editor-preview-modal__close:hover {
  background: linear-gradient(135deg, rgba(124, 58, 237, 0.18), rgba(139, 92, 246, 0.14));
  color: #4c1d95;
  box-shadow:
    inset 0 0 0 1px rgba(124, 58, 237, 0.14),
    0 8px 20px rgba(124, 58, 237, 0.12);
}

.editor-preview-modal__close:active {
  transform: translateY(1px);
}

.editor-preview-modal__close:focus,
.editor-preview-modal__close:focus-visible {
  outline: none;
  box-shadow:
    inset 0 0 0 1px rgba(124, 58, 237, 0.16),
    0 0 0 3px rgba(139, 92, 246, 0.14);
}

.editor-preview-modal__close-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.72);
  flex-shrink: 0;
}

.editor-preview-modal__close-icon svg {
  width: 12px;
  height: 12px;
}

.editor-preview-modal__body {
  position: relative;
  flex: 1;
  min-height: 0;
  overflow: auto;
  padding: 0px;
  background: #f8fafc;
}

.editor-preview-modal__loading {
  position: absolute;
  top: 20px;
  right: 20px;
  z-index: 2;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 999px;
  background: rgba(91, 33, 182, 0.92);
  color: #fff;
  box-shadow: 0 10px 24px rgba(91, 33, 182, 0.2);
}

.editor-preview-modal__spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.35);
  border-top-color: #fff;
  border-radius: 50%;
  animation: fe-upload-spin 0.8s linear infinite;
}

.editor-preview-modal__image,
.editor-preview-modal__video,
.editor-preview-modal__iframe,
.editor-preview-modal__office {
  width: 100%;
  height: 100%;
  min-height: calc(100vh - 89px);
  border: none;
  background: #fff;
}

.editor-preview-modal__image {
  object-fit: contain;
  background: #fff;
}

/* 将默认 file blot 美化为更明显的附件卡片，避免 docx 等“看起来没反应” */
:deep(.ql-editor .ql-file-item) {
  display: flex;
  align-items: center;
  gap: 12px;
  width: min(100%, 420px);
  max-width: 100%;
  height: auto;
  margin: 12px 0;
  padding: 14px 16px;
  border: 1px solid rgba(139, 92, 246, 0.14);
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(245, 243, 255, 0.96), rgba(255, 255, 255, 0.98));
  box-shadow: 0 10px 24px rgba(139, 92, 246, 0.08);
  color: #1f2937;
  line-height: 1.5;
  white-space: normal;
  text-decoration: none;
  vertical-align: middle;
  position: relative;
  padding-left: 68px;
  padding-right: 48px;
  justify-content: flex-start;
  transition:
    transform 0.18s ease,
    box-shadow 0.18s ease,
    border-color 0.18s ease,
    background 0.18s ease;
}

:deep(.ql-editor .ql-file-item:hover) {
  border-color: rgba(124, 58, 237, 0.24);
  box-shadow: 0 14px 30px rgba(124, 58, 237, 0.14);
  transform: translateY(-1px);
}

:deep(.ql-editor .ql-file-item:active) {
  transform: translateY(0);
}

:deep(.ql-editor .ql-file-item)::after {
  content: '';
  position: absolute;
  right: 18px;
  top: 50%;
  width: 9px;
  height: 9px;
  border-top: 2px solid rgba(124, 58, 237, 0.45);
  border-right: 2px solid rgba(124, 58, 237, 0.45);
  transform: translateY(-50%) rotate(45deg);
  transition:
    transform 0.18s ease,
    border-color 0.18s ease;
}

:deep(.ql-editor .ql-file-item:hover::after) {
  border-top-color: rgba(124, 58, 237, 0.72);
  border-right-color: rgba(124, 58, 237, 0.72);
  transform: translateY(-50%) translateX(2px) rotate(45deg);
}

:deep(.ql-editor .ql-file-item)::before {
  content: 'FILE';
  position: absolute;
  left: 16px;
  top: 0;
  bottom: 0;
  margin: auto 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  box-shadow:
    0 10px 18px rgba(124, 58, 237, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.24);
}

:deep(.ql-editor .ql-file-item svg) {
  display: none;
}

:deep(.ql-editor .ql-file-item.icon-file::before) {
  display: inline-flex;
}

:deep(.ql-editor .ql-file-item span) {
  display: flex;
  align-items: center;
  min-width: 0;
  min-height: 40px;
  text-decoration: none;
  word-break: break-all;
  font-weight: 500;
  color: #111827;
}

:deep(.ql-editor .ql-file-item[data-title$=".pdf" i]) {
  border-color: rgba(239, 68, 68, 0.18);
  background: linear-gradient(135deg, rgba(254, 242, 242, 0.98), rgba(255, 255, 255, 0.98));
}

:deep(.ql-editor .ql-file-item[data-title$=".pdf" i]::before) {
  content: 'PDF';
  background: linear-gradient(135deg, #ef4444, #dc2626);
  box-shadow: 0 8px 16px rgba(220, 38, 38, 0.2);
}

:deep(.ql-editor .ql-file-item[data-title$=".pdf" i]::after) {
  border-top-color: rgba(220, 38, 38, 0.48);
  border-right-color: rgba(220, 38, 38, 0.48);
}

:deep(.ql-editor .ql-file-item[data-title$=".pptx" i]),
:deep(.ql-editor .ql-file-item[data-title$=".ppt" i]) {
  border-color: rgba(249, 115, 22, 0.2);
  background: linear-gradient(135deg, rgba(255, 247, 237, 0.98), rgba(255, 255, 255, 0.98));
}

:deep(.ql-editor .ql-file-item[data-title$=".pptx" i]::before),
:deep(.ql-editor .ql-file-item[data-title$=".ppt" i]::before) {
  content: 'PPT';
  background: linear-gradient(135deg, #f97316, #ea580c);
  box-shadow: 0 8px 16px rgba(234, 88, 12, 0.18);
}

:deep(.ql-editor .ql-file-item[data-title$=".pptx" i]::after),
:deep(.ql-editor .ql-file-item[data-title$=".ppt" i]::after) {
  border-top-color: rgba(234, 88, 12, 0.48);
  border-right-color: rgba(234, 88, 12, 0.48);
}

:deep(.ql-editor .ql-file-item[data-title$=".docx" i]),
:deep(.ql-editor .ql-file-item[data-title$=".doc" i]) {
  border-color: rgba(37, 99, 235, 0.2);
  background: linear-gradient(135deg, rgba(239, 246, 255, 0.98), rgba(255, 255, 255, 0.98));
}

:deep(.ql-editor .ql-file-item[data-title$=".docx" i]::before),
:deep(.ql-editor .ql-file-item[data-title$=".doc" i]::before) {
  content: 'DOC';
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
  box-shadow: 0 8px 16px rgba(29, 78, 216, 0.18);
}

:deep(.ql-editor .ql-file-item[data-title$=".docx" i]::after),
:deep(.ql-editor .ql-file-item[data-title$=".doc" i]::after) {
  border-top-color: rgba(29, 78, 216, 0.48);
  border-right-color: rgba(29, 78, 216, 0.48);
}

:deep(.ql-editor .ql-file-item[data-title$=".xlsx" i]),
:deep(.ql-editor .ql-file-item[data-title$=".xls" i]) {
  border-color: rgba(22, 163, 74, 0.2);
  background: linear-gradient(135deg, rgba(240, 253, 244, 0.98), rgba(255, 255, 255, 0.98));
}

:deep(.ql-editor .ql-file-item[data-title$=".xlsx" i]::before),
:deep(.ql-editor .ql-file-item[data-title$=".xls" i]::before) {
  content: 'XLS';
  background: linear-gradient(135deg, #16a34a, #15803d);
  box-shadow: 0 8px 16px rgba(21, 128, 61, 0.18);
}

:deep(.ql-editor .ql-file-item[data-title$=".xlsx" i]::after),
:deep(.ql-editor .ql-file-item[data-title$=".xls" i]::after) {
  border-top-color: rgba(21, 128, 61, 0.48);
  border-right-color: rgba(21, 128, 61, 0.48);
}

:deep(.ql-editor .ql-file-item),
:deep(.ql-editor .my-video),
:deep(.ql-editor video) {
  overflow: hidden;
}

:deep(.ql-editor .my-video),
:deep(.ql-editor video) {
  display: block;
  width: min(100%, 560px);
  max-width: 100%;
  max-height: 320px;
  margin: 12px 0;
  border-radius: 14px;
  background: #0f172a;
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.14);
}

@keyframes fe-upload-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>

<style lang="less">
/* Modal.message 挂载在 body，需非 scoped */
.fluent-editor-md-paste-msg {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
  max-width: min(360px, 92vw);
}

.fluent-editor-md-paste-msg__text {
  line-height: 1.45;
  text-align: left;
}
</style>