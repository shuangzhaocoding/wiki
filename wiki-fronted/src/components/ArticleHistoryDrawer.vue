<template>
  <tiny-drawer
    :visible="visible"
    :title="translate('article.history.title')"
    width="80%"
    placement="right"
    :mask-closable="true"
    :show-footer="false"
    @update:visible="handleVisibleChange"
  >
    <div class="history-drawer-content">
      <!-- 工具栏 -->
      <div class="history-toolbar">
        <div class="toolbar-left">
          <tiny-button
            v-if="selectedVersions.length === 2"
            type="primary"
            @click="handleCompareVersions"
          >
            {{ translate('article.history.compare') }}
          </tiny-button>
          <span v-else class="hint-text">
            {{ translate('article.history.selectTwoHint') }}
          </span>
        </div>
        <div class="toolbar-right">
          <tiny-button @click="handleRefresh">
            {{ translate('common.refresh') }}
          </tiny-button>
        </div>
      </div>

      <!-- 版本列表表格 -->
      <div class="history-table-wrapper">
        <LoadingSpinner v-if="loading" :absolute="false" />
        <div v-else-if="versions.length === 0" class="empty-versions">
          <p>{{ translate('article.history.empty') }}</p>
        </div>
        <tiny-grid
          v-else
          :data="versions"
          :checkbox-config="{ checkMethod: checkVersion }"
          @checkbox-change="handleCheckboxChange"
          class="history-grid"
        >
          <tiny-grid-column type="checkbox" width="60" align="center" />
          <tiny-grid-column field="version" :title="translate('article.history.versionNumber')" width="100" align="center" />
          <tiny-grid-column field="title" :title="translate('article.titleLabel')" min-width="200" />
          <tiny-grid-column field="author_id" :title="translate('article.history.createdBy')" width="120" />
          <tiny-grid-column field="created_at" :title="translate('article.history.createdAt')" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </tiny-grid-column>
          <tiny-grid-column :title="translate('article.history.actions')" width="200" align="center" fixed="right">
            <template #default="{ row }">
              <tiny-button
                size="small"
                @click="handleViewVersion(row)"
              >
                {{ translate('article.history.view') }}
              </tiny-button>
              <tiny-button
                v-if="!row.is_current"
                size="small"
                type="primary"
                @click="handleRestoreVersion(row)"
                :loading="restoringVersionId === row.id"
              >
                {{ translate('article.history.restore') }}
              </tiny-button>
            </template>
          </tiny-grid-column>
        </tiny-grid>
      </div>

      <!-- 版本详情弹窗 -->
      <tiny-dialog-box
        v-model:visible="showVersionDetail"
        :title="translate('article.history.versionDetail')"
        width="70%"
      >
        <div v-if="viewingVersion" class="version-detail">
          <div class="detail-item">
            <label>{{ translate('article.history.versionNumber') }}:</label>
            <span>{{ viewingVersion.version_number }}</span>
          </div>
          <div class="detail-item">
            <label>{{ translate('article.title') }}:</label>
            <span>{{ viewingVersion.title }}</span>
          </div>
          <div class="detail-item">
            <label>{{ translate('article.history.createdBy') }}:</label>
            <span>{{ viewingVersion.created_by_name || '-' }}</span>
          </div>
          <div class="detail-item">
            <label>{{ translate('article.history.createdAt') }}:</label>
            <span>{{ formatDate(viewingVersion.created_at) }}</span>
          </div>
          <div class="detail-item">
            <label>{{ translate('article.content') }}:</label>
            <div class="version-content">
              <FluentEditorV4
                :model-value="viewingVersion.content || ''"
                :modules="previewEditorModules"
                :toolbar="false"
                :disabled="true"
                class="version-content-editor"
              />
            </div>
          </div>
        </div>
        <template #footer>
          <tiny-button @click="showVersionDetail = false">{{ translate('common.close') }}</tiny-button>
        </template>
      </tiny-dialog-box>

      <!-- 版本对比弹窗 -->
      <tiny-dialog-box
        v-model:visible="showCompareDialog"
        :title="translate('article.history.compare')"
        width="90%"
      >
        <div v-if="compareResult" class="compare-result">
          <div class="compare-header">
            <div class="compare-version">
              <h4>{{ translate('article.history.version') }} {{ compareResult.version1.version_number }}</h4>
              <p>{{ formatDate(compareResult.version1.created_at) }}</p>
            </div>
            <div class="compare-vs">VS</div>
            <div class="compare-version">
              <h4>{{ translate('article.history.version') }} {{ compareResult.version2.version_number }}</h4>
              <p>{{ formatDate(compareResult.version2.created_at) }}</p>
            </div>
          </div>
          <div class="compare-content">
            <div class="compare-panel">
              <div class="panel-header">{{ translate('article.history.version') }} {{ compareResult.version1.version_number }}</div>
              <div class="panel-content">
                <FluentEditorV4
                  :model-value="compareResult.version1.content || ''"
                  :modules="previewEditorModules"
                  :toolbar="false"
                  :disabled="true"
                  class="compare-editor"
                />
              </div>
            </div>
            <div class="compare-panel">
              <div class="panel-header">{{ translate('article.history.version') }} {{ compareResult.version2.version_number }}</div>
              <div class="panel-content">
                <FluentEditorV4
                  :model-value="compareResult.version2.content || ''"
                  :modules="previewEditorModules"
                  :toolbar="false"
                  :disabled="true"
                  class="compare-editor"
                />
              </div>
            </div>
          </div>
        </div>
        <template #footer>
          <tiny-button @click="showCompareDialog = false">{{ translate('common.close') }}</tiny-button>
        </template>
      </tiny-dialog-box>
    </div>
  </tiny-drawer>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Drawer as TinyDrawer, Button as TinyButton, Grid as TinyGrid, GridColumn as TinyGridColumn, DialogBox as TinyDialogBox } from '@opentiny/vue'
import { articleApi, type ArticleVersion } from '../api/article'
import { t } from '../i18n'
import { Modal } from '@opentiny/vue'
// @ts-ignore
import LoadingSpinner from './LoadingSpinner.vue'
import { useLocaleStore } from '../stores/locale'
import FluentEditorV4 from './FluentEditorV4.vue'

const props = defineProps<{
  visible: boolean
  articleId: number | null
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'version-restored'): void
}>()

const localeStore = useLocaleStore()
const translate = (key: string, params?: Record<string, string>) => t(key, params)

const versions = ref<ArticleVersion[]>([])
const loading = ref(false)
const selectedVersions = ref<ArticleVersion[]>([])
const restoringVersionId = ref<number | null>(null)
const showVersionDetail = ref(false)
const viewingVersion = ref<ArticleVersion | null>(null)
const showCompareDialog = ref(false)
const compareResult = ref<{
  diff: string
  version1: ArticleVersion
  version2: ArticleVersion
} | null>(null)

// 预览编辑器模块（只读）
const previewEditorModules = {
  toolbar: false
}

// 格式化日期
const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  try {
    const date = new Date(dateStr)
    const localeMap: Record<string, string> = {
      'zh': 'zh-CN',
      'en': 'en-US',
      'ko': 'ko-KR',
      'de': 'de-DE',
      'ja': 'ja-JP',
      'fr': 'fr-FR'
    }
    const locale = localeMap[localeStore.currentLocale] || 'zh-CN'
    return date.toLocaleString(locale)
  } catch {
    return dateStr
  }
}

// 检查版本是否可选（最多选2个）
const checkVersion = ({ row }: { row: ArticleVersion }) => {
  if (selectedVersions.value.length >= 2 && !selectedVersions.value.find(v => v.id === row.id)) {
    return false
  }
  return true
}

// 处理复选框变化
const handleCheckboxChange = (data: { records: ArticleVersion[] }) => {
  selectedVersions.value = data.records
}

// 加载历史版本列表
const loadVersions = async () => {
  if (!props.articleId) return
  
  try {
    loading.value = true
    versions.value = await articleApi.getArticleVersions(props.articleId)
  } catch (error: any) {
    Modal.message({
      message: error.message || translate('article.history.loadError'),
      status: 'error'
    })
    versions.value = []
  } finally {
    loading.value = false
  }
}

// 刷新
const handleRefresh = () => {
  loadVersions()
  selectedVersions.value = []
}

// 查看版本详情
const handleViewVersion = (version: ArticleVersion) => {
  viewingVersion.value = version
  showVersionDetail.value = true
}

// 回滚版本
const handleRestoreVersion = async (version: ArticleVersion) => {
  if (!props.articleId) return
  
  try {
    await Modal.confirm({
      title: translate('article.history.restoreConfirm'),
      message: translate('article.history.restoreMessage', { version: version.version_number.toString() })
    })
    
    restoringVersionId.value = version.id
    await articleApi.restoreArticleVersion(props.articleId, version.id)
    
    Modal.message({
      message: translate('article.history.restoreSuccess'),
      status: 'success'
    })
    
    // 重新加载版本列表
    await loadVersions()
    selectedVersions.value = []
    
    // 通知父组件刷新文章
    emit('version-restored')
  } catch (error: any) {
    if (error !== 'cancel') {
      Modal.message({
        message: error.message || translate('article.history.restoreError'),
        status: 'error'
      })
    }
  } finally {
    restoringVersionId.value = null
  }
}

// 对比版本
const handleCompareVersions = async () => {
  if (selectedVersions.value.length !== 2 || !props.articleId) return
  
  try {
    loading.value = true
    const [v1, v2] = selectedVersions.value
    if (!v1 || !v2) return
    const result = await articleApi.compareArticleVersions(props.articleId, v1.id, v2.id)
    compareResult.value = result
    showCompareDialog.value = true
  } catch (error: any) {
    Modal.message({
      message: error.message || translate('article.history.compareError'),
      status: 'error'
    })
  } finally {
    loading.value = false
  }
}

// 处理可见性变化
const handleVisibleChange = (value: boolean) => {
  emit('update:visible', value)
  if (!value) {
    selectedVersions.value = []
    showVersionDetail.value = false
    showCompareDialog.value = false
    compareResult.value = null
  }
}

// 监听 visible 和 articleId 变化
watch([() => props.visible, () => props.articleId], ([newVisible, newArticleId]) => {
  if (newVisible && newArticleId) {
    loadVersions()
  }
}, { immediate: true })
</script>

<style scoped lang="less">
.history-drawer-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 20px;
}

.history-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e4e7ed;

  .toolbar-left {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .hint-text {
    color: #999;
    font-size: 14px;
  }

  .toolbar-right {
    display: flex;
    gap: 8px;
  }
}

.history-table-wrapper {
  flex: 1;
  overflow: auto;
  min-height: 0;
}

.empty-versions {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}

.history-grid {
  width: 100%;
  
  :deep(.tiny-grid) {
    width: 100% !important;
  }
  
  :deep(.tiny-grid__wrapper) {
    width: 100% !important;
  }
  
  :deep(.tiny-grid__body-wrapper) {
    width: 100% !important;
  }
  
  :deep(.tiny-grid__header-wrapper) {
    width: 100% !important;
  }
}

.current-badge {
  display: inline-block;
  padding: 2px 8px;
  background-color: #8b5cf6;
  color: #fff;
  border-radius: 4px;
  font-size: 12px;
}

.version-detail {
  .detail-item {
    margin-bottom: 16px;

    label {
      display: inline-block;
      width: 120px;
      font-weight: 500;
      color: #333;
    }

    span {
      color: #666;
    }
  }

  .version-content {
    margin-top: 12px;
    border: 1px solid #e4e7ed;
    border-radius: 4px;
    padding: 12px;
    max-height: 500px;
    overflow-y: auto;
  }

  .version-content-editor {
    :deep(.ql-container) {
      border: none;
    }
  }
}

.compare-result {
  .compare-header {
    display: flex;
    align-items: center;
    justify-content: space-around;
    margin-bottom: 20px;
    padding-bottom: 16px;
    border-bottom: 1px solid #e4e7ed;

    .compare-version {
      flex: 1;
      text-align: center;

      h4 {
        margin: 0 0 8px 0;
        font-size: 16px;
        color: #333;
      }

      p {
        margin: 0;
        font-size: 12px;
        color: #999;
      }
    }

    .compare-vs {
      margin: 0 20px;
      font-size: 18px;
      font-weight: bold;
      color: #8b5cf6;
    }
  }

  .compare-content {
    display: flex;
    gap: 20px;
    height: 600px;

    .compare-panel {
      flex: 1;
      display: flex;
      flex-direction: column;
      border: 1px solid #e4e7ed;
      border-radius: 4px;
      overflow: hidden;

      .panel-header {
        padding: 12px 16px;
        background-color: #f5f7fa;
        border-bottom: 1px solid #e4e7ed;
        font-weight: 500;
        color: #333;
      }

      .panel-content {
        flex: 1;
        overflow-y: auto;
        padding: 16px;
      }
    }
  }

  .compare-editor {
    :deep(.ql-container) {
      border: none;
    }
  }
}
</style>
