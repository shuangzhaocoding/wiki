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
        <div v-if="!chartData.rows.length" class="empty-state">
          <p>{{ translate('personalCenter.dailyStatsEmpty') }}</p>
        </div>
        <div v-else class="chart-wrap">
          <tiny-chart-line
            :data="chartData"
            :settings="chartSettings"
            width="100%"
            height="400px"
          />
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { TinyHuichartsLine as TinyChartLine } from '@opentiny/vue-huicharts'
import { DatePicker as TinyDatePicker, Modal } from '@opentiny/vue'
import { userApi, type DailyStatItem } from '../api/user'
import { t } from '../i18n'
import { useLocaleStore } from '../stores/locale'
// @ts-ignore
import LoadingSpinner from '../components/LoadingSpinner.vue'

const localeStore = useLocaleStore()
const loading = ref(false)
const rawList = ref<DailyStatItem[]>([])

function formatDate(d: Date): string {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

/** 默认最近一个月 [开始, 结束] */
function getDefaultDateRange(): [string, string] {
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - 30)
  return [formatDate(start), formatDate(end)]
}

const dateRange = ref<[string, string]>(getDefaultDateRange())

const translate = (key: string, params?: Record<string, string>) => {
  void localeStore.localeKey
  return t(key, params)
}

const onDateChange = () => {
  fetchStats()
}

// 指标字段与 i18n 的映射，对应接口 { date, reads, collections, likes }
const METRIC_KEYS = ['reads', 'collections', 'likes'] as const
const METRIC_I18N: Record<string, string> = {
  reads: 'personalCenter.statsReads',
  collections: 'personalCenter.statsCollect',
  likes: 'personalCenter.statsLike'
}

function formatChartDate(dateStr: string): string {
  if (!dateStr) return ''
  try {
    const d = new Date(dateStr)
    const m = d.getMonth() + 1
    const day = d.getDate()
    return `${m}/${day}`
  } catch {
    return dateStr
  }
}

function getNum(item: DailyStatItem, key: string): number {
  const v = key === 'reads' ? item.reads : key === 'collections' ? item.collections : item.likes
  const n = Number(v)
  return Number.isFinite(n) ? n : 0
}

const chartData = computed(() => {
  const list = [...rawList.value].sort(
    (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()
  )
  const columns = ['date', ...METRIC_KEYS]
  const rows = list.map((r) => {
    const row: Record<string, string | number> = {
      date: formatChartDate(r.date)
    }
    METRIC_KEYS.forEach((k) => {
      row[k] = getNum(r, k)
    })
    return row
  })
  return { columns, rows }
})

const chartSettings = computed(() => {
  const labelMap: Record<string, string> = {}
  METRIC_KEYS.forEach((k) => {
    labelMap[k] = translate(METRIC_I18N[k] || k)
  })
  return {
    dimension: ['date'],
    metrics: chartData.value.columns.filter((c) => c !== 'date'),
    labelMap,
    smooth: true
  }
})

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

onMounted(() => {
  fetchStats()
})
</script>

<style scoped lang="less">
.daily-stats-page {
  width: 100%;
}

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

.date-range-wrap {
  flex-shrink: 0;
}

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

.chart-wrap {
  width: 100%;
  min-height: 400px;
}
</style>
