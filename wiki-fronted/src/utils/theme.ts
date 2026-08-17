// 主题管理
export type Theme = 'purple' | 'blue' | 'green' | 'orange'

interface ThemeConfig {
  name: string
  primaryColor: string
  gradient: string
}

const themes: Record<Theme, ThemeConfig> = {
  purple: {
    name: '紫色',
    primaryColor: '#8b5cf6',
    gradient: 'linear-gradient(135deg, #8b5cf6 0%, #7c3aed 50%, #6d28d9 100%)'
  },
  blue: {
    name: '蓝色',
    primaryColor: '#409eff',
    gradient: 'linear-gradient(135deg, #409eff 0%, #337ecc 50%, #2666a3 100%)'
  },
  green: {
    name: '绿色',
    primaryColor: '#67c23a',
    gradient: 'linear-gradient(135deg, #67c23a 0%, #529b2e 50%, #3d7422 100%)'
  },
  orange: {
    name: '橙色',
    primaryColor: '#e6a23c',
    gradient: 'linear-gradient(135deg, #e6a23c 0%, #c6891a 50%, #a6700f 100%)'
  }
}

const THEME_KEY = 'wiki_theme'

// 获取当前主题
export const getTheme = (): Theme => {
  const saved = localStorage.getItem(THEME_KEY) as Theme
  return saved || 'purple'
}

// 设置主题
export const setTheme = (theme: Theme) => {
  localStorage.setItem(THEME_KEY, theme)
  applyTheme(theme)
}

// 应用主题
export const applyTheme = (theme: Theme) => {
  const themeConfig = themes[theme]
  const root = document.documentElement
  
  // 设置 CSS 变量
  root.style.setProperty('--primary-color', themeConfig.primaryColor)
  root.style.setProperty('--primary-gradient', themeConfig.gradient)
  
  // 更新 meta theme-color（移动端浏览器）
  const metaThemeColor = document.querySelector('meta[name="theme-color"]')
  if (metaThemeColor) {
    metaThemeColor.setAttribute('content', themeConfig.primaryColor)
  } else {
    const meta = document.createElement('meta')
    meta.name = 'theme-color'
    meta.content = themeConfig.primaryColor
    document.head.appendChild(meta)
  }
}

// 获取主题配置
export const getThemeConfig = (theme?: Theme): ThemeConfig => {
  const currentTheme = theme || getTheme()
  return themes[currentTheme]
}

// 获取所有主题
export const getAllThemes = (): Array<{ value: Theme; label: string }> => {
  return Object.keys(themes).map(key => ({
    value: key as Theme,
    label: themes[key as Theme].name
  }))
}

// 初始化主题
export const initTheme = () => {
  const theme = getTheme()
  applyTheme(theme)
}
