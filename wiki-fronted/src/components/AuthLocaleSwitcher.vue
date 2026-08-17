<template>
  <div class="auth-locale-switcher" role="region" :aria-label="translate('auth.language')">
    <span class="auth-locale-switcher__label">{{ translate('auth.language') }}</span>
    <tiny-select
      v-model="currentLocaleValue"
      :options="localeOptions"
      size="small"
      class="auth-locale-switcher__select"
      @change="handleLocaleChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { Select as TinySelect } from '@opentiny/vue'
import { t, type Locale } from '../i18n'
import { useLocaleStore } from '../stores/locale'

const localeStore = useLocaleStore()

const localeOptions = [
  { label: '中文', value: 'zh' as Locale },
  { label: 'English', value: 'en' as Locale },
  { label: '한국어', value: 'ko' as Locale },
  { label: 'Deutsch', value: 'de' as Locale },
  { label: '日本語', value: 'ja' as Locale },
  { label: 'Français', value: 'fr' as Locale }
]

const currentLocaleValue = ref<Locale>(localeStore.currentLocale)

watch(
  () => localeStore.currentLocale,
  (v) => {
    currentLocaleValue.value = v
  }
)

const translate = (key: string) => {
  void localeStore.localeKey
  return t(key)
}

const handleLocaleChange = (value: Locale) => {
  localeStore.setLocale(value)
}
</script>

<style scoped lang="less">
.auth-locale-switcher {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
  max-width: min(100% - 32px, 280px);
}

.auth-locale-switcher__label {
  font-size: 13px;
  font-weight: 500;
  color: rgba(255, 255, 255, 0.92);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.12);
  white-space: nowrap;
}

.auth-locale-switcher__select {
  width: 128px;
  flex-shrink: 0;
}


@media (max-width: 1024px) {
  .auth-locale-switcher {
    top: max(12px, env(safe-area-inset-top, 0px));
    right: max(12px, env(safe-area-inset-right, 0px));
    max-width: calc(100% - 24px);
  }
}

@media (max-width: 768px) {
  .auth-locale-switcher__label {
    display: none;
  }

  .auth-locale-switcher__select {
    width: min(140px, 42vw);
  }
}

@media (max-width: 480px) {
  .auth-locale-switcher {
    top: max(10px, env(safe-area-inset-top, 0px));
    right: max(10px, env(safe-area-inset-right, 0px));
  }

  .auth-locale-switcher__select {
    width: min(132px, 48vw);
  }
}
</style>
