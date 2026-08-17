<template>
  <header class="header">
    <div class="header-content">
      <div class="header-leading">
        <button
          v-if="isCompactHeader"
          type="button"
          class="mobile-menu-btn"
          :aria-label="translate('nav.menuTitle')"
          :aria-expanded="mobileMenuOpen"
          @click="toggleMobileMenu"
        >
          <svg class="mobile-menu-icon" viewBox="0 0 1024 1024" width="20" height="20" fill="currentColor" aria-hidden="true">
            <path d="M128 256h768v64H128v-64zm0 352h768v64H128v-64zm0 352h768v64H128v-64z"/>
          </svg>
        </button>
        <router-link to="/" class="logo-section" :title="translate('nav.home')">
          <span class="logo-text">Wiki</span>
        </router-link>
      </div>
      <div class="search-section">
        <div
          class="search-trigger"
          :class="{ 'search-trigger--icon-only': isMobileSearch }"
          :title="translate('nav.searchPlaceholder')"
          @click="openSearchModal"
        >
          <component :is="TinyIconSearch" class="search-icon" />
          <span class="search-placeholder">{{ translate('nav.searchPlaceholder') }}</span>
          <span class="search-shortcut">⌘K</span>
        </div>
      </div>
      <nav v-if="!isCompactHeader" class="nav-menu">
        <router-link to="/" class="nav-item">{{ translate('nav.home') }}</router-link>
        <router-link to="/knowledge/team-spaces" class="nav-item">{{ translate('nav.teamSpace') }}</router-link>
        <router-link to="/knowledge/knowledge-spaces" class="nav-item">{{ translate('nav.knowledgeSpace') }}</router-link>
      </nav>
      <div class="header-actions">
        <div v-if="!isCompactHeader" class="header-selects">
          <tiny-select
            v-model="currentThemeValue"
            :options="themeOptions"
            class="header-select header-select--theme"
            @change="handleThemeChange"
            size="small"
          />
          <tiny-select
            v-model="currentLocaleValue"
            :options="localeOptions"
            class="header-select header-select--locale"
            @change="handleLocaleChange"
            size="small"
          />
          <tiny-select
            v-if="userInfo && userRoles.length > 0"
            v-model="currentRoleId"
            :options="roleOptions"
            class="header-select header-select--role"
            @change="handleRoleChange"
            size="small"
            :placeholder="translate('nav.selectRole')"
          />
          <tiny-select
            v-if="userInfo && knowledgeSpaceOptions.length > 0"
            v-model="selectedKnowledgeSpaceId"
            :options="knowledgeSpaceOptions"
            class="header-select header-select--knowledge"
            @change="handleKnowledgeSpaceChange"
            size="small"
            :placeholder="translate('nav.selectKnowledgeSpace')"
            filterable
          />
        </div>
        <div v-if="userInfo" class="notification-icon" @click="goToNotifications" :title="translate('nav.notifications')">
          <component :is="TinyIconPublicNotice" />
          <span v-if="unreadCount > 0" class="notification-badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
        </div>
        <tiny-button v-if="!userInfo" @click="goToLogin">{{ translate('nav.login') }}</tiny-button>
        <tiny-dropdown v-else trigger="click" placement="bottom-end">
          <div class="user-profile">
            <div class="user-avatar">
              <svg viewBox="0 0 1024 1024" width="18" height="18" fill="currentColor">
                <path d="M512 512c141.312 0 256-114.688 256-256S653.312 0 512 0 256 114.688 256 256s114.688 256 256 256zm0 85.333c-188.928 0-342.4 83.968-448 218.624 41.984 139.264 171.008 238.933 320 238.933s278.016-99.669 320-238.933C854.4 681.301 700.928 597.333 512 597.333z"/>
              </svg>
            </div>
            <span class="user-name">{{ userInfo.username }}</span>
          </div>
          <template #dropdown>
            <tiny-dropdown-menu class="user-dropdown-menu">
              <tiny-dropdown-item v-if="userInfo?.email" class="email-item">
                <div class="menu-item-content">
                  <component :is="TinyIconMail" class="menu-icon" style="margin-right: 12px;" />
                  <span class="email-text">{{ userInfo.email }}</span>
                </div>
              </tiny-dropdown-item>
              <tiny-dropdown-item @click="goToPersonalCenter">
                <div class="menu-item-content">
                  <component :is="TinyIconUser" class="menu-icon"  style="margin-right: 12px;"/>
                  <span>{{ translate('nav.personalCenter') }}</span>
                </div>
              </tiny-dropdown-item>
              <tiny-dropdown-item divided  @click="handleLogout">
                <div class="menu-item-content">
                  <svg class="menu-icon" viewBox="0 0 1024 1024" width="16" height="16" fill="currentColor" style="margin-right: 12px;">
                    <path d="M832 512a32 32 0 0 0-32-32H448V192a32 32 0 0 0-32-32H192a32 32 0 0 0-32 32v640a32 32 0 0 0 32 32h224a32 32 0 0 0 32-32V544h352a32 32 0 0 0 32-32z"/>
                    <path d="M704 384l128 128-128 128V384z"/>
                  </svg>
                  <span>{{ translate('nav.logout') }}</span>
                </div>
              </tiny-dropdown-item>
            </tiny-dropdown-menu>
          </template>
        </tiny-dropdown>
      </div>
    </div>

    <!-- 移动端 / 平板侧栏菜单 -->
    <Teleport to="body">
      <Transition name="mobile-nav">
        <div
          v-if="isCompactHeader && mobileMenuOpen"
          class="mobile-nav-overlay"
          @click="closeMobileMenu"
        >
          <aside class="mobile-nav-drawer" @click.stop>
            <div class="mobile-nav-header">
              <span class="mobile-nav-title">{{ translate('nav.menuTitle') }}</span>
              <button
                type="button"
                class="mobile-nav-close"
                :aria-label="translate('nav.closeMenu')"
                @click="closeMobileMenu"
              >
                <component :is="TinyIconClose" class="mobile-nav-close-icon" />
              </button>
            </div>
            <nav class="mobile-nav-links">
              <router-link to="/" class="mobile-nav-item" @click="closeMobileMenu">
                {{ translate('nav.home') }}
              </router-link>
              <router-link to="/knowledge/team-spaces" class="mobile-nav-item" @click="closeMobileMenu">
                {{ translate('nav.teamSpace') }}
              </router-link>
              <router-link to="/knowledge/knowledge-spaces" class="mobile-nav-item" @click="closeMobileMenu">
                {{ translate('nav.knowledgeSpace') }}
              </router-link>
            </nav>
            <div class="mobile-nav-settings">
              <div class="mobile-nav-settings-title">{{ translate('nav.settings') }}</div>
              <tiny-select
                v-model="currentThemeValue"
                :options="themeOptions"
                class="mobile-nav-select"
                :popper-class="mobileDrawerSelectPopperClass"
                :popper-options="mobileDrawerSelectPopperOptions"
                @change="handleThemeChange"
                size="small"
              />
              <tiny-select
                v-model="currentLocaleValue"
                :options="localeOptions"
                class="mobile-nav-select"
                :popper-class="mobileDrawerSelectPopperClass"
                :popper-options="mobileDrawerSelectPopperOptions"
                @change="handleLocaleChange"
                size="small"
              />
              <tiny-select
                v-if="userInfo && userRoles.length > 0"
                v-model="currentRoleId"
                :options="roleOptions"
                class="mobile-nav-select"
                :popper-class="mobileDrawerSelectPopperClass"
                :popper-options="mobileDrawerSelectPopperOptions"
                @change="handleRoleChange"
                size="small"
                :placeholder="translate('nav.selectRole')"
                :title="translate('nav.selectRole')"
              />
              <tiny-select
                v-if="userInfo && knowledgeSpaceOptions.length > 0"
                v-model="selectedKnowledgeSpaceId"
                :options="knowledgeSpaceOptions"
                class="mobile-nav-select"
                :popper-class="mobileDrawerSelectPopperClass"
                :popper-options="mobileDrawerSelectPopperOptions"
                @change="handleKnowledgeSpaceChange"
                size="small"
                :placeholder="translate('nav.selectKnowledgeSpace')"
                :title="translate('nav.selectKnowledgeSpace')"
                :filterable="false"
                :searchable="false"
              />
            </div>
          </aside>
        </div>
      </Transition>
    </Teleport>

    <!-- 搜索弹窗：挂载到 body，避免被页头 z-index 层叠上下文压住 -->
    <Teleport to="body">
      <div v-if="showSearchModal" class="search-modal-overlay" @click="closeSearchModal">
      <div class="search-modal" @click.stop>
        <div class="search-modal-header">
          <div class="search-input-wrapper">
            <svg class="search-input-icon" viewBox="0 0 1024 1024" width="20" height="20" fill="currentColor">
              <path d="M909.6 854.5L649.9 594.8C690.2 542.7 712 479 712 412c0-80.2-31.3-155.4-87.9-212.1-56.6-56.7-132-87.9-212.1-87.9s-155.5 31.3-212.1 87.9C143.2 256.5 112 331.8 112 412c0 80.1 31.3 155.5 87.9 212.1 56.6 56.7 132 87.9 212.1 87.9 67 0 130.6-21.8 182.7-62l259.7 259.6c3.2 3.2 8.4 3.2 11.6 0l43.6-43.5c3.2-3.2 3.2-8.4 0-11.6zM570.4 570.4c-56.5 56.5-131.8 87.9-212.1 87.9-80.2 0-155.5-31.3-212.1-87.9C89.3 513.8 58 438.5 58 358.3c0-80.1 31.3-155.5 87.9-212.1C202.5 89.6 277.8 58.3 358 58.3s155.5 31.3 212.1 87.9C626.7 202.1 658 277.5 658 357.6c0 80.2-31.3 155.5-87.9 212.1l.3.7z"/>
            </svg>
            <input
              ref="searchInputRef"
              v-model="searchQuery"
              type="text"
              class="search-input"
              :placeholder="translate('nav.searchPlaceholder')"
              @keydown.esc="closeSearchModal"
              @keydown.enter="handleSearchEnter"
            />
          </div>
          <div class="search-filter-options">
            <tiny-button
              :type="searchFilter === 'all' ? 'primary' : 'default'"
              size="small"
              @click="searchFilter = 'all'"
            >
              {{ translate('nav.searchFilter.all') }}
            </tiny-button>
            <tiny-button
              v-if="currentKnowledgeBaseId"
              :type="searchFilter === 'current' ? 'primary' : 'default'"
              size="small"
              @click="searchFilter = 'current'"
            >
              {{ translate('nav.searchFilter.currentKB') }}
            </tiny-button>
          </div>
        </div>
        <div class="search-modal-body">
          <div v-if="recentSearches.length > 0 && !searchQuery" class="search-section">
            <div class="search-section-title">{{ translate('nav.searchRecent') }}</div>
            <div class="search-results">
              <div
                v-for="(item, index) in recentSearches"
                :key="index"
                class="search-result-item"
                :class="{ 'is-active': selectedIndex === index }"
                @click="handleSelectRecent(item)"
                @mouseenter="selectedIndex = index"
              >
                <svg class="result-icon" viewBox="0 0 1024 1024" width="16" height="16" fill="currentColor">
                  <path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm0 820c-205.4 0-372-166.6-372-372s166.6-372 372-372 372 166.6 372 372-166.6 372-372 372z"/>
                  <path d="M464 336a48 48 0 1 0 96 0 48 48 0 1 0-96 0zm72 112h-48c-4.4 0-8 3.6-8 8v272c0 4.4 3.6 8 8 8h48c4.4 0 8-3.6 8-8V456c0-4.4-3.6-8-8-8z"/>
                </svg>
                <div class="result-content">
                  <div class="result-title">{{ item }}</div>
                </div>
                <div class="result-actions">
                  <svg class="result-action-icon" viewBox="0 0 1024 1024" width="14" height="14" fill="currentColor">
                    <path d="M512 64l128 256 288 32-224 192 64 288-256-128-256 128 64-288-224-192 288-32z"/>
                  </svg>
                  <svg class="result-action-icon" viewBox="0 0 1024 1024" width="14" height="14" fill="currentColor" @click.stop="removeRecentSearch(index)">
                    <path d="M563.8 512l262.5-312.9c4.4-5.2.7-13.1-6.1-13.1h-54.9c-4.7 0-9.2 2.1-12.3 5.7L511.6 449.8 295.1 191.7c-3.1-3.6-7.6-5.7-12.3-5.7H228c-6.8 0-10.5 7.9-6.1 13.1L459.4 512 196.9 824.9A7.95 7.95 0 0 0 203 838h54.8c4.7 0 9.2-2.1 12.3-5.7l216.5-258.1 216.5 258.1c3.1 3.6 7.6 5.7 12.3 5.7h54.8c6.8 0 10.5-7.9 6.1-13.1L563.8 512z"/>
                  </svg>
                </div>
              </div>
            </div>
          </div>
          <div v-if="!searchQuery" class="search-section recent-articles-section">
            <div v-if="recentCreatedArticles.length" class="recent-articles-block">
              <div class="search-section-title">{{ translate('nav.recentCreated') }}</div>
              <div class="search-results">
                <div
                  v-for="item in recentCreatedArticles"
                  :key="`created-${item.id}`"
                  class="search-result-item"
                  @click="handleSelectResult(item)"
                >
                  <svg class="result-icon" viewBox="0 0 1024 1024" width="16" height="16" fill="currentColor">
                    <path d="M512 64l128 256 288 32-224 192 64 288-256-128-256 128 64-288-224-192 288-32z" />
                  </svg>
                  <div class="result-content">
                    <div class="result-title">{{ item.title }}</div>
                    <div class="result-meta">
                      <span v-if="item.knowledge_base_name" class="result-meta-item knowledge-base-name" :title="translate('nav.searchKnowledgeBase')">
                        {{ item.knowledge_base_name }}
                      </span>
                      <span class="result-meta-item" :title="translate('nav.searchCreatedAt')">
                        {{ formatSearchDate(item.created_at) }}
                      </span>
                      <span class="result-meta-item" :title="translate('nav.searchAuthor')">
                        {{ item.author_name || '—' }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="recentUpdatedArticles.length" class="recent-articles-block">
              <div class="search-section-title">{{ translate('nav.recentUpdated') }}</div>
              <div class="search-results">
                <div
                  v-for="item in recentUpdatedArticles"
                  :key="`updated-${item.id}`"
                  class="search-result-item"
                  @click="handleSelectResult(item)"
                >
                  <svg class="result-icon" viewBox="0 0 1024 1024" width="16" height="16" fill="currentColor">
                    <path d="M512 64l128 256 288 32-224 192 64 288-256-128-256 128 64-288-224-192 288-32z" />
                  </svg>
                  <div class="result-content">
                    <div class="result-title">{{ item.title }}</div>
                    <div class="result-meta">
                      <span v-if="item.knowledge_base_name" class="result-meta-item knowledge-base-name" :title="translate('nav.searchKnowledgeBase')">
                        {{ item.knowledge_base_name }}
                      </span>
                      <span class="result-meta-item" :title="translate('nav.searchUpdatedAt')">
                        {{ formatSearchDate(item.updated_at) }}
                      </span>
                      <span class="result-meta-item" :title="translate('nav.searchAuthor')">
                        {{ item.author_name || item.updated_by_name || '—' }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else-if="searchQuery" class="search-section">
            <div class="search-results">
              <div v-if="isSearching" class="search-loading">
                <div class="loading-spinner">
                  <div class="spinner-circle"></div>
                  <div class="spinner-circle"></div>
                  <div class="spinner-circle"></div>
                </div>
                <span>{{ translate('common.loading') }}</span>
              </div>
              <div v-else-if="searchResults.length === 0" class="search-empty">
                {{ translate('nav.searchNoResults') }}
              </div>
              <template v-else>
                <div
                  v-for="(item, index) in searchResults"
                  :key="item.id"
                  class="search-result-item"
                  :class="{ 'is-active': selectedIndex === index }"
                  @click="handleSelectResult(item)"
                  @mouseenter="selectedIndex = index"
                >
                  <svg class="result-icon" viewBox="0 0 1024 1024" width="16" height="16" fill="currentColor">
                    <path d="M909.6 854.5L649.9 594.8C690.2 542.7 712 479 712 412c0-80.2-31.3-155.4-87.9-212.1-56.6-56.7-132-87.9-212.1-87.9s-155.5 31.3-212.1 87.9C143.2 256.5 112 331.8 112 412c0 80.1 31.3 155.5 87.9 212.1 56.6 56.7 132 87.9 212.1 87.9 67 0 130.6-21.8 182.7-62l259.7 259.6c3.2 3.2 8.4 3.2 11.6 0l43.6-43.5c3.2-3.2 3.2-8.4 0-11.6zM570.4 570.4c-56.5 56.5-131.8 87.9-212.1 87.9-80.2 0-155.5-31.3-212.1-87.9C89.3 513.8 58 438.5 58 358.3c0-80.1 31.3-155.5 87.9-212.1C202.5 89.6 277.8 58.3 358 58.3s155.5 31.3 212.1 87.9C626.7 202.1 658 277.5 658 357.6c0 80.2-31.3 155.5-87.9 212.1l.3.7z"/>
                  </svg>
                  <div class="result-content">
                    <div class="result-title">{{ item.title }}</div>
                    <div class="result-meta">
                      <span v-if="item.team_space_name" class="result-meta-item team-space-name clickable" :title="translate('nav.searchTeamSpace')" @click.stop="handleNavigateToTeamSpace(item)">
                        <svg class="search-meta-icon" viewBox="0 0 1024 1024" width="12" height="12" fill="currentColor"><path d="M832 64H192c-35.3 0-64 28.7-64 64v768c0 35.3 28.7 64 64 64h640c35.3 0 64-28.7 64-64V128c0-35.3-28.7-64-64-64zM832 832H192V128h640v704zM320 320h384v64H320v-64zm0 128h384v64H320v-64zm0 128h256v64H320v-64z"/></svg>
                        {{ item.team_space_name }}
                      </span>
                      <span v-if="item.knowledge_base_name" class="result-meta-item knowledge-base-name clickable" :title="translate('nav.searchKnowledgeBase')" @click.stop="handleNavigateToKnowledgeBase(item)">
                        <svg class="search-meta-icon" viewBox="0 0 1024 1024" width="12" height="12" fill="currentColor"><path d="M832 384H576V128H192v768h640V384zm-26.496-64L640 154.496V320h165.504zM160 64h448l256 256v608a32 32 0 0 1-32 32H160a32 32 0 0 1-32-32V96a32 32 0 0 1 32-32z"/></svg>
                        {{ item.knowledge_base_name }}
                      </span>
                      <span class="result-meta-item" :title="translate('nav.searchCreatedAt')">
                        <svg class="search-meta-icon" viewBox="0 0 1024 1024" width="12" height="12" fill="currentColor"><path d="M128 384h768v384H128V384zm0-256v128h768V128H128zm0 640h768V576H128v192z"/></svg>
                        {{ formatSearchDate(item.created_at) }}
                      </span>
                      <span class="result-meta-item" :title="translate('nav.searchUpdatedAt')">
                        <svg class="search-meta-icon" viewBox="0 0 1024 1024" width="12" height="12" fill="currentColor"><path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm0 820c-205.4 0-372-166.6-372-372s166.6-372 372-372 372 166.6 372 372-166.6 372-372 372zm32-588v268c0 4.4-3.6 8-8 8h-48c-4.4 0-8-3.6-8-8V352h-95c-4.4 0-8-3.6-8-8v-48c0-4.4 3.6-8 8-8h159c4.4 0 8 3.6 8 8v272z"/></svg>
                        {{ formatSearchDate(item.updated_at) }}
                      </span>
                      <span class="result-meta-item" :title="translate('nav.searchAuthor')">
                        <svg class="search-meta-icon" viewBox="0 0 1024 1024" width="12" height="12" fill="currentColor"><path d="M512 512c141.312 0 256-114.688 256-256S653.312 0 512 0 256 114.688 256 256s114.688 256 256 256zm0 85.333c-188.928 0-342.4 83.968-448 218.624 41.984 139.264 171.008 238.933 320 238.933s278.016-99.669 320-238.933C854.4 681.301 700.928 597.333 512 597.333z"/></svg>
                        {{ item.author_name || '—' }}
                      </span>
                      <span class="result-meta-item" :title="translate('nav.searchViews')">
                        <svg class="search-meta-icon" viewBox="0 0 1024 1024" width="12" height="12" fill="currentColor"><path d="M512 160c320 0 512 352 512 352S832 864 512 864 0 512 0 512s192-352 512-352zm0 64c-247.424 0-400 227.584-448 288 48.064 60.416 200.576 288 448 288 247.424 0 400-227.584 448-288-48.064-60.416-200.576-288-448-288zm0 64a224 224 0 1 1 0 448 224 224 0 0 1 0-448zm0 64a160.192 160.192 0 0 0-160 160c0 88.192 71.808 160 160 160s160-71.808 160-160-71.808-160-160-160z"/></svg>
                        {{ item.view_count ?? '—' }}
                      </span>
                    </div>
                  </div>
                </div>
                <div class="search-pager-wrap">
                  <tiny-pager
                    :current-page="searchPage"
                    :page-size="SEARCH_PAGE_SIZE"
                    :total="searchTotal"
                    :hide-on-single-page="true"
                    layout="prev, pager, next"
                    @page-change="onSearchPageChange"
                  />
                </div>
              </template>
            </div>
          </div>
        </div>
        <div class="search-modal-footer">
          <div class="search-shortcuts">
            <span class="shortcut-item">
              <kbd>←</kbd> <kbd>→</kbd> {{ translate('nav.searchSelect') }}
            </span>
            <span class="shortcut-item">
              <kbd>↑</kbd> <kbd>↓</kbd> {{ translate('nav.searchNavigate') }}
            </span>
            <span class="shortcut-item">
              <kbd>ESC</kbd> {{ translate('nav.searchClose') }}
            </span>
          </div>
        </div>
      </div>
    </div>
    </Teleport>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Button as TinyButton, Select as TinySelect, Modal, Dropdown as TinyDropdown, DropdownMenu as TinyDropdownMenu, DropdownItem as TinyDropdownItem, Pager as TinyPager } from '@opentiny/vue'
import { IconMail, IconUser, IconSearch, IconPublicNotice, IconClose } from '@opentiny/vue-icon'
import { useUserStore } from '../stores/user'
import { authUtils } from '../utils/auth'
import { articleApi, type ArticleSearchItem } from '../api/article'
import { t, type Locale } from '../i18n'
import { getTheme, setTheme, getAllThemes, type Theme } from '../utils/theme'
import { useLocaleStore } from '../stores/locale'
import { userManagementApi, type RoleInfo } from '../api/userManagement'
import { notificationApi } from '../api/notification'
import { knowledgeBaseApi, type KnowledgeBase } from '../api/knowledgeBase'
import { setRolesCache, clearRolesCache } from '../utils/permission'
import { useRecentArticlesStore } from '../stores/recentArticles'

const router = useRouter()
const route = useRoute()
const localeStore = useLocaleStore()
const userStore = useUserStore()

// 从 store 获取用户信息
const userInfo = computed(() => userStore.currentUser)

// 搜索相关：GET /api/articles/search 关键词模糊搜索 + 分页
const SEARCH_PAGE_SIZE = 10
const RECENT_SEARCH_KEY = 'wiki_recent_search_keywords'

function loadRecentFromStorage(): string[] {
  try {
    const raw = localStorage.getItem(RECENT_SEARCH_KEY)
    if (!raw) return []
    const arr = JSON.parse(raw)
    return Array.isArray(arr) && arr.every((x) => typeof x === 'string') ? arr : []
  } catch {
    return []
  }
}

function saveRecentToStorage(items: string[]) {
  try {
    localStorage.setItem(RECENT_SEARCH_KEY, JSON.stringify(items))
  } catch {
    // ignore
  }
}

const showSearchModal = ref(false)
const searchQuery = ref('')
const searchInputRef = ref<HTMLInputElement | null>(null)
const selectedIndex = ref(-1)
const recentSearches = ref<string[]>(loadRecentFromStorage())
const searchResults = ref<ArticleSearchItem[]>([])
const searchTotal = ref(0)
const searchPage = ref(1)
const isSearching = ref(false)
const searchFilter = ref<'all' | 'current'>('all')
let searchDebounceTimer: ReturnType<typeof setTimeout> | null = null

// 最近创建/更新的文章（从 store 复用，避免重复请求）
const recentArticlesStore = useRecentArticlesStore()
const recentCreatedArticles = computed(() => recentArticlesStore.recentCreated)
const recentUpdatedArticles = computed(() => recentArticlesStore.recentUpdated)

// 获取当前知识库ID
const currentKnowledgeBaseId = computed(() => {
  const id = route.params.knowledgeBaseId
  return id && !isNaN(Number(id)) ? Number(id) : null
})

// 语言选项
const localeOptions = [
  { label: '中文', value: 'zh' },
  { label: 'English', value: 'en' },
  { label: '한국어', value: 'ko' },
  { label: 'Deutsch', value: 'de' },
  { label: '日本語', value: 'ja' },
  { label: 'Français', value: 'fr' }
]

// 主题选项
const themeOptions = getAllThemes().map(theme => ({
  label: theme.label,
  value: theme.value
}))

const currentLocaleValue = ref<Locale>(localeStore.currentLocale)
const currentThemeValue = ref<Theme>(getTheme())

// 角色相关
const userRoles = ref<RoleInfo[]>([])
const currentRoleId = ref<number | null>(null)
const roleOptions = computed(() => {
  return userRoles.value.map(role => ({
    label: role.name,
    value: role.id
  }))
})

// 知识空间下拉
const knowledgeSpaces = ref<KnowledgeBase[]>([])
const selectedKnowledgeSpaceId = ref<number | null>(null)
const knowledgeSpaceOptions = computed(() => {
  return knowledgeSpaces.value.map(kb => ({
    label: kb.team_space_name ? `${kb.team_space_name} / ${kb.name}` : kb.name,
    value: kb.id
  }))
})

// OpenTiny 图标实例
const TinyIconMail = IconMail()
const TinyIconUser = IconUser()
const TinyIconSearch = IconSearch()
const TinyIconPublicNotice = IconPublicNotice()
const TinyIconClose = IconClose()

/** 低于此宽度切换汉堡菜单，避免导航与多个下拉挤在一行错乱 */
const HEADER_COMPACT_MAX = 1280
const HEADER_MOBILE_SEARCH_MAX = 768
const mobileDrawerSelectPopperClass = 'mobile-nav-select-popper'
const mobileDrawerSelectPopperOptions = {
  gpuAcceleration: false,
  boundariesPadding: 0
}
const mobileMenuOpen = ref(false)
const isCompactHeader = ref(false)
const isMobileSearch = ref(false)

function updateHeaderLayout() {
  isCompactHeader.value = window.matchMedia(`(max-width: ${HEADER_COMPACT_MAX}px)`).matches
  isMobileSearch.value = window.matchMedia(`(max-width: ${HEADER_MOBILE_SEARCH_MAX}px)`).matches
  if (!isCompactHeader.value) {
    mobileMenuOpen.value = false
  }
}

function toggleMobileMenu() {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

function closeMobileMenu() {
  mobileMenuOpen.value = false
}

function updateBodyScrollLock() {
  document.body.style.overflow = mobileMenuOpen.value || showSearchModal.value ? 'hidden' : ''
}

watch(mobileMenuOpen, (open) => {
  document.body.classList.toggle('mobile-nav-menu-open', open)
  updateBodyScrollLock()
})

watch(showSearchModal, (open) => {
  document.body.classList.toggle('search-modal-open', open)
  updateBodyScrollLock()
})

watch(
  () => route.path,
  () => {
    closeMobileMenu()
  }
)

function formatSearchDate(s: string | undefined): string {
  if (!s) return '—'
  try {
    const d = new Date(s)
    if (isNaN(d.getTime())) return '—'
    const y = d.getFullYear()
    const m = String(d.getMonth() + 1).padStart(2, '0')
    const day = String(d.getDate()).padStart(2, '0')
    const h = String(d.getHours()).padStart(2, '0')
    const min = String(d.getMinutes()).padStart(2, '0')
    return `${y}-${m}-${day} ${h}:${min}`
  } catch {
    return '—'
  }
}

// 未读消息数量，从 /api/notifications/unread-count 获取
const unreadCount = ref(0)

const fetchUnreadCount = async () => {
  if (!userInfo.value) {
    unreadCount.value = 0
    return
  }
  try {
    unreadCount.value = await notificationApi.getUnreadCount()
  } catch {
    unreadCount.value = 0
  }
}

// 响应式翻译函数
const translate = (key: string, params?: Record<string, string>) => {
  void localeStore.localeKey
  return t(key, params)
}

// 切换语言
const handleLocaleChange = (value: Locale) => {
  localeStore.setLocale(value)
  currentLocaleValue.value = value
}

// 切换主题
const handleThemeChange = (value: Theme) => {
  setTheme(value)
  currentThemeValue.value = value
}

// 加载用户角色
const fetchUserRoles = async () => {
  try {
    // 优先使用 userInfo.id，如果不存在则使用 currentUserId
    let userId: number | null = null
    
    if (userInfo.value?.id) {
      const id = userInfo.value.id
      userId = typeof id === 'string' ? parseInt(id, 10) : id
    } else if (userStore.currentUserId) {
      userId = userStore.currentUserId
    }
    
    if (!userId || isNaN(userId)) {
      console.log('fetchUserRoles: 用户ID无效，跳过加载', { userId, userInfo: userInfo.value })
      return
    }
    
    console.log('fetchUserRoles: 开始加载用户角色，用户ID:', userId)
    const roles = await userManagementApi.getUserRoles(userId)
    console.log('fetchUserRoles: 获取到的角色列表:', roles)
    userRoles.value = roles
    
    // 更新权限缓存
    setRolesCache(roles, userId)
    
    // 初始化时自动切换到本地缓存的角色
    if (roles.length > 0) {
      // 先尝试从 localStorage 读取缓存的角色ID
      const savedRoleId = localStorage.getItem('current_role_id')
      console.log('fetchUserRoles: 检查本地缓存，savedRoleId:', savedRoleId, '类型:', typeof savedRoleId)
      
      if (savedRoleId !== null && savedRoleId !== '' && !isNaN(parseInt(savedRoleId, 10))) {
        const roleId = parseInt(savedRoleId, 10)
        console.log('fetchUserRoles: 解析后的角色ID:', roleId)
        const roleExists = roles.some(role => role.id === roleId)
        console.log('fetchUserRoles: 角色是否存在:', roleExists, '可用角色列表:', roles.map(r => r.id))
        
        if (roleExists) {
          // 如果缓存的角色存在，自动切换到该角色
          currentRoleId.value = roleId
          console.log('fetchUserRoles: 从本地缓存恢复角色ID:', roleId)
        } else {
          // 如果缓存的角色不存在，切换到第一个角色并更新缓存
          const firstRole = roles[0]!
          currentRoleId.value = firstRole.id
          localStorage.setItem('current_role_id', String(firstRole.id))
          console.log('fetchUserRoles: 缓存的角色不存在，切换到默认角色:', firstRole.id)
        }
      } else {
        // 如果没有缓存或缓存无效，切换到第一个角色并保存到缓存
        const firstRole = roles[0]!
        currentRoleId.value = firstRole.id
        localStorage.setItem('current_role_id', String(firstRole.id))
        console.log('fetchUserRoles: 无缓存或缓存无效，设置默认角色:', firstRole.id)
      }
    }
  } catch (error) {
    console.error('加载用户角色失败:', error)
    userRoles.value = []
  }
}

// 切换角色
const handleRoleChange = (roleId: number) => {
  currentRoleId.value = roleId
  // 保存角色ID到本地存储
  localStorage.setItem('current_role_id', String(roleId))
  
  // 找到对应的角色并打印其权限
  const selectedRole = userRoles.value.find(r => r.id === roleId)
  if (selectedRole) {
    console.log('切换角色:', {
      id: selectedRole.id,
      name: selectedRole.name,
      code: selectedRole.code,
      permissions: selectedRole.permissions || []
    })
    
    // 打印权限详情
    if (selectedRole.permissions && selectedRole.permissions.length > 0) {
      console.log('角色权限列表:', selectedRole.permissions)
      selectedRole.permissions.forEach((permission, index) => {
        console.log(`权限 ${index + 1}:`, {
          id: permission.id,
          name: permission.name,
          code: permission.code,
          description: permission.description,
          category: permission.category
        })
      })
    } else {
      console.log('该角色暂无权限')
    }
  }
  
  // 显示切换成功消息
  Modal.message({ 
    message: translate('nav.roleSwitched', { roleName: selectedRole?.name || '' }), 
    status: 'success' 
  })
  // 切换角色后重新加载页面，确保权限生效
  setTimeout(() => {
    window.location.reload()
  }, 500)
}

const goToLogin = () => {
  authUtils.clearToken()
  userStore.clearUser()
  router.push('/login')
}

const goToNotifications = () => {
  router.push('/notifications')
}

const goToKnowledgeManagement = () => {
  router.push('/knowledge')
}

// 加载用户可见的知识空间
const fetchKnowledgeSpaces = async () => {
  if (!userInfo.value) return
  try {
    const res = await knowledgeBaseApi.getKnowledgeBases({
      filter_type: 'all',
      page: 1,
      page_size: 100
    })
    const items = Array.isArray(res) ? res : (res as { items: KnowledgeBase[] }).items || []
    knowledgeSpaces.value = items
  } catch {
    knowledgeSpaces.value = []
  }
}

const handleKnowledgeSpaceChange = (id: number) => {
  if (id) {
    window.location.href = `/articles/${id}`
  }
}

const goToPersonalCenter = () => {
  router.push('/knowledge/personal-center')
}

const handleLogout = () => {
  authUtils.clearToken()
  userStore.clearUser()
  // 清除角色相关的本地存储
  localStorage.removeItem('current_role_id')
  userRoles.value = []
  currentRoleId.value = null
  // 清除权限缓存
  clearRolesCache()
  Modal.message({ message: translate('nav.logout'), status: 'success' })
  router.push('/login')
}

// 搜索功能
const openSearchModal = () => {
  closeMobileMenu()
  showSearchModal.value = true
  nextTick(() => {
    searchInputRef.value?.focus()
    requestAnimationFrame(() => {
      searchInputRef.value?.focus()
    })
  })
}

const closeSearchModal = () => {
  showSearchModal.value = false
  searchQuery.value = ''
  selectedIndex.value = -1
  searchResults.value = []
  searchTotal.value = 0
  searchPage.value = 1
  searchFilter.value = 'all' // 重置筛选选项
}

const performSearch = async (keyword: string, page: number = 1) => {
  if (!keyword.trim()) {
    searchResults.value = []
    searchTotal.value = 0
    return
  }
  isSearching.value = true
  try {
    // 根据筛选选项决定是否传递知识库ID
    const knowledgeBaseId = searchFilter.value === 'current' && currentKnowledgeBaseId.value 
      ? currentKnowledgeBaseId.value 
      : undefined
    
    const r = await articleApi.searchArticles(keyword, page, SEARCH_PAGE_SIZE, knowledgeBaseId)
    searchResults.value = r.items
    searchTotal.value = r.total
    searchPage.value = r.page
  } catch (e: any) {
    searchResults.value = []
    searchTotal.value = 0
    Modal.message({ message: e?.message || translate('nav.searchError'), status: 'error' })
  } finally {
    isSearching.value = false
  }
  selectedIndex.value = -1
  const k = keyword.trim()
  if (k && !recentSearches.value.includes(k)) {
    recentSearches.value.unshift(k)
    if (recentSearches.value.length > 5) recentSearches.value.pop()
    saveRecentToStorage(recentSearches.value)
  }
}

// 处理搜索输入框回车
const handleSearchEnter = () => {
  if (searchQuery.value.trim()) {
    searchPage.value = 1
    performSearch(searchQuery.value.trim(), 1)
  }
}

const onSearchPageChange = (e: { currentPage: number }) => {
  searchPage.value = e.currentPage
  performSearch(searchQuery.value, e.currentPage)
}

const handleSelectRecent = (keyword: string) => {
  searchQuery.value = keyword
}

// 监听筛选选项变化，重新搜索
watch(searchFilter, () => {
  if (searchQuery.value.trim()) {
    searchPage.value = 1
    performSearch(searchQuery.value.trim(), 1)
  }
})

const handleSelectResult = (item: ArticleSearchItem) => {
  const path = `/articles/${item.knowledge_base_id}?articleId=${item.id}`
  window.open(router.resolve(path).href, '_blank')
  closeSearchModal()
}

// 跳转到团队空间
const handleNavigateToTeamSpace = (item: ArticleSearchItem) => {
  if (item.team_space_name) {
    closeSearchModal()
    // 只传递团队空间名称作为查询参数
    router.push({
      path: '/knowledge/team-spaces',
      query: {
        name: item.team_space_name
      }
    })
  }
}

// 跳转到知识库
const handleNavigateToKnowledgeBase = (item: ArticleSearchItem) => {
  if (item.knowledge_base_name) {
    closeSearchModal()
    // 只传递知识库名称作为查询参数
    const query: Record<string, string> = {
      name: item.knowledge_base_name
    }
    router.push({
      path: '/knowledge/knowledge-spaces',
      query
    })
  }
}

const removeRecentSearch = (index: number) => {
  recentSearches.value.splice(index, 1)
  saveRecentToStorage(recentSearches.value)
}

// 输入关键词时防抖触发搜索
watch(searchQuery, (newQuery) => {
  if (searchDebounceTimer) clearTimeout(searchDebounceTimer)
  if (!newQuery.trim()) {
    searchResults.value = []
    searchTotal.value = 0
    searchPage.value = 1
    selectedIndex.value = -1
    isSearching.value = false
    return
  }
  searchDebounceTimer = setTimeout(() => {
    searchDebounceTimer = null
    performSearch(newQuery, 1)
  }, 300)
  selectedIndex.value = -1
})

// 键盘快捷键
const handleKeyDown = (e: KeyboardEvent) => {
  // Cmd/Ctrl + K 打开搜索
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    if (showSearchModal.value) {
      closeSearchModal()
    } else {
      openSearchModal()
    }
  }
  
  // ESC 关闭搜索或移动端菜单
  if (e.key === 'Escape') {
    if (showSearchModal.value) {
      closeSearchModal()
    } else if (mobileMenuOpen.value) {
      closeMobileMenu()
    }
  }
  
  // 在搜索弹窗中的键盘导航
  if (showSearchModal.value) {
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      const maxIndex = searchQuery.value ? searchResults.value.length - 1 : recentSearches.value.length - 1
      selectedIndex.value = Math.min(selectedIndex.value + 1, maxIndex)
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      selectedIndex.value = Math.max(selectedIndex.value - 1, -1)
    } else if (e.key === 'Enter' && selectedIndex.value >= 0) {
      e.preventDefault()
      if (searchQuery.value) {
        const item = searchResults.value[selectedIndex.value]
        if (item) {
          handleSelectResult(item)
        }
      } else {
        const item = recentSearches.value[selectedIndex.value]
        if (item) {
          handleSelectRecent(item)
        }
      }
    }
  }
}

// 监听用户信息变化，加载角色
watch(
  () => userInfo.value?.id ?? null,
  async (userId) => {
    if (userId) {
      // 等待一下确保 userStore 已更新
      await nextTick()
      const numericUserId = typeof userId === 'string' ? parseInt(userId, 10) : userId
      if (!isNaN(numericUserId)) {
        await fetchUserRoles()
      }
      await fetchUnreadCount()
      await fetchKnowledgeSpaces()
    } else {
      unreadCount.value = 0
      // 只有在用户确实登出（没有 token）时才清除缓存
      // 初始化时如果还没有用户信息，不应该清除缓存
      if (!authUtils.isAuthenticated()) {
        userRoles.value = []
        currentRoleId.value = null
        knowledgeSpaces.value = []
        selectedKnowledgeSpaceId.value = null
        localStorage.removeItem('current_role_id')
        // 清除权限缓存
        clearRolesCache()
      }
    }
  },
  { immediate: true }
)

// 从通知页返回时刷新未读数量
watch(
  () => route.path,
  (path, prevPath) => {
    if (prevPath === '/notifications' && path !== '/notifications') {
      fetchUnreadCount()
    }
  }
)

// 路由变化时同步知识空间选中项
watch(
  () => route.params.knowledgeBaseId,
  (id) => {
    const numId = id && !isNaN(Number(id)) ? Number(id) : null
    selectedKnowledgeSpaceId.value = numId
  },
  { immediate: true }
)

onMounted(async () => {
  updateHeaderLayout()
  window.addEventListener('resize', updateHeaderLayout)
  document.addEventListener('keydown', handleKeyDown)
  
  // 如果有 token 但没有用户信息，则获取用户信息（解决刷新页面后登录状态显示异常的问题）
  if (authUtils.isAuthenticated() && !userInfo.value) {
    console.log('userStore.currentUser0000', userStore.currentUser)
    await userStore.fetchCurrentUser()
  }
  
  // 等待一下确保 userStore 已更新
  await nextTick()
  
  // 如果用户已登录，加载角色
  const userId = userStore.currentUserId
  if (userId) {
    await fetchUserRoles()
  }

  // 初始化加载未读消息数量
  if (userInfo.value) {
    await fetchUnreadCount()
  }

  // 仅登录后拉取最近文章；未登录页不应请求（与 App.vue 隐藏 header 一致，并避免 /login/ 等边界仍挂载时误请求）
  if (authUtils.isAuthenticated()) {
    await recentArticlesStore.fetchRecentArticles()
  }

  // 加载用户可见的知识空间
  if (userInfo.value) {
    await fetchKnowledgeSpaces()
    const kbId = currentKnowledgeBaseId.value
    if (kbId) {
      selectedKnowledgeSpaceId.value = kbId
    }
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', updateHeaderLayout)
  document.removeEventListener('keydown', handleKeyDown)
  document.body.style.overflow = ''
  document.body.classList.remove('mobile-nav-menu-open', 'search-modal-open')
})
</script>

<style scoped lang="less">
.header {
  width: 100%;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 50;
}

.header-content {
  width: 100%;
  max-width: 100%;
  margin: 0 auto;
  padding: 0 40px;
  height: 64px;
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
  overflow: hidden;
}

.header-leading {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
  min-width: 0;
}

.mobile-menu-btn {
  display: none;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  padding: 0;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: #666;
  cursor: pointer;
  transition: background-color 0.2s, color 0.2s;

  &:hover {
    background-color: #f5f5f5;
    color: var(--primary-color, #8b5cf6);
  }

  .mobile-menu-icon {
    width: 20px;
    height: 20px;
  }
}

.logo-section {
  display: flex;
  align-items: center;
  flex-shrink: 0;
  text-decoration: none;
  outline: none;

  &:hover .logo-text {
    opacity: 0.85;
  }

  &:focus-visible .logo-text {
    outline: 2px solid rgba(139, 92, 246, 0.45);
    outline-offset: 4px;
    border-radius: 4px;
  }

  &.router-link-active .logo-text {
    color: var(--primary-color, #8b5cf6);
  }
}

.logo-text {
  font-size: 22px;
  font-weight: 700;
  line-height: 1;
  letter-spacing: -0.03em;
  color: var(--primary-color, #8b5cf6);
  transition: opacity 0.2s, color 0.2s;
  user-select: none;
}

.header-selects {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.header-select {
  &--theme {
    width: 100px;
  }

  &--locale {
    width: 120px;
  }

  &--role {
    width: 140px;
  }

  &--knowledge {
    width: 160px;
  }
}

.search-section {
  margin-left: 30px;
  flex: 0 1 auto;
  min-width: 0;
  max-width: 240px;

  .search-trigger {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px 12px;
    background: #f5f7fa;
    border: 1px solid #e4e7ed;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.3s;
    width: 100%;
    max-width: 100%;
    min-width: 160px;
    box-sizing: border-box;
    
    &:hover {
      background: #fff;
      border-color: var(--primary-color, #8b5cf6);
    }
    
    .search-icon {
      width: 16px;
      height: 16px;
      color: #999;
      flex-shrink: 0;
    }
    
    .search-placeholder {
      flex: 1;
      color: #999;
      font-size: 14px;
      text-align: left;
    }
    
    .search-shortcut {
      padding: 2px 6px;
      background: #fff;
      border: 1px solid #e4e7ed;
      border-radius: 4px;
      font-size: 12px;
      color: #666;
      font-family: monospace;
    }

    &.search-trigger--icon-only {
      min-width: 36px;
      width: 36px;
      height: 36px;
      padding: 0;
      justify-content: center;
      border-radius: 50%;

      .search-placeholder,
      .search-shortcut {
        display: none;
      }

      .search-icon {
        width: 18px;
        height: 18px;
      }
    }
  }
}

.nav-menu {
  display: flex;
  gap: 24px;
  align-items: center;
  flex: 0 1 auto;
  min-width: 0;
  justify-content: flex-end;
  margin-left: auto;
  margin-right: 8px;

  .nav-item {
    color: #333;
    text-decoration: none;
    font-size: 14px;
    white-space: nowrap;
    flex-shrink: 0;
    transition: color 0.3s;

    &:hover {
      color: var(--primary-color, #8b5cf6);
    }

    &.router-link-active {
      color: var(--primary-color, #8b5cf6);
      font-weight: 500;
    }
  }
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-shrink: 0;
  min-width: 0;

  .edit-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    cursor: pointer;
    color: #666;
    border-radius: 50%;
    transition: all 0.3s;

    &:hover {
      background-color: #f5f5f5;
      color: var(--primary-color, #8b5cf6);
    }

    svg {
      width: 20px;
      height: 20px;
    }
  }

  .notification-icon {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    cursor: pointer;
    color: #666;
    border-radius: 50%;
    transition: all 0.3s;

    &:hover {
      background-color: #f5f5f5;
      color: var(--primary-color, #8b5cf6);
    }

    svg {
      width: 20px;
      height: 20px;
    }

    .notification-badge {
      position: absolute;
      top: 0;
      right: 0;
      min-width: 18px;
      height: 18px;
      padding: 0 4px;
      background-color: #f56c6c;
      color: #fff;
      font-size: 12px;
      font-weight: 600;
      border-radius: 9px;
      display: flex;
      align-items: center;
      justify-content: center;
      line-height: 1;
      border: 2px solid #fff;
    }
  }

  .user-profile {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    padding: 4px 8px;
    border-radius: 20px;
    transition: all 0.3s;
    
    &:hover {
      background-color: #f5f5f5;
    }
    
    .user-avatar {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: var(--primary-color, #8b5cf6);
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
      flex-shrink: 0;
      
      :deep(svg) {
        width: 18px;
        height: 18px;
      }
    }
    
    .user-name {
      color: #333;
      font-size: 14px;
      font-weight: 500;
      max-width: 120px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }
  
  // 下拉菜单样式
  :deep(.user-dropdown-menu) {
    min-width: auto;
    width: auto;
    
    .tiny-dropdown-item {
      padding: 8px 16px;
      white-space: nowrap;
      
      &.email-item {
        cursor: default;
        
        .menu-item-content {
          cursor: default;
        }
        
        .email-text {
          color: #999;
        }
        
        &:hover {
          .menu-item-content {
            .menu-icon,
            .email-text {
              color: #999;
            }
          }
        }
      }
      
      .menu-item-content {
        display: flex;
        align-items: center;
        gap: 12px;
        cursor: pointer;
        width: 100%;
        
        .menu-icon {
          flex-shrink: 0;
          color: #999;
          width: 16px;
          height: 16px;
          display: inline-flex;
          align-items: center;
          
          :deep(svg) {
            width: 16px;
            height: 16px;
            vertical-align: middle;
          }
        }
        
        span {
          color: #333;
          font-size: 14px;
          line-height: 1.5;
        }
      }
      
      &:hover:not(.email-item) {
        .menu-item-content {
          .menu-icon {
            color: var(--primary-color, #8b5cf6);
          }
          
          span {
            color: var(--primary-color, #8b5cf6);
          }
        }
      }
    }
  }
}

// 搜索弹窗样式
.search-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  /* 高于其他浮层，避免遮挡 ⌘K 搜索 */
  z-index: 2400;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 10vh;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.search-modal {
  width: 92%;
  max-width: 70%;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  animation: slideDown 0.2s ease-out;
  max-height: 85vh;
  min-height: 420px;
  display: flex;
  flex-direction: column;
}

@keyframes slideDown {
  from {
    transform: translateY(-20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

.search-modal-header {
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.search-filter-options {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  align-items: center;
  
  .tiny-button {
    font-size: 12px;
    padding: 4px 12px;
    height: 28px;
  }
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  
  .search-input-icon {
    position: absolute;
    left: 12px;
    color: #999;
    pointer-events: none;
  }
  
  .search-input {
    width: 100%;
    padding: 12px 12px 12px 40px;
    border: 1px solid #e4e7ed;
    border-radius: 8px;
    font-size: 16px;
    outline: none;
    transition: all 0.3s;
    
    &:focus {
      border-color: var(--primary-color, #8b5cf6);
      box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.1);
    }
    
    &::placeholder {
      color: #999;
    }
  }
}

.search-modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 10px 0;
}

.search-section {
  padding: 0 20px;
  
  .search-section-title {
    padding: 10px 0;
    font-size: 12px;
    font-weight: 600;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
}

.search-results {
  .search-result-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
    margin-bottom: 4px;
    
    &.is-active {
      background: #f5f5f5;
      color: #fff;
      
      .result-title,
      .result-subtitle,
      .result-meta-item {
        color: #fff;
      }
      
      .search-meta-icon {
        color: #fff;
      }
      
      .result-action-icon {
        color: #fff;
      }
    }
    
    .result-icon {
      flex-shrink: 0;
      color: #999;
    }
    
    .result-content {
      flex: 1;
      min-width: 0;
      
      .result-title {
        font-size: 14px;
        font-weight: 500;
        color: #333;
        margin-bottom: 6px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        text-align: left;
      }
      
      .result-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 4px 16px;
        align-items: center;
      }
      
      .result-meta-item {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-size: 12px;
        color: #999;
        
        &.clickable {
          cursor: pointer;
          transition: opacity 0.2s;
          
          &:hover {
            opacity: 0.8;
            text-decoration: underline;
          }
        }
        
        &.team-space-name {
          color: #666;
          font-weight: 500;
        }
        
        &.knowledge-base-name {
          color: var(--primary-color, #8b5cf6);
          font-weight: 500;
        }
      }
      
      .search-meta-icon {
        flex-shrink: 0;
        width: 12px;
        height: 12px;
        color: #999;
      }
      
      .team-space-name .search-meta-icon {
        color: #666;
      }
      
      .knowledge-base-name .search-meta-icon {
        color: var(--primary-color, #8b5cf6);
      }
      
      .result-subtitle {
        font-size: 12px;
        color: #999;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }
    
    .result-actions {
      display: flex;
      gap: 8px;
      opacity: 0;
      transition: opacity 0.2s;
      
      .result-action-icon {
        color: #999;
        cursor: pointer;
        transition: color 0.2s;
        
        &:hover {
          color: var(--primary-color, #8b5cf6);
        }
      }
    }
    
    &:hover .result-actions {
      opacity: 1;
    }
  }
}

.search-pager-wrap {
  padding: 12px 0 8px;
  display: flex;
  justify-content: center;
}

.search-empty {
  padding: 40px 20px;
  text-align: center;
  color: #999;
  font-size: 14px;
}

.search-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  gap: 12px;
  
  .loading-spinner {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    
    .spinner-circle {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background-color: var(--primary-color, #8b5cf6);
      animation: loading-bounce 1.4s ease-in-out infinite both;
      
      &:nth-child(1) {
        animation-delay: -0.32s;
      }
      
      &:nth-child(2) {
        animation-delay: -0.16s;
      }
      
      &:nth-child(3) {
        animation-delay: 0s;
      }
    }
  }
  
  span {
    color: #999;
    font-size: 14px;
  }
}

@keyframes loading-bounce {
  0%, 80%, 100% {
    transform: scale(0);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

.search-modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  border-top: 1px solid #e4e7ed;
  background: #f9fafb;
  font-size: 12px;
  
  .search-shortcuts {
    display: flex;
    gap: 16px;
    
    .shortcut-item {
      display: flex;
      align-items: center;
      gap: 4px;
      color: #666;
      
      kbd {
        padding: 2px 6px;
        background: #fff;
        border: 1px solid #e4e7ed;
        border-radius: 4px;
        font-size: 11px;
        font-family: monospace;
        color: #666;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
      }
    }
  }
}

// 移动端侧栏
.mobile-nav-overlay {
  position: fixed;
  inset: 0;
  /* 低于 OpenTiny 下拉层 (PopupManager ~2000+)，避免遮挡抽屉内 select */
  z-index: 1900;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(2px);
}

.mobile-nav-drawer {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  width: min(320px, 88vw);
  background: #fff;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.12);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.mobile-nav-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid #e4e7ed;
}

.mobile-nav-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.mobile-nav-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: #666;
  cursor: pointer;
  transition: background-color 0.2s, color 0.2s;

  &:hover {
    background: #f5f5f5;
    color: var(--primary-color, #8b5cf6);
  }

  .mobile-nav-close-icon {
    width: 18px;
    height: 18px;
  }
}

.mobile-nav-links {
  display: flex;
  flex-direction: column;
  padding: 12px 0;
  border-bottom: 1px solid #e4e7ed;
}

.mobile-nav-item {
  display: block;
  padding: 12px 20px;
  color: #333;
  text-decoration: none;
  font-size: 15px;
  transition: background-color 0.2s, color 0.2s;

  &:hover {
    background: rgba(139, 92, 246, 0.08);
    color: var(--primary-color, #8b5cf6);
  }

  &.router-link-active {
    color: var(--primary-color, #8b5cf6);
    font-weight: 500;
    background: rgba(139, 92, 246, 0.1);
  }
}

.mobile-nav-settings {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mobile-nav-settings-title {
  font-size: 12px;
  font-weight: 600;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.mobile-nav-select {
  width: 100%;
}

.mobile-nav-enter-active,
.mobile-nav-leave-active {
  transition: opacity 0.25s ease;

  .mobile-nav-drawer {
    transition: transform 0.25s ease;
  }
}

.mobile-nav-enter-from,
.mobile-nav-leave-to {
  opacity: 0;

  .mobile-nav-drawer {
    transform: translateX(-100%);
  }
}

// 平板 / 窄屏 (≤1280px)：汉堡菜单 + 侧栏承载导航与设置
@media (max-width: 1280px) {
  .header-content {
    padding: 0 20px;
    gap: 12px;
  }

  .mobile-menu-btn {
    display: flex;
  }

  .search-section {
    margin-left: 0;
    max-width: none;
    flex: 1;
    min-width: 0;

    .search-trigger {
      min-width: 0;
      width: 100%;
      max-width: 200px;

      .search-shortcut {
        display: none;
      }
    }
  }

  .nav-menu {
    display: none !important;
  }

  .header-selects {
    display: none !important;
  }

  .header-actions {
    gap: 8px;
    flex-shrink: 0;
    margin-left: auto;
  }
}

// 手机 (≤768px)
@media (max-width: 768px) {
  .header {
    box-shadow: 0 1px 6px rgba(0, 0, 0, 0.08);
  }

  .header-content {
    padding: 0 12px;
    height: 56px;
    gap: 8px;
  }

  .logo-text {
    font-size: 20px;
  }

  .search-section .search-trigger:not(.search-trigger--icon-only) {
    min-width: 0;

    .search-placeholder {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }

  .header-actions .user-profile .user-name {
    display: none;
  }

  .search-modal {
    width: 95%;
    max-width: none;
    max-height: 90vh;
    min-height: 0;
    padding-top: 0;
  }

  .search-modal-overlay {
    padding-top: 5vh;
    align-items: flex-start;
  }

  .search-modal-header {
    padding: 16px;
  }

  .search-modal-footer {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;

    .search-shortcuts {
      flex-wrap: wrap;
      gap: 8px;
    }
  }
}

// 小屏手机 (≤480px)
@media (max-width: 480px) {
  .header-content {
    padding: 0 10px;
  }

  .header-actions {
    gap: 4px;
  }

  .header-actions .tiny-button {
    padding: 0 10px;
    font-size: 12px;
  }
}
</style>

<!-- 抽屉内 tiny-select 下拉需高于 .mobile-nav-overlay (1900) -->
<style lang="less">
body.mobile-nav-menu-open {
  [data-tag='tiny-select-dropdown tiny-popper'].mobile-nav-select-popper,
  .mobile-nav-select-popper[data-tag='tiny-select-dropdown tiny-popper'] {
    z-index: 2200 !important;
  }

  [data-tag='tiny-select-dropdown'] > div.fixed {
    z-index: 2200 !important;
  }
}
</style>
