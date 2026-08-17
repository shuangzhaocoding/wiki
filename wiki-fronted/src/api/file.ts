import request from './request'

export interface FileUploadResponse {
  file_url: string
  filename: string
  file_type: string
  file_size: number
}

export const fileApi = {
  async uploadFile(file: File, articleId?: number, onProgress?: (progress: number) => void): Promise<FileUploadResponse> {
    const formData = new FormData()
    formData.append('file', file)
    if (articleId) {
      formData.append('article_id', articleId.toString())
    }
    
    const config: any = {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }
    
    // 如果提供了进度回调，添加进度配置
    if (onProgress) {
      config.onUploadProgress = (progressEvent: any) => {
        if (progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(percentCompleted)
        }
      }
    }
    
    return request.post('/files/upload', formData, config)
  },

  /** 删除文件 DELETE /files/{file_id} */
  async deleteFile(fileId: number): Promise<void> {
    return request.delete(`/files/${fileId}`)
  }
}
