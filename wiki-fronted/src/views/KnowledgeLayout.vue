<template>
  <div
    class="knowledge-layout-page"
    :class="{
      'knowledge-layout-page--compact': isCompactLayout,
      'knowledge-layout-page--mobile': isMobileLayout
    }"
  >
    <div class="main-layout">
      <Transition name="knowledge-drawer-fade">
        <div
          v-if="isCompactLayout && mobileDrawerOpen"
          class="sidebar-overlay"
          aria-hidden="true"
          @click="closeMobileDrawer"
        />
      </Transition>

      <KnowledgeSidebar
        :compact="isCompactLayout"
        :drawer-open="mobileDrawerOpen"
        @navigate="closeMobileDrawer"
      />

      <main class="content-area">
        <div v-if="isCompactLayout" class="content-mobile-toolbar">
          <button
            type="button"
            class="content-mobile-toolbar__btn"
            :aria-label="translate('nav.menuTitle')"
            :aria-expanded="mobileDrawerOpen"
            @click="toggleMobileDrawer"
          >
            <svg viewBox="0 0 1024 1024" width="18" height="18" fill="currentColor" aria-hidden="true">
              <path d="M128 256h768v64H128v-64zm0 352h768v64H128v-64zm0 352h768v64H128v-64z"/>
            </svg>
            <span>{{ translate('nav.menuTitle') }}</span>
          </button>
        </div>

        <div class="content-area__body">
          <NoPermission v-if="showNoPermission" />
          <router-view v-else />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRoute } from 'vue-router'
// @ts-ignore
import KnowledgeSidebar from '../components/KnowledgeSidebar.vue'
import NoPermission from './NoPermission.vue'
import { useResponsiveLayout } from '../composables/useResponsiveLayout'
import { t } from '../i18n'
import { useLocaleStore } from '../stores/locale'

const route = useRoute()
const localeStore = useLocaleStore()

const {
  isCompactLayout,
  isMobileLayout,
  mobileDrawerOpen,
  toggleMobileDrawer,
  closeMobileDrawer
} = useResponsiveLayout()

const translate = (key: string, params?: Record<string, string>) => {
  void localeStore.localeKey
  return t(key, params)
}

const showNoPermission = computed(() => route.meta.hasPermission === false)

watch(
  () => route.path,
  () => {
    closeMobileDrawer()
  }
)
</script>

<style scoped lang="less">
.knowledge-layout-page {
  height: calc(100vh - 64px);
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
  overflow: hidden;

  &--mobile {
    height: calc(100vh - 56px);
  }
}

.main-layout {
  display: flex;
  flex: 1;
  width: 100%;
  min-height: 0;
  overflow: hidden;
  position: relative;
}

.sidebar-overlay {
  position: fixed;
  inset: 0;
  z-index: 400;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(2px);
}

.knowledge-drawer-fade-enter-active,
.knowledge-drawer-fade-leave-active {
  transition: opacity 0.25s ease;
}

.knowledge-drawer-fade-enter-from,
.knowledge-drawer-fade-leave-to {
  opacity: 0;
}

.content-area {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  padding: 30px 40px;
  background: #fff;
  margin: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.content-area__body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
}

.content-mobile-toolbar {
  display: none;
}

.knowledge-layout-page--compact {
  .content-mobile-toolbar {
    display: flex;
    align-items: center;
    flex-shrink: 0;
    padding-bottom: 12px;
    margin-bottom: 4px;
    border-bottom: 1px solid #e4e7ed;
  }

  .content-mobile-toolbar__btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 14px;
    border: 1px solid rgba(139, 92, 246, 0.25);
    border-radius: 8px;
    background: rgba(139, 92, 246, 0.08);
    color: var(--primary-color, #8b5cf6);
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s, border-color 0.2s;

    &:hover {
      background: rgba(139, 92, 246, 0.14);
      border-color: rgba(139, 92, 246, 0.4);
    }
  }

  .content-area {
    margin: 12px;
    padding: 16px 20px;
    border-radius: 10px;
  }
}

.knowledge-layout-page--mobile {
  .content-area {
    margin: 8px;
    padding: 12px 14px;
    border-radius: 8px;
  }

  .content-mobile-toolbar {
    padding-bottom: 10px;
  }

  .content-mobile-toolbar__btn {
    padding: 7px 12px;
    font-size: 13px;
  }
}
</style>
