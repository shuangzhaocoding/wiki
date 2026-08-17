/// <reference types="vite/client" />

/** Globals attached at runtime for Fluent Editor / plugins */
interface Window {
  Html2Canvas?: typeof import('html2canvas').default
  /** Default export; `any` avoids KaTeX UMD `export as namespace` vs default mismatch */
  katex?: any
}

declare module 'quill-markdown-shortcuts' {
  import type { default as Quill } from 'quill'
  const MarkdownShortcuts: any
  export default MarkdownShortcuts
}

declare module 'simple-mind-map/src/plugins/Drag.js' {
  const Drag: any
  export default Drag
}

declare module 'simple-mind-map/src/plugins/Export.js' {
  const ExportPlugin: any
  export default ExportPlugin
}

declare module 'simple-mind-map-plugin-themes' {
  const Themes: any
  export default Themes
}

declare module 'simple-mind-map/src/svg/icons' {
  const nodeIconList: any
  export default nodeIconList
}

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<Record<string, any>, Record<string, any>, any>
  export default component
}

/* Asset URL modules: provided by vite/client — do not redeclare *.png etc. here (duplicate `src`) */

declare module '@opentiny/vue-icon' {
  import type { Component } from 'vue'
  
  // 导出所有图标函数
  export function IconPlusSquare(): Component
  export function IconPlus(): Component
  export function IconCheck(): Component
  export function IconClose(): Component
  export function IconChevronLeft(): Component
  export function IconChevronRight(): Component
  export function IconZoomIn(): Component
  export function IconZoomOut(): Component
  export function IconRefresh(): Component
  export function IconYes(): Component
  export function IconClose(): Component
  export function IconEdit(): Component
  export function IconPencil(): Component
  export function IconChevronRight(): Component
  export function IconChevronLeft(): Component
  export function IconUser(): Component
  export function IconMail(): Component
  export function IconSearch(): Component
  export function IconStarActive(): Component
  export function IconStarO(): Component
  export function IconHeartempty(): Component
  export function IconMessageCircle(): Component
  export function IconFeedback(): Component
  export function IconListMode(): Component
  export function IconPublicNotice(): Component
  export function IconEllipsis(): Component
  export function IconOperation(): Component
  export function IconMore(): Component
  export function IconDel(): Component
  export function IconChevronUp(): Component
  export function IconChevronDown(): Component
  export function IconAdd(): Component
  export function IconConmentRefresh(): Component
  export function IconRefres(): Component
  export function IconRepeat(): Component
  // 支持任意图标名称（使用 any 类型以支持所有图标）
  const iconModule: {
    [key: string]: () => Component
  }
  export default iconModule
}
