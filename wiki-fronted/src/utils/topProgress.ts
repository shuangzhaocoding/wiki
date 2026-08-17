/**
 * 顶部资源加载进度条。
 * 首屏由 index.html 内联脚本启动；Vue 挂载后接管同一 DOM，
 * 并在路由懒加载、脚本/样式资源、接口请求时继续显示。
 */

const ROOT_ID = 'wiki-top-progress'
const BAR_CLASS = 'wiki-top-progress-bar'
const MAX_TRICKLE = 92

type ProgressWindow = Window & {
  __wikiTopProgress?: {
    set: (n: number) => void
    start: () => void
    done: () => void
  }
  __wikiTopProgressBootstrap?: { stop: () => void }
}

let current = 0
let visible = false
let trickleTimer: number | null = null
let hideTimer: number | null = null
let initialLoading = false
let navigating = false
let pendingRequests = 0
let routeGeneration = 0

function isBusy(): boolean {
  return initialLoading || navigating || pendingRequests > 0
}

function getRoot(): HTMLElement | null {
  return document.getElementById(ROOT_ID)
}

function getBar(): HTMLElement | null {
  return document.querySelector(`#${ROOT_ID} .${BAR_CLASS}`)
}

function ensureDom(): { root: HTMLElement; bar: HTMLElement } | null {
  if (typeof document === 'undefined') return null
  let root = getRoot()
  if (!root) {
    root = document.createElement('div')
    root.id = ROOT_ID
    root.setAttribute('aria-hidden', 'true')
    const bar = document.createElement('div')
    bar.className = BAR_CLASS
    root.appendChild(bar)
    document.body.appendChild(root)
  }
  const bar = getBar()
  if (!bar) return null
  return { root, bar }
}

function clamp(n: number): number {
  return Math.max(0, Math.min(100, n))
}

function paint(n: number) {
  const el = ensureDom()
  if (!el) return
  current = clamp(n)
  el.bar.style.width = `${current}%`
  if (current > 0 && current < 100) {
    el.root.classList.add('is-active')
    el.root.classList.remove('is-done')
    visible = true
  }
}

function startTrickle() {
  if (trickleTimer != null) return
  trickleTimer = window.setInterval(() => {
    if (current >= MAX_TRICKLE) return
    const remain = MAX_TRICKLE - current
    const step = remain * (0.04 + Math.random() * 0.08)
    paint(current + Math.max(0.4, step))
  }, 320)
}

function stopTrickle() {
  if (trickleTimer != null) {
    window.clearInterval(trickleTimer)
    trickleTimer = null
  }
}

function showBar() {
  const el = ensureDom()
  if (!el) return
  if (hideTimer != null) {
    window.clearTimeout(hideTimer)
    hideTimer = null
  }
  el.root.classList.remove('is-done')
  el.root.classList.add('is-active')
  if (!visible || current >= 100) {
    paint(current > 0 && current < 100 ? current : 12)
  }
  visible = true
  startTrickle()
}

function finishBar() {
  const el = ensureDom()
  if (!el) return
  stopTrickle()
  paint(100)
  hideTimer = window.setTimeout(() => {
    el.root.classList.add('is-done')
    el.root.classList.remove('is-active')
    window.setTimeout(() => {
      current = 0
      el.bar.style.width = '0%'
      visible = false
    }, 240)
  }, 180)
}

function maybeFinish() {
  if (isBusy()) return
  finishBar()
}

export function startTopProgress() {
  navigating = true
  routeGeneration += 1
  showBar()
}

export function incTopProgress(amount = 8) {
  if (!visible) return
  paint(Math.min(MAX_TRICKLE, current + amount))
}

export function setTopProgress(n: number) {
  paint(Math.min(MAX_TRICKLE, n))
}

export function doneTopProgress() {
  const generation = routeGeneration
  window.setTimeout(() => {
    if (generation !== routeGeneration) return
    navigating = false
    maybeFinish()
  }, 120)
}

export function startRequestProgress() {
  pendingRequests += 1
  showBar()
}

export function doneRequestProgress() {
  pendingRequests = Math.max(0, pendingRequests - 1)
  maybeFinish()
}

function isAssetResource(entry: PerformanceResourceTiming): boolean {
  const type = entry.initiatorType
  if (type === 'script' || type === 'link' || type === 'css' || type === 'font') return true
  const name = entry.name || ''
  return /\.(js|mjs|css|woff2?|ttf|otf)(\?|$)/i.test(name)
}

function estimateLoadedRatio(): number {
  const nav = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming | undefined
  const resources = performance.getEntriesByType('resource') as PerformanceResourceTiming[]
  const assets = resources.filter(isAssetResource)
  const total = assets.length + (nav ? 1 : 0)
  if (total === 0) return document.readyState === 'complete' ? 1 : 0.15
  let doneCount = nav && nav.loadEventEnd > 0 ? 1 : 0
  for (const item of assets) {
    if (item.responseEnd > 0) doneCount += 1
  }
  return doneCount / Math.max(total, 1)
}

function syncFromPerformance() {
  if (!isBusy()) return
  const ratio = estimateLoadedRatio()
  const mapped = 12 + ratio * 78
  if (mapped > current) setTopProgress(mapped)
}

export function installTopProgress() {
  const w = window as ProgressWindow
  w.__wikiTopProgressBootstrap?.stop()
  w.__wikiTopProgress = {
    set: setTopProgress,
    start: startTopProgress,
    done: doneTopProgress
  }

  const el = ensureDom()
  if (el) {
    const fromDom = parseFloat(el.bar.style.width)
    if (!Number.isNaN(fromDom) && fromDom > current) {
      current = fromDom
      visible = true
    }
  }

  initialLoading = true
  showBar()
  syncFromPerformance()

  if (typeof PerformanceObserver !== 'undefined') {
    try {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries() as PerformanceResourceTiming[]
        if (!entries.some(isAssetResource)) return
        incTopProgress(4)
        syncFromPerformance()
      })
      observer.observe({ type: 'resource', buffered: true })
    } catch {
      // 部分环境不支持 resource timing
    }
  }

  const finishInitial = () => {
    syncFromPerformance()
    window.setTimeout(() => {
      initialLoading = false
      maybeFinish()
    }, 80)
  }

  if (document.readyState === 'complete') {
    finishInitial()
  } else {
    window.addEventListener('load', finishInitial, { once: true })
  }
}
