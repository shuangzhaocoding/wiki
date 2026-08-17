<template>
  <tiny-drawer
    :visible="visible"
    :title="translate('comment.title')"
    :width="drawerWidth"
    placement="right"
    :z-index="drawerZIndex"
    :custom-class="drawerCustomClass"
    :mask-closable="true"
    :show-footer="false"
    @update:visible="handleVisibleChange"
  >
    <div
      class="comment-drawer-content"
      :class="{
        'comment-drawer-content--compact': isCompactLayout,
        'comment-drawer-content--mobile': isMobileLayout
      }"
    >
      <!-- 评论输入区 -->
      <div class="comment-input-section">
        <div class="input-wrapper">
          <div class="user-avatar">
            <img v-if="currentUserAvatar" :src="currentUserAvatar" alt="avatar" />
            <span v-else class="avatar-placeholder">{{ currentUserInitial }}</span>
          </div>
          <div class="input-container">
            <div class="editor-wrapper">
              <FluentEditorV4
                ref="commentEditorRef"
                v-model="newCommentContent"
                :options="commentEditorOptions"
                :show-floating-scroll-actions="false"
                class="comment-editor"
              />
            </div>
            <div class="input-footer">
              <span class="char-count">{{ plainTextLength }}/1000</span>
              <tiny-button
                type="primary"
                size="small"
                :loading="submitting"
                :disabled="!hasContent"
                @click="handleSubmitComment"
              >
                {{ translate('comment.submit') }}
              </tiny-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 评论列表 -->
      <div class="comment-list-section">
        <LoadingSpinner v-if="loading" :absolute="false" />
        <div v-else-if="comments.length === 0" class="empty-comments">
          <p>{{ translate('comment.empty') }}</p>
        </div>
        <div v-else class="comment-list">
          <div v-for="comment in comments" :key="comment.id" class="comment-item">
            <!-- 主评论 -->
            <div class="comment-main">
              <div class="comment-avatar">
                <img v-if="comment.user_avatar" :src="comment.user_avatar" alt="avatar" />
                <span v-else class="avatar-placeholder">{{ getInitial(comment.user_name) }}</span>
              </div>
              <div class="comment-body">
                <div class="comment-header">
                  <span class="comment-author">{{ comment.user_name || translate('comment.anonymous') }}</span>
                </div>
                <div class="comment-content">
                  <!-- 编辑模式 -->
                  <div v-if="editingCommentId === comment.id" class="edit-mode">
                    <FluentEditorV4
                      ref="editEditorRef"
                      v-model="editingContent"
                      class="comment-editor"
                      :readonly="false"
                      :show-floating-scroll-actions="false"
                    />
                    <div class="edit-actions">
                      <tiny-button size="small" @click="cancelEdit">
                        {{ translate('common.cancel') }}
                      </tiny-button>
                      <tiny-button
                        type="primary"
                        size="small"
                        :loading="submitting"
                        :disabled="!hasEditContent"
                        @click="handleUpdateComment(comment)"
                      >
                        {{ translate('common.confirm') }}
                      </tiny-button>
                    </div>
                  </div>
                  <!-- 预览模式 -->
                  <FluentEditorV4
                    v-else
                    :model-value="comment.comment"
                    :readonly="true"
                    :show-floating-scroll-actions="false"
                    class="comment-preview-editor"
                  />
                </div>
                <div class="comment-footer">
                  <span class="comment-time">{{ comment.create_time }}</span>
                  <button class="reply-btn" @click="handleReply(comment)">
                    {{ translate('comment.reply') }}
                  </button>
                  <div class="comment-actions">
                    <!-- 编辑和删除按钮（仅作者可见） -->
                    <template v-if="isCommentOwner(comment) && editingCommentId !== comment.id">
                      <button 
                        class="action-btn edit-btn" 
                        @click="handleStartEdit(comment)"
                        :title="translate('comment.edit')"
                      >
                        <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                        </svg>
                      </button>
                      <button 
                        class="action-btn delete-btn" 
                        @click="handleDeleteComment(comment)"
                        :title="translate('comment.delete')"
                      >
                        <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M3 6h18"></path>
                          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                        </svg>
                      </button>
                    </template>
                    <button 
                      class="action-btn" 
                      :class="{ active: comment.is_liked }"
                      @click="handleLikeComment(comment)"
                    >
                      <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path>
                      </svg>
                      <span v-if="comment.like_count">{{ comment.like_count }}</span>
                    </button>
                    <button 
                      class="action-btn"
                      :class="{ active: comment.is_disliked }"
                      @click="handleDislikeComment(comment)"
                    >
                      <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h2.67A2.31 2.31 0 0 1 22 4v7a2.31 2.31 0 0 1-2.33 2H17"></path>
                      </svg>
                      <span v-if="comment.dislike_count">{{ comment.dislike_count }}</span>
                    </button>
                  </div>
                </div>

                <!-- 回复输入框 -->
                <div v-if="replyingTo === comment.id" class="reply-input-wrapper">
                  <div class="reply-editor-wrapper">
                    <FluentEditorV4
                      ref="replyEditorRef"
                      v-model="replyContent"
                      placeholder=""
                      :show-floating-scroll-actions="false"
                      class="reply-editor"
                    />
                  </div>
                  <div class="reply-actions">
                    <tiny-button size="small" @click="cancelReply">
                      {{ translate('common.cancel') }}
                    </tiny-button>
                    <tiny-button
                      type="primary"
                      size="small"
                      :loading="submittingReply"
                      :disabled="!hasReplyContent"
                      @click="handleSubmitReply(comment)"
                    >
                      {{ translate('comment.reply') }}
                    </tiny-button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 子评论 -->
            <div v-if="comment.children && comment.children.length > 0" class="comment-replies">
              <div v-for="reply in comment.children" :key="reply.id" class="reply-item">
                <div class="comment-avatar small">
                  <img v-if="reply.user_avatar" :src="reply.user_avatar" alt="avatar" />
                  <span v-else class="avatar-placeholder">{{ getInitial(reply.user_name) }}</span>
                </div>
                <div class="comment-body">
                  <div class="comment-header">
                    <span class="comment-author">{{ reply.user_name || translate('comment.anonymous') }}</span>
                    <span class="reply-to">
                      {{ translate('comment.replyTo') }}
                      <span class="reply-target">{{ getReplyTargetName(comment, reply) }}</span>
                    </span>
                  </div>
                  <div class="comment-content">
                    <!-- 编辑模式 -->
                    <div v-if="editingCommentId === reply.id" class="edit-mode">
                      <FluentEditorV4
                        ref="editEditorRef"
                        v-model="editingContent"
                        :readonly="false"
                        :placeholder="translate('comment.placeholder')"
                        :show-floating-scroll-actions="false"
                        class="comment-editor"
                      />
                      <div class="edit-actions">
                        <tiny-button size="small" @click="cancelEdit">
                          {{ translate('common.cancel') }}
                        </tiny-button>
                        <tiny-button
                          type="primary"
                          size="small"
                          :loading="submitting"
                          :disabled="!hasEditContent"
                          @click="handleUpdateComment(reply)"
                        >
                          {{ translate('common.confirm') }}
                        </tiny-button>
                      </div>
                    </div>
                    <!-- 预览模式 -->
                    <FluentEditorV4
                      v-else
                      :model-value="reply.comment"
                      :readonly="true"
                      :show-floating-scroll-actions="false"
                      class="reply-preview-editor"
                    />
                  </div>
                  <div class="comment-footer">
                    <span class="comment-time">{{ reply.create_time}}</span>
                    <button class="reply-btn" @click="handleReply(comment, reply)">
                      {{ translate('comment.reply') }}
                    </button>
                    <div class="comment-actions">
                      <!-- 编辑和删除按钮（仅作者可见） -->
                      <template v-if="isCommentOwner(reply) && editingCommentId !== reply.id">
                        <button 
                          class="action-btn edit-btn" 
                          @click="handleStartEdit(reply)"
                          :title="translate('comment.edit')"
                        >
                          <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                          </svg>
                        </button>
                        <button 
                          class="action-btn delete-btn" 
                          @click="handleDeleteComment(reply)"
                          :title="translate('comment.delete')"
                        >
                          <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M3 6h18"></path>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                          </svg>
                        </button>
                      </template>
                      <button 
                        class="action-btn"
                        :class="{ active: reply.is_liked }"
                        @click="handleLikeComment(reply)"
                      >
                        <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path>
                        </svg>
                        <span v-if="reply.like_count">{{ reply.like_count }}</span>
                      </button>
                      <button 
                        class="action-btn"
                        :class="{ active: reply.is_disliked }"
                        @click="handleDislikeComment(reply)"
                      >
                        <svg class="icon-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h2.67A2.31 2.31 0 0 1 22 4v7a2.31 2.31 0 0 1-2.33 2H17"></path>
                        </svg>
                        <span v-if="reply.dislike_count">{{ reply.dislike_count }}</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 文件预览弹窗 -->
    <tiny-dialog-box
      v-model:visible="filePreviewVisible"
      :title="previewFileName || '文件预览'"
      :fullscreen="true"
      :z-index="3000"
      :modal-append-to-body="true"
      :append-to-body="true"
      class="file-preview-dialog"
      @close="filePreviewVisible = false"
    >
      <div class="file-preview-content">
        <!-- 图片预览 -->
        <div v-if="previewFileType === 'image'" class="image-preview-container">
          <tiny-image
            :src="previewFileUrl"
            :alt="previewFileName"
            fit="contain"
            :preview-src-list="[previewFileUrl]"
            :z-index="1000"
          />
        </div>
        
        <!-- 视频预览 -->
        <div v-else-if="previewFileType === 'video'" class="video-preview-container">
          <video
            :src="previewFileUrl"
            controls
            style="max-height: calc(100vh - 120px); max-width: 100%;"
          >
            您的浏览器不支持视频播放
          </video>
        </div>
        
        <!-- 其他文件类型 -->
        <div v-else class="other-file-preview">
          <p>该文件类型不支持预览</p>
            <tiny-button type="primary" @click="openPreviewFile">
            下载文件
          </tiny-button>
        </div>
      </div>
    </tiny-dialog-box>
    
    <!-- 图片预览 - 使用自定义 CustomImageViewer 组件 -->
    <CustomImageViewer
      :visible="imagePreviewVisible"
      :url-list="imagePreviewList"
      :start-position="imagePreviewIndex"
      :z-index="3001"
      :close-show="true"
      :arrow-show="true"
      :tool-show="true"
      :show-index="true"
      @close="imagePreviewVisible = false"
      @switch="handleImageSwitch"
    />
  </tiny-drawer>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, computed, onBeforeUnmount } from 'vue'
import { Button as TinyButton, Drawer as TinyDrawer, Modal, DialogBox as TinyDialogBox, Image as TinyImage } from '@opentiny/vue'
import { commentApi, type Comment } from '../api/comment'
import { fileApi } from '../api/file'
import type { Range } from '@opentiny/fluent-editor'
import { useUserStore } from '../stores/user'
import { t } from '../i18n'
import { useLocaleStore } from '../stores/locale'
import { useDrawerResponsive, COMPACT_RICH_TEXT_TOOLBAR } from '../composables/useDrawerResponsive'
import FluentEditorV4 from './FluentEditorV4.vue'
// @ts-ignore
import LoadingSpinner from './LoadingSpinner.vue'
// @ts-ignore
import CustomImageViewer from './CustomImageViewer.vue'
import { openOfficeOnlinePreview } from '../utils/officePreview'

const props = defineProps<{
  visible: boolean
  articleId: number | null
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'comment-added'): void
}>()

const localeStore = useLocaleStore()
const {
  isCompactLayout,
  isMobileLayout,
  drawerWidth,
  drawerZIndex,
  drawerBodyClass
} = useDrawerResponsive()
const drawerCustomClass = drawerBodyClass('comment-drawer')

// 响应式翻译函数
const translate = (key: string, params?: Record<string, string>) => {
  void localeStore.localeKey
  return t(key, params)
}

// 评论编辑器配置 - 使用 options 方式，与文章管理页面保持一致
const commentEditorOptionsBase = ref({
  placeholder: translate('comment.placeholder'),
  theme: 'snow',
  readonly: false,
  modules: {
    toolbar: [
      [
        "undo",
        "redo",
        "clean",
        "format-painter"
      ],
      [
        {
          "header": [
            1,
            2,
            3,
            4,
            5,
            6,
            false
          ]
        },
        {
          "font": [
            false,
            "仿宋_GB2312, 仿宋",
            "楷体",
            "隶书",
            "黑体",
            "无效字体, 隶书"
          ]
        },
        {
          "size": [
            false,
            "12px",
            "14px",
            "16px",
            "18px",
            "20px",
            "24px",
            "32px",
            "36px",
            "48px",
            "72px"
          ]
        },
        {
          "line-height": [
            false,
            "1.2",
            "1.5",
            "1.75",
            "2",
            "3",
            "4",
            "5"
          ]
        }
      ],
      [
        "bold",
        "italic",
        "strike",
        "underline",
        "divider"
      ],
      [
        {
          "color": []
        },
        {
          "background": []
        }
      ],
      [
        {
          "align": ""
        },
        {
          "align": "center"
        },
        {
          "align": "right"
        },
        {
          "align": "justify"
        }
      ],
      [
        {
          "list": "ordered"
        },
        {
          "list": "bullet"
        },
        {
          "list": "check"
        }
      ],
      [
        {
          "script": "sub"
        },
        {
          "script": "super"
        }
      ],
      [
        {
          "indent": "-1"
        },
        {
          "indent": "+1"
        }
      ],
      [
        {
          "direction": "rtl"
        }
      ],
      [
        "link",
        "blockquote",
        "code",
        "code-block"
      ],
      ['better-table'],
      [
        "image",
        "file",
        "video",
        "fullscreen"
      ]
    ],
    file: true,
    uploader: {
      mimetypes: [
        'image/*', 
        'video/*', 
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation', // .pptx
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // .xlsx
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // .docx
        'application/zip',
        'application/x-zip-compressed',
        'application/x-zip',
        'application/octet-stream', // 通用二进制文件（包括 zip、rar 等）
        'application/x-rar-compressed',
        'application/x-7z-compressed',
        'application/x-tar',
        'application/gzip',
      ],
      maxSize: 500 * 1024 * 1024, // 500MB
      async handler(range: Range, files: File[]) {
        const Delta = (this as any).quill.constructor.import('delta')
        const results: (string | false)[] = []
        
        // 处理每个文件
        await Promise.all(files.map(async (file, index) => {
          try {
            // 上传文件（评论不需要 articleId）
            const response = await fileApi.uploadFile(file)
            let fileUrl = response.file_url
            // 构建完整的文件 URL
            if (!fileUrl.startsWith('http://') && !fileUrl.startsWith('https://')) {
              // 如果是相对路径，拼接完整的 URL
              const baseUrl = window.location.origin
              fileUrl = fileUrl.startsWith('/') ? `${baseUrl}${fileUrl}` : `${baseUrl}/${fileUrl}`
            }
            const fileType = response.file_type || file.type
            const fileName = response.filename || file.name
            
            // 根据文件类型生成预览内容
            let previewContent = ''
            if (fileType.toLowerCase().endsWith('.jpg') || 
                fileType.toLowerCase().endsWith('.png') || 
                fileType.toLowerCase().endsWith('.gif') || 
                fileType.toLowerCase().endsWith('.bmp') || 
                fileType.toLowerCase().endsWith('.webp') || 
                fileType.toLowerCase().endsWith('.svg') || 
                fileType.toLowerCase().endsWith('.jpeg')) {
              previewContent = `<img src="${fileUrl}" alt="${fileName}" style="max-width: 100%; display: block; margin: 10px 0;" />`
            } else if (fileType.toLowerCase().endsWith('.mp4') || 
                fileType.toLowerCase().endsWith('.webm') || 
                fileType.toLowerCase().endsWith('.ogg') || 
                fileType.toLowerCase().endsWith('.mov') || 
                fileType.toLowerCase().endsWith('.avi') || 
                fileType.toLowerCase().endsWith('.wmv') || 
                fileType.toLowerCase().endsWith('.flv') || 
                fileType.toLowerCase().endsWith('.mkv')) {
              previewContent = `<video src="${fileUrl}" class="my-video" controls style="max-width: 100%; display: block; margin: 10px 0;" />`
            } else if (fileName.toLowerCase().endsWith('.pptx')) {
              // PPTX：提供下载或预览链接
              previewContent = `<div id="pptx-preview-container" style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 4px; background-color: #f9f9f9;"><p style="margin: 0 0 10px 0;"><strong>📊 ${fileName}</strong></p>
              <p style="margin: 10px 0 0 0;"><a href="${fileUrl}" class="ql-normal-link" target="_blank" style="color: #1890ff; text-decoration: none;">⬇️ 点击下载或预览</a></p></div>`
            } else if (fileName.toLowerCase().endsWith('.xlsx')) {
              // XLSX：提供下载或预览链接
              previewContent = `<div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 4px; background-color: #f9f9f9;">
              <p style="margin: 0 0 10px 0;"><strong>📊 ${fileName}</strong></p><p style="margin: 10px 0 0 0;"><a href="${fileUrl}" tiile="${fileName}" class="ql-normal-link" target="_blank" style="color: #1890ff; text-decoration: none;">⬇️ 点击下载或预览${fileName}</a></p></div>`
            } else if (fileName.toLowerCase().endsWith('.docx')) {
              // DOCX：提供下载或预览链接
              previewContent = `<div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 4px; background-color: #f9f9f9;">
              <p style="margin: 0 0 10px 0;"><strong>📄 ${fileName}</strong></p>
              <p style="margin: 10px 0 0 0;">
              <a id="download-link" href="${fileUrl}" class="ql-normal-link" target="_blank" style="color: #1890ff; text-decoration: none;">⬇️ 点击下载或预览</a></p></div>`
            } else if (fileName.toLowerCase().endsWith('.pdf')) {
              // PDF：提供下载或预览链接
              previewContent = `<div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 4px; background-color: #f9f9f9;"><p style="margin: 0 0 10px 0;"><strong>📕 ${fileName}</strong></p><p style="margin: 10px 0 0 0;"><a href="${fileUrl}" class="ql-normal-link" target="_blank" style="color: #1890ff; text-decoration: none;">⬇️ 点击下载或预览</a></p></div>`
            } else if (fileName.toLowerCase().endsWith('.zip')) {
              // ZIP：提供下载链接
              previewContent = `<div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 4px; background-color: #f9f9f9;"><p style="margin: 0 0 10px 0;"><strong>📦 ${fileName}</strong></p><p style="margin: 0;"><a href="${fileUrl}" class="ql-normal-link" target="_blank" style="color: #1890ff; text-decoration: none;">⬇️ 点击下载或预览</a></p></div>`
            } else {
              // 其他文件：提供下载链接
              previewContent = `<div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 4px; background-color: #f9f9f9;"><p style="margin: 0 0 10px 0;"><strong>📎 ${fileName}</strong></p><p style="margin: 0;"><a href="${fileUrl}" class="ql-normal-link" target="_blank" style="color: #1890ff; text-decoration: none;">⬇️ 点击下载或预览</a></p></div>`
            }
            
            // 插入预览内容到编辑器
            if (previewContent && (this as any).quill && range) {
              const delta = new Delta()
                .retain(range.index)
                .delete(1) // 删除占位符
              ;(this as any).quill.updateContents(delta)
              ;(this as any).quill.clipboard.dangerouslyPasteHTML(range.index, previewContent)
            }
            
            results[index] = fileUrl
          } catch (error) {
            console.error('文件上传失败:', error)
            Modal.message({
              message: `文件 ${file.name} 上传失败: ${error instanceof Error ? error.message : '未知错误'}`,
              status: 'error'
            })
            results[index] = false
          }
        }))
        
        return results
      },
      success(file: File, range: Range) {
        console.log('文件上传成功:', file.name)
      },
      fail(file: File, range: Range) {
        console.error('文件上传失败:', file.name)
        Modal.message({
          message: `文件 ${file.name} 上传失败`,
          status: 'error'
        })
      }
    },
    // 表格
    'better-table': {
      operationMenu: {
        color: {
          text: '主题色',
          colors: [
            '#ffffff',
            '#f2f2f2',
            '#dddddd',
            '#a6a6a6',
            '#666666',
            '#000000',
            '#c00000',
            '#ff0000',
            '#ffc8d3',
            '#ffc000',
            '#ffff00',
            '#fff4cb',
            '#92d050',
            '#00b050',
            '#dff3d2',
            '#00b0f0',
            '#0070c0',
            '#d4f1f5',
            '#002060',
            '#7030a0',
            '#7b69ee',
            '#1476ff',
            '#ec66ab',
            '#42b883'
          ]
        }
      }
    }
  }
})

const commentEditorOptions = computed(() => {
  const base = commentEditorOptionsBase.value
  if (!isCompactLayout.value) return base
  return {
    ...base,
    modules: {
      ...base.modules,
      toolbar: [...COMPACT_RICH_TEXT_TOOLBAR]
    }
  }
})

// 回复编辑器配置 - 使用 options 方式，与文章管理页面保持一致
const replyEditorOptionsBase = ref({
  placeholder: translate('comment.placeholder'),
  theme: 'snow',
  readonly: false,
  modules: {
    toolbar: [
      [
        "undo",
        "redo",
        "clean",
        "format-painter"
      ],
      [
        {
          "header": [
            1,
            2,
            3,
            4,
            5,
            6,
            false
          ]
        },
        {
          "font": [
            false,
            "仿宋_GB2312, 仿宋",
            "楷体",
            "隶书",
            "黑体",
            "无效字体, 隶书"
          ]
        },
        {
          "size": [
            false,
            "12px",
            "14px",
            "16px",
            "18px",
            "20px",
            "24px",
            "32px",
            "36px",
            "48px",
            "72px"
          ]
        },
        {
          "line-height": [
            false,
            "1.2",
            "1.5",
            "1.75",
            "2",
            "3",
            "4",
            "5"
          ]
        }
      ],
      [
        "bold",
        "italic",
        "strike",
        "underline",
        "divider"
      ],
      [
        {
          "color": []
        },
        {
          "background": []
        }
      ],
      [
        {
          "align": ""
        },
        {
          "align": "center"
        },
        {
          "align": "right"
        },
        {
          "align": "justify"
        }
      ],
      [
        {
          "list": "ordered"
        },
        {
          "list": "bullet"
        },
        {
          "list": "check"
        }
      ],
      [
        {
          "script": "sub"
        },
        {
          "script": "super"
        }
      ],
      [
        {
          "indent": "-1"
        },
        {
          "indent": "+1"
        }
      ],
      [
        {
          "direction": "rtl"
        }
      ],
      [
        "link",
        "blockquote",
        "code",
        "code-block"
      ],
      ['better-table'],
      [
        "image",
        "file",
        "video",
        "fullscreen"
      ]
    ],
    file: true,
    uploader: {
      mimetypes: [
        'image/*', 
        'video/*', 
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation', // .pptx
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // .xlsx
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // .docx
        'application/zip',
        'application/x-zip-compressed',
        'application/x-zip',
        'application/octet-stream', // 通用二进制文件（包括 zip、rar 等）
        'application/x-rar-compressed',
        'application/x-7z-compressed',
        'application/x-tar',
        'application/gzip',
      ],
      maxSize: 500 * 1024 * 1024, // 500MB
      async handler(range: Range, files: File[]) {
        const Delta = (this as any).quill.constructor.import('delta')
        const results: (string | false)[] = []
        
        // 处理每个文件
        await Promise.all(files.map(async (file, index) => {
          try {
            // 上传文件（回复不需要 articleId）
            const response = await fileApi.uploadFile(file)
            let fileUrl = response.file_url
            // 构建完整的文件 URL
            if (!fileUrl.startsWith('http://') && !fileUrl.startsWith('https://')) {
              // 如果是相对路径，拼接完整的 URL
              const baseUrl = window.location.origin
              fileUrl = fileUrl.startsWith('/') ? `${baseUrl}${fileUrl}` : `${baseUrl}/${fileUrl}`
            }
            const fileType = response.file_type || file.type
            const fileName = response.filename || file.name
            
            // 根据文件类型生成预览内容
            let previewContent = ''
            if (fileType.toLowerCase().endsWith('.jpg') || 
                fileType.toLowerCase().endsWith('.png') || 
                fileType.toLowerCase().endsWith('.gif') || 
                fileType.toLowerCase().endsWith('.bmp') || 
                fileType.toLowerCase().endsWith('.webp') || 
                fileType.toLowerCase().endsWith('.svg') || 
                fileType.toLowerCase().endsWith('.jpeg')) {
              previewContent = `<img src="${fileUrl}" alt="${fileName}" style="max-width: 100%; display: block; margin: 10px 0;" />`
            } else if (fileType.toLowerCase().endsWith('.mp4') || 
                fileType.toLowerCase().endsWith('.webm') || 
                fileType.toLowerCase().endsWith('.ogg') || 
                fileType.toLowerCase().endsWith('.mov') || 
                fileType.toLowerCase().endsWith('.avi') || 
                fileType.toLowerCase().endsWith('.wmv') || 
                fileType.toLowerCase().endsWith('.flv') || 
                fileType.toLowerCase().endsWith('.mkv')) {
              previewContent = `<video src="${fileUrl}" class="my-video" controls style="max-width: 100%; display: block; margin: 10px 0;" />`
            } else if (fileName.toLowerCase().endsWith('.pptx')) {
              // PPTX：提供下载或预览链接
              previewContent = `<div id="pptx-preview-container" style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 4px; background-color: #f9f9f9;"><p style="margin: 0 0 10px 0;"><strong>📊 ${fileName}</strong></p>
              <p style="margin: 10px 0 0 0;"><a href="${fileUrl}" class="ql-normal-link" target="_blank" style="color: #1890ff; text-decoration: none;">⬇️ 点击下载或预览</a></p></div>`
            } else if (fileName.toLowerCase().endsWith('.xlsx')) {
              // XLSX：提供下载或预览链接
              previewContent = `<div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 4px; background-color: #f9f9f9;">
              <p style="margin: 0 0 10px 0;"><strong>📊 ${fileName}</strong></p><p style="margin: 10px 0 0 0;"><a href="${fileUrl}" class="ql-normal-link" target="_blank" style="color: #1890ff; text-decoration: none;">⬇️ 点击下载或预览</a></p></div>`
            } else if (fileName.toLowerCase().endsWith('.docx')) {
              // DOCX：提供下载或预览链接
              previewContent = `<div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 4px; background-color: #f9f9f9;"><p style="margin: 0 0 10px 0;"><strong>📄 ${fileName}</strong></p><p style="margin: 10px 0 0 0;"><a href="${fileUrl}" class="ql-normal-link" target="_blank" style="color: #1890ff; text-decoration: none;">⬇️ 点击下载或预览</a></p></div>`
            } else if (fileName.toLowerCase().endsWith('.pdf')) {
              // PDF：提供下载或预览链接
              previewContent = `<div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 4px; background-color: #f9f9f9;"><p style="margin: 0 0 10px 0;"><strong>📕 ${fileName}</strong></p><p style="margin: 10px 0 0 0;"><a href="${fileUrl}" class="ql-normal-link" target="_blank" style="color: #1890ff; text-decoration: none;">⬇️ 点击下载或预览</a></p></div>`
            } else if (fileName.toLowerCase().endsWith('.zip')) {
              // ZIP：提供下载链接
              previewContent = `<div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 4px; background-color: #f9f9f9;"><p style="margin: 0 0 10px 0;"><strong>📦 ${fileName}</strong></p><p style="margin: 0;"><a href="${fileUrl}" class="ql-normal-link" target="_blank" style="color: #1890ff; text-decoration: none;">⬇️ 点击下载或预览</a></p></div>`
            } else {
              // 其他文件：提供下载链接
              previewContent = `<div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 4px; background-color: #f9f9f9;"><p style="margin: 0 0 10px 0;"><strong>📎 ${fileName}</strong></p><p style="margin: 0;"><a href="${fileUrl}" class="ql-normal-link" target="_blank" style="color: #1890ff; text-decoration: none;">⬇️ 点击下载或预览</a></p></div>`
            }
            
            // 插入预览内容到编辑器
            if (previewContent && (this as any).quill && range) {
              const delta = new Delta()
                .retain(range.index)
                .delete(1) // 删除占位符
              ;(this as any).quill.updateContents(delta)
              ;(this as any).quill.clipboard.dangerouslyPasteHTML(range.index, previewContent)
            }
            
            results[index] = fileUrl
          } catch (error) {
            console.error('文件上传失败:', error)
            Modal.message({
              message: `文件 ${file.name} 上传失败: ${error instanceof Error ? error.message : '未知错误'}`,
              status: 'error'
            })
            results[index] = false
          }
        }))
        
        return results
      },
      success(file: File, range: Range) {
        console.log('文件上传成功:', file.name)
      },
      fail(file: File, range: Range) {
        console.error('文件上传失败:', file.name)
        Modal.message({
          message: `文件 ${file.name} 上传失败`,
          status: 'error'
        })
      }
    },
    // 表格
    'better-table': {
      operationMenu: {
        color: {
          text: '主题色',
          colors: [
            '#ffffff',
            '#f2f2f2',
            '#dddddd',
            '#a6a6a6',
            '#666666',
            '#000000',
            '#c00000',
            '#ff0000',
            '#ffc8d3',
            '#ffc000',
            '#ffff00',
            '#fff4cb',
            '#92d050',
            '#00b050',
            '#dff3d2',
            '#00b0f0',
            '#0070c0',
            '#d4f1f5',
            '#002060',
            '#7030a0',
            '#7b69ee',
            '#1476ff',
            '#ec66ab',
            '#42b883'
          ]
        }
      }
    }
  }
})

const replyEditorOptions = computed(() => {
  const base = replyEditorOptionsBase.value
  if (!isCompactLayout.value) return base
  return {
    ...base,
    modules: {
      ...base.modules,
      toolbar: [...COMPACT_RICH_TEXT_TOOLBAR]
    }
  }
})

// 编辑模式 FluentEditor 使用的 modules/toolbar（与 commentEditorOptions 保持一致）
const commentEditorModules = computed(() => ({
  toolbar: (commentEditorOptions.value as any).modules?.toolbar ?? []
}))
const commentEditorToolbar = computed(() => (commentEditorOptions.value as any).modules?.toolbar ?? [])

// 状态
const loading = ref(false)
const submitting = ref(false)
const submittingReply = ref(false)
const comments = ref<Comment[]>([])
const newCommentContent = ref('')
const replyingTo = ref<number | null>(null)
const replyContent = ref('')
const replyTargetUser = ref<string>('')
const editingCommentId = ref<number | null>(null)
const editingContent = ref('')
const editEditorRef = ref()

// 编辑器引用
const commentEditorRef = ref()
const replyEditorRef = ref()

// 文件预览相关状态
const filePreviewVisible = ref(false)
const previewFileUrl = ref('')
const previewFileName = ref('')
const previewFileType = ref('')

// 图片预览相关状态
const imagePreviewVisible = ref(false)
const imagePreviewList = ref<string[]>([])
const imagePreviewIndex = ref(0)

// 视频双击全屏相关
let videoDoubleClickObserver: MutationObserver | null = null
let imageDoubleClickObserver: MutationObserver | null = null
let fileLinkClickObserver: MutationObserver | null = null

// 计算纯文本长度
const plainTextLength = computed(() => {
  if (!newCommentContent.value) return 0
  // 移除 HTML 标签计算纯文本长度
  const tempDiv = document.createElement('div')
  tempDiv.innerHTML = newCommentContent.value
  return tempDiv.textContent?.length || 0
})

// 判断是否有内容
const hasContent = computed(() => {
  if (!newCommentContent.value) return false
  const tempDiv = document.createElement('div')
  tempDiv.innerHTML = newCommentContent.value
  const text = tempDiv.textContent?.trim() || ''
  return text.length > 0
})

// 判断回复是否有内容
const hasReplyContent = computed(() => {
  if (!replyContent.value) return false
  const tempDiv = document.createElement('div')
  tempDiv.innerHTML = replyContent.value
  const text = tempDiv.textContent?.trim() || ''
  return text.length > 0
})

// 判断编辑内容是否有内容
const hasEditContent = computed(() => {
  if (!editingContent.value) return false
  const tempDiv = document.createElement('div')
  tempDiv.innerHTML = editingContent.value
  const text = tempDiv.textContent?.trim() || ''
  return text.length > 0
})

// 使用用户 store
const userStore = useUserStore()

// 当前用户信息（从 store 获取）
const currentUserAvatar = computed(() => userStore.currentUserAvatar)
const currentUserInitial = computed(() => {
  const username = userStore.currentUsername
  return getInitial(username)
})

// 在浏览器新窗口打开预览文件
const openPreviewFile = () => {
  if (previewFileUrl.value) window.open(previewFileUrl.value, '_blank')
}

// 判断是否是评论作者（使用 store 的方法）
const isCommentOwner = (comment: Comment) => {
  return userStore.isCommentOwner(comment.user_id)
}

// 获取用户名首字母
const getInitial = (name?: string): string => {
  if (!name) return 'U'
  return name.charAt(0).toUpperCase()
}

// 获取回复目标用户名
const getReplyTargetName = (parentComment: Comment, reply: Comment): string => {
  // 如果回复的 parent_id 等于主评论的 id，则是直接回复主评论
  if (reply.parent_id === parentComment.id) {
    return parentComment.user_name || translate('comment.anonymous')
  }
  // 否则查找是回复哪条子评论
  const targetReply = parentComment.children?.find(c => c.id === reply.parent_id)
  return targetReply?.user_name || parentComment.user_name || translate('comment.anonymous')
}

// 格式化时间
const formatTime = (dateStr?: string): string => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return translate('comment.justNow')
  if (minutes < 60) return translate('comment.minutesAgo', { minutes: String(minutes) })
  if (hours < 24) return translate('comment.hoursAgo', { hours: String(hours) })
  if (days < 30) return translate('comment.daysAgo', { days: String(days) })
  
  return date.toLocaleDateString()
}

// 加载评论
const loadComments = async () => {
  if (!props.articleId) return
  
  loading.value = true
  try {
    comments.value = await commentApi.getArticleComments(props.articleId)
  } catch (error) {
    console.error('加载评论失败:', error)
    comments.value = []
  } finally {
    loading.value = false
  }
}

// 提交评论
const handleSubmitComment = async () => {
  if (!props.articleId || !hasContent.value || submitting.value) return
  
  submitting.value = true
  try {
    await commentApi.createComment({
      article_id: props.articleId,
      content: newCommentContent.value
    })
    newCommentContent.value = ''
    await nextTick()
    if (commentEditorRef.value?.quill) {
      commentEditorRef.value.quill.setContents([])
    }
    await loadComments()
    emit('comment-added')
  } catch (error) {
    console.error('提交评论失败:', error)
  } finally {
    submitting.value = false
  }
}

// 点击回复按钮
const handleReply = (comment: Comment, reply?: Comment) => {
  // 如果是回复子评论，使用子评论的父 ID（即主评论 ID），但记录目标用户
  replyingTo.value = comment.id
  replyTargetUser.value = reply ? (reply.user_name || '') : (comment.user_name || '')
  replyContent.value = ''
  
  nextTick(() => {
    if (replyEditorRef.value?.quill) {
      replyEditorRef.value.quill.focus()
    }
  })
}

// 取消回复
const cancelReply = () => {
  replyingTo.value = null
  replyContent.value = ''
  replyTargetUser.value = ''
}

// 提交回复
const handleSubmitReply = async (parentComment: Comment) => {
  if (!props.articleId || !hasReplyContent.value || submittingReply.value) return
  
  submittingReply.value = true
  try {
    await commentApi.createComment({
      article_id: props.articleId,
      parent_id: parentComment.id,
      content: replyContent.value
    })
    if (replyEditorRef.value?.quill) {
      replyEditorRef.value.quill.setContents([])
    }
    replyContent.value = ''
    replyingTo.value = null
    replyTargetUser.value = ''
    await loadComments()
    emit('comment-added')
  } catch (error) {
    console.error('提交回复失败:', error)
  } finally {
    submittingReply.value = false
  }
}

// 开始编辑评论
const handleStartEdit = (comment: Comment) => {
  editingCommentId.value = comment.id
  editingContent.value = comment.comment
  
  nextTick(() => {
    if (editEditorRef.value?.quill) {
      editEditorRef.value.quill.focus()
    }
  })
}

// 取消编辑
const cancelEdit = () => {
  editingCommentId.value = null
  editingContent.value = ''
}

// 更新评论
const handleUpdateComment = async (comment: Comment) => {
  if (!hasEditContent.value || submitting.value) return
  
  submitting.value = true
  try {
    await commentApi.updateComment(comment.id, {
      content: editingContent.value
    })
    editingCommentId.value = null
    editingContent.value = ''
    await loadComments()
    emit('comment-added')
  } catch (error: any) {
    console.error('更新评论失败:', error)
    Modal.message({
      message: error.message || translate('comment.updateError'),
      status: 'error'
    })
  } finally {
    submitting.value = false
  }
}

// 删除评论
const handleDeleteComment = (comment: Comment) => {
  Modal.confirm({
    title: translate('comment.deleteConfirm'),
    message: translate('comment.deleteMessage'),
    status: 'warning'
  }).then(async (result) => {
    if (result === 'confirm') {
      try {
      await commentApi.deleteComment(comment.id)
      await loadComments()
      emit('comment-added')
      Modal.message({
        message: translate('comment.deleteSuccess'),
        status: 'success'
      })
    } catch (error: any) {
      console.error('删除评论失败:', error)
      Modal.message({
        message: error.message || translate('comment.deleteError'),
        status: 'error'
      })
    }
    }
    
  }).catch(() => {
    // 用户取消
  })
}

// 查找并更新评论（包括子评论）
const updateCommentInList = (commentId: number, updater: (comment: Comment) => void) => {
  // 在主评论中查找
  const mainComment = comments.value.find(c => c.id === commentId)
  if (mainComment) {
    updater(mainComment)
    return
  }
  
  // 在子评论中查找
  for (const mainComment of comments.value) {
    if (mainComment.children) {
      const childComment = mainComment.children.find(c => c.id === commentId)
      if (childComment) {
        updater(childComment)
        return
      }
    }
  }
}

// 点赞评论
const handleLikeComment = async (comment: Comment) => {
  try {
    await commentApi.likeComment(comment.id)
    
    // 更新本地状态
    updateCommentInList(comment.id, (c) => {
      if (c.is_liked) {
        // 如果已经点赞，取消点赞
        c.is_liked = false
        c.like_count = Math.max((c.like_count || 0) - 1, 0)
      } else {
        // 如果未点赞，进行点赞
        c.is_liked = true
        c.like_count = (c.like_count || 0) + 1
        
        // 如果之前踩过，取消踩
        if (c.is_disliked) {
          c.is_disliked = false
          c.dislike_count = Math.max((c.dislike_count || 0) - 1, 0)
        }
      }
    })
  } catch (error: any) {
    console.error('点赞评论失败:', error)
    Modal.message({
      message: error.message || translate('comment.likeError'),
      status: 'error'
    })
  }
}

// 踩评论
const handleDislikeComment = async (comment: Comment) => {
  try {
    await commentApi.dislikeComment(comment.id)
    
    // 更新本地状态
    updateCommentInList(comment.id, (c) => {
      if (c.is_disliked) {
        // 如果已经踩过，取消踩
        c.is_disliked = false
        c.dislike_count = Math.max((c.dislike_count || 0) - 1, 0)
      } else {
        // 如果未踩过，进行踩
        c.is_disliked = true
        c.dislike_count = (c.dislike_count || 0) + 1
        
        // 如果之前点赞过，取消点赞
        if (c.is_liked) {
          c.is_liked = false
          c.like_count = Math.max((c.like_count || 0) - 1, 0)
        }
      }
    })
  } catch (error: any) {
    console.error('踩评论失败:', error)
    Modal.message({
      message: error.message || translate('comment.dislikeError'),
      status: 'error'
    })
  }
}

// 处理抽屉显示状态变化
const handleVisibleChange = (val: boolean) => {
  emit('update:visible', val)
}

// 判断是否为图片文件
const isImageFile = (filename: string): boolean => {
  const imageTypes = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg']
  const ext = filename.toLowerCase().split('.').pop() || ''
  return imageTypes.includes(ext)
}

// 判断是否为视频文件
const isVideoFile = (filename: string): boolean => {
  const videoTypes = ['mp4', 'webm', 'ogg', 'mov', 'avi', 'wmv', 'flv', 'mkv']
  const ext = filename.toLowerCase().split('.').pop() || ''
  return videoTypes.includes(ext)
}

// 从文件名获取文件类型
const getFileTypeFromName = (fileName: string): string => {
  const ext = fileName.toLowerCase().split('.').pop() || ''
  if (['pptx', 'ppt'].includes(ext)) return 'pptx'
  if (['xlsx', 'xls'].includes(ext)) return 'xlsx'
  if (['docx', 'doc'].includes(ext)) return 'docx'
  if (ext === 'pdf') return 'pdf'
  if (isImageFile(fileName)) return 'image'
  if (isVideoFile(fileName)) return 'video'
  return 'other'
}

// 从 URL 中获取文件类型
const getFileTypeFromUrl = (fileUrl: string): string => {
  try {
    const urlObj = new URL(fileUrl)
    
    // 优先从 URL 路径中提取扩展名
    const pathParts = urlObj.pathname.split('/')
    const urlFileName = pathParts[pathParts.length - 1]
    if (urlFileName && urlFileName.includes('.')) {
      const ext = urlFileName.toLowerCase().split('.').pop() || ''
      if (['pptx', 'ppt'].includes(ext)) return 'pptx'
      if (['xlsx', 'xls'].includes(ext)) return 'xlsx'
      if (['docx', 'doc'].includes(ext)) return 'docx'
      if (ext === 'pdf') return 'pdf'
      if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg'].includes(ext)) return 'image'
      if (['mp4', 'webm', 'ogg', 'mov', 'avi', 'wmv', 'flv', 'mkv'].includes(ext)) return 'video'
    }
    
    // 如果路径中没有扩展名，尝试从查询参数中获取
    const filenameParam = urlObj.searchParams.get('filename') || 
                         urlObj.searchParams.get('file') || 
                         urlObj.searchParams.get('name')
    if (filenameParam && filenameParam.includes('.')) {
      const ext = filenameParam.toLowerCase().split('.').pop() || ''
      if (['pptx', 'ppt'].includes(ext)) return 'pptx'
      if (['xlsx', 'xls'].includes(ext)) return 'xlsx'
      if (['docx', 'doc'].includes(ext)) return 'docx'
      if (ext === 'pdf') return 'pdf'
      if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg'].includes(ext)) return 'image'
      if (['mp4', 'webm', 'ogg', 'mov', 'avi', 'wmv', 'flv', 'mkv'].includes(ext)) return 'video'
    }
    
    // 尝试从 Content-Type 响应头判断（如果 URL 包含类型信息）
    const contentType = urlObj.searchParams.get('content_type') || urlObj.searchParams.get('type')
    if (contentType) {
      if (contentType.includes('presentation')) return 'pptx'
      if (contentType.includes('spreadsheet')) return 'xlsx'
      if (contentType.includes('wordprocessing') || contentType.includes('document')) return 'docx'
      if (contentType.includes('pdf')) return 'pdf'
      if (contentType.startsWith('image/')) return 'image'
      if (contentType.startsWith('video/')) return 'video'
    }
  } catch (e) {
    console.warn('无法从 URL 解析文件类型:', e)
  }
  
  return 'other'
}

// 处理文件链接点击事件
const handleFileLinkClick = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  
  // 检查是否是符合条件的链接
  if (target.tagName === 'A' && target.classList.contains('ql-normal-link')) {
    const linkText = target.textContent || ''
    if (linkText.includes('点击下载或预览')) {
      event.preventDefault()
      event.stopPropagation()
      
      // 获取链接的 href
      const fileUrl = (target as HTMLAnchorElement).href
      if (!fileUrl) return
      
      // 从 fileUrl 中提取文件名和文件类型
      let fileName = '文件'
      let fileType = 'other'
      
      try {
        const urlObj = new URL(fileUrl)
        
        // 优先从 URL 路径中提取文件名
        const pathParts = urlObj.pathname.split('/')
        const urlFileName = pathParts[pathParts.length - 1]
        if (urlFileName && urlFileName.includes('.')) {
          fileName = decodeURIComponent(urlFileName)
        } else {
          // 如果路径中没有文件名，尝试从查询参数中获取
          const filenameParam = urlObj.searchParams.get('filename') || 
                               urlObj.searchParams.get('file') || 
                               urlObj.searchParams.get('name')
          if (filenameParam && filenameParam.includes('.')) {
            fileName = decodeURIComponent(filenameParam)
          } else {
            // 如果还是没有，尝试从 strong 标签中获取（作为备用）
            const parentDiv = target.closest('div')
            if (parentDiv) {
              const fileNameElement = parentDiv.querySelector('strong')
              const textFileName = fileNameElement?.textContent?.trim() || ''
              // 移除 emoji
              const cleanedText = textFileName.replace(/^[\u{1F300}-\u{1F9FF}\s]+/u, '').trim()
              if (cleanedText && cleanedText.includes('.')) {
                fileName = cleanedText
              }
            }
          }
        }
        
        // 直接从 URL 中获取文件类型
        fileType = getFileTypeFromUrl(fileUrl)
        
      } catch (e) {
        console.warn('无法从 URL 解析文件名:', e)
        // 如果 URL 解析失败，尝试从 strong 标签中获取（作为备用）
        const parentDiv = target.closest('div')
        if (parentDiv) {
          const fileNameElement = parentDiv.querySelector('strong')
          const textFileName = fileNameElement?.textContent?.trim() || ''
          // 移除 emoji
          const cleanedText = textFileName.replace(/^[\u{1F300}-\u{1F9FF}\s]+/u, '').trim()
          if (cleanedText && cleanedText.includes('.')) {
            fileName = cleanedText
            // 如果从 HTML 中获取了文件名，使用文件名判断类型
            fileType = getFileTypeFromName(fileName)
          }
        }
      }
      
      console.log('文件预览信息:', {
        fileName,
        fileUrl,
        fileType,
        extension: fileName.toLowerCase().split('.').pop()
      })
      
      if (openOfficeOnlinePreview(fileUrl, fileName, fileType)) {
        return
      }

      previewFileUrl.value = fileUrl
      previewFileName.value = fileName
      previewFileType.value = fileType
      filePreviewVisible.value = true
    }
  }
}

// 处理图片双击事件
const handleImageDoubleClick = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  
  // 查找 img 元素
  let img: HTMLImageElement | null = null
  
  if (target.tagName === 'IMG') {
    img = target as HTMLImageElement
  } else {
    const imgElement = target.closest('img')
    if (imgElement) {
      img = imgElement as HTMLImageElement
    }
  }
  
  if (img && img.src) {
    // 收集所有评论和回复中的图片
    const allImages: HTMLImageElement[] = []
    const drawerContent = document.querySelector('.comment-drawer-content')
    if (drawerContent) {
      const images = drawerContent.querySelectorAll('img')
      images.forEach((image: HTMLImageElement) => {
        const src = image.src || image.getAttribute('src')
        if (src) {
          allImages.push(image)
        }
      })
    }
    
    if (allImages.length > 0) {
      const imageSrcList = allImages.map(img => img.src || img.getAttribute('src') || '').filter(Boolean)
      const currentSrc = img.src || img.getAttribute('src')
      const currentIndex = imageSrcList.findIndex(src => src === currentSrc)
      const validIndex = currentIndex >= 0 && currentIndex < imageSrcList.length ? currentIndex : 0
      
      imagePreviewList.value = imageSrcList
      imagePreviewIndex.value = validIndex
      imagePreviewVisible.value = true
    }
  }
}

// 处理图片切换
const handleImageSwitch = (index: number) => {
  if (index >= 0 && index < imagePreviewList.value.length) {
    imagePreviewIndex.value = index
  }
}

// 处理视频双击事件
const handleVideoDoubleClick = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  let video: HTMLVideoElement | null = null
  
  if (target.tagName === 'VIDEO') {
    video = target as HTMLVideoElement
  } else {
    const videoElement = target.closest('video')
    if (videoElement) {
      video = videoElement as HTMLVideoElement
    }
  }
  
  if (video) {
    // 检查当前是否处于全屏状态
    const isFullscreen = !!(
      document.fullscreenElement ||
      (document as any).webkitFullscreenElement ||
      (document as any).mozFullScreenElement ||
      (document as any).msFullscreenElement
    )

    if (isFullscreen) {
      // 如果已全屏，则退出全屏
      if (document.exitFullscreen) {
        document.exitFullscreen().catch((err) => {
          console.error('退出全屏失败:', err)
        })
      } else if ((document as any).webkitExitFullscreen) {
        ;(document as any).webkitExitFullscreen()
      } else if ((document as any).mozCancelFullScreen) {
        ;(document as any).mozCancelFullScreen()
      } else if ((document as any).msExitFullscreen) {
        ;(document as any).msExitFullscreen()
      }
    } else {
      // 如果未全屏，则进入全屏
      if (video.requestFullscreen) {
        video.requestFullscreen().catch((err) => {
          console.error('全屏失败:', err)
        })
      } else if ((video as any).webkitRequestFullscreen) {
        ;(video as any).webkitRequestFullscreen()
      } else if ((video as any).mozRequestFullScreen) {
        ;(video as any).mozRequestFullScreen()
      } else if ((video as any).msRequestFullscreen) {
        ;(video as any).msRequestFullscreen()
      }
    }
  }
}

// 设置文件链接点击监听器
const setupFileLinkClickListeners = () => {
  const drawerContent = document.querySelector('.comment-drawer-content')
  if (!drawerContent) return
  
  // 使用事件委托监听链接点击
  const attachLinkListeners = () => {
    drawerContent.removeEventListener('click', handleFileLinkClick as EventListener)
    drawerContent.addEventListener('click', handleFileLinkClick as EventListener)
  }
  
  // 初始添加监听器
  setTimeout(() => {
    attachLinkListeners()
  }, 500)
  
  // 使用 MutationObserver 监听新插入的内容
  if (fileLinkClickObserver) {
    fileLinkClickObserver.disconnect()
  }
  
  fileLinkClickObserver = new MutationObserver(() => {
    setTimeout(() => {
      attachLinkListeners()
    }, 100)
  })
  
  fileLinkClickObserver.observe(drawerContent, {
    childList: true,
    subtree: true,
  })
}

// 设置图片双击监听器
const setupImageDoubleClickListeners = () => {
  const drawerContent = document.querySelector('.comment-drawer-content')
  if (!drawerContent) return
  
  const attachImageListeners = () => {
    const images = drawerContent.querySelectorAll('img')
    images.forEach((image: HTMLImageElement) => {
      image.removeEventListener('dblclick', handleImageDoubleClick)
      image.addEventListener('dblclick', handleImageDoubleClick)
    })
  }
  
  setTimeout(() => {
    attachImageListeners()
  }, 500)
  
  if (imageDoubleClickObserver) {
    imageDoubleClickObserver.disconnect()
  }
  
  imageDoubleClickObserver = new MutationObserver((mutations) => {
    let hasNewImage = false
    mutations.forEach((mutation) => {
      mutation.addedNodes.forEach((node) => {
        if (node.nodeType === 1) {
          const element = node as HTMLElement
          if (element.tagName === 'IMG' || element.querySelector('img')) {
            hasNewImage = true
          }
        }
      })
    })
    if (hasNewImage) {
      setTimeout(() => {
        attachImageListeners()
      }, 100)
    }
  })
  
  imageDoubleClickObserver.observe(drawerContent, {
    childList: true,
    subtree: true,
  })
}

// 设置视频双击监听器
const setupVideoDoubleClickListeners = () => {
  const drawerContent = document.querySelector('.comment-drawer-content')
  if (!drawerContent) return
  
  const attachVideoListeners = () => {
    const videos = drawerContent.querySelectorAll('video')
    videos.forEach((video: HTMLVideoElement) => {
      video.removeEventListener('dblclick', handleVideoDoubleClick)
      video.addEventListener('dblclick', handleVideoDoubleClick)
    })
  }
  
  setTimeout(() => {
    attachVideoListeners()
  }, 500)
  
  if (videoDoubleClickObserver) {
    videoDoubleClickObserver.disconnect()
  }
  
  videoDoubleClickObserver = new MutationObserver((mutations) => {
    let hasNewVideo = false
    mutations.forEach((mutation) => {
      mutation.addedNodes.forEach((node) => {
        if (node.nodeType === 1) {
          const element = node as HTMLElement
          if (element.tagName === 'VIDEO' || element.querySelector('video')) {
            hasNewVideo = true
          }
        }
      })
    })
    if (hasNewVideo) {
      setTimeout(() => {
        attachVideoListeners()
      }, 100)
    }
  })
  
  videoDoubleClickObserver.observe(drawerContent, {
    childList: true,
    subtree: true,
  })
}

// 监听 visible 变化，加载评论
watch(() => props.visible, async (newVal) => {
  if (newVal && props.articleId) {
    await loadComments()
    // 聚焦编辑器
    nextTick(() => {
      setTimeout(() => {
        if (commentEditorRef.value?.quill) {
          commentEditorRef.value.quill.focus()
        }
        // 设置监听器
        setupFileLinkClickListeners()
        setupImageDoubleClickListeners()
        setupVideoDoubleClickListeners()
      }, 300)
    })
  } else {
    // 关闭时重置状态
    cancelReply()
    newCommentContent.value = ''
    if (commentEditorRef.value?.quill) {
      commentEditorRef.value.quill.setContents([])
    }
    // 清理监听器
    if (fileLinkClickObserver) {
      fileLinkClickObserver.disconnect()
      fileLinkClickObserver = null
    }
    if (imageDoubleClickObserver) {
      imageDoubleClickObserver.disconnect()
      imageDoubleClickObserver = null
    }
    if (videoDoubleClickObserver) {
      videoDoubleClickObserver.disconnect()
      videoDoubleClickObserver = null
    }
  }
}, { immediate: true })

// 监听 articleId 变化
watch(() => props.articleId, async (newVal) => {
  if (props.visible && newVal) {
    await loadComments()
  }
})

// 用户信息已在应用初始化时获取，这里不需要再次获取

// 组件卸载时清理监听器
onBeforeUnmount(() => {
  if (fileLinkClickObserver) {
    fileLinkClickObserver.disconnect()
    fileLinkClickObserver = null
  }
  if (imageDoubleClickObserver) {
    imageDoubleClickObserver.disconnect()
    imageDoubleClickObserver = null
  }
  if (videoDoubleClickObserver) {
    videoDoubleClickObserver.disconnect()
    videoDoubleClickObserver = null
  }
})
</script>

<style scoped lang="less">
.comment-drawer-content {
  display: flex;
  flex-direction: column;
  min-height: min-content;
}

// 评论输入区
.comment-input-section {
  position: sticky;
  top: 0;
  z-index: 2;
  padding: 16px;
  margin-bottom: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 12px;
  flex-shrink: 0;
  background: var(--ti-base-color-bg-1, #fff);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
}

.input-wrapper {
  display: flex;
  gap: 12px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  background: linear-gradient(135deg, #8b5cf6, #a78bfa);
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
    font-size: 16px;
    font-weight: 600;
  }
}

.input-container {
  flex: 1;
  min-width: 0;
}

.editor-wrapper {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
  transition: border-color 0.2s;
  
  &:focus-within {
    border-color: var(--primary-color, #8b5cf6);
  }
}

.comment-editor {
  :deep(.ql-toolbar) {
    border: none !important;
    border-bottom: 1px solid #e4e7ed !important;
    padding: 6px 8px !important;
    background: #fafafa;
    
    .ql-formats {
      margin-right: 8px;
    }
    
    button {
      width: 26px;
      height: 26px;
      padding: 3px;
      outline: none;
      
      &:focus,
      &:active {
        outline: none;
        box-shadow: none;
      }
    }
  }
  
  :deep(.ql-container) {
    border: none !important;
    font-size: 14px;
  }
  
  :deep(.ql-editor) {
    min-height: 80px;
    padding: 10px 12px;
    overflow-y: visible;
    
    &.ql-blank::before {
      color: #999;
      font-style: normal;
      left: 12px;
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

// 评论列表区
.comment-list-section {
  flex: 0 0 auto;
  padding: 16px 0;
}

.empty-comments {
  text-align: center;
  padding: 60px 20px;
  color: #999;
  font-size: 14px;
}

.comment-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.comment-item {
  padding-bottom: 16px;
  
  &:last-child {
    border-bottom: none;
  }
}

.comment-main {
  display: flex;
  gap: 12px;
}

.comment-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  background: linear-gradient(135deg, #64748b, #94a3b8);
  display: flex;
  align-items: center;
  justify-content: center;
  
  &.small {
    width: 32px;
    height: 32px;
    
    .avatar-placeholder {
      font-size: 12px;
    }
  }
  
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

.comment-body {
  flex: 1;
  min-width: 0;
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  flex-wrap: wrap;
}

.comment-author {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.reply-to {
  font-size: 12px;
  color: #999;
}

.reply-target {
  color: var(--primary-color, #8b5cf6);
}

.comment-content {
  font-size: 14px;
  line-height: 1.6;
  color: #333;
  word-break: break-word;
  text-align: left;
}

// 编辑模式
.edit-mode {
  .comment-editor {
    margin-bottom: 12px;
  }
  
  .edit-actions {
    display: flex;
    gap: 8px;
    justify-content: flex-end;
    margin-top: 8px;
  }
}

// 评论内容预览编辑器样式
.comment-preview-editor,
.reply-preview-editor {
  // 移除所有边框和背景
  border: none !important;
  box-shadow: none !important;
  outline: none !important;
  background: transparent !important;
  
  :deep(*) {
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
  }
  
  :deep(.ql-toolbar) {
    display: none !important;
  }
  
  :deep(.ql-container) {
    border: none !important;
    font-size: 14px;
    background: transparent !important;
    text-align: left !important;
  }
  
  :deep(.tiny-fluent-editor),
  :deep([class*="fluent-editor"]),
  :deep([class*="FluentEditor"]) {
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
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
    
    p {
      margin: 0 0 8px 0;
      text-align: left;
      
      &:last-child {
        margin-bottom: 0;
      }
    }
    
    ul, ol {
      margin: 8px 0;
      padding-left: 20px;
      text-align: left;
    }
    
    li {
      margin: 4px 0;
      text-align: left;
    }
    
    a {
      color: var(--primary-color, #8b5cf6);
      text-decoration: none;
      
      &:hover {
        text-decoration: underline;
      }
    }
    
    strong, b {
      font-weight: 600;
    }
    
    em, i {
      font-style: italic;
    }
    
    u {
      text-decoration: underline;
    }
  }
}

.reply-preview-editor {
  :deep(.ql-editor) {
    font-size: 13px;
  }
}

.comment-footer {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 8px;
}

.comment-time {
  font-size: 12px;
  color: #999;
}

.reply-btn {
  font-size: 12px;
  color: #666;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  outline: none;
  
  &:hover {
    color: var(--primary-color, #8b5cf6);
  }
  
  &:focus,
  &:active {
    outline: none;
    box-shadow: none;
  }
}

.comment-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: auto;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #999;
  background: none;
  border: none;
  cursor: pointer;
  padding: 2px 6px;
  border-radius: 4px;
  transition: all 0.2s;
  outline: none;
  
  &:focus,
  &:active {
    outline: none;
    box-shadow: none;
  }
  
  &.edit-btn {
    &:hover {
      color: #1890ff;
      background: #e6f7ff;
    }
  }
  
  &.delete-btn {
    &:hover {
      color: #f56c6c;
      background: #fef0f0;
    }
  }
  
  &:hover {
    background: #f5f5f5;
    color: #666;
  }
  
  &.active {
    color: var(--primary-color, #8b5cf6);
    
    .icon-svg {
      stroke: var(--primary-color, #8b5cf6);
    }
  }
  
  :deep(svg) {
    width: 14px;
    height: 14px;
  }
  
  .icon-svg {
    width: 14px;
    height: 14px;
    stroke: currentColor;
  }
}

// 回复输入框
.reply-input-wrapper {
  margin-top: 12px;
  padding: 12px;
  background: #f9f9f9;
  border-radius: 8px;
}

.reply-editor-wrapper {
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  overflow: hidden;
  background: #fff;
  
  &:focus-within {
    border-color: var(--primary-color, #8b5cf6);
  }
}

// 文件预览弹窗样式
.file-preview-dialog {
  z-index: 3000 !important;
  
  :deep(.tiny-dialog-box__body) {
    padding: 0;
    height: 100%;
    overflow: hidden;
  }
  
  :deep(.tiny-dialog-box__wrapper) {
    z-index: 3000 !important;
  }
  
  :deep(.tiny-dialog-box__mask) {
    z-index: 2999 !important;
  }
}

.file-preview-content {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  
  .image-preview-container,
  .video-preview-container,
  .office-preview-wrapper,
  .excel-preview-wrapper, .pptx-preview-wrapper {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .other-file-preview {
    text-align: center;
    padding: 40px;
    
    p {
      margin-bottom: 20px;
      color: #666;
      font-size: 16px;
    }
  }
}

.reply-editor {
  :deep(.ql-toolbar) {
    border: none !important;
    border-bottom: 1px solid #e4e7ed !important;
    padding: 4px 6px !important;
    background: #fafafa;
    
    .ql-formats {
      margin-right: 6px;
    }
    
    button {
      width: 24px;
      height: 24px;
      padding: 2px;
      outline: none;
      
      &:focus,
      &:active {
        outline: none;
        box-shadow: none;
      }
    }
  }
  
  :deep(.ql-container) {
    border: none !important;
    font-size: 13px;
  }
  
  :deep(.ql-editor) {
    min-height: 60px;
    padding: 8px 10px;
    overflow-y: visible;
    
    &.ql-blank::before {
      color: #999;
      font-style: normal;
      left: 10px;
    }
  }
}

.reply-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
}

// 子评论
.comment-replies {
  margin-left: 52px;
  margin-top: 12px;
  padding-left: 12px;
  border-left: 2px solid #f0f0f0;
}

.reply-item {
  display: flex;
  gap: 10px;
  padding: 10px 0;
  
  &:first-child {
    padding-top: 0;
  }
  
  .comment-content {
    font-size: 13px;
  }
  
  .comment-footer {
    margin-top: 6px;
  }
}

// 响应式
@media (max-width: 768px) {
  .comment-replies {
    margin-left: 32px;
  }
}

// OpenTiny Drawer 样式覆盖
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
    overflow-x: hidden;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
  }
}

.comment-drawer-content.comment-drawer-content--compact {
  .comment-input-section {
    padding: 12px;
    margin-bottom: 8px;
  }

  .input-wrapper {
    flex-direction: column;
    gap: 10px;
  }

  .user-avatar {
    width: 32px;
    height: 32px;
  }

  .comment-editor :deep(.ql-toolbar) {
    flex-wrap: wrap;
    max-height: 88px;
    overflow-x: auto;
    overflow-y: hidden;
    -webkit-overflow-scrolling: touch;
  }

  .comment-footer {
    flex-wrap: wrap;
    gap: 8px;
  }

  .comment-actions {
    flex-wrap: wrap;
    margin-left: 0;
    width: 100%;
    justify-content: flex-start;
  }

  .comment-replies {
    margin-left: 20px;
    padding-left: 8px;
  }
}

.comment-drawer-content.comment-drawer-content--mobile {
  .comment-input-section {
    border-radius: 10px;
  }

  .input-footer {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;

    .tiny-button {
      width: 100%;
    }
  }

  .reply-actions {
    flex-direction: column;
    align-items: stretch;

    .tiny-button {
      width: 100%;
    }
  }
}
</style>

<style lang="less">
/* 抽屉主体 class 由 custom-class 挂在 tiny-drawer-main */
.tiny-drawer-main.comment-drawer--mobile {
  width: 100% !important;
  max-width: 100% !important;
}

.tiny-drawer-main.comment-drawer--compact,
.tiny-drawer-main.comment-drawer--mobile {
  .tiny-drawer__header {
    padding-top: calc(12px + env(safe-area-inset-top, 0px));
    padding-left: calc(16px + env(safe-area-inset-left, 0px));
    padding-right: calc(16px + env(safe-area-inset-right, 0px));
  }

  .tiny-drawer__body {
    padding-left: calc(12px + env(safe-area-inset-left, 0px));
    padding-right: calc(12px + env(safe-area-inset-right, 0px));
    padding-bottom: calc(16px + env(safe-area-inset-bottom, 0px));
    height: calc(100% - 56px - env(safe-area-inset-top, 0px));
  }

  .tiny-drawer__close-btn {
    width: 36px;
    height: 36px;
  }
}
</style>
