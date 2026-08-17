<template>
  <div class="daily-stats-page">
    <div class="content-header">
      <h1 class="content-title">{{ translate('personalCenter.dailyStats') }}</h1>
      <div class="date-range-wrap">
        <tiny-date-picker
          v-model="dateRange"
          type="daterange"
          value-format="yyyy-MM-dd"
          :start-placeholder="translate('personalCenter.statsStartDate')"
          :end-placeholder="translate('personalCenter.statsEndDate')"
          :range-separator="'~'"
          clearable
          @update:model-value="onDateChange"
        />
      </div>
    </div>
    <div class="stats-content" :class="{ 'loading-active': loading }">
      <div v-if="loading" class="loading-wrapper">
        <LoadingSpinner :absolute="false" />
      </div>
      <template v-else>
        <div v-if="!sortedList.length" class="empty-state">
          <p>{{ translate('personalCenter.dailyStatsEmpty') }}</p>
        </div>
        <div v-else class="chart-wrap">
          <!-- 原生 SVG 折线图，避免引入 echarts/huicharts -->
          <svg
            ref="svgRef"
            class="line-chart-svg"
            :viewBox="`0 0 ${W} ${H}`"
            preserveAspectRatio="xMidYMid meet"
          >
            <!-- 网格线 -->
            <line
              v-for="i in gridLines"
              :key="'g' + i"
              :x1="PAD_L"
              :y1="yScale(i)"
              :x2="W - PAD_R"
              :y2="yScale(i)"
              stroke="#e8e8e8"
              stroke-width="1"
            />
            <!-- Y 轴标签 -->
            <text
              v-for="i in gridLines"
              :key="'yl' + i"
              :x="PAD_L - 6"
              :y="yScale(i) + 4"
              text-anchor="end"
              font-size="11"
              fill="#999"
            >{{ i }}</text>
            <!-- X 轴标签 -->
            <text
              v-for="(pt, idx) in xPoints"
              :key="'xl' + idx"
              :x="pt"
              :y="H - PAD_B + 16"
              text-anchor="middle"
              font-size="10"
              fill="#999"
            >{{ xLabels[idx] }}</text>
            <!-- 折线 + 点 -->
            <template v-for="(series, si) in seriesList" :key="si">
              <polyline
                :points="series.points"
                fill="none"
                :stroke="COLORS[si]"
                stroke-width="2"
                stroke-linejoin="round"
              />
              <circle
                v-for="(pt, pi) in series.dots"
                :key="pi"
                :cx="pt.x"
                :cy="pt.y"
                r="3"
                :fill="COLORS[si]"
              />
            </template>
            <!-- 图例 -->
            <g v-for="(s, si) in seriesList" :key="'leg' + si" :transform="`translate(${PAD_L + si * 90}, ${H - 8})`">
              <rect x="0" y="-8" width="12" height="4" :fill="COLORS[si]" rx="2" />
              <text x="16" y="0" font-size="11" :fill="COLORS[si]">{{ s.label }}</text>
            </g>
          </svg>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { DatePicker as TinyDatePicker, Modal } from '@opentiny/vue'
import { userApi, type DailyStatItem } from '../api/user'
import { t } from '../i18n'
import { useLocaleStore } from '../stores/locale'
// @ts-ignore
import LoadingSpinner from '../components/LoadingSpinner.vue'

const localeStore = useLocaleStore()
const loading = ref(false)
const rawList = ref<DailyStatItem[]>([])

// SVG 画布尺寸常量
const W = 800
const H = 300
const PAD_L = 40
const PAD_R = 20
const PAD_T = 20
const PAD_B = 36
const COLORS = ['#4e83fd', '#35b377', '#f5a524']

const METRIC_KEYS = ['reads', 'collections', 'likes'] as const
const METRIC_I18N: Record<string, string> = {
  reads: 'personalCenter.statsReads',
  collections: 'personalCenter.statsCollect',
  likes: 'personalCenter.statsLike'
}

function formatDate(d: Date): string {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function getDefaultDateRange(): [string, string] {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - 30)
  return [formatDate(start), formatDate(end)]
}

const dateRange = ref<[string, string]>(getDefaultDateRange())

const translate = (key: string) => {
  void localeStore.localeKey
  return t(key)
}

const onDateChange = () => { fetchStats() }

function getNum(item: DailyStatItem, key: string): number {
  const v = key === 'reads' ? item.reads : key === 'collections' ? item.collections : item.likes
  const n = Number(v)
  return Number.isFinite(n) ? n : 0
}

function fmtXLabel(dateStr: string): string {
  try {
    const d = new Date(dateStr)
    return `${d.getMonth() + 1}/${d.getDate()}`
  } catch { return dateStr }
}

const sortedList = computed(() =>
  [...rawList.value].sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
)

const xLabels = computed(() => sortedList.value.map((r) => fmtXLabel(r.date)))

// X 坐标列表
const xPoints = computed(() => {
  const n = sortedList.value.length
  if (n === 0) return []
  const chartW = W - PAD_L - PAD_R
  return sortedList.value.map((_, i) => PAD_L + (i / Math.max(n - 1, 1)) * chartW)
})

// 最大值（用于 Y 轴缩放）
const maxVal = computed(() => {
  let m = 0
  sortedList.value.forEach((r) => {
    METRIC_KEYS.forEach((k) => { m = Math.max(m, getNum(r, k)) })
  })
  return m || 1
})

// 网格刻度（4 条）
const gridLines = computed(() => {
  const step = Math.ceil(maxVal.value / 4)
  return [0, step, step * 2, step * 3, step * 4]
})

const chartH = H - PAD_T - PAD_B

function yScale(v: number): number {
  return PAD_T + chartH - (v / (gridLines.value[gridLines.value.length - 1] || 1)) * chartH
}

const seriesList = computed(() =>
  METRIC_KEYS.map((k, si) => {
    const dots = sortedList.value.map((r, i) => ({
      x: xPoints.value[i] ?? 0,
      y: yScale(getNum(r, k))
    }))
    const points = dots.map((d) => `${d.x},${d.y}`).join(' ')
    return {
      label: translate(METRIC_I18N[k] ?? k),
      color: COLORS[si],
      dots,
      points
    }
  })
)

const fetchStats = async () => {
  try {
    loading.value = true
    const dr = dateRange.value
    const params =
      dr && Array.isArray(dr) && dr.length === 2 && dr[0] && dr[1]
        ? { start_date: dr[0], end_date: dr[1] }
        : undefined
    rawList.value = await userApi.getDailyStats(params)
  } catch (e: any) {
    Modal.message({ message: e?.message || translate('personalCenter.fetchError'), status: 'error' })
  } finally {
    loading.value = false
  }
}

onMounted(() => { fetchStats() })
</script>

<style scoped lang="less">
.daily-stats-page { width: 100%; }

.content-header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 24px;
}

.content-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

.date-range-wrap { flex-shrink: 0; }

.stats-content {
  width: 100%;
  &.loading-active {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 320px;
  }
}

.loading-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #999;
  font-size: 15px;
}

.chart-wrap { width: 100%; min-height: 300px; }

.line-chart-svg {
  width: 100%;
  height: 300px;
  display: block;
}
</style>
