const OFFICE_PREVIEW_ORIGIN = 'https://office-preview-online.yugongcoding.com'

const OFFICE_EXT_TO_RESOURCE_TYPE: Record<string, string> = {
  pptx: 'pptx',
  ppt: 'pptx',
  xlsx: 'xlsx',
  xls: 'xlsx',
  docx: 'docx',
  doc: 'docx',
  pdf: 'pdf',
}

function toAbsoluteFileUrl(fileUrl: string): string {
  const raw = (fileUrl || '').trim()
  if (!raw) return raw
  if (/^https?:\/\//i.test(raw)) return raw
  if (typeof window === 'undefined') return raw
  try {
    return new URL(raw, window.location.origin).href
  } catch {
    return raw
  }
}

export function getOfficePreviewResourceType(
  fileName: string,
  fileType?: string | null
): string | null {
  const ext = (fileName || '').toLowerCase().split('.').pop() || ''
  if (OFFICE_EXT_TO_RESOURCE_TYPE[ext]) {
    return OFFICE_EXT_TO_RESOURCE_TYPE[ext]
  }
  const mime = (fileType || '').toLowerCase()
  if (mime.includes('presentation')) return 'pptx'
  if (mime.includes('spreadsheet') || mime.includes('excel')) return 'xlsx'
  if (mime.includes('wordprocessing') || mime.includes('msword')) return 'docx'
  if (mime.includes('pdf')) return 'pdf'
  return null
}

export function buildOfficePreviewUrl(fileUrl: string, resourceType: string): string {
  const params = new URLSearchParams({
    url: toAbsoluteFileUrl(fileUrl),
    resource_type: resourceType,
  })
  return `${OFFICE_PREVIEW_ORIGIN}/?${params.toString()}`
}

/** Office 文档打开在线预览页；非 Office 返回 false。 */
export function openOfficeOnlinePreview(
  fileUrl: string,
  fileName: string,
  fileType?: string | null
): boolean {
  const resourceType = getOfficePreviewResourceType(fileName, fileType)
  if (!resourceType || !fileUrl) return false
  window.open(buildOfficePreviewUrl(fileUrl, resourceType), '_blank', 'noopener,noreferrer')
  return true
}
