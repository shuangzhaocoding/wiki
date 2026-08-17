<template>
  <div class="banner-management">
    <div class="banner-toolbar">
      <tiny-input
        v-model="keyword"
        :placeholder="translate('banner.searchPlaceholder')"
        clearable
        class="toolbar-input"
        @clear="handleSearch"
        @keyup.enter="handleSearch"
      >
        <template #prefix>
          <component :is="TinyIconSearch" />
        </template>
      </tiny-input>
      <tiny-select
        v-model="statusFilter"
        class="toolbar-select"
        :placeholder="translate('banner.statusAll')"
        clearable
      >
        <tiny-option :label="translate('banner.statusEnabled')" :value="1" />
        <tiny-option :label="translate('banner.statusDisabled')" :value="0" />
      </tiny-select>
      <tiny-button type="primary" @click="handleSearch">
        {{ translate('common.search') }}
      </tiny-button>
      <tiny-button type="primary" @click="openCreateDialog">
        {{ translate('banner.create') }}
      </tiny-button>
    </div>

    <tiny-grid
      :data="bannerList"
      border
      stripe
      :loading="loading"
      height="100%"
      class="banner-table"
    >
      <tiny-grid-column type="index" width="60" :title="translate('common.index')" />
      <tiny-grid-column field="title" :title="translate('banner.title')" min-width="180" />
      <tiny-grid-column field="description" :title="translate('banner.description')" min-width="220" />
      <tiny-grid-column field="image_url" :title="translate('banner.image')" min-width="220">
        <template #default="{ row }">
          <img v-if="row.image_url" :src="row.image_url" class="banner-image" />
        </template>
      </tiny-grid-column>
      <tiny-grid-column field="link_url" :title="translate('banner.link')" min-width="200" />
      <tiny-grid-column field="created_by_name" :title="translate('common.createdBy')" min-width="120" />
      <tiny-grid-column field="updated_by_name" :title="translate('common.updatedBy')" min-width="120" />
      <tiny-grid-column :title="translate('common.createdAt')" min-width="180">
        <template #default="{ row }">
          {{ formatTime(row.created_at) }}
        </template>
      </tiny-grid-column>
      <tiny-grid-column :title="translate('common.updatedAt')" min-width="180">
        <template #default="{ row }">
          {{ formatTime(row.updated_at) }}
        </template>
      </tiny-grid-column>
      <tiny-grid-column field="status" :title="translate('banner.status')" width="100">
        <template #default="{ row }">
          <tiny-tag :type="row.status === 1 ? 'success' : 'info'">
            {{ row.status === 1 ? translate('banner.statusEnabled') : translate('banner.statusDisabled') }}
          </tiny-tag>
        </template>
      </tiny-grid-column>
      <tiny-grid-column :title="translate('common.actions')" width="200" fixed="right">
        <template #default="{ row }">
          <tiny-button :text="textBtn" size="small" @click="openEditDialog(row)">
            {{ translate('common.edit') }}
          </tiny-button>
          <tiny-button
            :text="textBtn"
            size="small"
            :type="row.status === 1 ? 'warning' : 'success'"
            @click="toggleStatus(row)"
          >
            {{ row.status === 1 ? translate('banner.disable') : translate('banner.enable') }}
          </tiny-button>
        </template>
      </tiny-grid-column>
    </tiny-grid>

    <div class="banner-pager">
      <tiny-pager
        :current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="total, prev, pager, next, sizes"
        @current-change="handlePageChange"
        @size-change="handlePageSizeChange"
      />
    </div>

    <tiny-dialog-box
      v-model:visible="dialogVisible"
      :title="isEdit ? translate('banner.editDialogTitle') : translate('banner.createDialogTitle')"
      width="600px"
    >
      <div class="banner-form">
        <tiny-form ref="formRef" :model="form" label-width="100px">
          <tiny-form-item :label="translate('banner.title')" prop="title">
            <tiny-input v-model="form.title" />
          </tiny-form-item>
          <tiny-form-item :label="translate('banner.description')" prop="description">
            <tiny-input v-model="form.description" type="textarea" :rows="3" />
          </tiny-form-item>
          <tiny-form-item :label="translate('banner.image')" prop="image_url">
            <div class="image-upload-row">
              <tiny-input
                v-model="form.image_url"
                :placeholder="translate('banner.imagePlaceholder')"
                class="image-url-input"
              />
              <tiny-button
                v-if="!form.image_url"
                size="small"
                @click="triggerImageSelect"
              >
                {{ translate('banner.upload') }}
              </tiny-button>
              <tiny-button
                v-else
                size="small"
                @click="triggerImageSelect"
              >
                {{ translate('banner.editCrop') }}
              </tiny-button>
            </div>
            <div v-if="form.image_url" class="image-preview">
              <img :src="form.image_url" alt="banner preview" class="image-preview-img" />
            </div>
            <div class="crop-wrapper" v-if="cropVisible">
              <tiny-crop
                :cropvisible="cropVisible"
                @update:cropvisible="cropVisible = $event"
                v-model="cropResult"
                :src="form.image_url"
                :auto-crop="false"
                :auto-crop-width="1920"
                :auto-crop-height="300"
                :aspect-ratio="64 / 8"
                :can-move="true"
                :center-box="false"
                @cropdata="cropdata"
              />
            </div>
          </tiny-form-item>
          <tiny-form-item :label="translate('banner.link')" prop="link_url">
            <tiny-input v-model="form.link_url" :placeholder="translate('banner.linkPlaceholder')" />
          </tiny-form-item>
          <tiny-form-item :label="translate('banner.status')" prop="status">
            <tiny-switch v-model="form.status" :true-value="1" :false-value="0" />
          </tiny-form-item>
        </tiny-form>
      </div>
      <template #footer>
        <tiny-button @click="dialogVisible = false">
          {{ translate('common.cancel') }}
        </tiny-button>
        <tiny-button type="primary" :loading="saving" @click="handleSave">
          {{ translate('common.save') }}
        </tiny-button>
      </template>
    </tiny-dialog-box>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import {
  Button as TinyButton,
  Input as TinyInput,
  Select as TinySelect,
  Option as TinyOption,
  Grid as TinyGrid,
  GridColumn as TinyGridColumn,
  Pager as TinyPager,
  DialogBox as TinyDialogBox,
  Form as TinyForm,
  FormItem as TinyFormItem,
  Switch as TinySwitch,
  Tag as TinyTag,
  Modal,
  TinyCrop
} from '@opentiny/vue'
import { IconSearch } from '@opentiny/vue-icon'
import { bannerApi, type Banner, type BannerCreate, type BannerUpdate } from '../api/banner'
import { fileApi } from '../api/file'
import { useLocaleStore } from '../stores/locale'
import { t } from '../i18n'

const TinyIconSearch = IconSearch()

// text 按钮样式（OpenTiny 类型定义为 string，实际可接受 boolean）
const textBtn = true as unknown as string

const localeStore = useLocaleStore()
const translate = (key: string, params?: Record<string, string>) => {
  void localeStore.localeKey
  return t(key, params)
}

const formatTime = (time?: string | null) => {
  if (!time) return ''
  const date = new Date(time)
  const localeMap: Record<string, string> = {
    zh: 'zh-CN',
    en: 'en-US',
    ko: 'ko-KR',
    de: 'de-DE',
    ja: 'ja-JP',
    fr: 'fr-FR'
  }
  const locale = localeMap[localeStore.currentLocale] || 'zh-CN'
  return date.toLocaleString(locale)
}

const loading = ref(false)
const saving = ref(false)
const bannerList = ref<Banner[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const keyword = ref('')
const statusFilter = ref<number | null>(null)

const dialogVisible = ref(false)
const isEdit = ref(false)
const currentId = ref<number | null>(null)

const _formRef = ref()
const cropResult = ref<string>('') // 裁剪后的 base64 或原图 url
const form = ref<Omit<BannerCreate, 'sort_order'> & { status: number }>({
  title: '',
  description: '',
  image_url: '',
  link_url: '',
  status: 1
})

const fetchBanners = async () => {
  loading.value = true
  try {
    const res = await bannerApi.getBanners({
      page: page.value,
      page_size: pageSize.value,
      keyword: keyword.value || null,
      status: statusFilter.value
    })
    bannerList.value = res.items
    total.value = res.total
  } catch (e: any) {
    Modal.message({
      message: e?.message || translate('common.loadFailed'),
      status: 'error'
    })
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  page.value = 1
  void fetchBanners()
}

const handlePageChange = (p: number) => {
  page.value = p
  void fetchBanners()
}

const handlePageSizeChange = (size: number) => {
  pageSize.value = size
  page.value = 1
  void fetchBanners()
}

const resetForm = () => {
  form.value = {
    title: '',
    description: '',
    image_url: '',
    link_url: '',
    status: 1
  }
  currentId.value = null
  cropResult.value = ''
}

const openCreateDialog = () => {
  isEdit.value = false
  resetForm()
  dialogVisible.value = true
}

const openEditDialog = (row: Banner) => {
  isEdit.value = true
  currentId.value = row.id
  form.value = {
    title: row.title,
    description: row.description || '',
    image_url: row.image_url,
    link_url: row.link_url || '',
    status: row.status
  }
  cropResult.value = ''
  dialogVisible.value = true
}

const handleSave = async () => {
  if (!form.value.title || !form.value.image_url) {
    Modal.message({
      message: translate('banner.requiredMessage'),
      status: 'warning'
    })
    return
  }
  saving.value = true
  try {
    // 如果有裁剪结果，优先上传裁剪后的图片并更新 image_url
    if (cropResult.value) {
      const file = await dataUrlToFile(cropResult.value, 'banner.png')
      const uploadRes = await fileApi.uploadFile(file)
      form.value.image_url = uploadRes.file_url
    }

    if (isEdit.value && currentId.value != null) {
      const payload: BannerUpdate = {
        title: form.value.title,
        description: form.value.description,
        image_url: form.value.image_url,
        link_url: form.value.link_url,
        status: form.value.status
      }
      await bannerApi.updateBanner(currentId.value, payload)
      Modal.message({ message: translate('common.updateSuccess'), status: 'success' })
    } else {
      await bannerApi.createBanner(form.value)
      Modal.message({ message: translate('common.createSuccess'), status: 'success' })
    }
    dialogVisible.value = false
    void fetchBanners()
  } catch (e: any) {
    Modal.message({
      message: e?.message || translate('common.saveFailed'),
      status: 'error'
    })
  } finally {
    saving.value = false
  }
}

const toggleStatus = async (row: Banner) => {
  try {
    if (row.status === 1) {
      await bannerApi.updateBannerStatus(row.id, 0)
      Modal.message({ message: translate('banner.disableSuccess'), status: 'success' })
    } else {
      await bannerApi.updateBannerStatus(row.id, 1)
      Modal.message({ message: translate('banner.enableSuccess'), status: 'success' })
    }
    void fetchBanners()
  } catch (e: any) {
    Modal.message({
      message: e?.message || translate('common.actionFailed'),
      status: 'error'
    })
  }
}
const cropVisible = ref(false)
const triggerImageSelect = () => {
  cropVisible.value = true
}

const _handleImageFileChange = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (!input.files || input.files.length === 0) return
  const file = input.files[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    form.value.image_url = reader.result as string
    cropResult.value = ''
    cropVisible.value = true
  }
  reader.readAsDataURL(file)
  // 清空 input 值，避免选择同一文件时不触发 change
  input.value = ''
}

// TinyCrop 裁剪完成回调：上传裁剪后的图片，并把返回的 URL 写回表单
const cropdata = async (val: any) => {
  try {
    const dataUrl =
      typeof val === 'string'
        ? val
        : (val && (val.base64 || val.url || val.dataUrl)) || ''
    if (!dataUrl) return

    const file = await dataUrlToFile(dataUrl, 'banner.png')
    const uploadRes = await fileApi.uploadFile(file)
    form.value.image_url = uploadRes.file_url

    // 使用新地址作为预览源，并关闭裁剪弹层
    cropResult.value = ''
    cropVisible.value = false
  } catch (e: any) {
    Modal.message({
      message: e?.message || translate('common.saveFailed'),
      status: 'error'
    })
  }
}

const dataUrlToFile = async (dataUrl: string, filename: string): Promise<File> => {
  const arr = dataUrl.split(',')
  const firstPart = arr[0]
  const secondPart = arr[1]
  if (!firstPart || !secondPart) throw new Error('Invalid data URL')
  const mimeMatch = firstPart.match(/:(.*?);/)
  const mime = mimeMatch ? mimeMatch[1] : 'image/png'
  const bstr = atob(secondPart)
  let n = bstr.length
  const u8arr = new Uint8Array(n)
  while (n--) {
    u8arr[n] = bstr.charCodeAt(n)
  }
  return new File([u8arr], filename, { type: mime })
}

onMounted(() => {
  void fetchBanners()
})
</script>

<style scoped lang="less">
.banner-management {
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  height: 100%;
  box-sizing: border-box;
}

.banner-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.toolbar-input {
  width: 260px;
}

.toolbar-select {
  width: 180px;
}

.banner-table {
  flex: 1;
}

.banner-image {
  width: 120px;
  height: 48px;
  object-fit: cover;
  border-radius: 4px;
}

.banner-pager {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}

.image-upload-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.image-url-input {
  flex: 1;
}

.crop-wrapper {
  margin-top: 8px;
  max-height: 260px;
  overflow: hidden;
}

.image-preview {
  margin-top: 8px;
}

.image-preview-img {
  max-width: 100%;
  max-height: 120px;
  border-radius: 4px;
  object-fit: cover;
  border: 1px solid #e4e7ed;
}
</style>

