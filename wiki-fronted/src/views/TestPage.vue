<template>
  <tiny-drawer
    :visible="true"
    :title="translate('feedback.title')"
    width="70%"
    placement="right"
    :mask-closable="true"
    :show-footer="false"
    @update:visible="handleVisibleChange"
  >
    <div class="feedback-drawer-content">
      <!-- 反馈输入区 -->
      <div class="feedback-input-section">
        <div class="input-row">
          <label class="input-label">{{ translate('feedback.type') }}</label>
          <tiny-select
            v-model="feedbackType"
            :placeholder="translate('feedback.typePlaceholder')"
            class="feedback-type-select"
          >
            <tiny-option :label="translate('feedback.typeSuggestion')" :value="FEEDBACK_TYPE_SUGGESTION" />
            <tiny-option :label="translate('feedback.typeBug')" :value="FEEDBACK_TYPE_BUG" />
            <tiny-option :label="translate('feedback.typeOther')" :value="FEEDBACK_TYPE_OTHER" />
          </tiny-select>
        </div>
        <div class="input-row">
          <label class="input-label">{{ translate('feedback.content') }}</label>
          <div class="editor-wrapper" ref="editorRef">
          </div>
          <div class="input-footer">
            <span class="char-count">{{ plainTextLength }}/1000</span>
            <tiny-button
              type="primary"
              size="small"
              :loading="submitting"
              :disabled="!canSubmit"
              @click="handleSubmit"
            >
              {{ translate('feedback.submit') }}
            </tiny-button>
          </div>
        </div>
      </div>

      <!-- 反馈列表 -->
      <div class="feedback-list-section">
        <LoadingSpinner v-if="loading" :absolute="false" />
        <div v-else-if="feedbacks.length === 0" class="empty-feedbacks">
          <p>{{ translate('feedback.empty') }}</p>
        </div>
        <div v-else class="feedback-list">
          <div v-for="item in feedbacks" :key="item.id" class="feedback-item">
            <div class="feedback-header">
              <div class="feedback-avatar">
                <img v-if="item.user_avatar" :src="item.user_avatar" alt="avatar" />
                <span v-else class="avatar-placeholder">{{ getInitial(item.user_name) }}</span>
              </div>
              <div class="feedback-meta">
                <span class="feedback-user">{{ translate('feedback.user') }}：{{ item.user_name || translate('comment.anonymous') }}</span>
                <span class="feedback-time">{{ translate('feedback.time') }}：{{ item.created_at || '—' }}</span>
              </div>
              <span class="feedback-type-tag" :class="typeTagClass(item.feedback_type)">
                {{ getTypeLabel(item.feedback_type) }}
              </span>
              <span class="feedback-status" :class="statusTagClass(item.status)">
                {{ getStatusLabel(item.status) }}
              </span>
            </div>
            <div class="feedback-body">
              <div class="feedback-content">
                <div
                  class="feedback-preview-editor"
                  :ref="(el) => setPreviewEditorHost(item.id, el)"
                />
              </div>
              <div v-if="item.admin_reply" class="admin-reply">
                <span class="admin-reply-label">{{ translate('feedback.adminReply') }}</span>
                <div class="admin-reply-content">{{ item.admin_reply }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </tiny-drawer>
</template>

<script setup lang="ts">

import { ref, watch, nextTick, computed, onBeforeUnmount } from 'vue'
import { Button as TinyButton, Drawer as TinyDrawer,
  Select as TinySelect, Option as TinyOption, Modal } from '@opentiny/vue'
import {
  feedbackApi,
  type Feedback,
  FEEDBACK_TYPE_SUGGESTION,
  FEEDBACK_TYPE_BUG,
  FEEDBACK_TYPE_OTHER,
  FEEDBACK_STATUS_PENDING,
  FEEDBACK_STATUS_PROCESSING,
  FEEDBACK_STATUS_RESOLVED,
  FEEDBACK_STATUS_CLOSED
} from '../api/feedback'
import { fileApi } from '../api/file'
import type { Range } from '@opentiny/fluent-editor'
import { t } from '../i18n'
import { useLocaleStore } from '../stores/locale'
// @ts-ignore
import LoadingSpinner from '../components/LoadingSpinner.vue'
import { onMounted } from 'vue';
import FluentEditor, {
  FULL_TOOLBAR,
  I18N,
  generateToolbarTip,
  generateTableUp,
  CollaborationModule,
} from '@opentiny/fluent-editor';
import '@opentiny/fluent-editor/style.css';
import '@opentiny/vue-theme/fluent-editor/index.css';

// emoji 表情
import data from '@emoji-mart/data';
import { computePosition } from '@floating-ui/dom';
import type { EmojiMartData } from '@emoji-mart/data';
import { Picker } from 'emoji-mart';

// table 表格
import {
  defaultCustomSelect,
  TableMenuContextmenu,
  TableSelection,
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
import 'highlight.js/styles/atom-one-dark.css';

// screenshot 截屏
import Html2Canvas from 'html2canvas';
window.Html2Canvas = Html2Canvas;

// 公式
import katex from 'katex';
import 'katex/dist/katex.min.css';
window.katex = katex;

// mention @提醒
const searchKey = 'name';
const mentionList = [
  {
    name: 'kagol',
    cn: '卡哥',
    followers: 156,
    avatar: 'https://avatars.githubusercontent.com/u/9566362?v=4',
  },
  {
    name: 'zzcr',
    cn: '超哥',
    followers: 10,
    avatar: 'https://avatars.githubusercontent.com/u/18521562?v=4',
  },
  {
    name: 'hexqi',
    cn: '小伍哥',
    followers: 2,
    avatar: 'https://avatars.githubusercontent.com/u/18585869?v=4',
  },
];

let editor: FluentEditor;
const editorRef = ref<HTMLElement>();
const feedbackContent = ref('')

onMounted(() => {
  if (!editorRef.value) return;

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

  // 初始化语言
  const lang = ref(localeStore.localeMap[localeStore.currentLocale]);
  console.log(lang.value)

  editor = new FluentEditor(editorRef.value, {
    theme: 'snow',
    modules: {
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
      markdownShortcuts: true,
      syntax: {
        hljs,
      },
      counter: true,
      mathlive: true,
      emoji: {
        emojiData: data as EmojiMartData,
        EmojiPicker: Picker,
        emojiPickerPosition: computePosition,
      },
      i18n: {
        lang: lang.value,
      },
      'toolbar-tip': {
        defaultTooltipOptions: {
          tipHoverable: false,
        },
      },
      'table-up': {
        customSelect: defaultCustomSelect,
        modules: [{ module: TableSelection }, { module: TableMenuContextmenu }],
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
      mention: {
        containerClass: 'ql-mention-list-container__custom-list',
        itemKey: 'cn',
        searchKey,
        search(term: string) {
          return mentionList.filter((item) => {
            return item[searchKey] && String(item[searchKey]).includes(term);
          });
        },
        renderMentionItem(item: any) {
          return `
            <div class="item-avatar">
              <img src="${item.avatar}">
            </div>
            <div class="item-info">
              <div class="item-name">${item.cn}</div>
              <div class="item-desc">${item.followers}粉丝</div>
            </div>
          `;
        },
      },
    },
  });

  editor.on('text-change', () => {
    feedbackContent.value = JSON.stringify(editor.getContents())
    console.log(feedbackContent.value)
  })
});
const props = defineProps<{
  visible: boolean
  articleId: number | null
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'feedback-added'): void
}>()

const localeStore = useLocaleStore()

const translate = (key: string, params?: Record<string, string>) => {
  void localeStore.localeKey
  return t(key, params)
}


const previewEditorHostMap = new Map<number, HTMLElement>()
const previewEditorMap = new Map<number, FluentEditor>()

const setPreviewEditorHost = (id: number, el: unknown) => {
  if (!(el instanceof HTMLElement)) {
    previewEditorHostMap.delete(id)
    return
  }
  previewEditorHostMap.set(id, el)
}

const applyPreviewContent = (previewEditor: FluentEditor, content?: string) => {
  const safeContent = content || ''
  if (!safeContent) {
    previewEditor.setContents([])
    return
  }

  try {
    const parsed = JSON.parse(safeContent)
    if (parsed && typeof parsed === 'object' && 'ops' in parsed) {
      previewEditor.setContents(parsed)
      return
    }
  } catch {
    // 非 JSON，按 HTML 渲染
  }

  previewEditor.clipboard.dangerouslyPasteHTML(safeContent)
}

const renderPreviewEditors = () => {
  const activeIds = new Set(feedbacks.value.map(item => item.id))

  for (const [id, editor] of previewEditorMap.entries()) {
    if (!activeIds.has(id)) {
      editor.off?.('text-change')
      previewEditorMap.delete(id)
    }
  }

  const lang = localeStore.localeMap[localeStore.currentLocale]
  for (const item of feedbacks.value) {
    const host = previewEditorHostMap.get(item.id)
    if (!host) continue

    let previewEditor = previewEditorMap.get(item.id)
    if (!previewEditor) {
      host.innerHTML = ''
      previewEditor = new FluentEditor(host, {
        theme: 'snow',
        readOnly: true,
        modules: {
          toolbar: false,
          i18n: { lang },
        },
      })
      previewEditorMap.set(item.id, previewEditor)
    }
    applyPreviewContent(previewEditor, item.content)
  }
}

// 状态
const loading = ref(false)
const submitting = ref(false)
const feedbacks = ref<Feedback[]>([])
const feedbackType = ref<number>(FEEDBACK_TYPE_SUGGESTION)

const contentEditorRef = ref()

const plainTextLength = computed(() => {
  if (!feedbackContent.value) return 0
  const temp = document.createElement('div')
  temp.innerHTML = feedbackContent.value
  return temp.textContent?.length || 0
})

const canSubmit = computed(() => {
  // 去除两端空格和换行符
  if (!feedbackContent.value) return false
  return true
})

const getTypeLabel = (type: number) => {
  if (type === FEEDBACK_TYPE_SUGGESTION) return translate('feedback.typeSuggestion')
  if (type === FEEDBACK_TYPE_BUG) return translate('feedback.typeBug')
  return translate('feedback.typeOther')
}

const typeTagClass = (type: number) => {
  if (type === FEEDBACK_TYPE_BUG) return 'type-bug'
  if (type === FEEDBACK_TYPE_SUGGESTION) return 'type-suggestion'
  return 'type-other'
}

const getStatusLabel = (status?: number) => {
  if (status === FEEDBACK_STATUS_PENDING) return translate('feedback.statusPending')
  if (status === FEEDBACK_STATUS_PROCESSING) return translate('feedback.statusProcessing')
  if (status === FEEDBACK_STATUS_RESOLVED) return translate('feedback.statusResolved')
  if (status === FEEDBACK_STATUS_CLOSED) return translate('feedback.statusClosed')
  return translate('feedback.statusPending')
}

const statusTagClass = (status?: number) => {
  if (status === FEEDBACK_STATUS_RESOLVED) return 'status-resolved'
  if (status === FEEDBACK_STATUS_CLOSED) return 'status-closed'
  if (status === FEEDBACK_STATUS_PROCESSING) return 'status-processing'
  return 'status-pending'
}

const getInitial = (name?: string): string => {
  if (!name) return 'U'
  return name.charAt(0).toUpperCase()
}

const loadFeedbacks = async () => {
  if (!props.articleId) return
  loading.value = true
  try {
    feedbacks.value = await feedbackApi.getArticleFeedbacks(props.articleId)
    await nextTick()
    renderPreviewEditors()
  } catch (e) {
    console.error('加载反馈列表失败:', e)
    feedbacks.value = []
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  
  if (!props.articleId || !canSubmit.value || submitting.value) return
  submitting.value = true
  try {
    await feedbackApi.createFeedback(props.articleId, {
      feedback_type: feedbackType.value,
      content: feedbackContent.value
    })
    feedbackContent.value = ''
    await nextTick()
    editor.setContents([])
    await loadFeedbacks()
    emit('feedback-added')
  } catch (e) {
    console.error('提交反馈失败:', e)
  } finally {
    submitting.value = false
  }
}

const handleVisibleChange = (val: boolean) => {
  emit('update:visible', val)
}

watch(
  () => props.visible,
  async (v) => {
    if (v && props.articleId) {
      await loadFeedbacks()
      nextTick(() => {
        setTimeout(() => editor.focus(), 300)
      })
    } else {
      feedbackContent.value = ''
      feedbackType.value = FEEDBACK_TYPE_SUGGESTION
      nextTick(() => {
        editor.setContents([])
      })
    }
  },
  { immediate: true }
)

watch(
  () => props.articleId,
  async (v) => {
    if (props.visible && v) await loadFeedbacks()
  }
)

watch(
  () => feedbacks.value,
  async () => {
    await nextTick()
    renderPreviewEditors()
  },
  { deep: true }
)

watch(
  () => localeStore.currentLocale,
  async () => {
    await nextTick()
    renderPreviewEditors()
  }
)

onBeforeUnmount(() => {
  previewEditorMap.forEach(editor => editor.off?.('text-change'))
  previewEditorMap.clear()
  previewEditorHostMap.clear()
})
</script>

<style scoped lang="less">

.feedback-drawer-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

.feedback-input-section {
  padding: 16px 0;
  border-bottom: 1px solid #e4e7ed;
  flex-shrink: 0;
  text-align: left;
}

.input-row {
  margin-bottom: 12px;
  text-align: left;

  &:last-of-type {
    margin-bottom: 0;
  }
}

.input-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
  text-align: left;
}

.feedback-type-select {
  width: 100%;
  max-width: 200px;
  text-align: left;

  :deep(.tiny-select__wrap),
  :deep(.tiny-select__input) {
    text-align: left;
  }
}

.editor-wrapper {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  transition: border-color 0.2s;
  text-align: left;

  &:focus-within {
    border-color: var(--primary-color, #8b5cf6);
  }
}

.feedback-editor {
  :deep(.ql-toolbar) {
    border: none !important;
    border-bottom: 1px solid #e4e7ed !important;
    padding: 6px 8px !important;
    background: #fafafa;
    text-align: left;
  }
  :deep(.ql-container) {
    border: none !important;
    font-size: 14px;
    text-align: left !important;
  }
  :deep(.ql-editor) {
    min-height: 100px;
    max-height: 180px;
    padding: 10px 12px;
    overflow-y: auto;
    text-align: left !important;

    &.ql-blank::before {
      left: 12px;
      text-align: left;
    }
  }
}

.input-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.char-count {
  font-size: 12px;
  color: #999;
}

.feedback-list-section {
  flex: 1;
  overflow-y: auto;
  padding: 16px 0;
}

.empty-feedbacks {
  text-align: center;
  padding: 60px 20px;
  color: #999;
  font-size: 14px;
}

.feedback-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feedback-item {
  padding: 14px;
  background: #fafafa;
  border-radius: 8px;
  border: 1px solid #f0f0f0;
}

.feedback-header {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}

.feedback-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  background: linear-gradient(135deg, #64748b, #94a3b8);
  display: flex;
  align-items: center;
  justify-content: center;

  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .avatar-placeholder {
    color: #fff;
    font-size: 14px;
    font-weight: 600;
  }
}

.feedback-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
  flex: 1;
  min-width: 0;
}

.feedback-user {
  font-size: 13px;
  color: #333;
}

.feedback-time {
  font-size: 12px;
  color: #999;
}

.feedback-type-tag {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;

  &.type-suggestion {
    background: #ede9fe;
    color: #6d28d9;
  }
  &.type-bug {
    background: #fee2e2;
    color: #b91c1c;
  }
  &.type-other {
    background: #e5e7eb;
    color: #4b5563;
  }
}

.feedback-status {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
  margin-left: auto;

  &.status-pending {
    background: #fef3c7;
    color: #b45309;
  }
  &.status-processing {
    background: #dbeafe;
    color: #1d4ed8;
  }
  &.status-resolved {
    background: #d1fae5;
    color: #047857;
  }
  &.status-closed {
    background: #f3f4f6;
    color: #6b7280;
  }
}

.feedback-body {
  font-size: 14px;
  color: #333;
  text-align: left;
}

.feedback-content {
  margin-bottom: 0;
}

.feedback-preview-editor {
  border: none !important;
  box-shadow: none !important;
  outline: none !important;
  background: transparent !important;

  :deep(.ql-toolbar) {
    display: none !important;
  }
  :deep(.ql-container) {
    border: none !important;
    background: transparent !important;
    text-align: left !important;
  }
  :deep(.ql-editor) {
    padding: 0 !important;
    min-height: auto !important;
    cursor: default !important;
    border: none !important;
    background: transparent !important;
    text-align: left !important;
    margin: 0 !important;
  }
}

.admin-reply {
  margin-top: 12px;
  padding: 10px 12px;
  background: #f0fdf4;
  border-left: 3px solid var(--primary-color, #8b5cf6);
  border-radius: 4px;
}

.admin-reply-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--primary-color, #8b5cf6);
  display: block;
  margin-bottom: 6px;
}

.admin-reply-content {
  font-size: 13px;
  line-height: 1.5;
  color: #333;
}

:deep(.tiny-drawer) {
  .tiny-drawer__header {
    padding: 16px 20px;
    border-bottom: 1px solid #e4e7ed;
  }
  .tiny-drawer__title {
    font-size: 18px;
    font-weight: 600;
    color: #333;
  }
  .tiny-drawer__body {
    padding: 0 20px;
    height: calc(100% - 60px);
    overflow: hidden;
  }
}

.ql-mention-list-container.ql-mention-list-container__custom-list
  .ql-mention-list
  .ql-mention-item {
  display: flex;
  align-items: center;
  height: 52px;
  line-height: 1.5;
  font-size: 12px;
  padding: 0 12px;

  &.ql-mention-item--active {
    background-color: #f1f2f3;
    color: #18191c;
  }

  .item-avatar {
    margin-right: 8px;

    img {
      width: 36px;
      border-radius: 50%;
    }
  }

  .item-info {
    .item-desc {
      color: #9499a0;
    }
  }
}
</style>
