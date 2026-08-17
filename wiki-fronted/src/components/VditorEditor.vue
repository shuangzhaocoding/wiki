<template>
  <div id="vditor" ref="vditorRef"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import Vditor from 'vditor'
import 'vditor/dist/index.css'

const vditorRef = ref<HTMLElement | null>(null)
let vditorInstance: Vditor | null = null

// 暴露 vditorInstance 供父组件使用
defineExpose({
  vditorInstance
})

onMounted(() => {
  if (vditorRef.value) {
    vditorInstance = new Vditor('vditor', {
      cache: {
        enable: false,
      },
      upload: {
        accept: 'image/*,.mp3, .wav, .rar, .pptx, .xlsx, .docx, .pdf',
        handler: (files: File[]) => {
          // 本地文件处理，不上传到服务器
          if (!files || files.length === 0) {
            return JSON.stringify({
              msg: '未选择文件',
              code: 1,
              data: {
                errFiles: [],
                succMap: {}
              }
            })
          }

          // 为所有文件创建本地预览 URL 并生成预览内容
          const previewContents: string[] = []
          
          files.forEach((file) => {
            const url = URL.createObjectURL(file)
            const fileType = file.type || ''
            const fileName = file.name
            
            if (fileType.indexOf('image/') === 0) {
              // 图片：使用 HTML img 标签确保预览显示
              previewContents.push(`\n<img src="${url}" alt="${fileName}" style="max-width: 100%; display: block; margin: 10px 0;" />\n`)
            } else if (fileType.indexOf('video/') === 0) {
              // 视频：使用 HTML video 标签预览
              previewContents.push(`\n<video controls width="100%" style="max-width: 800px; display: block; margin: 10px 0;">\n  <source src="${url}" type="${fileType}">\n  您的浏览器不支持视频播放。\n</video>\n`)
            } else if (fileName.toLowerCase().indexOf('.pptx') === fileName.length - 5) {
              // PPTX：提供下载链接和预览提示
              previewContents.push(`\n<div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 4px; background-color: #f9f9f9;">\n  <p style="margin: 0 0 10px 0;"><strong>📊 ${fileName}</strong></p>\n  <p style="margin: 0;"><a href="${url}" download="${fileName}" style="color: #1890ff; text-decoration: none;">⬇️ 点击下载文件</a></p>\n  <p style="margin: 10px 0 0 0; color: #999; font-size: 12px;">提示：PPTX 文件需要下载后在本地打开预览</p>\n</div>\n`)
            } else {
              // 其他文件：提供下载链接
              previewContents.push(`\n[📎 ${fileName}](${url})\n`)
            }
          })
          
          // 延迟插入预览内容，确保 Vditor 处理完上传响应
          if (previewContents.length > 0) {
            const content = previewContents.join('\n\n')
            setTimeout(() => {
              if (vditorInstance) {
                vditorInstance.insertValue(content)
              }
            }, 100)
          }
          
          // 返回空结果，因为我们手动插入内容
          return JSON.stringify({
            msg: '上传成功',
            code: 0,
            data: {
              errFiles: [],
              succMap: {}
            }
          })
        },
        filename(name) {
          return name
            .replace(/[^(a-zA-Z0-9\u4e00-\u9fa5\.)]/g, '')
            .replace(/[\?\\/:|<>\*\[\]\(\)\$%\{\}@~]/g, '')
            .replace(/\s/g, '')
        },
      },
      height: 360,
      typewriterMode: true,
    })
  }
})

onBeforeUnmount(() => {
  if (vditorInstance) {
    vditorInstance.destroy()
    vditorInstance = null
  }
})
</script>

<style scoped lang="less">
#vditor {
  width: 100%;
}
</style>
