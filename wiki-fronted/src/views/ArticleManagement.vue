<template>
  <div
    class="article-management-page"
    :class="{
      'article-management-page--editing': isEditing,
      'article-management-page--compact': isCompactLayout,
      'article-management-page--mobile': isMobileLayout
    }"
  >
    <div class="main-layout">
      <Transition name="tree-drawer-fade">
        <div
          v-if="isCompactLayout && mobileTreeDrawerOpen"
          class="tree-sidebar-overlay"
          aria-hidden="true"
          @click="closeMobileTreeDrawer"
        />
      </Transition>
      <!-- 左侧文章树 -->
      <aside
        class="tree-sidebar"
        :class="{ 'tree-sidebar--drawer-open': isCompactLayout && mobileTreeDrawerOpen }"
        :style="isCompactLayout ? undefined : { width: sidebarWidth + 'px' }"
      >
        <div class="sidebar-header">
          <div class="sidebar-header-stack">
            <Transition name="sidebar-cards-slide">
              <div
                v-show="sidebarCardsExpanded"
                :id="SIDEBAR_HEADER_MAIN_ID"
                class="sidebar-header-main"
              >
            <div
              v-if="knowledgeBase?.team_space_name"
              class="sidebar-team-space"
              :title="`${translate('nav.teamSpace')} · ${knowledgeBase.team_space_name}`"
              role="button"
              tabindex="0"
              @click.stop="openTeamSpacePageInNewWindow"
              @keydown.enter.prevent="openTeamSpacePageInNewWindow"
              @keydown.space.prevent="openTeamSpacePageInNewWindow"
            >
              <div class="sidebar-team-space-inner">
                <span class="sidebar-team-space-icon-wrap" aria-hidden="true">
                  <svg class="sidebar-team-space-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                    <circle cx="9" cy="7" r="4" />
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
                    <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                  </svg>
                </span>
                <div class="sidebar-team-space-text">
                  <span class="sidebar-team-space-label">{{ translate('nav.teamSpace') }}</span>
                  <div class="sidebar-team-space-title-row">
                    <span class="sidebar-team-space-name">{{ knowledgeBase.team_space_name }}</span>
                    <span
                      v-if="knowledgeBase.team_space_role !== undefined && knowledgeBase.team_space_role !== null"
                      class="role-badge sidebar-role-badge"
                      :class="getArticleMemberRoleClass(knowledgeBase.team_space_role)"
                    >
                      {{ getTeamSpaceMemberRoleText(knowledgeBase.team_space_role) }}
                    </span>
                  </div>
                </div>
                <span class="sidebar-team-space-open" aria-hidden="true" :title="translate('nav.teamSpace')">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                    <polyline points="15 3 21 3 21 9" />
                    <line x1="10" y1="14" x2="21" y2="3" />
                  </svg>
                </span>
              </div>
            </div>
            <div
              class="sidebar-title sidebar-title--clickable sidebar-title--card"
              :title="`${translate('knowledge.knowledgeBase')} · ${knowledgeBase?.name || translate('article.title')}`"
              @click="goToKnowledgeSpacePage"
            >
              <span class="sidebar-title-icon-wrap" aria-hidden="true">
                <svg
                  class="book-icon"
                  viewBox="0 0 24 24"
                  width="18"
                  height="18"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  aria-hidden="true"
                >
                  <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
                  <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
                </svg>
              </span>
              <span class="sidebar-title-body">
                <span class="sidebar-title-eyebrow">{{ translate('knowledge.knowledgeBase') }}</span>
                <div class="sidebar-title-title-row">
                  <span class="sidebar-title-name">{{ knowledgeBase?.name || translate('article.title') }}</span>
                  <span
                    v-if="knowledgeBase && knowledgeBase.knowledge_base_role !== undefined && knowledgeBase.knowledge_base_role !== null"
                    class="role-badge sidebar-role-badge"
                    :class="getArticleMemberRoleClass(knowledgeBase.knowledge_base_role)"
                  >
                    {{ getKnowledgeBaseMemberRoleText(knowledgeBase.knowledge_base_role) }}
                  </span>
                </div>
              </span>
              <span class="sidebar-title-open" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                  <polyline points="15 3 21 3 21 9" />
                  <line x1="10" y1="14" x2="21" y2="3" />
                </svg>
              </span>
            </div>

            <div v-if="canAddTreeArticles" class="sidebar-new-article">
              <tiny-dropdown trigger="click" placement="bottom-start" class="sidebar-new-article-dropdown">
                <template #default>
                  <div
                    class="sidebar-new-article-row sidebar-title sidebar-title--card sidebar-title--clickable"
                    :title="`${translate('article.addTop')} / ${translate('article.addBottom')}`"
                    role="button"
                    tabindex="0"
                  >
                    <span class="sidebar-title-icon-wrap" aria-hidden="true">
                      <svg
                        class="sidebar-new-article-glyph"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      >
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                        <polyline points="14 2 14 8 20 8" />
                        <line x1="12" y1="11" x2="12" y2="17" />
                        <line x1="9" y1="14" x2="15" y2="14" />
                      </svg>
                    </span>
                    <span class="sidebar-title-body">
                      <span class="sidebar-title-eyebrow">{{ translate('article.title') }}</span>
                      <span class="sidebar-title-name">{{ translate('article.newArticle') }}</span>
                    </span>
                    <span class="sidebar-title-open" aria-hidden="true">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                        <polyline points="15 3 21 3 21 9" />
                        <line x1="10" y1="14" x2="21" y2="3" />
                      </svg>
                    </span>
                  </div>
                </template>
                <template #dropdown>
                  <tiny-dropdown-menu class="article-new-dropdown-menu">
                    <tiny-dropdown-item @click="handleAddTop">
                      <span class="article-add-fab-menu-item">
                        <span class="article-add-fab-menu-dot article-add-fab-menu-dot--top" aria-hidden="true" />
                        {{ translate('article.addTop') }}
                      </span>
                    </tiny-dropdown-item>
                    <tiny-dropdown-item @click="handleAddBottom">
                      <span class="article-add-fab-menu-item">
                        <span class="article-add-fab-menu-dot article-add-fab-menu-dot--bottom" aria-hidden="true" />
                        {{ translate('article.addBottom') }}
                      </span>
                    </tiny-dropdown-item>
                  </tiny-dropdown-menu>
                </template>
              </tiny-dropdown>
            </div>
              </div>
            </Transition>
            <button
              type="button"
              class="sidebar-cards-flat-trigger"
              :aria-expanded="sidebarCardsExpanded"
              :aria-controls="SIDEBAR_HEADER_MAIN_ID"
              :title="
                sidebarCardsExpanded
                  ? translate('article.collapseSidebarCards')
                  : translate('article.expandSidebarCards')
              "
              @click="toggleSidebarCards"
            >
              <span class="sidebar-cards-flat-trigger-line" aria-hidden="true" />
              <svg
                class="sidebar-cards-flat-trigger-chevron"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="1.5"
                stroke-linecap="round"
                stroke-linejoin="round"
                aria-hidden="true"
              >
                <polyline points="7 10 12 15 17 10" />
              </svg>
            </button>
          </div>
        </div>
        <!-- 搜索框 -->
        <div class="tree-search">
          <tiny-input
            v-model="filterText"
            :placeholder="translate('article.searchPlaceholder')"
            size="small"
            clearable
            class="tree-search-input"
          >
            <template #prefix>
              <component :is="TinyIconSearch" class="search-icon" />
            </template>
          </tiny-input>
        </div>
        <div class="tree-container">
          <LoadingSpinner v-if="loading" :absolute="false" />
          <tiny-tree
            v-if="!loading"
            ref="treeRef"
            node-key="id"
            :expand-on-click-node="false"
            :data="treeData"
            :props="treeProps"
            :highlight-current="true"
            :default-expand-all="false"
            :filter-node-method="filterNode"
            :draggable="hasArticleCategoryMovePermission"
            :allow-drag="allowDrag"
            :allow-drop="allowDrop"
            @node-click="handleNodeClick"
            @node-expand="handleNodeExpand"
            @node-drag-start="handleNodeDragStart"
            @node-drop="handleNodeDrop"
            :default-expanded-keys="defaultExpandedKeys"
          >
            <template #default="{ node, data }">
              <template v-if="!data.isTemp">
                <div class="tree-node-wrapper" @dblclick.stop="handleNodeDoubleClick(data)">
                  <span class="tree-node-label">
                    <span class="node-icon" aria-hidden="true">
                      <svg
                        v-if="!isTreeNodeChildrenLoading(data.id) && data.node_type !== 2"
                        class="node-icon-svg"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      >
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                        <polyline points="14 2 14 8 20 8" />
                        <line x1="16" y1="13" x2="8" y2="13" />
                        <line x1="16" y1="17" x2="8" y2="17" />
                        <line x1="10" y1="9" x2="8" y2="9" />
                      </svg>
                      <svg
                        v-else-if="!isTreeNodeChildrenLoading(data.id) && data.node_type === 2"
                        class="node-icon-svg"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        aria-hidden="true"
                      >
                        <path d="M3 7v11a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-7l-2-2H5a2 2 0 0 0-2 2z" />
                      </svg>
                      <svg
                        v-else
                        class="node-icon-svg node-icon-svg--loading"
                        viewBox="0 0 24 24"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                        aria-hidden="true"
                      >
                        <circle
                          cx="12"
                          cy="12"
                          r="9"
                          stroke="currentColor"
                          stroke-width="2"
                          stroke-linecap="round"
                          stroke-dasharray="32 48"
                        />
                      </svg>
                    </span>
                    <span class="tree-node-title" :title="String(node.label || '')">{{ node.label }}</span>
                  </span>
                  <div 
                    class="node-actions" 
                    :class="{ 'dropdown-visible': dropdownVisibleNodeId === data.id }"
                    @click.stop
                  >
                    <tiny-dropdown 
                      v-if="canAddTreeArticles"
                      title="" 
                      :suffix-icon="TinyIconPlusSquare" 
                      class="node-action-icon"
                      @visible-change="handleDropdownVisibleChange($event, data.id)"
                    >
                      <template #dropdown>
                        <tiny-dropdown-menu class="node-add-menu">
                          <tiny-dropdown-item @click="handleInsertBefore(data)">
                            <div class="menu-item-content">
                              <component :is="TinyIconArrowUp" class="menu-icon" />
                              <span>{{ translate('tree.insertBefore') }}</span>
                            </div>
                          </tiny-dropdown-item>
                          <tiny-dropdown-item @click="handleInsertAfter(data)">
                            <div class="menu-item-content">
                              <component :is="TinyIconArrowDown" class="menu-icon" />
                              <span>{{ translate('tree.insertAfter') }}</span>
                            </div>
                          </tiny-dropdown-item>
                          <tiny-dropdown-item @click="handleAddChild(data)">
                            <div class="menu-item-content">
                              <component :is="TinyIconAdd" class="menu-icon" />
                              <span>{{ translate('tree.addChild') }}</span>
                            </div>
                          </tiny-dropdown-item>
                        </tiny-dropdown-menu>
                      </template>
                    </tiny-dropdown>
                    <tiny-dropdown 
                      title="" 
                      :suffix-icon="TinyIconMore" 
                      class="node-action-icon"
                      @visible-change="handleDropdownVisibleChange($event, data.id)"
                    >
                      <template #dropdown>
                        <tiny-dropdown-menu class="node-settings-menu">
                          <tiny-dropdown-item @click="handleTreeNodeEdit(data)" v-if="treeNodeCanEdit(data)">
                            <div class="menu-item-content">
                              <component :is="TinyIconEdit" class="menu-icon" />
                              <span>{{ translate('article.edit') }}</span>
                            </div>
                          </tiny-dropdown-item>
                          <tiny-dropdown-item @click="handleTreeNodeManageMembers(data)" v-if="treeNodeCanAdmin(data)">
                            <div class="menu-item-content">
                              <component :is="TinyIconUser" class="menu-icon" />
                              <span>{{ translate('article.manageMembers') }}</span>
                            </div>
                          </tiny-dropdown-item>
                          <tiny-dropdown-item @click="handleTreeNodeDelete(data)" v-if="treeNodeCanAdmin(data)">
                            <div class="menu-item-content">
                              <component :is="TinyIconDelete" class="menu-icon" />
                              <span>{{ translate('tree.delete') }}</span>
                            </div>
                          </tiny-dropdown-item>
                        </tiny-dropdown-menu>
                      </template>
                    </tiny-dropdown>
                  </div>
                </div>
              </template>
              <template v-else>
                <div
                  class="tree-node-edit"
                  @click.stop
                  @focusout="handleTempNodeFocusOut($event, data)"
                >
                  <tiny-select
                    v-model="data.node_type"
                    size="small"
                    class="temp-node-type-select"
                    :placeholder="translate('article.nodeType')"
                    @click.stop
                  >
                    <tiny-option :value="1" :label="translate('article.nodeTypeArticle')" />
                    <tiny-option :value="2" :label="translate('article.nodeTypeDirectory')" />
                  </tiny-select>
                  <tiny-select
                    v-model="data.visibility"
                    size="small"
                    class="temp-node-vis-select"
                    :placeholder="translate('knowledgeBase.visibility')"
                    @click.stop
                  >
                    <tiny-option :value="1" :label="translate('knowledgeBase.visibility.private')" />
                    <tiny-option :value="2" :label="translate('knowledgeBase.visibility.member')" />
                    <tiny-option :value="3" :label="translate('knowledgeBase.visibility.public')" />
                  </tiny-select>
                  <tiny-input
                    :ref="el => setTempInputRef(data.id, el)"
                    v-model="data.label"
                    :placeholder="translate('article.titlePlaceholder')"
                    size="small"
                    @keyup.enter="handleSaveTempNode(data)"
                    class="temp-node-input"
                  />
                  <div class="edit-actions">
                    <span
                      class="icon-button icon-button-check"
                      @mousedown="markTempNodeActionPointerDown"
                      @click.stop="handleClickSave(data)"
                      :title="translate('common.confirm')"
                    >
                      <component :is="TinyIconYes" />
                    </span>
                    <span
                      class="icon-button icon-button-cancel"
                      @mousedown="markTempNodeActionPointerDown"
                      @click.stop="handleCancelTempNode(data)"
                      :title="translate('common.cancel')"
                    >
                      <component :is="TinyIconClose" />
                    </span>
                  </div>
                </div>
              </template>
            </template>
          </tiny-tree>
          <div v-if="treeData.length === 0 && !loading" class="empty-state">
            <p>{{ translate('article.empty') }}</p>
          </div>
        </div>
      </aside>
      
      <!-- 可拖拽的分隔条（紧凑布局下隐藏） -->
      <div
        v-if="!isCompactLayout"
        class="sidebar-resizer"
        @mousedown="handleResizeStart"
        :class="{ resizing: isResizing }"
      >
        <div class="resizer-icon">
          <svg viewBox="0 0 1024 1024" width="16" height="16" fill="currentColor">
            <path d="M384 128h64v768h-64zM576 128h64v768h-64z"/>
          </svg>
        </div>
      </div>

      <!-- 右侧文章详情 -->
      <main ref="contentAreaRef" class="content-area" :class="{ 'content-area--editing': isEditing }">
        <div v-if="isCompactLayout && !isEditing" class="content-mobile-toolbar">
          <button
            type="button"
            class="content-mobile-toolbar__btn"
            :aria-label="translate('article.articleTree')"
            :aria-expanded="mobileTreeDrawerOpen"
            @click="toggleMobileTreeDrawer"
          >
            <svg viewBox="0 0 1024 1024" width="18" height="18" fill="currentColor" aria-hidden="true">
              <path d="M128 256h768v64H128v-64zm0 352h768v64H128v-64zm0 352h768v64H128v-64z"/>
            </svg>
            <span>{{ translate('article.articleTree') }}</span>
          </button>
          <p v-if="selectedArticle" class="content-mobile-toolbar__title">{{ selectedArticle.title }}</p>
        </div>
        <!-- 加载动画 -->
        <LoadingSpinner v-if="articleLoading" :absolute="true" />
        
        <div v-else-if="selectedArticle" class="article-detail" :class="{ 'article-detail--editing': isEditing }">
          <div class="article-header" :class="{ 'article-header--editing': isEditing }">
            <div class="article-title-wrapper">
              <h1 v-if="!isEditingArticleTitle" class="article-title" @click="hasArticleMemberRole ? handleArticleTitleClick() : undefined">
                {{ selectedArticle.title }}
                <span v-if="hasArticleMemberRole" class="edit-icon" @click.stop="handleArticleTitleClick">
                  <svg viewBox="0 0 1024 1024" width="14" height="14" fill="currentColor">
                    <path d="M832 512a32 32 0 1 1 64 0v352a32 32 0 0 1-32 32H160a32 32 0 0 1-32-32V160a32 32 0 0 1 32-32h352a32 32 0 0 1 0 64H192v640h640V512z"/>
                    <path d="M469.952 554.24l45.248-45.248 141.888 141.888-45.248 45.248zM832 128a32 32 0 0 1 9.408 62.592l-9.408 1.408-192 192a32 32 0 0 1-45.248-45.248L786.752 128H832z"/>
                  </svg>
                </span>
              </h1>
              <div v-else class="article-title-edit" @click.stop>
                <tiny-input
                  ref="articleTitleInputRef"
                  v-model="editingArticleTitle"
                  @keyup.enter="handleSaveArticleTitle"
                  @blur="handleSaveArticleTitle"
                  class="title-input"
                />
                <div class="title-edit-actions">
                  <span class="icon-button icon-button-check" @click="handleSaveArticleTitle">
                    <component :is="TinyIconYes" />
                  </span>
                  <span class="icon-button icon-button-cancel" @click="handleCancelArticleTitleEdit">
                    <component :is="TinyIconClose" />
                  </span>
                </div>
              </div>
              <div class="article-actions">
                <template v-if="!isEditing">
                  <tiny-button 
                    v-if="hasArticleMemberRole"
                    type="primary" 
                    @click="handleStartEdit"
                  >
                    {{ translate('article.edit') }}
                  </tiny-button>
                  <tiny-button
                    v-if="false && selectedArticle?.id && hasCreateReadTaskPermission"
                    style="margin-left: 8px;"
                    @click="openSignReadDialog"
                  >
                    {{ translate('article.signRead') }}
                  </tiny-button>
                  <tiny-button 
                    v-if="selectedArticle?.id && hasArticleMemberRole" 
                    @click="handleUploadAttachment"
                    :loading="attachmentUploading"
                    style="margin-left: 8px;"
                  >
                    <component :is="TinyIconPlusSquare" style="margin-right: 4px;" />
                    {{ translate('article.uploadAttachment') }}
                  </tiny-button>
                  <tiny-button 
                    v-if="false && selectedArticle?.id && hasArticleMemberRole" 
                    @click="showHistoryDrawer = true"
                    style="margin-left: 8px;"
                  >
                    {{ translate('article.history.title') }}
                  </tiny-button>
                </template>
                <template v-else>
                  <div class="article-edit-toolbar-flags">
                    <div class="article-header-edit-flag">
                      <span class="article-header-edit-flag__icon" aria-hidden="true">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M12 20h9" />
                          <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
                        </svg>
                      </span>
                      <span class="article-header-edit-flag__label">{{ translate('article.isOriginal') }}</span>
                      <tiny-switch v-model="editingIsOriginal" />
                    </div>
                    <div class="article-header-edit-flag">
                      <span class="article-header-edit-flag__icon" aria-hidden="true">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3L12 3Z" />
                          <path d="M5 3v4" />
                          <path d="M19 17v4" />
                          <path d="M3 5h4" />
                          <path d="M17 19h4" />
                        </svg>
                      </span>
                      <span class="article-header-edit-flag__label">{{ translate('article.isAiGenerated') }}</span>
                      <tiny-switch v-model="editingIsAiGenerated" />
                    </div>
                    <div class="article-header-edit-flag article-header-edit-flag--tags">
                      <span class="article-header-edit-flag__icon" aria-hidden="true">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                          <path d="M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4a2 2 0 0 0-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42zM5.5 7A1.5 1.5 0 1 1 7 5.5 5.5 5.5 0 0 1 5.5 7z" />
                        </svg>
                      </span>
                      <span class="article-header-edit-flag__label">{{ translate('article.tags') }}</span>
                      <!-- 不使用 click-expand：该模式会给 tags-group 加 position:absolute，在工具栏 flex 内易错位；多选折叠用 collapse-tags 即可 -->
                      <tiny-select
                        v-model="editingTagIds"
                        multiple
                        filterable
                        collapse-tags
                        clearable
                        size="small"
                        :loading="kbTagsLoading"
                        :placeholder="translate('article.kbTagsSelectPlaceholder')"
                        class="article-edit-tags-select"
                      >
                        <tiny-option
                          v-for="tag in kbTagsForEdit"
                          :key="tag.id"
                          :label="tag.name"
                          :value="tag.id"
                        />
                      </tiny-select>
                    </div>
                  </div>
                  <tiny-button @click="handleCancelEdit">
                    {{ translate('common.cancel') }}
                  </tiny-button>
                  <tiny-button type="primary" @click="handleSaveArticle" :loading="saving">
                    {{ translate('common.save') }}
                  </tiny-button>
                </template>
              </div>
            </div>
            <!-- 签读状态/倒计时/完成区域（仅在非编辑状态下显示） -->
            <div
              v-if="!isEditing && signReadCheck?.need_sign_read && signReadCheck.status !== undefined"
              :class="['sign-read-banner', `sign-read-banner--status-${signReadCheck.status}`]"
            >
              <div class="sign-read-status-row">
                <span v-if="signReadRemainingSeconds > 0 && signReadCheck.status === 1" class="sign-read-time-badge">
                  {{ formatSignReadTime(signReadRemainingSeconds) }}
                </span>
                <span class="sign-read-status-value">{{ getSignReadStatusText(signReadCheck.status) }}</span>
              </div>
              <div v-if="signReadCheck.created_by_name || signReadCheck.created_at || signReadCheck.deadline" class="sign-read-meta-row">
                <span v-if="signReadCheck.created_by_name" class="sign-read-meta-item">
                  {{ translate('article.signReadCreatedBy') }}: {{ signReadCheck.created_by_name }}
                </span>
                <span v-if="signReadCheck.created_at" class="sign-read-meta-item">
                  {{ translate('article.signReadCreatedAt') }}: {{ formatSignReadDateTime(signReadCheck.created_at) }}
                </span>
                <span v-if="signReadCheck.deadline" class="sign-read-meta-item">
                  {{ translate('article.signReadDeadline') }}: {{ formatSignReadDateTime(signReadCheck.deadline) }}
                </span>
              </div>
              <template v-if="signReadCheck.status === 0 || signReadCheck.status === 1">
                <div v-if="signReadRemainingSeconds <= 0" class="sign-read-complete">
                  <tiny-button type="primary" :loading="signReadCompleting" @click="handleSignReadComplete">
                    {{ translate('article.signReadComplete') }}
                  </tiny-button>
                </div>
              </template>
            </div>
          </div>
          <div class="article-content-wrapper" :class="{ 'article-content-wrapper--editing': isEditing }">
            <div class="article-content">
              
              
              <div v-if="selectedArticle.content || isEditing" :class="['editor-container', { 'editor-preview': !isEditing }]">
                <FluentEditorV4
                  v-if="isEditing"
                  ref="editorRef"
                  v-model="editorContent"
                  :article-id="selectedArticle.id"
                  :show-edit-toc="true"
                />
                <FluentEditorV4
                  v-else
                  ref="previewRef"
                  :model-value="editorContent"
                  :article-id="selectedArticle.id"
                  :readonly="true"
                  :show-edit-toc="false"
                  :show-floating-scroll-actions="false"
                />
              </div>
              <div v-else class="empty-content">
                <p>{{ translate('article.emptyContent') }}</p>
              </div>
              <div
                v-if="!isEditing && articleDisplayTagNames.length > 0"
                class="article-tags article-tags--content-footer"
              >
                <span class="article-tags__lead-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4a2 2 0 0 0-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42zM5.5 7A1.5 1.5 0 1 1 7 5.5 5.5 5.5 0 0 1 5.5 7z" />
                  </svg>
                </span>
                <div class="article-tags__chips">
                  <span
                    v-for="(tag, idx) in articleDisplayTagNames"
                    :key="`${tag}-${idx}`"
                    class="tag tag--theme"
                  >
                    {{ tag }}
                  </span>
                </div>
              </div>
              <div v-if="!isEditing" class="article-meta">
              <div class="article-meta__main">
                <div class="meta-text-line">
                  <span v-if="selectedArticle.author_id" class="meta-item">
                    {{ translate('article.author') }}: {{ selectedArticle.author_name }}
                  </span>
                  <span v-if="selectedArticle.created_at" class="meta-item">
                    {{ translate('article.createdAt') }}: {{ formatDate(selectedArticle.created_at) }}
                  </span>
                  <span v-if="selectedArticle.updated_by_name" class="meta-item">
                    {{ translate('article.updatedBy') }}: {{ selectedArticle.updated_by_name }}
                  </span>
                  <span v-if="selectedArticle.updated_at" class="meta-item">
                    {{ translate('article.updatedAt') }}: {{ formatDate(selectedArticle.updated_at) }}
                  </span>
                  <div
                    v-if="hasArticleMetaBadges"
                    class="meta-badge-strip meta-badge-strip--after-updated"
                  >
                    <span
                      v-if="selectedArticle.visibility !== undefined && selectedArticle.visibility !== null"
                      class="meta-visibility-badge"
                      :class="`meta-visibility-badge--${selectedArticle.visibility}`"
                      :title="translate('knowledgeBase.visibility')"
                    >
                      <!-- 私有：锁图标 -->
                      <svg v-if="selectedArticle.visibility === 1" class="visibility-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                        <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                        <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                      </svg>
                      <!-- 成员：用户组图标 -->
                      <svg v-else-if="selectedArticle.visibility === 2" class="visibility-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                        <circle cx="9" cy="7" r="4"></circle>
                        <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                        <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                      </svg>
                      <!-- 公开：地球图标 -->
                      <svg v-else-if="selectedArticle.visibility === 3" class="visibility-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                        <circle cx="12" cy="12" r="10"></circle>
                        <path d="M2 12h20"></path>
                        <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>
                      </svg>
                      <span class="visibility-text">{{ formatVisibility(selectedArticle.visibility) }}</span>
                    </span>
                    <span
                      v-if="selectedArticle.is_original === true"
                      class="meta-flag-badge meta-flag-badge--original"
                      :title="translate('article.badgeOriginal')"
                    >
                      <svg class="meta-flag-badge__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <path d="M12 20h9" />
                        <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
                      </svg>
                      <span>{{ translate('article.badgeOriginal') }}</span>
                    </span>
                    <span
                      v-if="selectedArticle.is_ai_generated === true"
                      class="meta-flag-badge meta-flag-badge--ai"
                      :title="translate('article.badgeAiGenerated')"
                    >
                      <svg class="meta-flag-badge__icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3L12 3Z" />
                        <path d="M5 3v4M19 17v4M3 5h4M17 19h4" />
                      </svg>
                      <span>{{ translate('article.badgeAiGenerated') }}</span>
                    </span>
                  </div>
                </div>
              </div>
              <div class="meta-right">
                <span v-if="selectedArticle.view_count !== undefined && selectedArticle.view_count !== null" class="stat-item" :title="translate('article.viewCount')">
                  <svg class="stat-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                  </svg>
                  <span class="stat-value">{{ selectedArticle.view_count }}</span>
                </span>
                <span v-if="selectedArticle.like_count !== undefined && selectedArticle.like_count !== null" class="stat-item" :title="translate('article.likeCount')">
                  <component :is="TinyIconHeartempty" class="stat-icon" />
                  <span class="stat-value">{{ selectedArticle.like_count }}</span>
                </span>
                <span v-if="selectedArticle.collect_count !== undefined && selectedArticle.collect_count !== null" class="stat-item" :title="translate('article.collectCount')">
                  <component :is="TinyIconStarO" class="stat-icon" />
                  <span class="stat-value">{{ selectedArticle.collect_count }}</span>
                </span>
                <span v-if="selectedArticle.comment_count !== undefined && selectedArticle.comment_count !== null" class="stat-item" :title="translate('article.commentCount')">
                  <component :is="TinyIconMessageCircle" class="stat-icon" />
                  <span class="stat-value">{{ selectedArticle.comment_count }}</span>
                </span>
                <span v-if="selectedArticle.feedback_count !== undefined && selectedArticle.feedback_count !== null" class="stat-item" :title="translate('article.feedbackCount')">
                  <component :is="TinyIconFeedback" class="stat-icon" />
                  <span class="stat-value">{{ selectedArticle.feedback_count }}</span>
                </span>
              </div>
            </div>
            </div>
            
            <!-- 附件区域 - 编辑模式下不显示 -->
            <Transition :name="isEditing ? 'article-attachments-edit' : 'article-attachments-reveal'">
              <div
                v-if="selectedArticle && attachmentsVisible && !isEditing"
                class="article-attachments-rail"
                key="article-attachments-rail"
                @click.self="isMobileLayout && toggleAttachments()"
              >
                <div class="article-attachments-wrapper">
                  <div class="article-attachments">
              <div class="attachments-header">
                <h3 class="attachments-title">
                  <svg class="attachment-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path>
                  </svg>
                  {{ translate('article.attachments') }}
                  <span class="attachments-count">({{ attachments.length }})</span>
                </h3>
              </div>
              
              <LoadingSpinner v-if="attachmentsLoading" :absolute="false" />
              
              <div v-else-if="attachments.length > 0" class="attachments-list">
                <div 
                  v-for="attachment in attachments" 
                  :key="attachment.id"
                  class="attachment-item"
                  :class="{ 'attachment-previewable': isPreviewable(attachment) }"
                  @click="handleAttachmentClick(attachment)"
                >
                  <div class="attachment-icon-wrapper">
                    <span class="attachment-file-icon">{{ getFileIcon(attachment.filename, attachment.file_type) }}</span>
                  </div>
                  <div class="attachment-info">
                    <div class="attachment-name" :title="attachment.filename">
                      {{ attachment.filename }}
                    </div>
                    <div class="attachment-meta">
                      <span class="attachment-size">{{ formatFileSize(attachment.file_size) }}</span>
                      <span v-if="attachment.created_at" class="attachment-date">
                        {{ formatDate(attachment.created_at) }}
                      </span>
                    </div>
                  </div>
                  <div class="attachment-actions" @click.stop>
                    <button
                      v-if="isPreviewable(attachment)"
                      class="attachment-preview-btn"
                      :title="translate('article.previewAttachment')"
                      @click.stop="handleAttachmentClick(attachment)"
                    >
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                        <circle cx="12" cy="12" r="3"></circle>
                      </svg>
                    </button>
                    <a 
                      :href="attachment.file_url" 
                      :download="attachment.filename"
                      class="attachment-download-btn"
                      :title="translate('article.downloadAttachment')"
                    >
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="7 10 12 15 17 10"></polyline>
                        <line x1="12" y1="15" x2="12" y2="3"></line>
                      </svg>
                    </a>
                    <button
                      v-if="hasArticleMemberRole"
                      class="attachment-delete-btn"
                      :title="translate('article.deleteAttachment')"
                      @click.stop="handleDeleteAttachment(attachment)"
                    >
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                        <line x1="10" y1="11" x2="10" y2="17"></line>
                        <line x1="14" y1="11" x2="14" y2="17"></line>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
              
              <div v-else class="attachments-empty">
                <p>{{ translate('article.noAttachments') }}</p>
              </div>
              
              <!-- 隐藏的文件输入 -->
              <input
                ref="attachmentFileInputRef"
                type="file"
                multiple
                style="display: none"
                @change="handleAttachmentFileChange"
              />
                  </div>
                </div>
              </div>
            </Transition>
            
            <Transition :name="isEditing ? 'article-toc-edit' : 'article-toc-reveal'">
              <div
                v-if="!isEditing && tocVisible"
                class="article-toc-rail"
                key="article-toc-rail"
                @click.self="isMobileLayout && toggleToc()"
              >
                <!-- 目录分隔条 -->
                <div
                  class="toc-resizer"
                  @mousedown="handleTocResizeStart"
                  :class="{ resizing: isTocResizing }"
                >
                  <div class="toc-resizer-handle" @mousedown="handleTocResizeStart">
                    <svg viewBox="0 0 1024 1024" width="12" height="12" fill="currentColor">
                      <path d="M384 128h64v768h-64zM576 128h64v768h-64z" />
                    </svg>
                  </div>
                </div>

                <!-- 文章目录 -->
                <aside
                  class="article-toc"
                  :class="{ 'article-toc--mobile-sheet': isMobileLayout }"
                  :style="isMobileLayout ? undefined : { width: tocWidth + 'px' }"
                >
                  <div v-if="isMobileLayout" class="toc-sheet-handle" aria-hidden="true" />
                  <div class="toc-header">
                    <h3 class="toc-title">{{ translate('article.tableOfContents') }}</h3>
                    <button
                      type="button"
                      class="toc-collapse-btn"
                      @click.stop="toggleToc"
                      :title="translate('article.hideToc')"
                      :aria-label="translate('article.hideToc')"
                    >
                      <component :is="isMobileLayout ? TinyIconClose : TinyIconChevronRight" />
                    </button>
                  </div>
                  <div ref="tocTreeContainerRef" class="toc-tree-container">
                    <LoadingSpinner v-if="tocLoading" :absolute="false" :show-text="true" />
                    <tiny-tree
                      v-else-if="tocTreeData && tocTreeData.length > 0"
                      :data="tocTreeData"
                      :expand-on-click-node="false"
                      :props="{ children: 'children', label: 'label' }"
                      node-key="id"
                      :default-expand-all="true"
                      :highlight-current="false"
                      @node-click="handleTocNodeClick"
                    >
                      <template #default="{ node, data }">
                        <span
                          class="toc-tree-node"
                          :class="{ 'is-toc-active': tocActiveHeadingId === data.id }"
                          :data-toc-id="data.id"
                          @click="scrollToHeading(data.id)"
                        >
                          {{ node.label }}
                        </span>
                      </template>
                    </tiny-tree>
                    <div v-else-if="!tocLoading" class="toc-empty">
                      {{ translate('article.emptyContent') }}
                    </div>
                  </div>
                </aside>
              </div>
            </Transition>

            <!-- 右侧操作按钮栏 -->
            <Transition name="mobile-actions-fade">
              <div
                v-if="isMobileLayout && mobileActionsExpanded"
                class="mobile-actions-backdrop"
                aria-hidden="true"
                @click="closeMobileActionsSheet"
              />
            </Transition>
            <div
              v-if="!isEditing"
              class="article-actions-bar"
              :class="{
                'article-actions-bar--mobile': isMobileLayout,
                'article-actions-bar--expanded': mobileActionsExpanded,
                'article-actions-bar--concealed': isMobileLayout && (tocVisible || attachmentsVisible)
              }"
            >
            <button
              v-if="hasArticleMemberRole"
              class="action-btn"
              data-mobile-tier="dock"
              @click="handleStartEdit"
              :title="translate('article.edit')"
            >
              <svg class="action-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 20h9" />
                <path d="M16.5 3.5a2.121 2.121 0 1 1 3 3L7 19l-4 1 1-4 12.5-12.5z" />
              </svg>
              <span class="action-text">{{ translate('article.edit') }}</span>
            </button>
            <button
              v-if="isMobileLayout"
              type="button"
              class="action-btn action-btn--more"
              data-mobile-tier="dock"
              :class="{ 'is-active': mobileActionsExpanded }"
              :title="translate('article.moreActions')"
              :aria-label="translate('article.moreActions')"
              :aria-expanded="mobileActionsExpanded"
              @click="mobileActionsExpanded = !mobileActionsExpanded"
            >
              <component :is="TinyIconMore" class="action-icon" />
              <span class="action-text">{{ translate('article.moreActions') }}</span>
            </button>
            <button
              v-if="false && selectedArticle?.id && hasCreateReadTaskPermission"
              class="action-btn"
              data-mobile-tier="sheet"
              @click="openSignReadDialog"
              :title="translate('article.signRead')"
            >
              <svg class="action-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 8v4l3 3" />
                <circle cx="12" cy="12" r="9" />
              </svg>
              <span class="action-text">{{ translate('article.signRead') }}</span>
            </button>
            <button
              class="action-btn"
              data-mobile-tier="dock"
              :class="{ 'is-active': tocVisible }"
              @click="toggleToc"
              :title="translate('article.tableOfContents')"
            >
              <component :is="TinyIconListMode" class="action-icon" />
              <span class="action-text">{{ translate('article.tableOfContents') }}</span>
            </button>
            <button
              class="action-btn"
              data-mobile-tier="dock"
              :class="{ 'is-active': attachmentsVisible }"
              @click="toggleAttachments"
              :title="translate('article.attachments')"
            >
              <svg class="action-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path>
              </svg>
              <span class="action-text">{{ translate('article.attachments') }}</span>
            </button>
            <button
              v-if="hasArticleMemberRole && selectedArticle?.id"
              class="action-btn"
              data-mobile-tier="sheet"
              type="button"
              :disabled="attachmentUploading"
              @click="handleUploadAttachment"
              :title="translate('article.uploadAttachment')"
            >
              <component :is="TinyIconPlusSquare" class="action-icon" />
              <span class="action-text">{{ translate('article.uploadAttachment') }}</span>
            </button>
            <button
              class="action-btn"
              data-mobile-tier="sheet"
              :class="{ 'is-active': isLiked }"
              @click="handleLike"
              :title="translate('article.like')"
            >
              <IconHeartFill v-if="isLiked" class="action-icon" :color="'var(--primary-color, #8b5cf6)'" />
              <component v-else :is="TinyIconHeartempty" class="action-icon" />
              <span class="action-text">{{ translate('article.like') }}</span>
            </button>
            <button
              class="action-btn"
              data-mobile-tier="sheet"
              :class="{ 'is-active': isFavorited }"
              @click="handleFavorite"
              :title="translate('article.favorite')"
            >
              <component :is="isFavorited ? TinyIconStarActive : TinyIconStarO" class="action-icon" />
              <span class="action-text">{{ translate('article.favorite') }}</span>
            </button>
            <button
              class="action-btn"
              data-mobile-tier="sheet"
              @click="handleComment"
              :title="translate('article.comment')"
            >
              <component :is="TinyIconMessageCircle" class="action-icon" />
              <span class="action-text">{{ translate('article.comment') }}</span>
            </button>
            <button
              class="action-btn"
              data-mobile-tier="sheet"
              @click="handleFeedback"
              :title="translate('article.feedback')"
            >
              <component :is="TinyIconFeedback" class="action-icon" />
              <span class="action-text">{{ translate('article.feedback') }}</span>
            </button>
            <button
              class="action-btn"
              data-mobile-tier="sheet"
              @click="scrollPreviewToTop"
              :title="translate('article.backToTop')"
            >
              <svg class="action-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 19V5" />
                <path d="m5 12 7-7 7 7" />
              </svg>
              <span class="action-text">{{ translate('article.backToTop') }}</span>
            </button>
            <button
              class="action-btn"
              data-mobile-tier="sheet"
              @click="scrollPreviewToBottom"
              :title="translate('article.backToBottom')"
            >
              <svg class="action-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 5v14" />
                <path d="m19 12-7 7-7-7" />
              </svg>
              <span class="action-text">{{ translate('article.backToBottom') }}</span>
            </button>
          </div>

          </div>
        </div>
        <div v-else-if="articleLoadError === 'permission'" class="article-error-panel article-error-permission">
          <div class="article-error-card">
            <div class="article-error-icon-wrap article-error-icon-lock">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
            </div>
            <h3 class="article-error-heading">{{ translate('article.noPermission') }}</h3>
            <p class="article-error-desc">{{ translate('article.noPermissionHint') }}</p>
            <tiny-button type="primary" class="article-apply-trigger-btn" @click="handleApplyForArticleAccess">
              {{ translate('article.applyForEdit') }}
            </tiny-button>
            <transition name="article-apply-slide">
              <div v-if="showApplyEditForm" class="article-apply-edit-form">
                <div class="article-apply-field">
                  <label class="article-apply-edit-label">{{ translate('article.applyRoleLabel') }}</label>
                  <tiny-select
                    v-model="applyEditRole"
                    :placeholder="translate('article.applyRolePlaceholder')"
                    class="article-apply-role-select"
                  >
                    <tiny-option
                      v-for="option in applyRoleOptions"
                      :key="option.value"
                      :label="translate(option.labelKey)"
                      :value="option.value"
                    />
                  </tiny-select>
                </div>
                <div class="article-apply-field">
                  <label class="article-apply-edit-label">
                    {{ translate('article.applyReviewersLabel') }}
                    <span class="article-apply-optional-hint">{{ translate('article.optional') }}</span>
                  </label>
                  <tiny-select
                    v-model="applyReviewerIds"
                    multiple
                    :placeholder="translate('article.applyReviewersPlaceholder')"
                    class="article-apply-reviewers-select"
                    :disabled="articleAdminsLoading || articleAdmins.length === 0"
                  >
                    <tiny-option
                      v-for="admin in articleAdmins"
                      :key="admin.id"
                      :label="admin.username || admin.email || String(admin.user_id)"
                      :value="admin.id"
                    />
                  </tiny-select>
                  <p v-if="articleAdmins.length === 0 && !articleAdminsLoading" class="article-apply-reviewers-empty">
                    {{ translate('article.noAdminsForReview') }}
                  </p>
                </div>
                <div class="article-apply-field">
                  <label class="article-apply-edit-label">{{ translate('article.remarkLabel') }}</label>
                  <tiny-input
                    v-model="applyEditRemark"
                    type="textarea"
                    :placeholder="translate('article.applyEditRemarkPlaceholder')"
                    :rows="4"
                    class="article-apply-edit-remark"
                  />
                </div>
            <div class="article-apply-edit-actions">
                  <tiny-button :disabled="applyEditSubmitting" @click="showApplyEditForm = false">
                    {{ translate('common.cancel') }}
                  </tiny-button>
                  <tiny-button type="primary" :loading="applyEditSubmitting" @click="handleSubmitApplyEdit">
                    {{ translate('article.submitApplyEdit') }}
                  </tiny-button>
                </div>
              </div>
            </transition>
            <div class="article-admins-section">
              <div class="article-admins-header">
                <svg class="article-admins-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                  <circle cx="9" cy="7" r="4"/>
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                </svg>
                <span class="article-admins-title">{{ translate('article.articleAdmins') }}</span>
              </div>
              <LoadingSpinner v-if="articleAdminsLoading" :absolute="false" />
              <ul v-else-if="articleAdmins.length > 0" class="article-admins-list">
                <li v-for="admin in articleAdmins" :key="admin.user_id" class="article-admin-item">
                  <span class="article-admin-avatar">{{ (admin.username || admin.email || '?').charAt(0).toUpperCase() }}</span>
                  <div class="article-admin-info">
                    <span class="article-admin-name">{{ admin.username || admin.email || String(admin.user_id) }}</span>
                    <span v-if="admin.email && admin.username" class="article-admin-email">{{ admin.email }}</span>
                  </div>
                </li>
              </ul>
              <p v-else class="article-admins-empty">{{ translate('article.noAdmins') }}</p>
            </div>
          </div>
        </div>
        <div v-else-if="articleLoadError === 'not_found'" class="article-error-panel article-error-not-found">
          <div class="article-error-card">
            <div class="article-error-icon-wrap article-error-icon-ghost">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                <polyline points="16 17 21 12 16 7"/>
                <line x1="21" y1="12" x2="9" y2="12"/>
              </svg>
            </div>
            <h3 class="article-error-heading">{{ translate('article.deletedOrNotExist') }}</h3>
            <p class="article-error-desc">{{ translate('article.deletedOrNotExistHint') }}</p>
          </div>
        </div>
        <div v-else class="empty-selection">
          <p>{{ translate('article.selectArticle') }}</p>
        </div>
      </main>
    </div>

    <!-- 评论弹窗 -->
    <CommentDrawer
      v-model:visible="commentDrawerVisible"
      :article-id="selectedArticle?.id || null"
      @comment-added="handleCommentAdded"
    />
    <!-- 反馈弹窗 -->
    <FeedbackDrawer
      v-model:visible="feedbackDrawerVisible"
      :article-id="selectedArticle?.id || null"
      @feedback-added="handleFeedbackAdded"
    />
    <!-- 历史版本弹窗 -->
    <ArticleHistoryDrawer
      v-model:visible="showHistoryDrawer"
      :article-id="selectedArticle?.id || null"
      @version-restored="handleVersionRestored"
    />
    <!-- 编辑文章弹窗（标题、节点类型、可见范围） -->
    <tiny-dialog-box
      v-model:visible="editArticleModalVisible"
      :title="translate('article.edit')"
      width="460px"
      @close="editArticleModalVisible = false"
    >
      <tiny-form
        ref="editArticleFormRef"
        :model="editArticleForm"
        :rules="editArticleRules"
        label-width="100px"
      >
        <tiny-form-item :label="translate('article.titleLabel')" prop="title">
          <tiny-input
            v-model="editArticleForm.title"
            :placeholder="translate('article.titlePlaceholder')"
          />
        </tiny-form-item>
        <tiny-form-item :label="translate('article.nodeType')" prop="node_type">
          <tiny-select v-model="editArticleForm.node_type" :placeholder="translate('article.nodeType')">
            <tiny-option :value="1" :label="translate('article.nodeTypeArticle')" />
            <tiny-option :value="2" :label="translate('article.nodeTypeDirectory')" />
          </tiny-select>
        </tiny-form-item>
        <tiny-form-item :label="translate('knowledgeBase.visibility')" prop="visibility">
          <tiny-select v-model="editArticleForm.visibility" :placeholder="translate('knowledgeBase.visibilityPlaceholder')">
            <tiny-option :label="translate('knowledgeBase.visibility.private')" :value="1" />
            <tiny-option :label="translate('knowledgeBase.visibility.member')" :value="2" />
            <tiny-option :label="translate('knowledgeBase.visibility.public')" :value="3" />
          </tiny-select>
        </tiny-form-item>
      </tiny-form>
      <template #footer>
        <tiny-button @click="editArticleModalVisible = false">{{ translate('common.cancel') }}</tiny-button>
        <tiny-button type="primary" :loading="editArticleSaving" @click="handleEditArticleSave">{{ translate('common.confirm') }}</tiny-button>
      </template>
    </tiny-dialog-box>
    
    <!-- 签读配置弹窗 -->
    <tiny-dialog-box
      v-model:visible="signReadDialogVisible"
      :title="translate('article.signRead')"
      width="640px"
      :close-on-click-modal="false"
    >
      <tiny-form ref="signReadFormRef" :model="signReadForm" label-width="140px">
        <tiny-form-item :label="translate('article.signReadDuration')" prop="duration">
          <tiny-input
            v-model.number="signReadForm.duration"
            type="number"
            min="1"
            :placeholder="translate('article.signReadDurationPlaceholder')"
          />
        </tiny-form-item>
        <tiny-form-item :label="translate('article.signReadDeadline')" prop="deadline">
          <tiny-date-picker
            type="datetime" 
            v-model="signReadForm.deadline"
            :picker-options="pickerOptions"
            :placeholder="translate('article.signReadDeadlinePlaceholder')"
            style="width: 100%;"
          />
        </tiny-form-item>
        <tiny-form-item :label="translate('article.signReadTargets')" prop="roleIds">
          <tiny-select
            v-model="signReadForm.roleIds"
            multiple
            :placeholder="translate('article.signReadTargetsPlaceholder')"
          >
            <tiny-option
              v-for="role in allRoles"
              :key="role.id"
              :label="role.name"
              :value="role.id"
            />
          </tiny-select>
        </tiny-form-item>
      </tiny-form>
      <template #footer>
        <tiny-button @click="signReadDialogVisible = false">{{ translate('common.cancel') }}</tiny-button>
        <tiny-button type="primary" :loading="signReadSubmitting" @click="handleSignReadConfirm">
          {{ translate('common.confirm') }}
        </tiny-button>
      </template>
    </tiny-dialog-box>
    
    <!-- 附件预览弹窗 -->
    <tiny-dialog-box
      v-model:visible="attachmentPreviewVisible"
      :title="previewAttachment?.filename || translate('article.previewAttachment')"
      width="100vw"
      height="100vh"
      :fullscreen="true"
      class="attachment-preview-dialog"
      @close="attachmentPreviewVisible = false"
    >
      <div class="attachment-preview-layout">
        <!-- 左侧附件列表 -->
        <div class="attachment-preview-sidebar">
          <div class="sidebar-header">
            <h3 class="sidebar-title">
              <svg class="sidebar-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path>
              </svg>
              {{ translate('article.attachments') }}
              <span class="attachments-count">({{ attachments.length }})</span>
            </h3>
          </div>
          <div class="sidebar-content">
            <div class="sidebar-content-scrollable">
              <div v-if="attachments.length === 0" class="empty-attachments">
                <p>{{ translate('article.noAttachments') }}</p>
              </div>
              <div v-else class="attachment-list">
              <div
                v-for="attachment in attachments"
                :key="attachment.id"
                class="attachment-list-item"
                :class="{ 'active': previewAttachment?.id === attachment.id }"
              >
                <div class="attachment-item-main" @click="handleSelectAttachmentForPreview(attachment)">
                  <div class="attachment-item-icon">
                    <span class="attachment-file-icon">{{ getFileIcon(attachment.filename, attachment.file_type) }}</span>
                  </div>
                  <div class="attachment-item-info">
                    <div class="attachment-item-name" :title="attachment.filename">
                      {{ attachment.filename }}
                    </div>
                    <div class="attachment-item-meta">
                      <span class="attachment-item-size">{{ formatFileSize(attachment.file_size) }}</span>
                    </div>
                  </div>
                </div>
                <div class="attachment-item-actions" @click.stop>
                  <button
                    class="attachment-action-btn"
                    :title="translate('article.downloadAttachment')"
                    @click.stop="handleDownloadAttachment(attachment)"
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                      <polyline points="7 10 12 15 17 10"></polyline>
                      <line x1="12" y1="15" x2="12" y2="3"></line>
                    </svg>
                  </button>
                  <button
                    v-if="hasArticleMemberRole"
                    class="attachment-action-btn"
                    :title="translate('article.deleteAttachment')"
                    @click.stop="handleDeleteAttachmentInPreview(attachment)"
                  >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <polyline points="3 6 5 6 21 6"></polyline>
                      <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                      <line x1="10" y1="11" x2="10" y2="17"></line>
                      <line x1="14" y1="11" x2="14" y2="17"></line>
                    </svg>
                  </button>
                </div>
              </div>
            </div>
            </div>
            
            <!-- 上传附件区域 -->
            <div v-if="hasArticleMemberRole" class="sidebar-upload-section">
              <div class="upload-divider"></div>
              <div class="upload-area">
                <input
                  ref="previewUploadFileInputRef"
                  type="file"
                  multiple
                  style="display: none"
                  @change="handlePreviewUploadFileSelect"
                />
                <button
                  class="upload-attachment-btn"
                  @click="previewUploadFileInputRef?.click()"
                  :disabled="!selectedArticle?.id || attachmentUploading"
                >
                  <component :is="TinyIconPlusSquare" class="upload-btn-icon" />
                  <span>{{ translate('article.uploadAttachment') }}</span>
                </button>
                <div v-if="attachmentUploading" class="upload-status">
                  <LoadingSpinner :absolute="false" />
                  <span>{{ translate('article.uploading') }}...</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 右侧附件预览 -->
        <div class="attachment-preview-content" style="position: relative;">
          <!-- 为每个已缓存的附件创建独立的预览组件，使用 v-show 保留组件实例 -->
          
          <!-- 图片预览缓存 -->
          <template v-for="attachment in Array.from(previewCacheMap.values())" :key="`img-${attachment.id}`">
            <div 
              v-show="previewAttachment?.id === attachment.id && isImageFile(attachment.filename)" 
              class="image-preview-container"
              style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
            >
              <tiny-image
                :src="attachment.file_url"
                :alt="attachment.filename"
                fit="contain"
                :preview-src-list="[attachment.file_url]"
                :z-index="1000"
              />
            </div>
          </template>
          
          <!-- 视频预览缓存 -->
          <template v-for="attachment in Array.from(previewCacheMap.values())" :key="`video-${attachment.id}`">
            <div 
              v-show="previewAttachment?.id === attachment.id && isVideoFile(attachment.filename)" 
              class="video-preview-container"
              style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;"
            >
              <video
                :src="attachment.file_url"
                controls
                style="max-height: calc(100vh - 120px); max-width: 100%;"
              >
                您的浏览器不支持视频播放
              </video>
            </div>
          </template>
          
          <div v-if="!previewAttachment" class="no-preview-selected">
            <svg class="empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path>
            </svg>
            <p>{{ translate('article.selectAttachmentToPreview') }}</p>
          </div>
        </div>
      </div>
    </tiny-dialog-box>
    
    <!-- 图片预览 - 使用自定义 CustomImageViewer 组件 -->
    <CustomImageViewer
      :visible="imagePreviewVisible"
      :url-list="imagePreviewList"
      :start-position="imagePreviewIndex"
      :z-index="2000"
      :close-show="true"
      :arrow-show="true"
      :tool-show="true"
      :show-index="true"
      @close="imagePreviewVisible = false"
      @switch="handleImageSwitch"
    />
    
    <!-- 文章权限设置弹窗 -->
    <tiny-dialog-box
      v-model:visible="showArticleMemberModal"
      :title="translate('article.manageMembers')"
      width="700px"
      :modal-append-to-body="true"
      :close-on-click-modal="false"
      @update:visible="handleArticleMemberModalClose"
    >
      <div class="member-management">
        <tiny-tabs v-model="articleMemberActiveTab" class="member-modal-tabs">
          <tiny-tab-item :title="translate('teamSpace.member.tabByUser')" name="user">
            <div class="member-tab-panel">
              <tiny-input
                v-model="articleMemberSearchKeyword"
                :placeholder="translate('article.member.searchPlaceholder') || translate('knowledgeBase.member.searchPlaceholder')"
                clearable
                @input="handleArticleMemberSearch"
                @keyup.enter="handleArticleMemberSearch"
                style="width: 100%"
              >
                <template #prefix>
                  <component :is="TinyIconSearch" />
                </template>
              </tiny-input>
            </div>
          </tiny-tab-item>
          <tiny-tab-item :title="translate('teamSpace.member.tabByRole')" name="role">
            <div class="member-tab-panel member-role-batch">
              <span class="member-role-filter-label">{{ translate('teamSpace.member.filterByRoles') }}</span>
              <tiny-select
                v-model="articleMemberFilterRoleIds"
                multiple
                filterable
                :placeholder="translate('teamSpace.member.filterRolePlaceholder')"
                style="width: 100%"
              >
                <tiny-option
                  v-for="role in articleMemberFilterRoles"
                  :key="role.id"
                  :label="role.name"
                  :value="role.id"
                />
              </tiny-select>
              <span class="member-role-filter-label member-batch-role-label">{{ translate('article.member.unifiedArticleRole') }}</span>
              <tiny-select
                v-model="articleMemberBatchArticleRole"
                :placeholder="translate('article.member.unifiedArticleRole')"
                style="width: 100%"
              >
                <tiny-option :label="translate('article.member.role.readonly')" :value="0" />
                <tiny-option :label="translate('article.member.role.editor')" :value="1" />
                <tiny-option :label="translate('article.member.role.admin')" :value="2" />
              </tiny-select>
              <tiny-button
                type="primary"
                class="member-batch-confirm-btn"
                :loading="articleMemberBatchAdding"
                :disabled="articleMemberFilterRoleIds.length === 0"
                @click="handleConfirmArticleBatchAddByRoles"
              >
                {{ translate('teamSpace.member.batchAddConfirm') }}
              </tiny-button>
            </div>
          </tiny-tab-item>
          <tiny-tab-item :title="translate('teamSpace.member.tabBatchRemove')" name="batchRemove">
            <div class="member-tab-panel member-role-batch member-role-batch-remove">
              <span class="member-role-filter-label">{{ translate('teamSpace.member.filterByRoles') }}</span>
              <tiny-select
                v-model="articleMemberRemoveRoleIds"
                multiple
                filterable
                :placeholder="translate('teamSpace.member.filterRolePlaceholder')"
                style="width: 100%"
              >
                <tiny-option
                  v-for="role in articleMemberFilterRoles"
                  :key="role.id"
                  :label="role.name"
                  :value="role.id"
                />
              </tiny-select>
              <tiny-button
                type="danger"
                plain
                class="member-batch-remove-btn"
                :loading="articleMemberBatchRemoving"
                :disabled="articleMemberRemoveRoleIds.length === 0"
                @click="handleConfirmArticleBatchRemoveByRoles"
              >
                {{ translate('teamSpace.member.batchRemoveConfirm') }}
              </tiny-button>
            </div>
          </tiny-tab-item>
        </tiny-tabs>

        <template v-if="articleMemberActiveTab === 'user'">
          <div class="member-list">
            <LoadingSpinner v-if="articleMemberLoading" :absolute="false" />
            <div v-else-if="articleMemberUsers.length === 0" class="empty-members">
              {{ translate('article.member.empty') }}
            </div>
            <div v-else>
              <div v-for="user in articleMemberUsers" :key="user.id" class="member-item">
                <div class="member-info">
                  <div class="member-basic">
                    <span class="member-name">{{ user.username || `User ${user.user_id ?? user.id}` }}</span>
                    <span v-if="user.email" class="member-email">{{ user.email }}</span>
                  </div>
                  <div v-if="user.is_member" class="member-meta">
                    <span v-if="user.role !== undefined && user.role !== null" class="member-role">
                      <span class="role-badge" :class="getArticleMemberRoleClass(user.role)">{{ getArticleMemberRoleText(user.role) }}</span>
                    </span>
                    <span v-if="user.joined_at" class="member-joined">
                      {{ translate('article.member.joinedAt') }}: {{ formatDate(user.joined_at) }}
                    </span>
                  </div>
                </div>
                <div v-if="user.is_member" class="member-actions">
                  <tiny-button
                    size="small"
                    type="danger"
                    @click="handleRemoveArticleMember(user)"
                  >
                    {{ translate('article.member.remove') }}
                  </tiny-button>
                  <tiny-dropdown trigger="click" placement="bottom-end" border :title="translate('article.member.changeTo')">
                    <template #dropdown>
                      <tiny-dropdown-menu>
                        <tiny-dropdown-item @click="handleChangeArticleMemberRole(user, 0)">
                          {{ translate('article.member.role.readonly') }}
                        </tiny-dropdown-item>
                        <tiny-dropdown-item @click="handleChangeArticleMemberRole(user, 1)">
                          {{ translate('article.member.role.editor') }}
                        </tiny-dropdown-item>
                        <tiny-dropdown-item @click="handleChangeArticleMemberRole(user, 2)">
                          {{ translate('article.member.role.admin') }}
                        </tiny-dropdown-item>
                      </tiny-dropdown-menu>
                    </template>
                  </tiny-dropdown>
                </div>
                <div v-else class="member-actions">
                  <tiny-dropdown trigger="click" placement="bottom-end" border :title="translate('article.member.addAs') || translate('knowledgeBase.member.addAs')">
                    <template #dropdown>
                      <tiny-dropdown-menu>
                        <tiny-dropdown-item @click="handleAddArticleMemberWithRole(user, 0)">
                          {{ translate('article.member.role.readonly') || translate('knowledgeBase.member.role.readonly') }}
                        </tiny-dropdown-item>
                        <tiny-dropdown-item @click="handleAddArticleMemberWithRole(user, 1)">
                          {{ translate('article.member.role.editor') || translate('knowledgeBase.member.role.editor') }}
                        </tiny-dropdown-item>
                        <tiny-dropdown-item @click="handleAddArticleMemberWithRole(user, 2)">
                          {{ translate('article.member.role.admin') || translate('knowledgeBase.member.role.admin') }}
                        </tiny-dropdown-item>
                      </tiny-dropdown-menu>
                    </template>
                  </tiny-dropdown>
                </div>
              </div>
            </div>
          </div>
          <div v-if="!articleMemberLoading && articleMemberUsers.length > 0" class="member-pager-wrap">
            <tiny-pager
              :current-page="articleMemberCurrentPage"
              :page-size="articleMemberPageSize"
              :total="articleMemberTotal"
              :page-sizes="[10, 20, 50]"
              layout="total, sizes, prev, pager, next"
              :hide-on-single-page="true"
              @page-change="onArticleMemberPageChange"
              @size-change="onArticleMemberSizeChange"
            />
          </div>
        </template>
        <div v-else-if="articleMemberActiveTab === 'role'" class="member-role-batch-hint">
          <p>{{ translate('teamSpace.member.batchAddByRoleHint') }}</p>
        </div>
        <div v-else class="member-role-batch-hint">
          <p>{{ translate('teamSpace.member.batchRemoveTabHint') }}</p>
        </div>
      </div>
    </tiny-dialog-box>

    <!-- 上传附件弹窗 -->
    <tiny-dialog-box
      v-model:visible="uploadAttachmentModalVisible"
      :title="translate('article.uploadAttachment')"
      width="900px"
      :modal-append-to-body="true"
      @close="handleCloseUploadModal"
    >
      <div class="upload-attachment-dialog">
        <div class="upload-dialog-layout">
          <!-- 左侧：已上传的附件列表 -->
          <div class="upload-dialog-sidebar">
            <div class="sidebar-header">
              <h4 class="section-title">
                <svg class="section-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path>
                </svg>
                {{ translate('article.existingAttachments') }}
                <span class="attachments-count">({{ attachments.length }})</span>
              </h4>
            </div>
            <div class="sidebar-content">
              <div v-if="attachments.length === 0" class="empty-attachments">
                <p>{{ translate('article.noAttachments') }}</p>
              </div>
              <div v-else class="existing-attachments-list">
                <div 
                  v-for="attachment in attachments" 
                  :key="attachment.id"
                  class="existing-attachment-item"
                >
                  <div class="attachment-item-info">
                    <span class="attachment-icon">{{ getFileIcon(attachment.filename, attachment.file_type) }}</span>
                    <div class="attachment-details">
                      <div class="attachment-name" :title="attachment.filename">
                        {{ attachment.filename }}
                      </div>
                      <div class="attachment-meta">
                        <span class="attachment-size">{{ formatFileSize(attachment.file_size) }}</span>
                        <span v-if="attachment.created_at" class="attachment-date">
                          {{ formatDate(attachment.created_at) }}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div class="attachment-item-actions">
                    <button
                      v-if="isPreviewable(attachment)"
                      class="attachment-preview-btn-small"
                      :title="translate('article.previewAttachment')"
                      @click.stop="handleAttachmentClick(attachment)"
                    >
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                        <circle cx="12" cy="12" r="3"></circle>
                      </svg>
                    </button>
                    <a 
                      :href="attachment.file_url" 
                      :download="attachment.filename"
                      class="attachment-download-btn-small"
                      :title="translate('article.downloadAttachment')"
                    >
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="7 10 12 15 17 10"></polyline>
                        <line x1="12" y1="15" x2="12" y2="3"></line>
                      </svg>
                    </a>
                    <button
                      v-if="hasArticleMemberRole"
                      class="attachment-delete-btn-small"
                      :title="translate('article.deleteAttachment')"
                      @click.stop="handleDeleteAttachment(attachment)"
                    >
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="3 6 5 6 21 6"></polyline>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                        <line x1="10" y1="11" x2="10" y2="17"></line>
                        <line x1="14" y1="11" x2="14" y2="17"></line>
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 右侧：上传区域 -->
          <div v-if="hasArticleMemberRole" class="upload-dialog-content">
            <h4 class="section-title">
              <svg class="section-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="17 8 12 3 7 8"></polyline>
                <line x1="12" y1="3" x2="12" y2="15"></line>
              </svg>
              {{ translate('article.uploadNewFiles') }}
            </h4>
            <div 
              class="upload-dropzone"
              @dragover="handleDragOver"
              @drop="handleDrop"
              @click="attachmentFileInputRef?.click()"
            >
              <div class="dropzone-content">
                <svg class="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                  <polyline points="17 8 12 3 7 8"></polyline>
                  <line x1="12" y1="3" x2="12" y2="15"></line>
                </svg>
                <p class="dropzone-text">{{ translate('article.dragFilesHere') }}</p>
                <p class="dropzone-hint">{{ translate('article.maxFileSize') }}</p>
              </div>
            </div>
            
            <!-- 待上传文件列表 -->
            <div v-if="selectedFiles.length > 0" class="upload-file-list">
              <div 
                v-for="(file, index) in selectedFiles" 
                :key="index"
                class="upload-file-item"
              >
                <div class="file-item-info">
                  <span class="file-icon">{{ getFileIcon(file.name, file.type) }}</span>
                  <div class="file-details">
                    <div class="file-name" :title="file.name">{{ file.name }}</div>
                    <div class="file-meta">
                      <span class="file-size">{{ formatFileSize(file.size) }}</span>
                      <span v-if="uploadingFiles.has(index)" class="upload-status uploading">
                        {{ translate('article.uploading') }}...
                      </span>
                      <span v-else-if="uploadProgress[index] === 100" class="upload-status success">
                        {{ translate('article.uploadSuccess') }}
                      </span>
                    </div>
                    <!-- 上传进度条 -->
                    <div v-if="uploadingFiles.has(index) || uploadProgress[index]" class="upload-progress-bar">
                      <div 
                        class="upload-progress-fill" 
                        :style="{ width: `${uploadProgress[index] || 0}%` }"
                      ></div>
                    </div>
                  </div>
                </div>
                <button
                  class="file-remove-btn"
                  :disabled="uploadingFiles.has(index)"
                  @click.stop="handleRemoveFile(index)"
                  :title="translate('article.removeFile')"
                >
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 隐藏的文件输入 -->
        <input
          ref="attachmentFileInputRef"
          type="file"
          multiple
          style="display: none;"
          @change="handleFileSelect"
        />
      </div>
      
      <template #footer>
        <tiny-button @click="handleCloseUploadModal">
          {{ translate('common.cancel') }}
        </tiny-button>
        <tiny-button 
          v-if="hasArticleMemberRole"
          type="primary" 
          :loading="attachmentUploading"
          :disabled="selectedFiles.length === 0 || uploadingFiles.size > 0"
          @click="handleStartUpload"
        >
          {{ translate('article.startUpload') }}
        </tiny-button>
      </template>
    </tiny-dialog-box>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { TinyDropdown, TinyDropdownMenu, TinyDropdownItem, Button as TinyButton, Image as TinyImage } from '@opentiny/vue'
import { Tree as TinyTree, Input as TinyInput, Modal, TinyDialogBox, Form as TinyForm, FormItem as TinyFormItem, Select as TinySelect, 
  Option as TinyOption, Pager as TinyPager, DatePicker as TinyDatePicker, TinyTabs, TinyTabItem, Switch as TinySwitch } from '@opentiny/vue'
import { articleApi, type Article, type ArticleMemberSearchItem, type ArticleAdminItem } from '../api/article'
import type { Attachment } from '../api/article'
import { knowledgeBaseApi, type KnowledgeBase, type KnowledgeBaseTag } from '../api/knowledgeBase'
import { fileApi } from '../api/file'
import { roleApi, type Role } from '../api/role'
import { readingTaskApi, type SignReadCheckResponse } from '../api/readingTask'
import { getCurrentRolePermissions } from '../utils/permission'
import type { Range } from '@opentiny/fluent-editor'
import { t } from '../i18n'
import { useLocaleStore } from '../stores/locale'
import FluentEditorV4 from '../components/FluentEditorV4.vue'
import { IconMore, IconEllipsis, IconEdit, IconDel, IconAdd, IconChevronUp, IconChevronDown, IconListMode, IconPlusSquare, IconYes, IconClose, IconChevronRight, 
  IconChevronLeft, IconSearch, IconStarActive, IconStarO, IconHeartempty, IconMessageCircle, IconFeedback, IconUser } from '@opentiny/vue-icon'
import { openOfficeOnlinePreview } from '../utils/officePreview'
// @ts-ignore
import LoadingSpinner from '../components/LoadingSpinner.vue'
// @ts-ignore
import IconHeartFill from '../components/icons/IconHeartFill.vue'
// @ts-ignore
import CommentDrawer from '../components/CommentDrawer.vue'
// @ts-ignore
import FeedbackDrawer from '../components/FeedbackDrawer.vue'
// @ts-ignore
import ArticleHistoryDrawer from '../components/ArticleHistoryDrawer.vue'
// @ts-ignore
import CustomImageViewer from '../components/CustomImageViewer.vue'



const TinyIconMore = IconMore()

const TinyIconAdd = IconAdd()
const TinyIconEllipsis = IconEllipsis()
const TinyIconEdit = IconEdit()
const TinyIconDelete = IconDel()
const TinyIconArrowUp = IconChevronUp()
const TinyIconArrowDown = IconChevronDown()
const TinyIconListMode = IconListMode()
const TinyIconPlusSquare = IconPlusSquare()
const TinyIconYes = IconYes()
const TinyIconClose = IconClose()
const TinyIconChevronRight = IconChevronRight()
const _TinyIconChevronLeft = IconChevronLeft()
const TinyIconSearch = IconSearch()
const TinyIconStarActive = IconStarActive()
const TinyIconStarO = IconStarO()
const TinyIconHeartempty = IconHeartempty()
const TinyIconMessageCircle = IconMessageCircle()
const TinyIconFeedback = IconFeedback()
const TinyIconUser = IconUser()
// 设置/更多 操作图标（与添加图标区分，用右箭头表示展开菜单）
const _TinyIconSetting = IconChevronRight()

const route = useRoute()
const router = useRouter()
const localeStore = useLocaleStore()

// 响应式翻译函数
const translate = (key: string, params?: Record<string, string>) => {
  void localeStore.localeKey
  return t(key, params)
}

// 获取知识库ID
const knowledgeBaseId = computed(() => {
  const id = route.params.knowledgeBaseId
  return id && !isNaN(Number(id)) ? Number(id) : null
})

// 树组件引用
const treeRef = ref()
const loading = ref(false)
/** 正在拉取子文章的节点 id，用于 .node-icon 显示加载动画 */
const treeNodeChildrenLoadingIds = ref<Set<number>>(new Set())

function setTreeNodeChildrenLoading(nodeId: number, loadingChildren: boolean) {
  const next = new Set(treeNodeChildrenLoadingIds.value)
  if (loadingChildren) next.add(nodeId)
  else next.delete(nodeId)
  treeNodeChildrenLoadingIds.value = next
}

function isTreeNodeChildrenLoading(nodeId: number): boolean {
  return treeNodeChildrenLoadingIds.value.has(nodeId)
}
const articleLoading = ref(false)
/** 文章加载失败原因：permission=无权限，not_found=文章不存在或已删除 */
const articleLoadError = ref<'permission' | 'not_found' | null>(null)
/** 无权限时展示的文章管理员列表（来自 GET /api/permissions/admins） */
const articleAdmins = ref<ArticleAdminItem[]>([])
const articleAdminsLoading = ref(false)
const DEFAULT_APPLY_ROLE = 1
const applyRoleOptions = [
  { value: 0, labelKey: 'article.role.readonly' },
  { value: 1, labelKey: 'article.role.editor' },
  { value: 2, labelKey: 'article.role.admin' }
] as const
/** 是否展开申请编辑表单（备注 + 提交） */
const showApplyEditForm = ref(false)
/** 申请的角色 */
const applyEditRole = ref<number>(DEFAULT_APPLY_ROLE)
/** 申请的审核人ID列表（可选，多选） */
const applyReviewerIds = ref<number[]>([])
/** 申请编辑时的备注内容 */
const applyEditRemark = ref('')
/** 申请编辑提交中 */
const applyEditSubmitting = ref(false)
const treeData = ref<any[]>([])
const treeDataBeforeDrag = ref<any[]>([]) // 拖拽前树数据快照，用于失败回滚
const defaultExpandedKeys = ref<number[]>([])
const selectedArticle = ref<Article | null>(null)
const knowledgeBase = ref<KnowledgeBase | null>(null)

/** 递归查找树节点（供 my_role 等与 treeData 相关的逻辑使用） */
const findNodeInTree = (
  tree: any[],
  nodeId: number | string,
  parent: any = null
): { node: any; parent: any; children: any[]; index: number } | null => {
  for (let i = 0; i < tree.length; i++) {
    const item = tree[i]
    if (String(item.id) === String(nodeId)) {
      return { node: item, parent, children: tree, index: i }
    }
    if (item.children && item.children.length > 0) {
      const result = findNodeInTree(item.children, nodeId, item)
      if (result) return result
    }
  }
  return null
}

/** 树节点上的 my_role（树数据与 originalData 均可能携带） */
const getTreeNodeMyRole = (data: any): number | null | undefined =>
  data?.my_role ?? data?.originalData?.my_role

/** 树节点菜单：非仅浏览 (my_role≠0) 时可编辑 */
const treeNodeCanEdit = (data: any) => {
  const r = getTreeNodeMyRole(data)
  if (r === undefined || r === null) return false
  return Number(r) !== 0
}

/** 树节点菜单：管理员 (my_role===2) 时权限设置、删除 */
const treeNodeCanAdmin = (data: any) => Number(getTreeNodeMyRole(data)) === 2

/** 文章成员角色：0 为仅浏览；非 0 才显示编辑、上传、历史版本、删附件等（以 treeData 中当前文章节点 my_role 为准） */
const hasArticleMemberRole = computed(() => {
  const id = selectedArticle.value?.id
  if (id == null) return false
  const found = findNodeInTree(treeData.value, id)
  const r = found?.node ? getTreeNodeMyRole(found.node) : undefined
  if (r === undefined || r === null) return false
  return Number(r) !== 0
})

/** 只读模式：文章底部标签文案（文章详情优先 tag_names，兼容 tags） */
const articleDisplayTagNames = computed(() => {
  const a = selectedArticle.value
  if (!a) return []
  const raw =
    a.tag_names != null && Array.isArray(a.tag_names) && a.tag_names.length > 0
      ? a.tag_names
      : a.tags ?? []
  return raw.map((x) => String(x).trim()).filter(Boolean)
})

/** 知识库或团队空间侧角色任一侧非「仅浏览」(≠0) 时，可：新建文章、树顶/底添加、节点前/后插入、添加子节点（来自 GET /knowledge-bases/{id}） */
const canAddTreeArticles = computed(() => {
  const kb = knowledgeBase.value
  if (!kb) return false
  const ts = kb.team_space_role
  const kbr = kb.knowledge_base_role
  const tsNonZero = ts !== undefined && ts !== null && Number(ts) !== 0
  const kbNonZero = kbr !== undefined && kbr !== null && Number(kbr) !== 0
  return tsNonZero || kbNonZero
})

const SIDEBAR_CARDS_STORAGE_KEY = 'article-sidebar-cards-expanded'
const SIDEBAR_HEADER_MAIN_ID = 'article-sidebar-header-main'

function loadSidebarCardsExpanded(): boolean {
  try {
    const s = localStorage.getItem(SIDEBAR_CARDS_STORAGE_KEY)
    if (s === null) return true
    return s === '1' || s === 'true'
  } catch {
    return true
  }
}

const sidebarCardsExpanded = ref(loadSidebarCardsExpanded())

function toggleSidebarCards() {
  sidebarCardsExpanded.value = !sidebarCardsExpanded.value
  try {
    localStorage.setItem(SIDEBAR_CARDS_STORAGE_KEY, sidebarCardsExpanded.value ? '1' : '0')
  } catch {
    /* ignore */
  }
}

// 文章操作状态
const isLiked = ref(false)
const isFavorited = ref(false)
const likeLoading = ref(false)
const favoriteLoading = ref(false)

// 评论弹窗状态
const commentDrawerVisible = ref(false)
// 反馈弹窗状态
const feedbackDrawerVisible = ref(false)
// 历史版本弹窗状态
const showHistoryDrawer = ref(false)
// 编辑文章弹窗（标题、节点类型、可见范围）
const editArticleModalVisible = ref(false)
const editArticleFormRef = ref()
const editArticleSaving = ref(false)
const editArticleForm = ref<{ id: number | null; title: string; node_type: number; visibility: number }>({
  id: null,
  title: '',
  node_type: 1,
  visibility: 1
})
const editArticleRules = {
  title: [{ required: true, message: () => translate('article.titleRequired'), trigger: 'blur' }]
}

// 全部角色列表（用于签读对象选择）
const allRoles = ref<Role[]>([])

// 签读配置状态
const signReadDialogVisible = ref(false)
const hasCreateReadTaskPermission = ref(false)
const hasArticleCategoryMovePermission = ref(false)
const _signReadFormRef = ref()
const signReadSubmitting = ref(false)
// 签读截止日期：仅可选当天及以后
const pickerOptions = {
  disabledDate(time: Date) {
    const todayStart = new Date()
    todayStart.setHours(0, 0, 0, 0)
    return time.getTime() < todayStart.getTime()
  }
}
const signReadForm = ref<{
  duration: number | null
  deadline: Date | null
  roleIds: number[]
}>({
  duration: null,
  deadline: null,
  roleIds: []
})

const openSignReadDialog = () => {
  if (!selectedArticle.value?.id) return
  // 重置表单
  signReadForm.value = {
    duration: null,
    deadline: null,
    roleIds: []
  }
  signReadDialogVisible.value = true
}

// 签读检查状态（当前用户是否需要签读此文）
const signReadCheck = ref<SignReadCheckResponse | null>(null)
const signReadElapsed = ref(0) // 本地累计阅读秒数（页面停留时递增）
const signReadTimer = ref<ReturnType<typeof setInterval> | null>(null)
const signReadProgressTimer = ref<ReturnType<typeof setInterval> | null>(null) // 每10秒上报状态
const signReadCompleting = ref(false)

// 剩余需阅读秒数
const signReadRemainingSeconds = computed(() => {
  const c = signReadCheck.value
  if (!c?.need_sign_read || c.required_seconds == null) return 0
  const actual = (c.actual_seconds ?? 0) + signReadElapsed.value
  return Math.max(0, c.required_seconds - actual)
})

// 格式化签读倒计时显示（分:秒）
const formatSignReadTime = (seconds: number) => {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}:${String(s).padStart(2, '0')}`
}

// 格式化签读时间（创建时间、截止时间）
const formatSignReadDateTime = (isoStr: string) => {
  if (!isoStr) return '—'
  try {
    const d = new Date(isoStr)
    if (isNaN(d.getTime())) return '—'
    const loc = localeStore.getLocale ?? 'zh'
    return d.toLocaleString(loc === 'zh' ? 'zh-CN' : 'en-US', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return '—'
  }
}

// 签读状态文案：0-未开始，1-进行中，2-已完成，3-已过期，4-已取消
const getSignReadStatusText = (status: number) => {
  const map: Record<number, string> = {
    0: translate('readingTask.statusNotStarted'),
    1: translate('readingTask.statusInProgress'),
    2: translate('readingTask.statusCompleted'),
    3: translate('readingTask.statusExpired'),
    4: translate('readingTask.statusCancelled')
  }
  return map[status] ?? ''
}

// 检查签读状态并启动定时器
const fetchSignReadCheck = async (articleId: number) => {
  clearSignReadTimer()
  signReadCheck.value = null
  signReadElapsed.value = 0

  try {
    const res = await readingTaskApi.checkArticleSignRead(articleId)
    signReadCheck.value = res

    if (res.need_sign_read && res.task_id != null && (res.status === 0 || res.status === 1)) {
      // 状态为未开始时，先更新为进行中
      if (res.status === 0) {
        try {
          await readingTaskApi.updateTaskStatus(res.task_id, { status: 1 })
          signReadCheck.value = { ...res, status: 1 }
        } catch (e) {
          console.error('更新签读状态为进行中失败', e)
        }
      }

      // 启动1秒倒计时定时器
      signReadTimer.value = setInterval(() => {
        signReadElapsed.value += 1
        const c = signReadCheck.value
        if (c && (c.actual_seconds ?? 0) + signReadElapsed.value >= (c.required_seconds ?? 0)) {
          clearSignReadTimer()
        }
      }, 1000)

      // 启动每10秒上报状态的定时器
      signReadProgressTimer.value = setInterval(async () => {
        const c = signReadCheck.value
        if (!c?.task_id || c.status === 2 || c.status === 3 || c.status === 4) return
        const actual = (c.actual_seconds ?? 0) + signReadElapsed.value
        try {
          await readingTaskApi.updateTaskStatus(c.task_id, {
            status: 1,
            actual_seconds: actual
          })
          signReadCheck.value = { ...c, actual_seconds: actual }
          signReadElapsed.value = 0 // 已同步到服务端，本地归零
        } catch (e) {
          console.error('上报签读进度失败', e)
        }
      }, 10000)
    }
  } catch (e) {
    console.error('检查签读状态失败', e)
    signReadCheck.value = null
  }
}

// 清除签读定时器
const clearSignReadTimer = () => {
  if (signReadTimer.value) {
    clearInterval(signReadTimer.value)
    signReadTimer.value = null
  }
  if (signReadProgressTimer.value) {
    clearInterval(signReadProgressTimer.value)
    signReadProgressTimer.value = null
  }
}

// 签读完成
const handleSignReadComplete = async () => {
  const c = signReadCheck.value
  if (!c?.need_sign_read || !c.task_id) return

  signReadCompleting.value = true
  try {
    const actual = (c.actual_seconds ?? 0) + signReadElapsed.value
    await readingTaskApi.updateTaskStatus(c.task_id, {
      status: 2,
      actual_seconds: Math.max(c.required_seconds ?? 0, actual)
    })
    clearSignReadTimer()
    signReadCheck.value = { ...c, need_sign_read: true, status: 2 }
    signReadElapsed.value = 0
    Modal.message({ message: translate('article.signReadCompleteSuccess'), status: 'success' })
  } catch (e) {
    Modal.message({ message: translate('common.unknownError'), status: 'error' })
  } finally {
    signReadCompleting.value = false
  }
}

const handleSignReadConfirm = async () => {
  if (!selectedArticle.value?.id) {
    return
  }
  if (!signReadForm.value.duration || signReadForm.value.duration <= 0) {
    Modal.message({
      message: translate('article.signReadDurationRequired'),
      status: 'warning'
    })
    return
  }
  if (!signReadForm.value.deadline) {
    Modal.message({
      message: translate('article.signReadDeadlineRequired'),
      status: 'warning'
    })
    return
  }
  if (!signReadForm.value.roleIds.length) {
    Modal.message({
      message: translate('article.signReadTargetsRequired'),
      status: 'warning'
    })
    return
  }

  try {
    signReadSubmitting.value = true
    const deadlineDate = signReadForm.value.deadline as Date
    const deadlineStr = new Date(deadlineDate).toISOString()

    const kbId = knowledgeBaseId.value ?? selectedArticle.value.knowledge_base_id

    await readingTaskApi.assignTask({
      article_id: selectedArticle.value.id,
      knowledge_base_id: kbId!,
      required_seconds: (signReadForm.value.duration as number) * 60,
      deadline: deadlineStr,
      role_ids: signReadForm.value.roleIds
    })

    Modal.message({
      message: translate('article.signReadConfigured'),
      status: 'success'
    })
    signReadDialogVisible.value = false
  } catch (e) {
    Modal.message({
      message: translate('common.unknownError'),
      status: 'error'
    })
  } finally {
    signReadSubmitting.value = false
  }
}

// 附件相关状态
const attachments = ref<Attachment[]>([])
const attachmentsLoading = ref(false)
const attachmentUploading = ref(false)
const attachmentFileInputRef = ref<HTMLInputElement | null>(null)
const previewUploadFileInputRef = ref<HTMLInputElement | null>(null)

// 附件预览弹窗状态
const attachmentPreviewVisible = ref(false)
const previewAttachment = ref<Attachment | null>(null)
const previewCacheMap = ref<Map<number, Attachment>>(new Map())

// 文章权限设置状态
const showArticleMemberModal = ref(false)
const managingArticleId = ref<number | null>(null)
const articleMemberUsers = ref<ArticleMemberSearchItem[]>([])
const articleMemberTotal = ref(0)
const articleMemberLoading = ref(false)
const articleMemberSearchKeyword = ref('')
const articleMemberCurrentPage = ref(1)
const articleMemberPageSize = ref(10)
let articleMemberSearchTimer: ReturnType<typeof setTimeout> | null = null

const articleMemberActiveTab = ref<'user' | 'role' | 'batchRemove'>('user')
const articleMemberFilterRoleIds = ref<number[]>([])
const articleMemberRemoveRoleIds = ref<number[]>([])
const articleMemberFilterRoles = ref<Role[]>([])
const articleMemberBatchArticleRole = ref(1)
const articleMemberBatchAdding = ref(false)
const articleMemberBatchRemoving = ref(false)
/** 当前管理中的文章可见性；1=个人可见不可添加成员 */
const managingArticleVisibility = ref<number | null>(null)

// 图片预览状态
const imagePreviewVisible = ref(false)
const imagePreviewList = ref<string[]>([])
const imagePreviewIndex = ref(0)

// 上传附件弹窗状态
const uploadAttachmentModalVisible = ref(false)
const selectedFiles = ref<File[]>([])
const uploadProgress = ref<Record<number, number>>({}) // 文件索引 -> 上传进度
const uploadingFiles = ref<Set<number>>(new Set()) // 正在上传的文件索引

// 搜索过滤
const filterText = ref('')
const contentAreaRef = ref<HTMLElement | null>(null)

// 编辑相关
const isEditing = ref(false)
const editorRef = ref()
const previewRef = ref()

/** 当前正文区域：编辑态 / 预览态各一个 FluentEditorV4 实例（预览为 readonly） */
function getArticleContentHost(): { quill?: any; focus?: () => void; $el?: HTMLElement } | null {
  return (isEditing.value ? editorRef.value : previewRef.value) ?? null
}
const editorContent = ref('')
const saving = ref(false)
const originalContent = ref('') // 保存原始内容，用于取消编辑
/** 编辑态：是否原创 / 是否AI生成（与保存一并提交） */
const editingIsOriginal = ref(false)
const editingIsAiGenerated = ref(false)

/** 编辑态：知识库标签多选（选项来自 GET /knowledge-bases/{id}/tags，保存时提交 tag_ids） */
const kbTagsForEdit = ref<KnowledgeBaseTag[]>([])
const kbTagsLoading = ref(false)
const editingTagIds = ref<number[]>([])

/** 是否展示顶部徽章条（可见性 / 原创 / AI，至少一项） */
const hasArticleMetaBadges = computed(() => {
  const a = selectedArticle.value
  if (!a) return false
  if (a.visibility !== undefined && a.visibility !== null) return true
  if (a.is_original === true) return true
  if (a.is_ai_generated === true) return true
  return false
})

function syncEditTagIdsFromArticle() {
  const a = selectedArticle.value
  if (!a) {
    editingTagIds.value = []
    return
  }
  if (a.tag_ids != null && Array.isArray(a.tag_ids)) {
    const validIds = new Set(kbTagsForEdit.value.map((t) => t.id))
    editingTagIds.value = a.tag_ids.map((id) => Number(id)).filter((id) => Number.isFinite(id) && validIds.has(id))
    return
  }
  const nameSource =
    a.tag_names != null && Array.isArray(a.tag_names) && a.tag_names.length > 0 ? a.tag_names : a.tags || []
  const names = new Set(nameSource.map((x) => String(x).trim()).filter(Boolean))
  editingTagIds.value = kbTagsForEdit.value.filter((t) => names.has(t.name)).map((t) => t.id)
}

function syncEditFlagsFromArticle() {
  const a = selectedArticle.value
  if (!a) return
  editingIsOriginal.value = a.is_original ?? false
  editingIsAiGenerated.value = a.is_ai_generated ?? false
  syncEditTagIdsFromArticle()
}

const loadKbTagsForEdit = async () => {
  const kbId = knowledgeBaseId.value ?? selectedArticle.value?.knowledge_base_id
  if (!kbId) {
    kbTagsForEdit.value = []
    return
  }
  kbTagsLoading.value = true
  try {
    kbTagsForEdit.value = await knowledgeBaseApi.listKnowledgeBaseTags(kbId)
  } catch (error: any) {
    kbTagsForEdit.value = []
    Modal.message({
      message: error?.message || translate('article.kbTagsLoadError'),
      status: 'error'
    })
  } finally {
    kbTagsLoading.value = false
  }
}

// 本地缓存相关
const DRAFT_CACHE_KEY = 'article_draft_cache'
const DRAFT_CACHE_TIMEOUT = 7 * 24 * 60 * 60 * 1000 // 7天过期时间

// 文章标题编辑相关
const isEditingArticleTitle = ref(false)
const editingArticleTitle = ref('')
const originalArticleTitle = ref('')
const articleTitleInputRef = ref()
const savingArticleTitle = ref(false)

watch(hasArticleMemberRole, (ok) => {
  if (!ok) {
    isEditing.value = false
    isEditingArticleTitle.value = false
    showHistoryDrawer.value = false
    if (uploadAttachmentModalVisible.value) uploadAttachmentModalVisible.value = false
  }
})

// 侧边栏宽度调整相关
const sidebarWidth = ref(300) // 默认宽度
const isResizing = ref(false)
const MIN_SIDEBAR_WIDTH = 200 // 最小宽度
const MAX_SIDEBAR_WIDTH = 600 // 最大宽度

const LAYOUT_COMPACT_MAX = 1024
const LAYOUT_MOBILE_MAX = 768
const isCompactLayout = ref(false)
const isMobileLayout = ref(false)
const mobileTreeDrawerOpen = ref(false)
const mobileActionsExpanded = ref(false)

const closeMobileActionsSheet = () => {
  mobileActionsExpanded.value = false
}

const updateArticlePageLayout = () => {
  isCompactLayout.value = window.matchMedia(`(max-width: ${LAYOUT_COMPACT_MAX}px)`).matches
  isMobileLayout.value = window.matchMedia(`(max-width: ${LAYOUT_MOBILE_MAX}px)`).matches
  if (!isCompactLayout.value) {
    mobileTreeDrawerOpen.value = false
    document.body.style.overflow = ''
  }
}

const toggleMobileTreeDrawer = () => {
  mobileTreeDrawerOpen.value = !mobileTreeDrawerOpen.value
}

const closeMobileTreeDrawer = () => {
  mobileTreeDrawerOpen.value = false
}

watch(mobileTreeDrawerOpen, (open) => {
  if (isCompactLayout.value && !isEditing.value) {
    document.body.style.overflow = open ? 'hidden' : ''
  }
})

watch(isCompactLayout, (compact) => {
  if (!compact) {
    mobileTreeDrawerOpen.value = false
    document.body.style.overflow = ''
  }
})

watch(isEditing, (editing) => {
  if (editing) {
    closeMobileTreeDrawer()
    closeMobileActionsSheet()
    if (!isCompactLayout.value) return
    document.body.style.overflow = ''
  }
})

watch(isMobileLayout, (mobile) => {
  if (!mobile) {
    closeMobileActionsSheet()
  }
})

// 文章目录相关
interface TocItem {
  id: string
  text: string
  level: number
}

const tableOfContents = ref<TocItem[]>([])
const tocTreeData = ref<any[]>([])
const tocLoading = ref(false) // 目录加载状态
const tocVisible = ref(true) // 目录显示/隐藏状态
/** 随正文滚动高亮的当前标题 id（与 .ql-editor 内标题 id 对应） */
const tocActiveHeadingId = ref<string | null>(null)
const tocTreeContainerRef = ref<HTMLElement | null>(null)
let tocScrollSpyRaf = 0
let tocContentScrollBound = false

const teardownTocScrollSpy = () => {
  if (tocScrollSpyRaf) {
    cancelAnimationFrame(tocScrollSpyRaf)
    tocScrollSpyRaf = 0
  }
  if (tocContentScrollBound && contentAreaRef.value) {
    contentAreaRef.value.removeEventListener('scroll', onTocContentAreaScroll)
    tocContentScrollBound = false
  }
}

const onTocContentAreaScroll = () => {
  if (tocScrollSpyRaf) return
  tocScrollSpyRaf = requestAnimationFrame(() => {
    tocScrollSpyRaf = 0
    updateTocActiveFromScroll()
  })
}

/** 根据 .content-area 滚动位置，高亮「越过」视口参考线的最后一个标题，并滚动目录树使该项可见 */
const updateTocActiveFromScroll = () => {
  const root = contentAreaRef.value
  if (!root || isEditing.value || !tocVisible.value || tableOfContents.value.length === 0) {
    return
  }
  const rootRect = root.getBoundingClientRect()
  const offset = Math.min(100, Math.max(48, rootRect.height * 0.08))
  const lineY = rootRect.top + offset
  let active: string | null = null
  for (const item of tableOfContents.value) {
    const el = document.getElementById(item.id)
    if (!el) continue
    const top = el.getBoundingClientRect().top
    if (top <= lineY) active = item.id
  }
  if (active === null && root.scrollTop < 32 && tableOfContents.value[0]) {
    active = tableOfContents.value[0].id
  }
  const prev = tocActiveHeadingId.value
  tocActiveHeadingId.value = active
  if (active && active !== prev) {
    nextTick(() => scrollTocPanelToActive(active))
  }
}

/** 仅在目录树容器内滚动，禁止 scrollIntoView（否则会滚动到 .content-area，与正文锚点滚动互相打架） */
const scrollTocPanelToActive = (id: string) => {
  const container = tocTreeContainerRef.value
  if (!container) return
  const nodes = container.querySelectorAll('[data-toc-id]')
  for (const n of nodes) {
    const el = n as HTMLElement
    if (el.dataset.tocId !== id) continue
    const c = container.getBoundingClientRect()
    const e = el.getBoundingClientRect()
    if (e.top < c.top) {
      container.scrollTop -= c.top - e.top + 6
    } else if (e.bottom > c.bottom) {
      container.scrollTop += e.bottom - c.bottom + 6
    }
    break
  }
}

const syncTocScrollSpy = () => {
  teardownTocScrollSpy()
  if (isEditing.value || !selectedArticle.value || !tocVisible.value || tocLoading.value) {
    tocActiveHeadingId.value = null
    return
  }
  if (tableOfContents.value.length === 0) return
  if (!contentAreaRef.value) return
  contentAreaRef.value.addEventListener('scroll', onTocContentAreaScroll, { passive: true })
  tocContentScrollBound = true
  updateTocActiveFromScroll()
}

watch(
  () =>
    [
      isEditing.value,
      selectedArticle.value?.id,
      tocVisible.value,
      tocLoading.value,
      tableOfContents.value.length,
    ] as const,
  () => {
    nextTick(() => syncTocScrollSpy())
  }
)

const attachmentsVisible = ref(true) // 附件显示/隐藏状态
const tocWidth = ref(240) // 目录宽度
const isTocResizing = ref(false) // 目录调整宽度状态
const MIN_TOC_WIDTH = 180 // 目录最小宽度
const MAX_TOC_WIDTH = 800 // 目录最大宽度

// 计算按钮栏的右侧位置，避免与目录重叠
const _actionsBarRight = computed(() => {
  if (!isEditing.value && tocVisible.value) {
    // 目录显示时，按钮栏向左移动（目录宽度 + 间距）
    return 20
  }
  return 0
})

// 切换目录显示/隐藏（只有通过按钮调用）
const toggleToc = () => {
  tocVisible.value = !tocVisible.value
  localStorage.setItem('articleTocVisible', tocVisible.value.toString())
  if (isMobileLayout.value && tocVisible.value) {
    closeMobileActionsSheet()
    attachmentsVisible.value = false
    localStorage.setItem('articleAttachmentsVisible', 'false')
  }
}

// 切换附件显示/隐藏
const toggleAttachments = () => {
  attachmentsVisible.value = !attachmentsVisible.value
  localStorage.setItem('articleAttachmentsVisible', attachmentsVisible.value.toString())
  if (isMobileLayout.value && attachmentsVisible.value) {
    closeMobileActionsSheet()
    tocVisible.value = false
    localStorage.setItem('articleTocVisible', 'false')
  }
}

// 开始调整目录宽度
const handleTocResizeStart = (e: MouseEvent) => {
  if (isMobileLayout.value) return
  e.preventDefault()
  e.stopPropagation()
  isTocResizing.value = true
  const startX = e.clientX
  const startWidth = tocWidth.value
  
  // 禁用文本选择
  document.body.style.userSelect = 'none'
  document.body.style.cursor = 'col-resize'
  
  const handleMouseMove = (moveEvent: MouseEvent) => {
    moveEvent.preventDefault()
    const diff = startX - moveEvent.clientX // 向右拖拽是缩小宽度，向左拖拽是增加宽度
    const newWidth = startWidth + diff
    
    // 限制在最小和最大宽度之间
    if (newWidth >= MIN_TOC_WIDTH && newWidth <= MAX_TOC_WIDTH) {
      tocWidth.value = newWidth
    } else if (newWidth < MIN_TOC_WIDTH) {
      tocWidth.value = MIN_TOC_WIDTH
    } else if (newWidth > MAX_TOC_WIDTH) {
      tocWidth.value = MAX_TOC_WIDTH
    }
  }
  
  const handleMouseUp = () => {
    isTocResizing.value = false
    // 恢复文本选择和光标
    document.body.style.userSelect = ''
    document.body.style.cursor = ''
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
    // 保存到本地存储
    localStorage.setItem('articleTocWidth', tocWidth.value.toString())
  }
  
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

// 将扁平目录数组转换为树形结构
const buildTocTree = (items: TocItem[]): any[] => {
  if (items.length === 0) return []
  
  const tree: any[] = []
  const stack: any[] = [] // 用于跟踪当前路径的节点栈
  
  items.forEach((item) => {
    const node = {
      id: item.id,
      label: item.text,
      level: item.level,
      children: []
    }
    
    // 找到当前节点的父节点（栈中最后一个 level < 当前 level 的节点）
    while (stack.length > 0 && stack[stack.length - 1].level >= item.level) {
      stack.pop()
    }
    
    if (stack.length === 0) {
      // 顶级节点
      tree.push(node)
    } else {
      // 子节点，添加到父节点的 children
      const parent = stack[stack.length - 1]
      if (!parent.children) {
        parent.children = []
      }
      parent.children.push(node)
    }
    
    // 将当前节点压入栈
    stack.push(node)
  })
  
  return tree
}

// 开始调整宽度
const handleResizeStart = (e: MouseEvent) => {
  if (isCompactLayout.value) return
  e.preventDefault() // 防止默认行为
  isResizing.value = true
  const startX = e.clientX
  const startWidth = sidebarWidth.value
  
  // 禁用文本选择
  document.body.style.userSelect = 'none'
  document.body.style.cursor = 'col-resize'
  
  const handleMouseMove = (moveEvent: MouseEvent) => {
    moveEvent.preventDefault()
    const diff = moveEvent.clientX - startX
    const newWidth = startWidth + diff
    
    // 限制在最小和最大宽度之间
    if (newWidth >= MIN_SIDEBAR_WIDTH && newWidth <= MAX_SIDEBAR_WIDTH) {
      sidebarWidth.value = newWidth
    } else if (newWidth < MIN_SIDEBAR_WIDTH) {
      sidebarWidth.value = MIN_SIDEBAR_WIDTH
    } else if (newWidth > MAX_SIDEBAR_WIDTH) {
      sidebarWidth.value = MAX_SIDEBAR_WIDTH
    }
  }
  
  const handleMouseUp = () => {
    isResizing.value = false
    // 恢复文本选择和光标
    document.body.style.userSelect = ''
    document.body.style.cursor = ''
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
    // 保存到本地存储
    localStorage.setItem('articleSidebarWidth', sidebarWidth.value.toString())
  }
  
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

// 添加节点相关
const creating = ref(false)
const isClickingButton = ref(false) // 用于防止 blur 和 click 冲突

const markTempNodeActionPointerDown = () => {
  isClickingButton.value = true
}
const isPressingEnter = ref(false) // 用于防止 Enter 键和 blur 冲突
const tempInputRefs = ref<Record<string, any>>({}) // 存储临时输入框的引用
const dropdownVisibleNodeId = ref<string | number | null>(null) // 当前显示 dropdown 的节点 id

// dropdown 显示状态变化处理
const handleDropdownVisibleChange = (visible: boolean, nodeId: string | number) => {
  dropdownVisibleNodeId.value = visible ? nodeId : null
}
const savingNodeIds = ref<Set<string>>(new Set()) // 正在保存的节点ID集合，防止重复提交

// 树组件配置
const treeProps = {
  children: 'children',
  label: 'label'
}

// 树节点过滤方法
const filterNode = (value: string, data: any, node: any) => {
  if (!value) return true
  
  // 检查当前节点标签是否包含搜索文本（不区分大小写）
  const label = data.label || node.label || ''
  if (label.toLowerCase().includes(value.toLowerCase())) {
    return true
  }
  
  // 如果当前节点不匹配，检查是否有子节点匹配
  // 如果有子节点匹配，也应该显示当前节点
  if (data.children && data.children.length > 0) {
    const hasMatchingChild = data.children.some((child: any) => {
      const childLabel = child.label || ''
      return childLabel.toLowerCase().includes(value.toLowerCase())
    })
    if (hasMatchingChild) {
      return true
    }
  }
  
  return false
}

// 监听搜索文本变化，触发过滤
watch(filterText, (value) => {
  if (treeRef.value) {
    treeRef.value.filter(value)
  }
})

// 拖拽：是否允许拖拽该节点（需 article_category_move 权限，临时节点不可拖）
const allowDrag = (data: any) => {
  if (!hasArticleCategoryMovePermission.value) return false
  if (!data) return false
  if (data.isTemp === true) return false
  const id = data.id
  if (id == null) return false
  if (String(id).startsWith('temp-')) return false
  return true
}

// 拖拽：是否允许放置到目标节点（需 article_category_move 权限，临时节点不可作为放置目标）
const allowDrop = (_draggingNode: any, dropNode: any, _type: string) => {
  if (!hasArticleCategoryMovePermission.value) return false
  if (!dropNode?.data) return false
  const d = dropNode.data
  if (d.isTemp === true || (d.id != null && String(d.id).startsWith('temp-'))) return false
  return true
}

// 拖拽开始：保存当前树数据快照，用于失败时回滚
const handleNodeDragStart = () => {
  treeDataBeforeDrag.value = JSON.parse(JSON.stringify(treeData.value))
}

// 拖拽放置：调用 PUT /api/articles/{article_id}/position
// 接口参数：event_type: "inner"|"before"|"after"|"none"；target_node_id：inner/before/after 时必填
const handleNodeDrop = async (
  draggingNode: { data?: any },
  dropNode: { data?: any; parent?: any },
  dropType: string
) => {
  const dragData = draggingNode?.data ?? draggingNode
  const dropData = dropNode?.data ?? dropNode
  const draggedId = dragData?.id
  const dropId = dropData?.id

  if (draggedId == null || (typeof draggedId === 'number' && isNaN(draggedId)) || String(draggedId).startsWith('temp-')) {
    revertTreeAfterDrop()
    return
  }
  if (dropId != null && String(dropId).startsWith('temp-')) {
    revertTreeAfterDrop()
    return
  }

  const eventType = dropType === 'inner' ? 'inner' : dropType === 'before' ? 'before' : dropType === 'after' ? 'after' : 'none'
  if (eventType === 'none') {
    revertTreeAfterDrop()
    return
  }

  // inner/before/after 时 target_node_id 必填
  const targetId = dropId != null && typeof dropId === 'number' && !isNaN(dropId)
    ? dropId
    : dropId != null
      ? (parseInt(String(dropId), 10) || null)
      : null
  if (targetId == null || (typeof targetId === 'number' && isNaN(targetId))) {
    revertTreeAfterDrop()
    Modal.message({ message: translate('tree.dragPositionFailed'), status: 'error' })
    return
  }

  try {
    await articleApi.updateArticlePosition(Number(draggedId), {
      event_type: eventType,
      target_node_id: targetId
    })
  } catch (e) {
    revertTreeAfterDrop()
    Modal.message({ message: (e as Error)?.message || translate('tree.dragPositionFailed'), status: 'error' })
  }
}

const revertTreeAfterDrop = () => {
  if (treeDataBeforeDrag.value && treeDataBeforeDrag.value.length >= 0) {
    treeData.value = JSON.parse(JSON.stringify(treeDataBeforeDrag.value))
  }
}

/** 将当前节点滚动到可视区域（在 setCurrentKey 之后调用） */
const scrollToTreeNode = (_articleId: number) => {
  nextTick(() => {
    setTimeout(() => {
      const treeEl = treeRef.value?.$el
      if (!treeEl) return
      const current = treeEl.querySelector('.tiny-tree-node.is-current')
      if (current) {
        current.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
      }
    }, 50)
  })
}

// 将文章转换为树节点格式（递归处理children）
const convertToTreeNode = (item: Article): any => {
  const node: any = {
    id: item.id,
    label: item.title,
    type: 'article',
    parent_id: item.parent_id,
    originalData: item,
    my_role: item.my_role,
    node_type: item.node_type ?? 1,
    visibility: item.visibility != null ? Number(item.visibility) : 1
  }
  
  // 如果item包含children字段，递归转换children
  if (item.children && Array.isArray(item.children) && item.children.length > 0) {
    node.children = item.children.map((child: Article) => convertToTreeNode(child))
  }
  
  // 确保没有 isTemp 标记
  delete node.isTemp
  
  return node
}

// 加载顶级文章（parent_id为null，表示没有父文章）
const loadTopLevelArticles = async () => {
  if (!knowledgeBaseId.value) return

  loading.value = true
  try {
    // 获取顶级文章（parent_id为null，表示顶级文章）
    const articles = await articleApi.getArticles(knowledgeBaseId.value, null, route.query.articleId ? Number(route.query.articleId) : null)
    
    // 转换为树节点格式
    const allTopLevel = articles.map(convertToTreeNode)
    console.log('allTopLevel', allTopLevel)

    treeData.value = allTopLevel
  } catch (error) {
    console.error('加载顶级文章失败:', error)
  } finally {
    loading.value = false
  }
}

// 加载节点的子文章（category_id指向父文章id）
const loadNodeChildren = async (node: any) => {
  if (!knowledgeBaseId.value || !node) return

  const parentArticleId = node.id
  setTreeNodeChildrenLoading(parentArticleId, true)
  try {
    // 获取该文章的子文章（category_id等于父文章id）
    const childArticles = await articleApi.getArticles(knowledgeBaseId.value, parentArticleId)
    // 转换为树节点格式
    const children = childArticles.map(convertToTreeNode)

    // 更新节点的children
    const treeNode = treeRef.value?.getNode(node.id)
    if (treeNode) {
      treeNode.data.children = children
      // 更新树数据
      updateTreeData(treeData.value, node.id, children)
    }
  } catch (error) {
    console.error('加载子文章失败:', error)
  } finally {
    setTreeNodeChildrenLoading(parentArticleId, false)
  }
}

// 递归更新树数据
const updateTreeData = (data: any[], nodeId: number, children: any[]) => {
  for (const item of data) {
    if (item.id === nodeId) {
      item.children = children
      return true
    }
    if (item.children && item.children.length > 0) {
      if (updateTreeData(item.children, nodeId, children)) {
        return true
      }
    }
  }
  return false
}

// 生成文章目录（直接从DOM获取HTML，不依赖Quill）
const generateTableOfContents = (retryCount = 0, maxRetries = 15) => {
  // 设置加载状态
  if (retryCount === 0) {
    tocLoading.value = true
    tocTreeData.value = []
  }
  
  // 直接通过 DOM 查询编辑器内容区域
  let contentContainer: HTMLElement | null = null
  
  // 方式1: 查找 .editor-container 内的 .ql-container 或 .ql-editor
  const editorContainer = document.querySelector('.editor-container')
  if (editorContainer) {
    // 查找 Quill 编辑器内容区域
    const quillContainer = editorContainer.querySelector('.ql-container')
    const quillEditor = editorContainer.querySelector('.ql-editor')
    contentContainer = (quillEditor || quillContainer) as HTMLElement
  }
  
  // 方式2: 如果方式1失败，直接查找 .ql-editor 或 .ql-container
  if (!contentContainer) {
    contentContainer = document.querySelector('.ql-editor') as HTMLElement
    if (!contentContainer) {
      contentContainer = document.querySelector('.ql-container') as HTMLElement
    }
  }
  
  // 方式3: 如果还是找不到，查找 article-content 区域内的所有标题
  if (!contentContainer) {
    const articleContent = document.querySelector('.article-content')
    if (articleContent) {
      contentContainer = articleContent as HTMLElement
    }
  }
  
  if (!contentContainer) {
    if (retryCount < maxRetries) {
      setTimeout(() => generateTableOfContents(retryCount + 1, maxRetries), 300)
    }
    return
  }
  
  tableOfContents.value = []
  
  try {
    // 直接从DOM中提取标题
    const headings = contentContainer.querySelectorAll('h1, h2, h3, h4, h5, h6')
    
    if (headings.length > 0) {
      headings.forEach((heading: Element, index: number) => {
        const level = parseInt(heading.tagName.charAt(1))
        const text = heading.textContent?.trim() || ''
        
        if (text) {
          // 生成唯一ID（如果还没有ID）
          if (!heading.id) {
            heading.id = `heading-${index}-${Date.now()}`
          }
          
          tableOfContents.value.push({
            id: heading.id,
            text,
            level
          })
        }
      })
      
      // 打印目录数据
      console.log('📋 目录数据 (扁平):', tableOfContents.value)
      
      // 转换为树形结构
      tocTreeData.value = buildTocTree(tableOfContents.value)
      console.log('🌳 目录树数据:', tocTreeData.value)
    }
    
    // 停止加载
    tocLoading.value = false
  } catch (error) {
    console.error('生成目录失败:', error)
    // 出错时也停止加载
    tocLoading.value = false
  }
  nextTick(() => syncTocScrollSpy())
}

// 处理目录树节点点击
const handleTocNodeClick = (data: any) => {
  scrollToHeading(data.id)
}

const scrollPreviewToTop = () => {
  if (contentAreaRef.value) {
    contentAreaRef.value.scrollTo({
      top: 0,
      behavior: 'smooth'
    })
    return
  }

  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  })
}

const scrollPreviewToBottom = () => {
  if (contentAreaRef.value) {
    contentAreaRef.value.scrollTo({
      top: contentAreaRef.value.scrollHeight,
      behavior: 'smooth'
    })
    return
  }

  window.scrollTo({
    top: document.documentElement.scrollHeight,
    behavior: 'smooth'
  })
}

// 滚动到指定标题
const scrollToHeading = (id: string) => {
  tocActiveHeadingId.value = id
  nextTick(() => scrollTocPanelToActive(id))
  const element = document.getElementById(id)
  if (element) {
    // 使用 scrollIntoView，通过 CSS scroll-margin-top 设置偏移
    element.scrollIntoView({ behavior: 'smooth', block: 'start' })
    
    // 添加高亮效果
    element.classList.add('toc-highlight')
    setTimeout(() => {
      element.classList.remove('toc-highlight')
    }, 2000)
  }

  if (isMobileLayout.value && tocVisible.value) {
    tocVisible.value = false
    localStorage.setItem('articleTocVisible', 'false')
  }
}

// 加载文章附件
const loadAttachments = async (articleId: number) => {
  if (!articleId) return
  
  attachmentsLoading.value = true
  try {
    attachments.value = await articleApi.getArticleAttachments(articleId)
  } catch (error) {
    console.error('加载附件失败:', error)
    attachments.value = []
    Modal.message({
      message: translate('article.loadAttachmentsError'),
      status: 'error'
    })
  } finally {
    attachmentsLoading.value = false
  }
}

// 获取文件图标
const getFileIcon = (fileName: string, fileType?: string | null): string => {
  const ext = fileName.toLowerCase().split('.').pop() || ''
  if (fileType?.startsWith('image/')) return '🖼️'
  if (fileType?.startsWith('video/')) return '🎬'
  if (ext === 'pptx' || ext === 'ppt') return '📊'
  if (ext === 'xlsx' || ext === 'xls') return '📊'
  if (ext === 'docx' || ext === 'doc') return '📄'
  if (ext === 'pdf') return '📕'
  if (ext === 'zip' || ext === 'rar' || ext === '7z') return '📦'
  return '📎'
}

// 格式化文件大小
const formatFileSize = (bytes?: number | null): string => {
  if (!bytes || bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// 判断文件是否可预览
const isPreviewable = (attachment: Attachment): boolean => {
  const ext = attachment.filename.toLowerCase().split('.').pop() || ''
  const previewableTypes = ['pptx', 'pdf', 'docx', 'xlsx', 'ppt', 'doc', 'xls']
  const imageTypes = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg']
  const videoTypes = ['mp4', 'webm', 'ogg', 'mov', 'avi', 'wmv', 'flv', 'mkv']
  return previewableTypes.includes(ext) || imageTypes.includes(ext) || videoTypes.includes(ext)
}

// 判断是否为图片文件
const isImageFile = (filename: string): boolean => {
  const imageTypes = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg']
  const ext = filename.toLowerCase().split('.').pop() || ''
  return imageTypes.includes(ext)
}

// 判断是否为视频文件
const isVideoFile = (filename: string): boolean => {
  const videoTypes = ['mp4', 'webm', 'ogg', 'mov', 'avi', 'wmv', 'flv', 'mkv']
  const ext = filename.toLowerCase().split('.').pop() || ''
  return videoTypes.includes(ext)
}

// 处理附件点击
const handleAttachmentClick = (attachment: Attachment) => {
  if (openOfficeOnlinePreview(attachment.file_url, attachment.filename, attachment.file_type)) {
    return
  }
  if (isImageFile(attachment.filename) || isVideoFile(attachment.filename)) {
    const isCached = previewCacheMap.value.has(attachment.id)
    previewAttachment.value = attachment
    if (!isCached) {
      nextTick(() => {
        previewCacheMap.value.set(attachment.id, { ...attachment })
      })
    }
    attachmentPreviewVisible.value = true
    return
  }
  const link = document.createElement('a')
  link.href = attachment.file_url
  link.download = attachment.filename
  link.click()
}

// 下载附件
const handleDownloadAttachment = (attachment: Attachment) => {
  const link = document.createElement('a')
  link.href = attachment.file_url
  link.download = attachment.filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 在预览弹窗中删除附件
const handleDeleteAttachmentInPreview = async (attachment: Attachment) => {
  if (!selectedArticle.value?.id) {
    Modal.message({
      message: translate('article.selectArticleFirst'),
      status: 'warning'
    })
    return
  }
  if (!hasArticleMemberRole.value) return

  const articleId = selectedArticle.value.id
  
  Modal.confirm({
    title: translate('article.deleteAttachment'),
    message: `${translate('article.deleteAttachmentConfirm')} "${attachment.filename}"？${translate('article.deleteAttachmentMessage')}`,
    status: 'warning'
  }).then(async (result: string) => {
    if (result !== 'confirm') return
    try {
      await fileApi.deleteFile(attachment.id)
      Modal.message({
        message: translate('article.deleteAttachmentSuccess'),
        status: 'success'
      })
      
      // 重新加载附件列表
      await loadAttachments(articleId)
      
      // 如果删除的是当前预览的附件，清空预览
      if (previewAttachment.value?.id === attachment.id) {
        previewAttachment.value = null
      }
      // 从缓存中移除已删除的附件
      previewCacheMap.value.delete(attachment.id)
    } catch (error) {
      Modal.message({
        message: `${translate('article.deleteAttachmentError')}: ${error instanceof Error ? error.message : translate('common.unknownError')}`,
        status: 'error'
      })
    }
  }).catch(() => {})
}

const loadArticleMemberFilterRoles = async () => {
  try {
    const res = await roleApi.getRoles({ page: 1, page_size: 100, status: 1 })
    articleMemberFilterRoles.value = res.items || []
  } catch {
    articleMemberFilterRoles.value = []
  }
}

// 获取文章成员列表（仅「按用户」Tab）
const fetchArticleMemberUsers = async () => {
  if (!managingArticleId.value) return
  
  try {
    articleMemberLoading.value = true
    
    const response = await articleApi.searchArticleMembers({
      article_id: managingArticleId.value,
      keyword: articleMemberSearchKeyword.value.trim(),
      page: articleMemberCurrentPage.value,
      page_size: articleMemberPageSize.value
    })
    
    articleMemberUsers.value = response.items || []
    articleMemberTotal.value = response.total || 0
  } catch (error: any) {
    Modal.message({
      message: error.message || translate('article.member.fetchError'),
      status: 'error'
    })
    articleMemberUsers.value = []
    articleMemberTotal.value = 0
  } finally {
    articleMemberLoading.value = false
  }
}

// 文章权限设置弹窗关闭处理
const handleArticleMemberModalClose = (visible: boolean) => {
  if (!visible) {
    articleMemberUsers.value = []
    articleMemberActiveTab.value = 'user'
    articleMemberSearchKeyword.value = ''
    articleMemberFilterRoleIds.value = []
    articleMemberRemoveRoleIds.value = []
    articleMemberBatchArticleRole.value = 1
    articleMemberCurrentPage.value = 1
    articleMemberTotal.value = 0
    managingArticleVisibility.value = null
    if (articleMemberSearchTimer) {
      clearTimeout(articleMemberSearchTimer)
      articleMemberSearchTimer = null
    }
  }
}

watch(articleMemberActiveTab, () => {
  if (!showArticleMemberModal.value) return
  articleMemberCurrentPage.value = 1
  if (articleMemberActiveTab.value === 'user') {
    fetchArticleMemberUsers()
  } else {
    articleMemberUsers.value = []
    articleMemberTotal.value = 0
  }
})

// 文章成员搜索（防抖）
const handleArticleMemberSearch = () => {
  if (articleMemberSearchTimer) {
    clearTimeout(articleMemberSearchTimer)
  }
  
  articleMemberSearchTimer = setTimeout(() => {
    articleMemberCurrentPage.value = 1
    fetchArticleMemberUsers()
  }, 500)
}

// 文章成员分页变化
const onArticleMemberPageChange = (e: { currentPage: number; pageSize?: number }) => {
  articleMemberCurrentPage.value = e.currentPage
  if (e.pageSize !== undefined) {
    articleMemberPageSize.value = e.pageSize
  }
  fetchArticleMemberUsers()
}

// 文章成员每页数量变化
const onArticleMemberSizeChange = (e: { currentPage: number; pageSize: number }) => {
  articleMemberPageSize.value = e.pageSize
  articleMemberCurrentPage.value = 1
  fetchArticleMemberUsers()
}

// 直接添加文章成员并设置角色
const handleAddArticleMemberWithRole = async (user: ArticleMemberSearchItem, role: number) => {
  if (!managingArticleId.value) return
  if (managingArticleVisibility.value === 1) {
    Modal.message({
      message: translate('article.member.cannotAddMembersPrivateVisibility'),
      status: 'warning'
    })
    return
  }

  const userId = user.user_id ?? user.id
  
  try {
    await articleApi.addArticleMember(managingArticleId.value!, {
      user_id: userId,
      role: role
    })
    Modal.message({
      message: translate('article.member.addSuccess'),
      status: 'success'
    })
    await fetchArticleMemberUsers()
  } catch (error: any) {
    Modal.message({
      message: error.message || translate('article.member.addError'),
      status: 'error'
    })
  }
}

// 修改文章成员角色
const handleChangeArticleMemberRole = async (user: ArticleMemberSearchItem, role: number) => {
  if (!managingArticleId.value) return
  
  const userId = user.user_id ?? user.id
  
  try {
    await articleApi.updateArticleMemberRole(managingArticleId.value!, userId, role)
    Modal.message({
      message: translate('article.member.roleChangeSuccess'),
      status: 'success'
    })
    await fetchArticleMemberUsers()
  } catch (error: any) {
    Modal.message({
      message: error.message || translate('article.member.roleChangeError'),
      status: 'error'
    })
  }
}

// 移除文章成员
const handleRemoveArticleMember = (user: ArticleMemberSearchItem) => {
  if (!managingArticleId.value) return
  
  const userId = user.user_id ?? user.id
  
  Modal.confirm({
    title: translate('article.member.removeConfirm'),
    message: translate('article.member.removeMessage', { name: user.username || `User ${userId}` }) || `确定要移除成员 ${user.username || `User ${userId}`} 吗？`,
    status: 'warning'
  }).then(async () => {
    try {
      await articleApi.removeArticleMember(managingArticleId.value!, userId)
      Modal.message({
        message: translate('article.member.removeSuccess'),
        status: 'success'
      })
      await fetchArticleMemberUsers()
    } catch (error: any) {
      Modal.message({
        message: error.message || translate('article.member.removeError'),
        status: 'error'
      })
    }
  }).catch(() => {
    // 用户取消
  })
}

const handleConfirmArticleBatchAddByRoles = async () => {
  if (!managingArticleId.value) return
  if (managingArticleVisibility.value === 1) {
    Modal.message({
      message: translate('article.member.cannotAddMembersPrivateVisibility'),
      status: 'warning'
    })
    return
  }
  if (articleMemberFilterRoleIds.value.length === 0) {
    Modal.message({
      message: translate('teamSpace.member.batchAddSelectRolesFirst'),
      status: 'warning'
    })
    return
  }
  articleMemberBatchAdding.value = true
  try {
    await articleApi.addArticleMember(managingArticleId.value, {
      role_ids: [...articleMemberFilterRoleIds.value],
      role: Number(articleMemberBatchArticleRole.value)
    })
    Modal.message({
      message: translate('teamSpace.member.batchAddSuccess'),
      status: 'success'
    })
    articleMemberActiveTab.value = 'user'
    articleMemberCurrentPage.value = 1
    await fetchArticleMemberUsers()
  } catch (e: any) {
    Modal.message({
      message: e?.message || translate('teamSpace.member.batchAddError'),
      status: 'error'
    })
  } finally {
    articleMemberBatchAdding.value = false
  }
}

const handleConfirmArticleBatchRemoveByRoles = () => {
  if (!managingArticleId.value) return
  if (articleMemberRemoveRoleIds.value.length === 0) {
    Modal.message({
      message: translate('teamSpace.member.batchAddSelectRolesFirst'),
      status: 'warning'
    })
    return
  }
  Modal.confirm({
    title: translate('teamSpace.member.batchRemoveTitle'),
    message: translate('teamSpace.member.batchRemoveMessage'),
    status: 'warning'
  })
    .then(async () => {
      articleMemberBatchRemoving.value = true
      try {
        await articleApi.batchRemoveArticleMembers(managingArticleId.value!, {
          role_ids: [...articleMemberRemoveRoleIds.value]
        })
        Modal.message({
          message: translate('teamSpace.member.batchRemoveSuccess'),
          status: 'success'
        })
        articleMemberActiveTab.value = 'user'
        articleMemberCurrentPage.value = 1
        await fetchArticleMemberUsers()
      } catch (e: any) {
        Modal.message({
          message: e?.message || translate('teamSpace.member.batchRemoveError'),
          status: 'error'
        })
      } finally {
        articleMemberBatchRemoving.value = false
      }
    })
    .catch(() => {})
}

// 获取角色文本
const getArticleMemberRoleText = (role?: number | null): string => {
  if (role === undefined || role === null) return '-'
  switch (role) {
    case 0:
      return translate('article.member.role.readonly') || translate('knowledgeBase.member.role.readonly')
    case 1:
      return translate('article.member.role.editor') || translate('knowledgeBase.member.role.editor')
    case 2:
      return translate('article.member.role.admin') || translate('knowledgeBase.member.role.admin')
    default:
      return '-'
  }
}

// 获取角色样式类
const getArticleMemberRoleClass = (role?: number | null): string => {
  if (role === undefined || role === null) return ''
  switch (role) {
    case 0:
      return 'role-readonly'
    case 1:
      return 'role-editor'
    case 2:
      return 'role-admin'
    default:
      return ''
  }
}

/** 侧栏团队空间卡片：当前用户团队空间角色（来自 knowledge-bases/{id}.team_space_role） */
const getTeamSpaceMemberRoleText = (role?: number | null): string => {
  if (role === undefined || role === null) return ''
  switch (role) {
    case 0:
      return translate('teamSpace.member.role.readonly')
    case 1:
      return translate('teamSpace.member.role.editor')
    case 2:
      return translate('teamSpace.member.role.admin')
    default:
      return ''
  }
}

/** 侧栏知识库卡片：当前用户知识库角色（来自 knowledge-bases/{id}.knowledge_base_role） */
const getKnowledgeBaseMemberRoleText = (role?: number | null): string => {
  if (role === undefined || role === null) return ''
  switch (role) {
    case 0:
      return translate('knowledgeBase.member.role.readonly')
    case 1:
      return translate('knowledgeBase.member.role.editor')
    case 2:
      return translate('knowledgeBase.member.role.admin')
    default:
      return ''
  }
}

// 在预览弹窗中选择附件
const handleSelectAttachmentForPreview = (attachment: Attachment) => {
  if (openOfficeOnlinePreview(attachment.file_url, attachment.filename, attachment.file_type)) {
    return
  }
  if (isImageFile(attachment.filename) || isVideoFile(attachment.filename)) {
    const isCached = previewCacheMap.value.has(attachment.id)
    previewAttachment.value = attachment
    if (!isCached) {
      nextTick(() => {
        previewCacheMap.value.set(attachment.id, { ...attachment })
      })
    }
    return
  }
  Modal.confirm({
    title: translate('article.previewNotSupported'),
    message: translate('article.previewNotSupportedMessage'),
    status: 'info'
  }).then((result: string) => {
    if (result !== 'confirm') return
    handleDownloadAttachment(attachment)
  }).catch(() => {})
}

// 在预览弹窗中选择文件上传
const handlePreviewUploadFileSelect = async (e: Event) => {
  const target = e.target as HTMLInputElement
  const files = target.files
  if (!files || files.length === 0) return
  
  if (!selectedArticle.value?.id) {
    Modal.message({
      message: translate('article.selectArticleFirst'),
      status: 'warning'
    })
    return
  }
  
  attachmentUploading.value = true
  
  try {
    const uploadPromises = Array.from(files).map(async (file) => {
      // 检查文件大小（200MB）
      const maxSize = 500 * 1024 * 1024
      if (file.size > maxSize) {
        throw new Error(`${translate('article.fileSizeExceeded')} ${maxSize / 1024 / 1024}MB`)
      }
      
      await fileApi.uploadFile(file, selectedArticle.value!.id)
    })
    
    await Promise.all(uploadPromises)
    
    Modal.message({
      message: translate('article.uploadAttachmentSuccess'),
      status: 'success'
    })
    
    // 重新加载附件列表
    await loadAttachments(selectedArticle.value.id)
    
    // 清空文件输入
    target.value = ''
  } catch (error) {
    Modal.message({
      message: `${translate('article.uploadAttachmentError')}: ${error instanceof Error ? error.message : translate('common.unknownError')}`,
      status: 'error'
    })
  } finally {
    attachmentUploading.value = false
  }
}

// 删除附件
const handleDeleteAttachment = (attachment: Attachment) => {
  if (!selectedArticle.value?.id) {
    Modal.message({
      message: translate('article.selectArticleFirst'),
      status: 'warning'
    })
    return
  }
  if (!hasArticleMemberRole.value) return

  const articleId = selectedArticle.value.id
  
  Modal.confirm({
    title: translate('article.deleteAttachmentConfirm'),
    message: translate('article.deleteAttachmentMessage', { filename: attachment.filename }),
    status: 'warning'
  }).then(async (result: string) => {
    if (result !== 'confirm') return
    
    try {
      // 使用 /api/files/{file_id} 接口删除文件
      // attachment.id 是附件ID，应该对应 file_id
      await fileApi.deleteFile(attachment.id)
      
      // 重新加载附件列表
      await loadAttachments(articleId)
      
      Modal.message({
        message: translate('article.deleteAttachmentSuccess'),
        status: 'success'
      })
    } catch (error) {
      console.error('删除附件失败:', error)
      Modal.message({
        message: `${translate('article.deleteAttachmentError')}: ${error instanceof Error ? error.message : translate('common.unknownError')}`,
        status: 'error'
      })
    }
  }).catch(() => {})
}

// 打开上传附件弹窗
const handleUploadAttachment = async () => {
  if (!selectedArticle.value?.id) {
    Modal.message({
      message: translate('article.selectArticleFirst'),
      status: 'warning'
    })
    return
  }
  if (!hasArticleMemberRole.value) return

  // 确保附件列表已加载
  if (attachments.value.length === 0 && !attachmentsLoading.value) {
    await loadAttachments(selectedArticle.value.id)
  }
  
  uploadAttachmentModalVisible.value = true
  selectedFiles.value = []
  uploadProgress.value = {}
  uploadingFiles.value.clear()
}

// 选择文件
const handleFileSelect = (e: Event) => {
  const target = e.target as HTMLInputElement
  const files = target.files
  if (files && files.length > 0) {
    selectedFiles.value = [...selectedFiles.value, ...Array.from(files)]
    // 清空文件输入，以便可以再次选择相同文件
    target.value = ''
  }
}

// 移除选中的文件
const handleRemoveFile = (index: number) => {
  selectedFiles.value.splice(index, 1)
  delete uploadProgress.value[index]
  uploadingFiles.value.delete(index)
}

// 处理拖拽上传
const handleDragOver = (e: DragEvent) => {
  e.preventDefault()
  e.stopPropagation()
}

const handleDrop = (e: DragEvent) => {
  e.preventDefault()
  e.stopPropagation()
  
  const files = e.dataTransfer?.files
  if (files && files.length > 0) {
    selectedFiles.value = [...selectedFiles.value, ...Array.from(files)]
  }
}

// 开始上传文件
const handleStartUpload = async () => {
  if (selectedFiles.value.length === 0) {
    Modal.message({
      message: translate('article.selectFilesFirst'),
      status: 'warning'
    })
    return
  }
  
  if (!selectedArticle.value?.id) {
    Modal.message({
      message: translate('article.selectArticleFirst'),
      status: 'warning'
    })
    return
  }
  
  attachmentUploading.value = true
  
  try {
    const uploadPromises = selectedFiles.value.map(async (file, index) => {
      // 检查文件大小（200MB）
      const maxSize = 500 * 1024 * 1024
      if (file.size > maxSize) {
        throw new Error(`${translate('article.fileSizeExceeded')} ${maxSize / 1024 / 1024}MB`)
      }
      
      uploadingFiles.value.add(index)
      uploadProgress.value[index] = 0
      
      try {
        await fileApi.uploadFile(
          file, 
          selectedArticle.value!.id,
          (progress) => {
            uploadProgress.value[index] = progress
          }
        )
        uploadProgress.value[index] = 100
      } catch (error) {
        uploadingFiles.value.delete(index)
        throw error
      } finally {
        uploadingFiles.value.delete(index)
      }
    })
    
    await Promise.all(uploadPromises)
    
    // 重新加载附件列表
    await loadAttachments(selectedArticle.value.id)
    
    // 关闭弹窗并清空文件列表
    uploadAttachmentModalVisible.value = false
    selectedFiles.value = []
    uploadProgress.value = {}
    
    Modal.message({
      message: translate('article.uploadAttachmentSuccess'),
      status: 'success'
    })
  } catch (error) {
    console.error('附件上传失败:', error)
    Modal.message({
      message: `${translate('article.uploadAttachmentError')}: ${error instanceof Error ? error.message : translate('common.unknownError')}`,
      status: 'error'
    })
  } finally {
    attachmentUploading.value = false
  }
}

// 关闭上传弹窗
const handleCloseUploadModal = () => {
  if (uploadingFiles.value.size > 0) {
    Modal.confirm({
      title: translate('article.cancelUploadConfirm'),
      message: translate('article.cancelUploadMessage'),
      status: 'warning'
    }).then((result: string) => {
      if (result === 'confirm') {
        uploadAttachmentModalVisible.value = false
        selectedFiles.value = []
        uploadProgress.value = {}
        uploadingFiles.value.clear()
      }
    }).catch(() => {})
  } else {
    uploadAttachmentModalVisible.value = false
    selectedFiles.value = []
    uploadProgress.value = {}
  }
}

// 处理附件文件选择
const handleAttachmentFileChange = async (e: Event) => {
  const target = e.target as HTMLInputElement
  const files = target.files
  if (!files || files.length === 0) return
  
  if (!selectedArticle.value?.id) {
    Modal.message({
      message: '请先选择文章',
      status: 'warning'
    })
    return
  }
  
  attachmentUploading.value = true
  
  try {
    // 上传所有文件
    const uploadPromises = Array.from(files).map(async (file) => {
      // 检查文件大小（200MB）
      const maxSize = 500 * 1024 * 1024
      if (file.size > maxSize) {
        throw new Error(`${translate('article.fileSizeExceeded')} ${maxSize / 1024 / 1024}MB`)
      }
      
      return await fileApi.uploadFile(file, selectedArticle.value!.id)
    })
    
    await Promise.all(uploadPromises)
    
    // 重新加载附件列表
    await loadAttachments(selectedArticle.value.id)
    
    Modal.message({
      message: translate('article.uploadAttachmentSuccess'),
      status: 'success'
    })
  } catch (error) {
    console.error('附件上传失败:', error)
    Modal.message({
      message: `${translate('article.uploadAttachmentError')}: ${error instanceof Error ? error.message : translate('common.unknownError')}`,
      status: 'error'
    })
  } finally {
    attachmentUploading.value = false
    // 清空文件输入
    if (target) {
      target.value = ''
    }
  }
}

// 加载文章详情（可复用函数）
const loadArticle = async (articleId: number) => {
  // 如果正在编辑，先退出编辑模式
  if (isEditing.value) {
    isEditing.value = false
  }
  
  // 立即显示加载状态，清空之前的内容
  articleLoading.value = true
  articleLoadError.value = null
  articleAdmins.value = []
  showApplyEditForm.value = false
  applyEditRemark.value = ''
  applyEditRole.value = DEFAULT_APPLY_ROLE
  applyReviewerIds.value = []
  selectedArticle.value = null
  clearSignReadTimer()
  signReadCheck.value = null
  signReadElapsed.value = 0
  
  // 加载文章详情
  try {
    const article = await articleApi.getArticle(articleId)
    selectedArticle.value = article
    const treeHit = findNodeInTree(treeData.value, articleId)
    if (treeHit?.node) {
      treeHit.node.my_role = article.my_role
      if (treeHit.node.originalData) {
        treeHit.node.originalData.my_role = article.my_role
      }
    }
    articleLoadError.value = null
    // 重置编辑器内容（用于预览和编辑）
    editorContent.value = article.content || ''
    originalContent.value = article.content || ''
    
    // 加载附件列表
    await loadAttachments(articleId)
    
    // 生成目录 - 使用多次重试确保编辑器已完全初始化
    setTimeout(() => {
      generateTableOfContents()
    }, 800) // 延迟800ms确保编辑器内容已完全渲染

    // 检查当前用户是否需要签读
    await fetchSignReadCheck(articleId)
  } catch (error: any) {
    console.error('加载文章详情失败:', error)
    selectedArticle.value = null
    const status = error?.response?.status ?? error?.code
    if (status === 404) {
      articleLoadError.value = 'not_found'
    } else if (status === 403) {
      articleLoadError.value = 'permission'
      fetchArticleAdmins(articleId)
    } else {
      articleLoadError.value = null
    }
  } finally {
    articleLoading.value = false
  }
}

// 无权限时拉取文章管理员列表（GET /api/permissions/admins）用于展示
const fetchArticleAdmins = async (articleId: number) => {
  articleAdminsLoading.value = true
  articleAdmins.value = []
  try {
    const list = await articleApi.getArticleAdmins(articleId)
    articleAdmins.value = Array.isArray(list) ? list : []
  } catch (e) {
    console.error('获取文章管理员列表失败:', e)
    articleAdmins.value = []
  } finally {
    articleAdminsLoading.value = false
  }
}

const treeNodeHasExpandableChildren = (data: any, treeNode: { childNodes?: unknown[] } | null) => {
  const hasLazyChildren = data.originalData?.has_children === true || data.has_children === true
  const hasLoadedChildren =
    (treeNode?.childNodes && treeNode.childNodes.length > 0) ||
    (data.children && Array.isArray(data.children) && data.children.length > 0)
  return hasLazyChildren || hasLoadedChildren
}

const setTreeNodeExpanded = (treeNode: { expand?: () => void; collapse?: () => void; expanded?: boolean }, expanded: boolean) => {
  if (expanded) {
    if (typeof treeNode.expand === 'function') {
      treeNode.expand()
    } else {
      treeNode.expanded = true
    }
    return
  }
  if (typeof treeNode.collapse === 'function') {
    treeNode.collapse()
  } else {
    treeNode.expanded = false
  }
}

/** 展开/折叠树节点（懒加载与 @node-expand 一致） */
const toggleTreeNodeExpand = async (data: any) => {
  if (!treeRef.value || !data) return false

  try {
    const treeNode = treeRef.value.getNode(data.id)
    if (!treeNode || !treeNodeHasExpandableChildren(data, treeNode)) return false

    if (treeNode.expanded) {
      setTreeNodeExpanded(treeNode, false)
    } else {
      await handleNodeExpand(data)
      await nextTick()
      setTreeNodeExpanded(treeNode, true)
    }
    return true
  } catch (error) {
    console.error('切换树节点展开状态失败:', error)
    return false
  }
}

// 节点点击事件
const handleNodeClick = async (data: any) => {
  // 平板/手机：未展开的父节点单击先展开，便于浏览子级（双击仍可折叠）
  if (isCompactLayout.value && treeRef.value && data) {
    const treeNode = treeRef.value.getNode(data.id)
    if (
      treeNode &&
      !treeNode.expanded &&
      treeNodeHasExpandableChildren(data, treeNode)
    ) {
      await handleNodeExpand(data)
      await nextTick()
      setTreeNodeExpanded(treeNode, true)
      return
    }
  }

  // 如果点击的是当前选中的文章，不需要重复加载
  if (selectedArticle.value?.id === data.id) {
    closeMobileTreeDrawer()
    return
  }

  closeMobileTreeDrawer()
  // 更新 URL 参数，让 watch 监听路由变化来加载文章
  router.push({
    path: route.path,
    query: {
      ...route.query,
      articleId: data.id.toString()
    }
  })
  // 不再直接调用 loadArticle，避免与 watch 重复请求
}

// 处理节点双击事件 - 展开/折叠节点（桌面端；紧凑布局亦可折叠已展开节点）
const handleNodeDoubleClick = async (data: any) => {
  await toggleTreeNodeExpand(data)
}

// 树节点设置 - 修改（打开编辑弹窗：标题、节点类型、可见范围）
const handleTreeNodeEdit = async (data: any) => {
  if (!data?.id) return
  try {
    const art = await articleApi.getArticle(data.id)
    const nt = art.node_type != null ? Number(art.node_type) : 1
    editArticleForm.value = {
      id: art.id,
      title: art.title || '',
      node_type: nt === 1 || nt === 2 ? nt : 1,
      visibility: art.visibility != null ? Number(art.visibility) : 1
    }
    editArticleModalVisible.value = true
    nextTick(() => editArticleFormRef.value?.clearValidate?.())
  } catch (e) {
    Modal.message({ message: (e as Error)?.message || translate('article.fetchError'), status: 'error' })
  }
}

// 树节点设置 - 权限设置（个人可见 visibility=1 不可添加成员）
const handleTreeNodeManageMembers = async (data: any) => {
  if (!data?.id) return
  let vis: number | null | undefined = data.originalData?.visibility
  if (vis === undefined || vis === null) {
    try {
      const art = await articleApi.getArticle(data.id)
      vis = art.visibility != null ? Number(art.visibility) : undefined
    } catch (e: any) {
      Modal.message({ message: e?.message || translate('article.fetchError'), status: 'error' })
      return
    }
  }
  if (Number(vis) === 1) {
    Modal.message({
      message: translate('article.member.cannotAddMembersPrivateVisibility'),
      status: 'warning'
    })
    return
  }
  managingArticleId.value = data.id
  managingArticleVisibility.value = vis != null ? Number(vis) : null
  articleMemberActiveTab.value = 'user'
  articleMemberSearchKeyword.value = ''
  articleMemberFilterRoleIds.value = []
  articleMemberRemoveRoleIds.value = []
  articleMemberBatchArticleRole.value = 1
  articleMemberCurrentPage.value = 1
  articleMemberPageSize.value = 10
  showArticleMemberModal.value = true
  await loadArticleMemberFilterRoles()
  await fetchArticleMemberUsers()
}

// 无权限时点击「申请编辑」：展开下方的备注输入与提交表单
const handleApplyForArticleAccess = () => {
  showApplyEditForm.value = true
}

// 提交申请编辑（带备注）到后端
const handleSubmitApplyEdit = async () => {
  const articleId = route.query.articleId ? Number(route.query.articleId) : null
  if (!articleId || isNaN(articleId)) return
  applyEditSubmitting.value = true
  try {
    const remark = applyEditRemark.value.trim()
    await articleApi.applyForEdit(articleId, {
      role: applyEditRole.value,
      message: remark ? remark : undefined,
      reviewer_ids: applyReviewerIds.value.length > 0 ? applyReviewerIds.value : null
    })
    Modal.message({ message: translate('article.applyEditSuccess'), status: 'success' })
    showApplyEditForm.value = false
    applyEditRemark.value = ''
    applyEditRole.value = DEFAULT_APPLY_ROLE
    applyReviewerIds.value = []
  } catch (e: any) {
    Modal.message({ message: e?.message || translate('article.applyEditError'), status: 'error' })
  } finally {
    applyEditSubmitting.value = false
  }
}

// 递归更新树中某节点的 label、节点类型、可见范围与 originalData
const updateNodeInTreeData = (
  tree: any[],
  id: number,
  patch: { label?: string; visibility?: number; node_type?: number }
): boolean => {
  for (const node of tree) {
    if (Number(node.id) === id) {
      if (patch.label != null) {
        node.label = patch.label
        if (node.originalData) node.originalData.title = patch.label
      }
      if (patch.node_type != null) {
        node.node_type = patch.node_type
        if (node.originalData) node.originalData.node_type = patch.node_type
      }
      if (node.originalData && patch.visibility != null) node.originalData.visibility = patch.visibility
      return true
    }
    if (node.children?.length && updateNodeInTreeData(node.children, id, patch)) return true
  }
  return false
}

// 编辑文章弹窗 - 保存
const handleEditArticleSave = async () => {
  if (!editArticleFormRef.value || !editArticleForm.value.id) return
  await editArticleFormRef.value.validate(async (valid: boolean) => {
    if (!valid) return
    editArticleSaving.value = true
    try {
      const { id, title, visibility, node_type } = editArticleForm.value
      const nt = node_type === 1 || node_type === 2 ? node_type : 1
      await articleApi.updateArticle(id!, { title: title || null, visibility, node_type: nt })
      updateNodeInTreeData(treeData.value, id!, { label: title, visibility, node_type: nt })
      if (selectedArticle.value?.id === id) {
        selectedArticle.value = { ...selectedArticle.value!, title, visibility, node_type: nt }
      }
      editArticleModalVisible.value = false
      Modal.message({ message: translate('article.updateSuccess'), status: 'success' })
    } catch (e) {
      Modal.message({ message: (e as Error)?.message || translate('article.saveError'), status: 'error' })
    } finally {
      editArticleSaving.value = false
    }
  })
}

// 递归从树中移除节点
const removeNodeFromTreeData = (tree: any[], targetId: string): boolean => {
  for (let i = 0; i < tree.length; i++) {
    if (String(tree[i].id) === targetId) {
      tree.splice(i, 1)
      return true
    }
    if (tree[i].children?.length) {
      if (removeNodeFromTreeData(tree[i].children, targetId)) return true
    }
  }
  return false
}

// 树节点设置 - 删除
const handleTreeNodeDelete = (data: any) => {
  if (!data?.id) return
  const title = data.label || data.originalData?.title || ''
  Modal.confirm({
    title: translate('article.deleteConfirm'),
    message: translate('article.deleteMessage', { title: title || String(data.id) }),
    status: 'warning'
  }).then(async (result: string) => {
    if (result !== 'confirm') return
    try {
      await articleApi.deleteArticle(data.id)
      if (treeRef.value && typeof treeRef.value.remove === 'function') {
        treeRef.value.remove(String(data.id))
      }
      removeNodeFromTreeData(treeData.value, String(data.id))
      if (selectedArticle.value?.id === data.id) {
        selectedArticle.value = null
        const q = { ...route.query }
        delete (q as Record<string, unknown>).articleId
        router.replace({ path: route.path, query: q })
      }
      Modal.message({ message: translate('article.deleteSuccess'), status: 'success' })
    } catch (e) {
      Modal.message({ message: (e as Error)?.message || translate('article.deleteError'), status: 'error' })
    }
  }).catch(() => {})
}

// 开始编辑
// 获取所有缓存的草稿（对象形式，键为文章ID）
const getAllDraftsFromCache = (): Record<number, { content: string; timestamp: number }> => {
  try {
    const cached = localStorage.getItem(DRAFT_CACHE_KEY)
    if (!cached) return {}
    
    const drafts = JSON.parse(cached)
    const now = Date.now()
    const validDrafts: Record<number, { content: string; timestamp: number }> = {}
    
    // 清理过期缓存并返回有效缓存
    for (const [articleIdStr, draft] of Object.entries(drafts)) {
      const articleId = Number(articleIdStr)
      const draftData = draft as { content: string; timestamp: number }
      
      // 检查是否过期
      if (now - draftData.timestamp <= DRAFT_CACHE_TIMEOUT) {
        validDrafts[articleId] = draftData
      }
    }
    
    // 如果有过期缓存被清理，更新存储
    if (Object.keys(validDrafts).length !== Object.keys(drafts).length) {
      localStorage.setItem(DRAFT_CACHE_KEY, JSON.stringify(validDrafts))
    }
    
    return validDrafts
  } catch (error) {
    console.error('读取草稿缓存失败:', error)
    // 如果解析失败，清除缓存
    try {
      localStorage.removeItem(DRAFT_CACHE_KEY)
    } catch {}
    return {}
  }
}

// 保存编辑内容到本地缓存
const saveDraftToCache = () => {
  if (!selectedArticle.value || !isEditing.value) return
  
  try {
    const drafts = getAllDraftsFromCache()
    const articleId = selectedArticle.value.id
    
    // 更新或添加当前文章的草稿
    drafts[articleId] = {
      content: editorContent.value,
      timestamp: Date.now()
    }
    
    localStorage.setItem(DRAFT_CACHE_KEY, JSON.stringify(drafts))
  } catch (error) {
    console.error('保存草稿到本地缓存失败:', error)
  }
}

// 清除本地缓存（可以清除特定文章或全部）
const clearDraftCache = (articleId?: number) => {
  try {
    if (articleId !== undefined) {
      // 清除特定文章的缓存
      const drafts = getAllDraftsFromCache()
      delete drafts[articleId]
      localStorage.setItem(DRAFT_CACHE_KEY, JSON.stringify(drafts))
    } else {
      // 清除所有缓存
      localStorage.removeItem(DRAFT_CACHE_KEY)
    }
  } catch (error) {
    console.error('清除草稿缓存失败:', error)
  }
}

// 获取指定文章的本地缓存草稿
const getDraftFromCache = (articleId: number): { content: string; timestamp: number } | null => {
  try {
    const drafts = getAllDraftsFromCache()
    return drafts[articleId] || null
  } catch (error) {
    console.error('读取草稿缓存失败:', error)
    return null
  }
}

const handleStartEdit = async () => {
  if (!selectedArticle.value) return
  if (!hasArticleMemberRole.value) return
  isEditing.value = true
  editorContent.value = selectedArticle.value.content || ''
  originalContent.value = selectedArticle.value.content || ''
  await loadKbTagsForEdit()
  syncEditFlagsFromArticle()

  // 等待编辑用 FluentEditorV4 挂载后聚焦
  nextTick(() => {
    if (editorRef.value?.focus) {
      setTimeout(() => {
        editorRef.value?.focus?.()
      }, 100)
    }
  })
}

// 取消编辑
const handleCancelEdit = () => {
  if (!selectedArticle.value) return
  isEditing.value = false
  editorContent.value = originalContent.value
  syncEditFlagsFromArticle()
  // 清除当前文章的本地缓存（取消编辑时也清除缓存）
  clearDraftCache(selectedArticle.value.id)
  // 生成目录
  setTimeout(() => {
    generateTableOfContents()
  }, 800)
}

// 文章操作处理函数
// 加载文章统计信息
const loadArticleStats = async () => {
  if (!selectedArticle.value) return
  
  try {
    const stats = await articleApi.getArticleStats(selectedArticle.value.id)
    isLiked.value = stats.is_liked || false
    isFavorited.value = stats.is_collected || false
    
    // 更新文章的统计数据
    if (selectedArticle.value) {
      if (stats.like_count !== undefined) {
        selectedArticle.value.like_count = stats.like_count
      }
      if (stats.collect_count !== undefined) {
        selectedArticle.value.collect_count = stats.collect_count
      }
      if (stats.view_count !== undefined) {
        selectedArticle.value.view_count = stats.view_count
      }
      if (stats.comment_count !== undefined) {
        selectedArticle.value.comment_count = stats.comment_count
      }
      if (stats.feedback_count !== undefined) {
        selectedArticle.value.feedback_count = stats.feedback_count
      }
    }
  } catch (error) {
    console.error('获取文章统计信息失败:', error)
  }
}

const handleLike = async () => {
  if (!selectedArticle.value) return
  
  // 防止重复点击
  if (likeLoading.value) return
  likeLoading.value = true
  
  try {
    if (isLiked.value) {
      // 取消点赞
      await articleApi.unlikeArticle(selectedArticle.value.id)
    } else {
      // 点赞
      await articleApi.likeArticle(selectedArticle.value.id)
    }
    // 重新加载统计信息
    await loadArticleStats()
  } catch (error) {
    console.error('点赞操作失败:', error)
  } finally {
    likeLoading.value = false
  }
}

const handleFavorite = async () => {
  if (!selectedArticle.value) return
  
  // 防止重复点击
  if (favoriteLoading.value) return
  favoriteLoading.value = true
  
  try {
    if (isFavorited.value) {
      // 取消收藏
      await articleApi.uncollectArticle(selectedArticle.value.id)
    } else {
      // 收藏
      await articleApi.collectArticle(selectedArticle.value.id)
    }
    // 重新加载统计信息
    await loadArticleStats()
  } catch (error) {
    console.error('收藏操作失败:', error)
  } finally {
    favoriteLoading.value = false
  }
}

const dismissMobileChromeForDrawer = () => {
  mobileActionsExpanded.value = false
  if (isMobileLayout.value) {
    tocVisible.value = false
    attachmentsVisible.value = false
  }
}

const handleComment = () => {
  if (!selectedArticle.value) return
  dismissMobileChromeForDrawer()
  commentDrawerVisible.value = true
}

// 评论添加后的处理
const handleCommentAdded = async () => {
  // 重新加载统计信息
  await loadArticleStats()
}

const handleFeedback = () => {
  if (!selectedArticle.value) return
  dismissMobileChromeForDrawer()
  feedbackDrawerVisible.value = true
}

// 反馈添加后的处理
const handleFeedbackAdded = async () => {
  // 重新加载统计信息
  await loadArticleStats()
}

// 保存文章
const handleSaveArticle = async () => {
  if (!selectedArticle.value) return
  
  saving.value = true
  try {
    const updatedArticle = await articleApi.updateArticle(selectedArticle.value.id, {
      content: editorContent.value,
      is_original: editingIsOriginal.value,
      is_ai_generated: editingIsAiGenerated.value,
      tag_ids: [...editingTagIds.value]
    })
    
    // 更新选中的文章
    selectedArticle.value = updatedArticle
    originalContent.value = updatedArticle.content || ''
    editorContent.value = updatedArticle.content || ''
    isEditing.value = false
    
    // 清除当前文章的本地缓存
    if (selectedArticle.value) {
      clearDraftCache(selectedArticle.value.id)
    }
    
    // 重新加载附件列表
    if (selectedArticle.value?.id) {
      await loadAttachments(selectedArticle.value.id)
    }
    
    // 生成目录
    setTimeout(() => {
      generateTableOfContents()
    }, 800)
    
    // 显示成功消息
    Modal.message({
      message: translate('article.updateSuccess'),
      status: 'success'
    })
  } catch (error) {
    console.error('保存文章失败:', error)
    // 显示错误消息（可以后续添加消息提示组件）
    console.error(translate('article.saveError'))
  } finally {
    saving.value = false
  }
}

// 节点展开事件（懒加载子节点）
const handleNodeExpand = async (data: any) => {
  // 检查节点是否已经加载过子节点
  // 如果 children 已经存在且有实际数据（长度 > 0），说明已经加载过，无需重复加载
  if (data.children && Array.isArray(data.children) && data.children.length > 0) {
    // 检查是否是有效的子节点（不是占位符）
    const hasValidChildren = data.children.some((child: any) => child.id && child.id !== undefined)
    if (hasValidChildren) {
      // 已经加载过子节点，无需重复请求
      return
    }
  }
  
  // 检查 has_children 为 true，且节点还没有加载过子节点，则加载
  const hasChildren = data.originalData?.has_children === true || data.has_children === true
  if (hasChildren) {
    await loadNodeChildren(data)
  }
}

// 格式化日期
const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

// 格式化可见性显示
const formatVisibility = (visibility?: number | null): string => {
  if (visibility === undefined || visibility === null) return '-'
  switch (visibility) {
    case 1:
      return translate('knowledgeBase.visibility.private')
    case 2:
      return translate('knowledgeBase.visibility.member')
    case 3:
      return translate('knowledgeBase.visibility.public')
    default:
      return '-'
  }
}

// 格式化内容（简单的markdown转HTML，可以后续优化）
const _formatContent = (content: string) => {
  if (!content) return ''
  // 简单的换行处理
  return content.replace(/\n/g, '<br>')
}

/** OpenTiny 下拉/弹层常挂在 body，焦点不在 .tree-node-edit 内但仍属于「正在选下拉」 */
function isTempNodeFocusInOpentinyOverlay(el: HTMLElement | null): boolean {
  if (!el) return false
  return !!(
    el.closest?.('.tiny-select-dropdown') ||
    el.closest?.('.tiny-popper') ||
    el.closest?.('.tiny-popover') ||
    el.closest?.('.tiny-picker-panel')
  )
}

// 设置临时输入框引用
const setTempInputRef = (nodeId: string, el: any) => {
  if (el) {
    tempInputRefs.value[nodeId] = el
    // 等待 DOM 更新后聚焦
    nextTick(() => {
      if (el.focus) {
        el.focus()
      } else if (el.$el && el.$el.querySelector) {
        const input = el.$el.querySelector('input')
        if (input) {
          input.focus()
        }
      }
    })
  }
}

// 处理顶部添加
const handleAddTop = () => {
  if (!knowledgeBaseId.value || !canAddTreeArticles.value) return
  
  // 创建临时节点
  const tempId = `temp-${Date.now()}`
  const tempNode = {
    id: tempId,
    label: '',
    type: 'article' as const,
    node_type: 1,
    visibility: 1,
    parent_id: null,
    originalData: null,
    children: [],
    isTemp: true
  }
  
  // 添加到顶部
  treeData.value.unshift(tempNode)
  
  // 强制更新树组件
  nextTick(() => {
    // 确保树组件更新
    if (treeRef.value) {
      // 尝试调用树组件的更新方法
      if (typeof treeRef.value.updateKeyChildren === 'function') {
        treeRef.value.updateKeyChildren(tempId, tempNode)
      }
    }
  })
}

// 处理底部添加
const handleAddBottom = () => {
  if (!knowledgeBaseId.value || !canAddTreeArticles.value) return
  
  // 创建临时节点
  const tempId = `temp-${Date.now()}`
  const tempNode = {
    id: tempId,
    label: '',
    type: 'article' as const,
    node_type: 1,
    visibility: 1,
    parent_id: null,
    originalData: null,
    children: [],
    isTemp: true
  }
  
  // 添加到底部
  treeData.value.push(tempNode)
  console.log('treeData', treeData.value, treeData.value.length, treeData.value[treeData.value.length - 1])
  // 强制更新树组件并聚焦输入框
  nextTick(() => {
    // 使用 setTimeout 确保 DOM 完全渲染
    setTimeout(() => {
      const inputRef = tempInputRefs.value[tempId]
      if (inputRef) {
        if (inputRef.focus) {
          inputRef.focus()
        } else if (inputRef.$el) {
          const input = inputRef.$el.querySelector?.('input') || inputRef.$el
          if (input && input.focus) {
            input.focus()
          }
        }
      }
    }, 50)
  })
}

// 处理前插入
const handleInsertBefore = (data: any) => {
  if (!knowledgeBaseId.value || !treeRef.value || !canAddTreeArticles.value) return
  
  const tree = treeRef.value
  const treeNode = tree.getNode(data.id)
  
  if (!treeNode) return
  
  // 创建临时节点
  const tempId = `temp-${Date.now()}`
  const tempNode = {
    id: tempId,
    label: '',
    type: 'article' as const,
    node_type: 1,
    visibility: 1,
    parent_id: data.parent_id, // 使用相同的父节点
    originalData: null,
    children: [],
    isTemp: true,
    insertType: 'before' as const, // 标记为前插入
    targetNodeId: data.id // 保存目标节点ID
  }
  
  // 使用 TinyTree 的 insertBefore 方法
  if (typeof tree.insertBefore === 'function') {
    tree.insertBefore(tempNode, treeNode)
  } else {
    // 如果方法不存在，直接操作数据
    const parent = treeNode.parent
    const children = parent ? (parent.data.children || []) : treeData.value
    const index = children.findIndex((item: any) => String(item.id) === String(data.id))
    if (index !== -1) {
      children.splice(index, 0, tempNode)
    } else {
      // 如果找不到，使用递归查找
      const result = findNodeInTree(treeData.value, data.id)
      if (result) {
        result.children.splice(result.index, 0, tempNode)
      }
    }
  }
  
  // 聚焦输入框
  nextTick(() => {
    setTimeout(() => {
      const inputRef = tempInputRefs.value[tempId]
      if (inputRef) {
        if (inputRef.focus) {
          inputRef.focus()
        } else if (inputRef.$el) {
          const input = inputRef.$el.querySelector?.('input') || inputRef.$el
          if (input && input.focus) {
            input.focus()
          }
        }
      }
    }, 50)
  })
}

// 处理后插入
const handleInsertAfter = (data: any) => {
  if (!knowledgeBaseId.value || !treeRef.value || !canAddTreeArticles.value) return
  
  const tree = treeRef.value
  const treeNode = tree.getNode(data.id)
  
  if (!treeNode) return
  
  // 创建临时节点
  const tempId = `temp-${Date.now()}`
  const tempNode = {
    id: tempId,
    label: '',
    type: 'article' as const,
    node_type: 1,
    visibility: 1,
    parent_id: data.parent_id, // 使用相同的父节点
    originalData: null,
    children: [],
    isTemp: true,
    insertType: 'after' as const, // 标记为后插入
    targetNodeId: data.id // 保存目标节点ID
  }
  
  // 使用 TinyTree 的 insertAfter 方法
  if (typeof tree.insertAfter === 'function') {
    tree.insertAfter(tempNode, treeNode)
  } else {
    // 如果方法不存在，直接操作数据
    const parent = treeNode.parent
    const children = parent ? (parent.data.children || []) : treeData.value
    const index = children.findIndex((item: any) => String(item.id) === String(data.id))
    if (index !== -1) {
      children.splice(index + 1, 0, tempNode)
    } else {
      // 如果找不到，使用递归查找
      const result = findNodeInTree(treeData.value, data.id)
      if (result) {
        result.children.splice(result.index + 1, 0, tempNode)
      }
    }
  }
  
  // 聚焦输入框
  nextTick(() => {
    setTimeout(() => {
      const inputRef = tempInputRefs.value[tempId]
      if (inputRef) {
        if (inputRef.focus) {
          inputRef.focus()
        } else if (inputRef.$el) {
          const input = inputRef.$el.querySelector?.('input') || inputRef.$el
          if (input && input.focus) {
            input.focus()
          }
        }
      }
    }, 50)
  })
}

// 处理添加子节点（支持嵌套，可以在任何层级的节点上添加子节点）
const handleAddChild = (data: any) => {
  if (!knowledgeBaseId.value || !treeRef.value || !canAddTreeArticles.value) return
  
  const tree = treeRef.value
  const treeNode = tree.getNode(data.id)
  
  if (!treeNode) return
  
  // 创建临时节点，确保设置父节点ID（支持嵌套，无论父节点在哪一层）
  const tempId = `temp-${Date.now()}`
  const parentNodeId = data.id // 父节点ID（数字类型），可以是任何层级的节点
  const tempNode = {
    id: tempId,
    label: '',
    type: 'article' as const,
    node_type: 1,
    visibility: 1,
    parent_id: parentNodeId, // 父节点ID，支持嵌套结构
    originalData: null,
    children: [],
    isTemp: true
  }
  
  // 使用 TinyTree 的 append 方法插入子节点（支持嵌套）
  if (typeof tree.append === 'function') {
    tree.append(tempNode, treeNode)
    // 确保使用内置方法后，节点的 parent_id 仍然保留
    // 因为组件可能会修改节点对象，所以需要重新获取并设置
    nextTick(() => {
      const appendedNode = tree.getNode(tempId)
      if (appendedNode && appendedNode.data) {
        appendedNode.data.parent_id = parentNodeId
        // 确保 isTemp 标记保留
        appendedNode.data.isTemp = true
      }
    })
  } else {
    // 如果方法不存在，直接操作数据（支持嵌套）
    if (!treeNode.data.children) {
      treeNode.data.children = []
    }
    treeNode.data.children.push(tempNode)
    // 同时更新树数据，确保嵌套结构正确
    updateTreeDataForNode(treeData.value, data.id, tempNode)
  }
  
  // 如果节点未展开，需要展开它（支持嵌套展开）
  if (!treeNode.expanded && typeof treeNode.expand === 'function') {
    treeNode.expand()
  }
  
  // 聚焦输入框
  nextTick(() => {
    setTimeout(() => {
      const inputRef = tempInputRefs.value[tempId]
      if (inputRef) {
        if (inputRef.focus) {
          inputRef.focus()
        } else if (inputRef.$el) {
          const input = inputRef.$el.querySelector?.('input') || inputRef.$el
          if (input && input.focus) {
            input.focus()
          }
        }
      }
    }, 50)
  })
}

// 递归更新树数据中的节点（支持嵌套结构）
const updateTreeDataForNode = (tree: any[], parentId: number | string, newNode: any): boolean => {
  for (const item of tree) {
    if (String(item.id) === String(parentId)) {
      if (!item.children) {
        item.children = []
      }
      item.children.push(newNode)
      return true
    }
    if (item.children && item.children.length > 0) {
      if (updateTreeDataForNode(item.children, parentId, newNode)) {
        return true
      }
    }
  }
  return false
}

// 保存临时节点（内部方法）
const saveTempNode = async (node: any) => {
  if (!node || !node.isTemp) return
  
  const nodeId = String(node.id)
  
  // 如果该节点正在保存中，直接返回，防止重复提交
  if (savingNodeIds.value.has(nodeId)) {
    return
  }
  
  const title = node.label?.trim()
  if (!title) {
    // 如果标题为空，移除临时节点
    removeTempNode(nodeId)
    return
  }
  
  if (!knowledgeBaseId.value) return
  
  // 标记该节点正在保存
  savingNodeIds.value.add(nodeId)
  creating.value = true
  
  try {
    // 获取节点的parent_id（可能为null表示顶级，或为父节点ID）
    // 如果是子节点，parent_id 应该是父节点的ID（数字类型）
    let parentId: number | null = null
    if (node.parent_id !== undefined && node.parent_id !== null) {
      // 确保 parent_id 是数字类型
      if (typeof node.parent_id === 'string') {
        const parsedId = parseInt(node.parent_id, 10)
        if (!isNaN(parsedId)) {
          parentId = parsedId
        }
      } else if (typeof node.parent_id === 'number') {
        parentId = node.parent_id
      }
    }
    
    // 计算 after_article_id：根据插入类型正确计算
    let after_article_id: number | null = null
    
    // 如果节点有 insertType 和 targetNodeId，说明是通过前插入或后插入创建的
    if (node.insertType && node.targetNodeId) {
      const targetId = node.targetNodeId
      const targetFound = findNodeInTree(treeData.value, targetId)
      
      if (targetFound) {
        if (node.insertType === 'after') {
          // 后插入：after_article_id 应该是目标节点本身
          const targetNodeId = targetFound.node?.id
          if (targetNodeId != null && !String(targetNodeId).startsWith('temp-')) {
            const n = Number(targetNodeId)
            after_article_id = Number.isFinite(n) ? n : null
          }
        } else if (node.insertType === 'before') {
          // 前插入：临时节点插在目标前，故 targetFound.children[index-1] 是临时节点本身
          // 需取 index-2 才是真正的“前一个兄弟”，作为 after_article_id
          if (targetFound.index >= 2) {
            const prev = targetFound.children[targetFound.index - 2]
            const prevId = prev?.id
            if (prevId != null && !String(prevId).startsWith('temp-')) {
              const n = Number(prevId)
              after_article_id = Number.isFinite(n) ? n : null
            }
          } else if (targetFound.index === 1) {
            // 临时节点在 index 0，目标在 index 1，无真实前兄弟
            after_article_id = null
          }
          // index === 0 理论上不应出现（目标前已有临时节点）
        }
      }
    } else {
      // 如果没有 insertType，使用原来的逻辑（用于顶部添加、底部添加、添加子节点等情况）
      const found = findNodeInTree(treeData.value, nodeId)
      if (found && found.index >= 1) {
        const prev = found.children[found.index - 1]
        const prevId = prev?.id
        if (prevId != null && !String(prevId).startsWith('temp-')) {
          const n = Number(prevId)
          after_article_id = Number.isFinite(n) ? n : null
        }
      }
    }
    
    const rawNodeType = node.node_type
    const nodeType =
      rawNodeType === 1 || rawNodeType === 2 ? rawNodeType : 1

    const rawVis = node.visibility
    const visibility =
      rawVis === 1 || rawVis === 2 || rawVis === 3 ? rawVis : 1

    // 调用API创建文章，传入父节点ID与前节点ID
    const article = await articleApi.createArticle({
      knowledge_base_id: knowledgeBaseId.value,
      parent_id: parentId, // 父节点ID，如果是子节点则传入父节点ID，顶级节点则为null
      title: title,
      content: null,
      summary: null,
      tag_ids: null,
      sort_order: null,
      after_article_id,
      node_type: nodeType,
      visibility
    })
    
    // 用返回的数据更新节点（需要递归查找并更新，支持嵌套结构）
    const updateNodeInTree = (tree: any[], targetId: string, newNode: any): boolean => {
      for (let i = 0; i < tree.length; i++) {
        if (String(tree[i].id) === targetId) {
          // 确保新节点没有 isTemp 标记
          const updatedNode = { ...newNode }
          delete updatedNode.isTemp
          // 保留原有的 children 结构（如果有的话，且新节点没有 children）
          if (tree[i].children !== undefined && updatedNode.children === undefined) {
            updatedNode.children = tree[i].children
          }
          // 如果新节点有 has_children，根据它设置 children
          if (updatedNode.originalData?.has_children === true && !updatedNode.children) {
            updatedNode.children = []
          }
          
          // 使用 Vue 的响应式方式替换节点，确保触发更新（支持嵌套）
          tree.splice(i, 1, updatedNode)
          
          // 强制更新树组件（支持嵌套结构）
          nextTick(() => {
            if (treeRef.value) {
              const treeNode = treeRef.value.getNode(targetId)
              if (treeNode && treeNode.data) {
                // 确保树节点数据也更新，移除 isTemp 标记
                delete treeNode.data.isTemp
                // 更新节点数据
                Object.assign(treeNode.data, updatedNode)
                // 强制触发树组件更新（支持嵌套）
                if (typeof treeRef.value.updateKeyChildren === 'function') {
                  treeRef.value.updateKeyChildren(targetId, updatedNode)
                }
              }
            }
          })
          
          return true
        }
        // 递归查找嵌套的子节点（支持多级嵌套）
        if (tree[i].children && tree[i].children.length > 0) {
          if (updateNodeInTree(tree[i].children, targetId, newNode)) {
            return true
          }
        }
      }
      return false
    }
    
    const newNode = convertToTreeNode(article)
    // 确保新节点有 children 字段
    if (!newNode.children) {
      newNode.children = []
    }
    
    // 如果是顶级节点（parent_id 为 null），直接在 treeData 中替换节点（保持接口/列表顺序，不按 sort_order 排序）
    if (parentId === null) {
      // 找到临时节点在 treeData 中的位置
      const tempIndex = treeData.value.findIndex((item: any) => String(item.id) === nodeId)
      
      if (tempIndex !== -1) {
        // 在临时节点的位置替换为新节点
        treeData.value.splice(tempIndex, 1, newNode)
      } else {
        // 如果找不到临时节点，直接添加到末尾
        treeData.value.push(newNode)
      }
      
      // 更新选中的文章
      selectedArticle.value = article
      
      // 设置新节点为当前选中节点
      await nextTick()
      if (treeRef.value) {
        try {
          treeRef.value.setCurrentKey(newNode.id)
          scrollToTreeNode(newNode.id)
        } catch (error) {
          console.error('设置树节点选中状态失败:', error)
        }
      }
      
      // 同步更新 URL 参数
      router.replace({
        path: route.path,
        query: {
          ...route.query,
          articleId: newNode.id.toString()
        }
      })
    } else {
      // 非顶级节点，使用树组件的内置方法来替换节点
      if (treeRef.value) {
        const tree = treeRef.value
        const tempNode = tree.getNode(nodeId)
        
        if (tempNode) {
          const parentNode = tempNode.parent
          const parentData = parentNode?.data
          
          // 获取临时节点在兄弟节点中的位置
          let siblingIndex = -1
          let siblings: any[] = []
          
          if (parentData && parentData.children) {
            siblings = parentData.children
          }
          
          // 找到临时节点的位置
          siblingIndex = siblings.findIndex((s: any) => String(s.id) === nodeId)
          
          // 获取前一个兄弟节点（用于 insertAfter）
          const prevSibling = siblingIndex > 0 ? siblings[siblingIndex - 1] : null
          // 获取后一个兄弟节点（用于 insertBefore）
          const nextSibling = siblingIndex < siblings.length - 1 ? siblings[siblingIndex + 1] : null
          
          // 移除临时节点
          if (typeof tree.remove === 'function') {
            tree.remove(nodeId)
          }
          
          // 在原位置插入新节点
          nextTick(() => {
            if (prevSibling && typeof tree.insertAfter === 'function') {
              // 在前一个兄弟节点后插入
              tree.insertAfter(newNode, prevSibling.id)
            } else if (nextSibling && typeof tree.insertBefore === 'function') {
              // 在后一个兄弟节点前插入
              tree.insertBefore(newNode, nextSibling.id)
            } else if (parentData && typeof tree.append === 'function') {
              // 作为父节点的子节点追加
              tree.append(newNode, parentData.id)
            }
            
            // 确保父节点保持展开状态
            if (parentData) {
              const newParentNode = tree.getNode(parentData.id)
              if (newParentNode && !newParentNode.expanded) {
                newParentNode.expanded = true
              }
            }
            
            // 设置新节点为当前选中节点
            nextTick(() => {
              if (typeof tree.setCurrentKey === 'function') {
                tree.setCurrentKey(newNode.id)
              } else if (typeof tree.setCurrentNode === 'function') {
                const insertedNode = tree.getNode(newNode.id)
                if (insertedNode) {
                  tree.setCurrentNode(insertedNode)
                }
              }
              // 同时更新选中的文章
              selectedArticle.value = newNode.originalData || newNode
              
              // 同步更新 URL 参数
              router.replace({
                path: route.path,
                query: {
                  ...route.query,
                  articleId: newNode.id.toString()
                }
              })
            })
          })
        } else {
          // 如果树组件中找不到节点，回退到直接更新数据
          updateNodeInTree(treeData.value, nodeId, newNode)
          selectedArticle.value = article
          await nextTick()
          if (treeRef.value) {
            try {
              treeRef.value.setCurrentKey(newNode.id)
              scrollToTreeNode(newNode.id)
            } catch (error) {
              console.error('设置树节点选中状态失败:', error)
            }
          }
          router.replace({
            path: route.path,
            query: {
              ...route.query,
              articleId: newNode.id.toString()
            }
          })
        }
      } else {
        // 如果树组件不可用，直接更新数据
        updateNodeInTree(treeData.value, nodeId, newNode)
        selectedArticle.value = article
        await nextTick()
        router.replace({
          path: route.path,
          query: {
            ...route.query,
            articleId: newNode.id.toString()
          }
        })
      }
    }
    
    // 清理临时输入框引用
    delete tempInputRefs.value[nodeId]
  } catch (error) {
    console.error('创建文章失败:', error)
    // 创建失败，移除临时节点
    removeTempNode(nodeId)
  } finally {
    creating.value = false
    // 移除保存标记
    savingNodeIds.value.delete(nodeId)
  }
}

// 点击保存按钮
const handleClickSave = (node: any) => {
  isClickingButton.value = true
  setTimeout(() => {
    saveTempNode(node)
    isClickingButton.value = false
  }, 250)
}

/** 临时节点整行 focusout：避免 input 失焦时误触发保存（点选类型/可见性下拉时节点会消失） */
const handleTempNodeFocusOut = (e: FocusEvent, node: any) => {
  if (isClickingButton.value || isPressingEnter.value) return
  const root = e.currentTarget as HTMLElement | null
  setTimeout(() => {
    if (isClickingButton.value || isPressingEnter.value) return
    const active = document.activeElement as HTMLElement | null
    if (active && root?.contains(active)) return
    if (isTempNodeFocusInOpentinyOverlay(active)) return
    saveTempNode(node)
  }, 240)
}

// 保存临时节点（Enter 键）
const handleSaveTempNode = (node: any) => {
  isPressingEnter.value = true
  saveTempNode(node)
  // 延迟重置标志，确保 blur 事件不会触发
  setTimeout(() => {
    isPressingEnter.value = false
  }, 300)
}

// 取消临时节点
const handleCancelTempNode = (node: any) => {
  if (!node || !node.isTemp) return
  removeTempNode(node.id)
}

// 移除临时节点
const removeTempNode = (tempId: string) => {
  const nodeId = String(tempId)
  
  // 首先尝试使用 TinyTree 的 remove 方法移除节点
  if (treeRef.value && typeof treeRef.value.remove === 'function') {
    try {
      treeRef.value.remove(nodeId)
    } catch (error) {
      console.warn('使用树组件 remove 方法失败，使用备用方法:', error)
    }
  }
  
  // 递归查找并删除节点（从 treeData 中移除）
  const removeFromTree = (tree: any[], targetId: string): boolean => {
    for (let i = 0; i < tree.length; i++) {
      if (String(tree[i].id) === targetId) {
        tree.splice(i, 1)
        return true
      }
      if (tree[i].children && tree[i].children.length > 0) {
        if (removeFromTree(tree[i].children, targetId)) {
          return true
        }
      }
    }
    return false
  }
  
  // 从 treeData 中移除节点
  removeFromTree(treeData.value, nodeId)
  
  // 强制更新树组件
  nextTick(() => {
    if (treeRef.value) {
      // 尝试获取节点，如果还存在则强制移除
      try {
        const node = treeRef.value.getNode(nodeId)
        if (node) {
          // 如果节点还存在，尝试从父节点中移除
          const parent = node.parent
          if (parent && parent.data && parent.data.children) {
            const index = parent.data.children.findIndex((child: any) => String(child.id) === nodeId)
            if (index !== -1) {
              parent.data.children.splice(index, 1)
            }
          }
        }
      } catch (error) {
        // 节点可能已经不存在，忽略错误
      }
    }
  })
  
  // 清理引用
  delete tempInputRefs.value[nodeId]
  // 清理保存标记
  savingNodeIds.value.delete(nodeId)
}

// 加载知识库信息
const loadKnowledgeBase = async () => {
  if (!knowledgeBaseId.value) return

  try {
    const kb = await knowledgeBaseApi.getKnowledgeBase(knowledgeBaseId.value)
    knowledgeBase.value = kb
  } catch (error) {
    console.error('加载知识库信息失败:', error)
  }
}

/** 侧栏标题：新窗口打开知识空间管理页（团队空间路径 + ?name=当前知识库名称，供列表搜索） */
const goToKnowledgeSpacePage = async () => {
  let tsId = knowledgeBase.value?.team_space_id
  let kbName = knowledgeBase.value?.name?.trim() || ''
  if (tsId == null && knowledgeBaseId.value) {
    try {
      const kb = await knowledgeBaseApi.getKnowledgeBase(knowledgeBaseId.value)
      tsId = kb.team_space_id
      if (!kbName) kbName = kb.name?.trim() || ''
    } catch {
      /* ignore */
    }
  }
  const query: Record<string, string> = {}
  if (kbName) query.name = kbName

  const path =
    tsId != null && !Number.isNaN(Number(tsId))
      ? `/knowledge/knowledge-spaces/${Number(tsId)}`
      : '/knowledge/knowledge-spaces'
  const r = router.resolve({ path, query })
  const href = r.href.startsWith('http') ? r.href : `${window.location.origin}${r.href}`
  window.open(href, '_blank', 'noopener,noreferrer')
}

/** 新窗口打开团队空间管理页，携带团队空间名称查询参数 */
const openTeamSpacePageInNewWindow = async () => {
  let teamName = knowledgeBase.value?.team_space_name?.trim() || ''
  if (!teamName && knowledgeBaseId.value) {
    try {
      const kb = await knowledgeBaseApi.getKnowledgeBase(knowledgeBaseId.value)
      teamName = kb.team_space_name?.trim() || ''
      if (!knowledgeBase.value) knowledgeBase.value = kb
      else if (teamName) knowledgeBase.value = { ...knowledgeBase.value, team_space_name: kb.team_space_name }
    } catch {
      /* ignore */
    }
  }
  const query: Record<string, string> = {}
  if (teamName) query.name = teamName
  const r = router.resolve({ path: '/knowledge/team-spaces', query })
  const href = r.href.startsWith('http') ? r.href : `${window.location.origin}${r.href}`
  window.open(href, '_blank', 'noopener,noreferrer')
}

// 点击文章标题进入编辑模式
const handleArticleTitleClick = () => {
  if (!selectedArticle.value) return
  if (!hasArticleMemberRole.value) return
  isEditingArticleTitle.value = true
  editingArticleTitle.value = selectedArticle.value.title || ''
  originalArticleTitle.value = selectedArticle.value.title || ''
  
  // 聚焦输入框
  nextTick(() => {
    if (articleTitleInputRef.value) {
      setTimeout(() => {
        if (articleTitleInputRef.value.focus) {
          articleTitleInputRef.value.focus()
        } else if (articleTitleInputRef.value.$el) {
          const input = articleTitleInputRef.value.$el.querySelector('input')
          if (input) {
            input.focus()
            input.select()
          }
        }
      }, 100)
    }
  })
}

// 保存文章标题
const handleSaveArticleTitle = async () => {
  if (!selectedArticle.value || savingArticleTitle.value) return
  
  const newTitle = editingArticleTitle.value.trim()
  if (!newTitle) {
    // 标题不能为空，恢复原值
    editingArticleTitle.value = originalArticleTitle.value
    isEditingArticleTitle.value = false
    return
  }
  
  if (newTitle === originalArticleTitle.value) {
    // 没有变化，直接退出编辑模式
    isEditingArticleTitle.value = false
    return
  }
  
  savingArticleTitle.value = true
  try {
    const updatedArticle = await articleApi.updateArticle(selectedArticle.value.id, {
      title: newTitle
    })
    
    // 更新选中的文章
    selectedArticle.value = updatedArticle
    originalArticleTitle.value = newTitle
    isEditingArticleTitle.value = false
    
    // 更新树中对应节点的标题
    const updateNodeInTree = (tree: any[], targetId: number | string): boolean => {
      for (let i = 0; i < tree.length; i++) {
        if (String(tree[i].id) === String(targetId)) {
          tree[i].label = newTitle
          if (tree[i].originalData) {
            tree[i].originalData.title = newTitle
          }
          return true
        }
        if (tree[i].children && tree[i].children.length > 0) {
          if (updateNodeInTree(tree[i].children, targetId)) {
            return true
          }
        }
      }
      return false
    }
    
    updateNodeInTree(treeData.value, selectedArticle.value.id)
    
    // 更新树组件显示
    await nextTick()
    if (treeRef.value) {
      treeRef.value.setCurrentKey(selectedArticle.value.id)
    }
    
    console.log(translate('article.updateSuccess'))
  } catch (error) {
    console.error('更新文章标题失败:', error)
    // 恢复原值
    editingArticleTitle.value = originalArticleTitle.value
    isEditingArticleTitle.value = false
  } finally {
    savingArticleTitle.value = false
  }
}

// 取消文章标题编辑
const handleCancelArticleTitleEdit = () => {
  editingArticleTitle.value = originalArticleTitle.value
  isEditingArticleTitle.value = false
}

// 初始化
// 监听编辑器引用变化，当编辑器准备好时生成目录
// 监听文章变化，更新操作状态
watch(selectedArticle, async (newArticle) => {
  if (newArticle) {
    // 重置状态
    isLiked.value = false
    isFavorited.value = false
    
    // 加载文章统计信息
    await loadArticleStats()
  } else {
    isLiked.value = false
    isFavorited.value = false
  }
}, { immediate: true })

// 监听评论弹窗关闭，重新加载统计信息
// 注意：comment-added 事件也会触发重新加载，这里只在弹窗关闭时加载（避免重复）
watch(commentDrawerVisible, async (newVal, oldVal) => {
  // 当弹窗从打开变为关闭时，重新加载统计信息
  if (oldVal && !newVal && selectedArticle.value) {
    await loadArticleStats()
  }
})

// 监听反馈弹窗关闭，重新加载统计信息
// 注意：feedback-added 事件也会触发重新加载，这里只在弹窗关闭时加载（避免重复）
watch(feedbackDrawerVisible, async (newVal, oldVal) => {
  // 当弹窗从打开变为关闭时，重新加载统计信息
  if (oldVal && !newVal && selectedArticle.value) {
    await loadArticleStats()
  }
})

// 历史版本回滚后刷新文章
const handleVersionRestored = async () => {
  if (selectedArticle.value?.id) {
    await loadArticle(selectedArticle.value.id)
    await loadArticleStats()
  }
}

// 添加视频双击事件监听 - 双击全屏/退出全屏视频
const handleVideoDoubleClick = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  let video: HTMLVideoElement | null = null
  
  if (target.tagName === 'VIDEO') {
    video = target as HTMLVideoElement
  } else {
    const videoElement = target.closest('video')
    if (videoElement) {
      video = videoElement as HTMLVideoElement
    }
  }
  
  if (video) {
    console.log('双击视频事件:', {
      event,
      video,
      src: video.src || video.getAttribute('src'),
      currentTime: video.currentTime,
      duration: video.duration,
      paused: video.paused,
      volume: video.volume,
      clientX: event.clientX,
      clientY: event.clientY,
      target: event.target,
      timestamp: new Date().toISOString(),
    })

    // 检查当前是否处于全屏状态
    const isFullscreen = !!(
      document.fullscreenElement ||
      (document as any).webkitFullscreenElement ||
      (document as any).mozFullScreenElement ||
      (document as any).msFullscreenElement
    )

    if (isFullscreen) {
      // 如果已全屏，则退出全屏
      if (document.exitFullscreen) {
        document.exitFullscreen().catch((err) => {
          console.error('退出全屏失败:', err)
        })
      } else if ((document as any).webkitExitFullscreen) {
        // Safari 浏览器
        ;(document as any).webkitExitFullscreen()
      } else if ((document as any).mozCancelFullScreen) {
        // Firefox 浏览器
        ;(document as any).mozCancelFullScreen()
      } else if ((document as any).msExitFullscreen) {
        // IE/Edge 浏览器
        ;(document as any).msExitFullscreen()
      } else {
        console.warn('浏览器不支持退出全屏API')
      }
    } else {
      // 如果未全屏，则进入全屏
      if (video.requestFullscreen) {
        video.requestFullscreen().catch((err) => {
          console.error('全屏失败:', err)
        })
      } else if ((video as any).webkitRequestFullscreen) {
        // Safari 浏览器
        ;(video as any).webkitRequestFullscreen()
      } else if ((video as any).mozRequestFullScreen) {
        // Firefox 浏览器
        ;(video as any).mozRequestFullScreen()
      } else if ((video as any).msRequestFullscreen) {
        // IE/Edge 浏览器
        ;(video as any).msRequestFullscreen()
      } else {
        console.warn('浏览器不支持全屏API')
      }
    }
  }
}

// 使用事件委托监听编辑器内的视频双击事件
const setupVideoDoubleClickListeners = () => {
  const host = getArticleContentHost()
  if (!host) return
  
  // 获取编辑器元素
  const editorElement = (host as any).$el || host
  if (!editorElement) return
  
  // 查找编辑器内容区域
  const quillEditor = editorElement.querySelector('.ql-editor') || editorElement
  
  // 监听现有视频的双击事件
  const attachVideoListeners = () => {
    const videos = quillEditor.querySelectorAll('video')
    videos.forEach((video: HTMLVideoElement) => {
      // 移除之前的监听器（如果存在）
      video.removeEventListener('dblclick', handleVideoDoubleClick)
      // 添加新的双击监听器
      video.addEventListener('dblclick', handleVideoDoubleClick)
    })
  }

  // 初始添加监听器
  setTimeout(() => {
    attachVideoListeners()
  }, 500)

  // 使用 MutationObserver 监听新插入的视频
  const observer = new MutationObserver((mutations) => {
    let hasNewVideo = false
    mutations.forEach((mutation) => {
      mutation.addedNodes.forEach((node) => {
        if (node.nodeType === 1) {
          const element = node as HTMLElement
          if (element.tagName === 'VIDEO' || element.querySelector('video')) {
            hasNewVideo = true
          }
        }
      })
    })
    if (hasNewVideo) {
      setTimeout(() => {
        attachVideoListeners()
      }, 100)
    }
  })

  // 开始观察编辑器内容变化
  observer.observe(quillEditor, {
    childList: true,
    subtree: true,
  })
}

// 添加图片双击事件监听 - 双击图片使用 TinyImage 预览
const handleImageDoubleClick = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  
  // 打印双击事件信息
  console.log('双击事件触发:', {
    event: event,
    target: target,
    targetTagName: target.tagName,
    targetClassName: target.className,
    targetId: target.id,
    clientX: event.clientX,
    clientY: event.clientY,
    timestamp: new Date().toISOString(),
  })
  
  // 查找 img 元素
  let img: HTMLImageElement | null = null
  
  if (target.tagName === 'IMG') {
    img = target as HTMLImageElement
  } else {
    const imgElement = target.closest('img')
    if (imgElement) {
      img = imgElement as HTMLImageElement
    }
  }
  
  if (img && img.src) {
    console.log('双击图片事件 (img):', {
      event: event,
      img,
      src: img.src,
      alt: img.alt,
      clientX: event.clientX,
      clientY: event.clientY,
      target: event.target,
      timestamp: new Date().toISOString(),
    })

    // 收集编辑器内所有图片的 src
    const host = getArticleContentHost()
    if (!host) return
    
    const editorElement = (host as any).$el || host
    if (!editorElement) return
    
    const quillEditor = editorElement.querySelector('.ql-editor') || editorElement
    const allImages = quillEditor.querySelectorAll('img')
    const imageSrcList: string[] = []
    
    allImages.forEach((image: HTMLImageElement) => {
      const src = image.src || image.getAttribute('src')
      if (src) {
        imageSrcList.push(src)
      }
    })
    
    if (imageSrcList.length > 0) {
      // 找到当前点击的图片在列表中的索引
      const currentSrc = img.src || img.getAttribute('src')
      const currentIndex = imageSrcList.findIndex(src => src === currentSrc)
      
      // 确保索引在有效范围内
      const validIndex = currentIndex >= 0 && currentIndex < imageSrcList.length ? currentIndex : 0
      
      imagePreviewList.value = imageSrcList
      imagePreviewIndex.value = validIndex
      imagePreviewVisible.value = true
      
      console.log('打开图片预览:', {
        imageList: imagePreviewList,
        currentIndex: validIndex,
        currentSrc: currentSrc
      })
    }
  }
}

// 处理图片切换
const handleImageSwitch = (index: number) => {
  if (index >= 0 && index < imagePreviewList.value.length) {
    imagePreviewIndex.value = index
    console.log('切换到图片索引:', index, 'URL:', imagePreviewList.value[index])
  }
}


// 使用事件委托监听编辑器内的图片双击事件
const setupImageDoubleClickListeners = () => {
  // 如果是编辑状态，不添加监听
  if (isEditing.value) {
    console.log('编辑状态下，不添加图片双击监听')
    return
  }
  
  const host = getArticleContentHost()
  if (!host) return
  
  // 获取编辑器元素
  const editorElement = (host as any).$el || host
  if (!editorElement) return
  console.log('editorElement', editorElement) 
  // 查找编辑器内容区域
  const quillEditor = editorElement.querySelector('.ql-editor') || editorElement
  console.log('quillEditor', quillEditor)
  
  // 监听现有图片的双击事件
  const attachImageListeners = () => {
    // 如果是编辑状态，不添加监听
    if (isEditing.value) {
      console.log('编辑状态下，不添加图片双击监听')
      return
    }
    
    const images = quillEditor.querySelectorAll('img')
    console.log('找到图片数量:', images.length)
    images.forEach((img: HTMLImageElement) => {
      // 移除之前的监听器（如果存在）
      img.removeEventListener('click', handleImageDoubleClick)
      // 添加新的双击监听器
      img.addEventListener('click', handleImageDoubleClick)
      console.log('为图片添加双击监听器:', img.src)
    })
  }

  // 初始添加监听器
  setTimeout(() => {
    attachImageListeners()
  }, 500)

  // 使用 MutationObserver 监听新插入的图片
  const observer = new MutationObserver((mutations) => {
    let hasNewImage = false
    mutations.forEach((mutation) => {
      mutation.addedNodes.forEach((node) => {
        if (node.nodeType === 1) {
          const element = node as HTMLElement
          // 检查是否是 img 标签
          if (element.tagName === 'IMG' || element.querySelector('img')) {
            hasNewImage = true
          }
        }
      })
    })
    if (hasNewImage) {
      setTimeout(() => {
        attachImageListeners()
      }, 100)
    }
  })

  // 开始观察编辑器内容变化
  observer.observe(quillEditor, {
    childList: true,
    subtree: true,
  })
}

// 处理编辑器内文件链接点击事件
const handleFileLinkClick = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  
  // 检查是否是符合条件的链接
  if (target.tagName === 'A' && target.classList.contains('ql-normal-link')) {
    const linkText = target.textContent || ''
    if (linkText.includes('点击下载或预览')) {
      event.preventDefault()
      event.stopPropagation()
      
      // 获取链接的 href
      const fileUrl = (target as HTMLAnchorElement).href
      if (!fileUrl) return
      
      // 从链接的父元素中查找文件名（在 strong 标签中）
      const parentDiv = target.closest('div')
      if (!parentDiv) return
      
      const fileNameElement = parentDiv.querySelector('strong')
      const fileName = fileNameElement?.textContent?.trim() || '文件'
      
      // 规范化URL用于比对（去除协议和域名，只保留路径）
      const normalizeUrl = (url: string): string => {
        try {
          const urlObj = new URL(url)
          return urlObj.pathname + urlObj.search
        } catch {
          // 如果URL解析失败，尝试直接使用路径部分
          return url.replace(/^https?:\/\/[^\/]+/, '')
        }
      }
      
      const normalizedFileUrl = normalizeUrl(fileUrl)
      
      // 在附件列表中查找匹配的附件
      const matchedAttachment = attachments.value.find(att => {
        if (!att.file_url) return false
        const normalizedAttUrl = normalizeUrl(att.file_url)
        // 比对规范化后的URL或完整URL
        return normalizedAttUrl === normalizedFileUrl || att.file_url === fileUrl
      })
      
      if (matchedAttachment) {
        if (openOfficeOnlinePreview(matchedAttachment.file_url, matchedAttachment.filename, matchedAttachment.file_type)) {
          return
        }
        handleSelectAttachmentForPreview(matchedAttachment)
        attachmentPreviewVisible.value = true
      } else {
        if (openOfficeOnlinePreview(fileUrl, fileName)) {
          return
        }
        // 如果没找到，创建临时的 Attachment 对象用于预览
        const fileExtension = fileName.split('.').pop()?.toLowerCase() || ''
        let fileType = ''
        if (['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg'].includes(fileExtension)) {
          fileType = 'image'
        } else if (['mp4', 'webm', 'ogg', 'mov', 'avi', 'wmv', 'flv', 'mkv'].includes(fileExtension)) {
          fileType = 'video'
        } else if (fileExtension === 'pdf') {
          fileType = 'pdf'
        } else if (['pptx', 'ppt'].includes(fileExtension)) {
          fileType = 'pptx'
        } else if (['xlsx', 'xls'].includes(fileExtension)) {
          fileType = 'xlsx'
        } else if (['docx', 'doc'].includes(fileExtension)) {
          fileType = 'docx'
        } else {
          fileType = 'other'
        }
        
        const tempAttachment: Attachment = {
          id: Date.now(), // 使用时间戳作为临时 ID
          article_id: selectedArticle.value?.id || 0,
          filename: fileName,
          file_url: fileUrl,
          file_type: fileType,
          file_size: null,
          created_at: null,
          created_by_id: null,
          created_by_name: null
        }
        
        // 打开预览弹窗
        attachmentPreviewVisible.value = true
        previewAttachment.value = tempAttachment
      }
    }
  }
}

// 设置文件链接点击监听器
const setupFileLinkClickListeners = () => {
  // 如果是编辑状态，不添加监听
  if (isEditing.value) {
    return
  }
  
  const host = getArticleContentHost()
  if (!host) return
  
  // 获取编辑器元素
  const editorElement = (host as any).$el || host
  if (!editorElement) return
  
  // 查找编辑器内容区域
  const quillEditor = editorElement.querySelector('.ql-editor') || editorElement
  
  // 使用事件委托监听链接点击
  const attachLinkListeners = () => {
    // 如果是编辑状态，不添加监听
    if (isEditing.value) {
      return
    }
    
    // 移除之前的监听器（如果存在）
    quillEditor.removeEventListener('click', handleFileLinkClick)
    // 添加新的点击监听器
    quillEditor.addEventListener('click', handleFileLinkClick)
  }
  
  // 初始添加监听器
  setTimeout(() => {
    attachLinkListeners()
  }, 500)
  
  // 使用 MutationObserver 监听新插入的内容
  const observer = new MutationObserver(() => {
    setTimeout(() => {
      attachLinkListeners()
    }, 100)
  })
  
  // 开始观察编辑器内容变化
  observer.observe(quillEditor, {
    childList: true,
    subtree: true,
  })
}

watch([editorRef, previewRef, selectedArticle, isEditing], () => {
  if (!isEditing.value && selectedArticle.value && getArticleContentHost()) {
    // 当预览正文区域挂载/更新时，重新设置附件链接等监听
    nextTick(() => {
      setupFileLinkClickListeners()
    })
    // 延迟生成目录，确保编辑器已初始化
    setTimeout(() => {
      generateTableOfContents()
    }, 1000)
  }
}, { deep: true })

// 监听编辑器内容变化，自动保存到本地缓存
let draftSaveTimer: ReturnType<typeof setTimeout> | null = null
watch([editorContent, isEditing, selectedArticle], () => {
  if (draftSaveTimer) {
    clearTimeout(draftSaveTimer)
  }
  
  if (isEditing.value && selectedArticle.value && editorContent.value !== originalContent.value) {
    // 使用防抖，避免频繁写入 localStorage
    draftSaveTimer = setTimeout(() => {
      saveDraftToCache()
      draftSaveTimer = null
    }, 1000) // 1秒后保存
  }
}, { deep: true })

onMounted(async () => {
  updateArticlePageLayout()
  window.addEventListener('resize', updateArticlePageLayout)

  defaultExpandedKeys.value = route.query.articleId ? [Number(route.query.articleId)] : []
  // 从本地存储恢复侧边栏宽度
  const savedWidth = localStorage.getItem('articleSidebarWidth')
  if (savedWidth) {
    const width = parseInt(savedWidth, 10)
    if (width >= MIN_SIDEBAR_WIDTH && width <= MAX_SIDEBAR_WIDTH) {
      sidebarWidth.value = width
    }
  }
  
  // 从本地存储恢复目录显示状态
  const savedTocVisible = localStorage.getItem('articleTocVisible')
  if (savedTocVisible !== null) {
    tocVisible.value = savedTocVisible === 'true'
  }
  
  // 从本地存储恢复附件显示状态
  const savedAttachmentsVisible = localStorage.getItem('articleAttachmentsVisible')
  if (savedAttachmentsVisible !== null) {
    attachmentsVisible.value = savedAttachmentsVisible === 'true'
  } else {
    attachmentsVisible.value = true // 默认显示
  }
  
  // 从本地存储恢复目录宽度
  const savedTocWidth = localStorage.getItem('articleTocWidth')
  if (savedTocWidth) {
    const width = parseInt(savedTocWidth, 10)
    if (width >= MIN_TOC_WIDTH && width <= MAX_TOC_WIDTH) {
      tocWidth.value = width
    }
  }

  // 加载角色权限（签读按钮、目录拖拽）
  const loadRolePermissions = async () => {
    try {
      const codes = await getCurrentRolePermissions()
      hasCreateReadTaskPermission.value = codes.includes('create_read_task')
      hasArticleCategoryMovePermission.value = codes.includes('article_category_move')
    } catch {
      hasCreateReadTaskPermission.value = false
      hasArticleCategoryMovePermission.value = false
    }
  }
  await loadRolePermissions()
  setTimeout(loadRolePermissions, 500)

  // 加载所有角色列表（用于签读对象选择）
  try {
    const res = await roleApi.getRoles({ page: 1, page_size: 100, status: 1 })
    allRoles.value = res.items || []
  } catch (e) {
    console.error('加载角色列表失败', e)
    allRoles.value = []
  }
  
  // 添加视频双击事件监听 - 双击全屏/退出全屏视频（当前通过编辑器配置已处理）
  const _handleVideoDoubleClick = (event: MouseEvent) => {
    const target = event.target as HTMLElement
    let video: HTMLVideoElement | null = null
    
    if (target.tagName === 'VIDEO') {
      video = target as HTMLVideoElement
    } else {
      const videoElement = target.closest('video')
      if (videoElement) {
        video = videoElement as HTMLVideoElement
      }
    }
    
    if (video) {
      console.log('双击视频事件:', {
        event,
        video,
        src: video.src || video.getAttribute('src'),
        currentTime: video.currentTime,
        duration: video.duration,
        paused: video.paused,
        volume: video.volume,
        clientX: event.clientX,
        clientY: event.clientY,
        target: event.target,
        timestamp: new Date().toISOString(),
      })

      // 检查当前是否处于全屏状态
      const isFullscreen = !!(
        document.fullscreenElement ||
        (document as any).webkitFullscreenElement ||
        (document as any).mozFullScreenElement ||
        (document as any).msFullscreenElement
      )

      if (isFullscreen) {
        // 如果已全屏，则退出全屏
        if (document.exitFullscreen) {
          document.exitFullscreen().catch((err) => {
            console.error('退出全屏失败:', err)
          })
        } else if ((document as any).webkitExitFullscreen) {
          // Safari 浏览器
          ;(document as any).webkitExitFullscreen()
        } else if ((document as any).mozCancelFullScreen) {
          // Firefox 浏览器
          ;(document as any).mozCancelFullScreen()
        } else if ((document as any).msExitFullscreen) {
          // IE/Edge 浏览器
          ;(document as any).msExitFullscreen()
        } else {
          console.warn('浏览器不支持退出全屏API')
        }
      } else {
        // 如果未全屏，则进入全屏
        if (video.requestFullscreen) {
          video.requestFullscreen().catch((err) => {
            console.error('全屏失败:', err)
          })
        } else if ((video as any).webkitRequestFullscreen) {
          // Safari 浏览器
          ;(video as any).webkitRequestFullscreen()
        } else if ((video as any).mozRequestFullScreen) {
          // Firefox 浏览器
          ;(video as any).mozRequestFullScreen()
        } else if ((video as any).msRequestFullscreen) {
          // IE/Edge 浏览器
          ;(video as any).msRequestFullscreen()
        } else {
          console.warn('浏览器不支持全屏API')
        }
      }
    }
  }

  // 先正常加载知识库和文章列表
  await loadKnowledgeBase()
  await loadTopLevelArticles()
  
  // 获取当前地址栏中的文章ID
  const currentArticleId = route.query.articleId ? Number(route.query.articleId) : null
  
  // 如果有文章ID，先加载对应的文章
  if (currentArticleId && !isNaN(currentArticleId)) {
    await loadArticle(currentArticleId)
    
    // 在树中高亮选中的节点，并滚动到该节点
    await nextTick()
    if (treeRef.value) {
      try {
        treeRef.value.setCurrentKey(currentArticleId)
        scrollToTreeNode(currentArticleId)
      } catch (error) {
        console.error('设置树节点选中状态失败:', error)
      }
    }
  }
  
  // 加载完成后，检查是否有未保存的草稿（根据当前文章ID）
  if (currentArticleId) {
    const draft = getDraftFromCache(currentArticleId)
    
    // 如果有缓存，弹窗提示
    if (draft) {
      Modal.confirm({
        title: translate('article.restoreDraftTitle'),
        message: translate('article.restoreDraftMessage'),
        status: 'warning'
      }).then(async (result: string) => {
        if (result !== 'confirm') {
          // 用户取消，清除当前文章的缓存
          clearDraftCache(currentArticleId)
          return
        }
        
        // 用户选择恢复草稿
        // 进入编辑模式并恢复内容
        await nextTick()
        isEditing.value = true
        editorContent.value = draft.content
        originalContent.value = selectedArticle.value?.content || ''
        await loadKbTagsForEdit()
        syncEditFlagsFromArticle()

        // 启用编辑器
        await nextTick()
        if (editorRef.value && editorRef.value.quill) {
          editorRef.value.quill.enable(true)
        }
      }).catch(() => {
        // 用户选择不恢复，清除当前文章的缓存
        clearDraftCache(currentArticleId)
      })
    }
  }
  
  // 设置视频和图片双击事件监听器
  await nextTick()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', updateArticlePageLayout)
  document.body.style.overflow = ''
  clearSignReadTimer()
  teardownTocScrollSpy()
})

// 监听路由查询参数变化
// 加载文章并高亮树节点
const loadArticleAndHighlight = async (articleId: number) => {
  await loadArticle(articleId)
  await nextTick()
  if (treeRef.value) {
    try {
      treeRef.value.setCurrentKey(articleId)
      scrollToTreeNode(articleId)
    } catch (error) {
      console.error('设置树节点选中状态失败:', error)
    }
  }
}

watch(() => route.query.articleId, async (newArticleId, oldArticleId) => {
  if (!newArticleId) {
    articleLoadError.value = null
    articleAdmins.value = []
    showApplyEditForm.value = false
    applyEditRemark.value = ''
    applyEditRole.value = DEFAULT_APPLY_ROLE
    applyReviewerIds.value = []
    return
  }
  if (newArticleId && !isNaN(Number(newArticleId))) {
    const articleId = Number(newArticleId)
    
    // 如果当前选中的文章ID与URL参数相同，不需要重新加载
    if (selectedArticle.value && selectedArticle.value.id === articleId) {
      return
    }
    
    // 先正常加载文章
    await loadArticleAndHighlight(articleId)
    
    // 加载完成后，检查是否有缓存
    if (oldArticleId !== newArticleId) {
      const draft = getDraftFromCache(articleId)
      
      // 如果有缓存且不在编辑模式，弹窗提示
      if (draft && !isEditing.value) {
        Modal.confirm({
          title: translate('article.restoreDraftTitle'),
          message: translate('article.restoreDraftMessage'),
          status: 'warning'
        }).then(async (result: string) => {
          if (result !== 'confirm') {
            // 用户取消，清除当前文章的缓存
            clearDraftCache(articleId)
            return
          }
          
          // 用户选择恢复草稿
          // 进入编辑模式并恢复内容
          await nextTick()
          isEditing.value = true
          editorContent.value = draft.content
          originalContent.value = selectedArticle.value?.content || ''
          await loadKbTagsForEdit()
          syncEditFlagsFromArticle()

          // 启用编辑器
          await nextTick()
          if (editorRef.value && editorRef.value.quill) {
            editorRef.value.quill.enable(true)
          }
        }).catch(() => {
          // 用户选择不恢复，清除当前文章的缓存
          clearDraftCache(articleId)
        })
      }
    }
  }
})
</script>

<style scoped lang="less">
.article-management-page {
  height: calc(100vh - 64px);
  background-color: #f5f7fa;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.main-layout {
  display: flex;
  flex: 1;
  height: 0; // 配合 flex: 1 使用，确保不会超出父容器
  overflow: hidden;
}

.tree-sidebar {
  width: 300px;
  background: #fff;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
  flex-shrink: 0;
}

.sidebar-resizer {
  width: 0px;
  background: transparent;
  cursor: col-resize;
  position: relative;
  flex-shrink: 0;
  z-index: 10;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  
  &:hover {
    background-color: #b2b0b8;
    
    .resizer-icon {
      opacity: 1;
    }
  }
  
  &.resizing {
    background-color: #b2b0b8;
    
    .resizer-icon {
      opacity: 1;
    }
  }
  
  &::before {
    content: '';
    position: absolute;
    left: -2px;
    top: 0;
    width: 8px;
    height: 100%;
    cursor: col-resize;
  }
  
  .resizer-icon {
    position: absolute;
    right: -8px;
    top: 50%;
    transform: translateY(-50%);
    width: 16px;
    height: 16px;
    opacity: 0.6;
    transition: opacity 0.2s;
    pointer-events: none;
    color: #606266;
    display: flex;
    align-items: center;
    justify-content: center;
    
    svg {
      width: 100%;
      height: 100%;
    }
  }
}

.sidebar-header {
  padding: 16px 16px 4px 16px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  position: relative;
  gap: 12px;

  .sidebar-role-badge {
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
    white-space: nowrap;
    flex-shrink: 0;
    display: inline-block;
    border: 1px solid transparent;
    line-height: 1.2;

    &.role-readonly {
      background-color: #f5f5f5;
      color: #666666;
      border-color: #d9d9d9;
    }

    &.role-editor {
      background-color: #e6f4ff;
      color: #1677ff;
      border-color: #69b1ff;
    }

    &.role-admin {
      background-color: #fff7e6;
      color: #fa8c16;
      border-color: #ffc53d;
    }
  }
}

.sidebar-header-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sidebar-header-stack {
  width: 100%;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sidebar-cards-slide-enter-active,
.sidebar-cards-slide-leave-active {
  transition:
    max-height 0.3s cubic-bezier(0.4, 0, 0.2, 1),
    opacity 0.22s ease,
    transform 0.26s ease;
  overflow: hidden;
}

.sidebar-cards-slide-enter-from,
.sidebar-cards-slide-leave-to {
  max-height: 0;
  opacity: 0;
  transform: translateY(-4px);
}

.sidebar-cards-slide-enter-to,
.sidebar-cards-slide-leave-from {
  max-height: 1200px;
  opacity: 1;
  transform: translateY(0);
}

.sidebar-cards-flat-trigger {
  width: 100%;
  margin: 0;
  padding: 2px 0 0;
  border: none;
  border-radius: 6px;
  background: transparent;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0;
  color: rgba(124, 58, 237, 0.55);
  outline: none;
  -webkit-tap-highlight-color: transparent;
  transition:
    color 0.2s ease,
    background 0.2s ease;

  &:hover {
    color: var(--primary-color, #8b5cf6);
    background: rgba(139, 92, 246, 0.06);
  }

  &:focus {
    outline: none;
  }

  &:focus-visible {
    outline: none;
    box-shadow: none;
    background: rgba(139, 92, 246, 0.08);
  }
}

.sidebar-cards-flat-trigger-line {
  display: block;
  width: 100%;
  height: 1px;
  margin-bottom: 4px;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(139, 92, 246, 0.22) 20%,
    rgba(139, 92, 246, 0.28) 50%,
    rgba(139, 92, 246, 0.22) 80%,
    transparent 100%
  );
}

.sidebar-cards-flat-trigger-chevron {
  width: 22px;
  height: 11px;
  flex-shrink: 0;
  display: block;
  transform: rotate(0deg);
  transition: transform 0.28s cubic-bezier(0.4, 0, 0.2, 1);
}

.sidebar-cards-flat-trigger[aria-expanded='true'] .sidebar-cards-flat-trigger-chevron {
  transform: rotate(180deg);
}

.sidebar-team-space {
  margin-top: 2px;
  padding: 0;
  border-radius: 10px;
  cursor: pointer;
  user-select: none;
  outline: none;
  transition:
    background 0.2s ease,
    box-shadow 0.2s ease,
    border-color 0.2s ease;
  border: 1px solid rgba(139, 92, 246, 0.18);
  background: linear-gradient(
    135deg,
    rgba(139, 92, 246, 0.07) 0%,
    rgba(124, 58, 237, 0.05) 100%
  );
  box-shadow: 0 1px 2px rgba(139, 92, 246, 0.06);

  &:hover {
    border-color: rgba(139, 92, 246, 0.35);
    background: linear-gradient(
      135deg,
      rgba(139, 92, 246, 0.11) 0%,
      rgba(124, 58, 237, 0.08) 100%
    );
    box-shadow: 0 2px 8px rgba(139, 92, 246, 0.12);

    .sidebar-team-space-open svg {
      color: var(--primary-color, #8b5cf6);
      opacity: 1;
    }
  }

  &:focus {
    outline: none;
  }

  &:focus-visible {
    outline: none;
    box-shadow: none;
    background: linear-gradient(
      135deg,
      rgba(139, 92, 246, 0.12) 0%,
      rgba(124, 58, 237, 0.09) 100%
    );
  }
}

.sidebar-team-space-inner {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  min-height: 44px;
  box-sizing: border-box;
}

.sidebar-team-space-icon-wrap {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(139, 92, 246, 0.12);
  color: var(--primary-color, #8b5cf6);
}

.sidebar-team-space-icon {
  width: 18px;
  height: 18px;
}

.sidebar-team-space-text {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
  text-align: left;
}

.sidebar-team-space-label {
  display: block;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.02em;
  color: #a78bfa;
  line-height: 1.2;
}

// 与知识空间/团队空间卡片 card-header 一致：标题与徽章同一行左右对齐
.sidebar-team-space-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  min-width: 0;
  width: 100%;

  .sidebar-role-badge {
    align-self: center;
  }
}

.sidebar-team-space-name {
  display: block;
  flex: 1;
  min-width: 0;
  font-size: 13px;
  font-weight: 600;
  color: #5b21b6;
  line-height: 1.35;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.sidebar-team-space-open {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.65;

  svg {
    width: 15px;
    height: 15px;
    color: #7c3aed;
    transition: color 0.2s ease;
  }
}

.sidebar-title {
  margin: 0;
  flex: 1;
  min-width: 0;

  &--card {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    border-radius: 10px;
    border: 1px solid rgba(139, 92, 246, 0.14);
    background: linear-gradient(145deg, #ffffff 0%, rgba(250, 245, 255, 0.92) 100%);
    box-shadow: 0 1px 3px rgba(91, 33, 182, 0.06);
    transition:
      border-color 0.2s ease,
      box-shadow 0.2s ease,
      background 0.2s ease;

    // 与 .sidebar-team-space-icon-wrap 一致：浅紫底 + 主色描边图标（非渐变实心底）
    .sidebar-title-icon-wrap {
      flex-shrink: 0;
      width: 32px;
      height: 32px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: rgba(139, 92, 246, 0.12);
      color: var(--primary-color, #8b5cf6);
    }

    .book-icon {
      width: 18px;
      height: 18px;
      flex-shrink: 0;
    }

    .sidebar-new-article-glyph {
      width: 18px;
      height: 18px;
      flex-shrink: 0;
      display: block;
    }

    .sidebar-title-body {
      flex: 1;
      min-width: 0;
      display: flex;
      flex-direction: column;
      gap: 4px;
      text-align: left;
    }

    .sidebar-title-eyebrow {
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: #a78bfa;
      line-height: 1.2;
    }

    .sidebar-title-title-row {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 8px;
      min-width: 0;
      width: 100%;
    }

    // 与团队空间名称 .sidebar-team-space-name 一致：字号与主色
    .sidebar-title-name {
      flex: 1;
      min-width: 0;
      font-size: 13px;
      font-weight: 600;
      color: #5b21b6;
      line-height: 1.35;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      word-break: break-word;
    }

    .sidebar-title-title-row .sidebar-role-badge {
      margin-top: 1px;
      align-self: flex-start;
    }

    .sidebar-title-open {
      flex-shrink: 0;
      display: flex;
      align-items: center;
      opacity: 0.55;
      transition: opacity 0.2s ease;

      svg {
        width: 15px;
        height: 15px;
        color: #7c3aed;
      }
    }

    &.sidebar-title--clickable:hover {
      border-color: rgba(139, 92, 246, 0.32);
      box-shadow: 0 4px 14px rgba(124, 58, 237, 0.12);
      background: linear-gradient(145deg, #ffffff 0%, rgba(245, 243, 255, 0.98) 100%);

      .sidebar-title-name {
        color: #5b21b6;
      }

      .sidebar-title-open {
        opacity: 1;
      }
    }
  }

  &--clickable {
    cursor: pointer;
    user-select: none;
    outline: none;
    -webkit-tap-highlight-color: transparent;

    &:focus {
      outline: none;
    }

    &:focus-visible {
      outline: none;
      box-shadow: none;
      border-color: rgba(139, 92, 246, 0.35);
      background: linear-gradient(145deg, #ffffff 0%, rgba(245, 243, 255, 0.98) 100%);
    }
  }
}

// 与知识库卡片同一套 sidebar-title--card（图标区与团队空间 .sidebar-team-space-icon-wrap 一致）
.sidebar-new-article {
  width: 100%;
}

.sidebar-new-article-dropdown {
  display: block;
  width: 100%;

  :deep(.tiny-dropdown__trigger) {
    display: block;
    width: 100%;
    border: none;
    background: transparent;
    padding: 0;
    box-shadow: none;
  }

  :deep(.tiny-dropdown__suffix-inner) {
    display: none !important;
  }
}

.sidebar-new-article-row {
  cursor: pointer;
  outline: none;
  -webkit-tap-highlight-color: transparent;

  &:focus {
    outline: none;
  }

  &:focus-visible {
    outline: none;
    box-shadow: none;
  }
}

.article-new-dropdown-menu {
  min-width: 180px;
  margin-top: 4px;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.12);
  border: 1px solid #ebeef5;
}

.article-add-fab-menu-item {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
}

.article-add-fab-menu-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;

  &--top {
    background: linear-gradient(180deg, #a78bfa, #7c3aed);
  }

  &--bottom {
    background: linear-gradient(180deg, #c4b5fd, #8b5cf6);
  }
}

.tree-search {
  padding: 12px 20px;
  border-bottom: 1px solid #e4e7ed;
  background: #fff;

  .tree-search-input {
    width: 100%;

    :deep(.tiny-input__inner) {
      border-radius: 6px;
      border-color: #e4e7ed;
      font-size: 14px;

      &:focus {
        border-color: var(--primary-color, #8b5cf6);
      }
    }

    .search-icon {
      color: #999;
      width: 16px;
      height: 16px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      
      :deep(svg) {
        width: 16px;
        height: 16px;
      }
    }
  }
}

.tree-container {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
  font-size: 14px;
  
  :deep(.tiny-tree) {
    font-size: 14px;
    padding: 0px;
  }
  
  :deep(.tiny-tree-node) {
    font-size: 14px;
  }
  
  :deep(.tiny-tree-node__content) {
    font-size: 14px;
  }
}

.tree-node-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding-right: 10px;
  font-size: 14px;
}

.tree-node-label {
  display: inline-flex;
  font-size: 14px;
  align-items: center;
  justify-content: flex-start;
  text-align: left;
  gap: 6px;
  flex: 1 1 auto;
  min-width: 0;
}

.tree-node-title {
  display: block;
  flex: 1 1 auto;
  min-width: 0;
  text-align: left;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.node-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.node-icon-svg {
  width: 14px;
  height: 14px;
  color: var(--primary-color, #8b5cf6);
}

.node-icon-svg--loading {
  display: block;
  transform-origin: center;
  animation: article-tree-node-icon-spin 0.75s linear infinite;
}

@keyframes article-tree-node-icon-spin {
  to {
    transform: rotate(360deg);
  }
}

.node-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: 8px;
  flex-shrink: 0;
  min-width: 56px;
  justify-content: flex-end;
  visibility: hidden;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease;
}

.tree-node-wrapper:hover .node-actions,
.tree-node-wrapper .node-actions:has(.tiny-dropdown--visible),
.tree-node-wrapper .node-actions.dropdown-visible {
  visibility: visible;
  opacity: 1;
  pointer-events: auto;
}

.node-action-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  
  :deep(svg),
  :deep(.tiny-svg) {
    color: #909399 !important;
    fill: #909399 !important;
    font-size: 18px !important;
    width: 18px !important;
    height: 18px !important;
  }
  
  :deep(.tiny-dropdown__suffix-icon) {
    color: #909399 !important;
    fill: #909399 !important;
    font-size: 18px !important;
    width: 18px !important;
    height: 18px !important;
    border-radius: 6px;
    
    svg {
      width: 18px !important;
      height: 18px !important;
      color: #909399 !important;
      fill: #909399 !important;
    }
  }
  
  :deep(.tiny-dropdown__suffix) {
    color: #909399 !important;
    border-radius: 6px;
    
    svg {
      color: #909399 !important;
      fill: #909399 !important;
      width: 18px !important;
      height: 18px !important;
    }
  }
  
  :deep(.tiny-dropdown__wrap) {
    border-radius: 6px;
  }
  
  &:hover {
    :deep(svg),
    :deep(.tiny-svg) {
      color: #8b5cf6 !important;
      fill: #8b5cf6 !important;
    }
    
    :deep(.tiny-dropdown__suffix-icon),
    :deep(.tiny-dropdown__suffix) {
      color: #8b5cf6 !important;
      
      svg {
        color: #8b5cf6 !important;
        fill: #8b5cf6 !important;
      }
    }
  }
}

.tree-node-edit {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  flex-wrap: wrap;

  .temp-node-type-select,
  .temp-node-vis-select {
    flex-shrink: 0;
    width: 84px;
  }

  .temp-node-vis-select {
    width: 92px;
  }
  
  .temp-node-input {
    flex: 1 1 120px;
    min-width: 0;
  }
  
  .edit-actions {
    display: flex;
    gap: 6px;
    flex-shrink: 0;
    align-items: center;
  }
  
  .icon-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    cursor: pointer;
    border-radius: 4px;
    transition: all 0.2s;
    color: #909399;
    
    &:hover {
      background-color: #f5f7fa;
    }
    
    svg {
      width: 14px;
      height: 14px;
    }
  }
  
  .icon-button-check {
    color: #67c23a;
    
    &:hover {
      color: #67c23a;
    }
  }
  
  .icon-button-cancel {
    color: #f56c6c;
    
    &:hover {
      background-color: #fef0f0;
      color: #f56c6c;
    }
  }
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #999;
}

.content-area {
  flex: 1;
  overflow-y: auto;
  padding: 30px 0 0px 30px;
  background: #fff;
  color: #303133;
  color-scheme: light;
  position: relative;
  /* 固定右侧文章详情区域高度，随视口自适应 */

  &.content-area--editing {
    position: fixed;
    inset: 0;
    z-index: 300;
    padding: 0;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    min-height: 0;
    box-sizing: border-box;
    background:
      radial-gradient(circle at top right, rgba(139, 92, 246, 0.12), transparent 26%),
      radial-gradient(circle at bottom left, rgba(124, 58, 237, 0.08), transparent 24%),
      linear-gradient(180deg, #fcfbff 0%, #f6f3ff 100%);
  }
}


.article-detail {
  margin: 0 auto;

  &.article-detail--editing {
    flex: 1;
    min-height: 0;
    width: 100%;
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
}

.article-header {
  padding-bottom: 20px;

  &.article-header--editing {
    flex-shrink: 0;
    padding: 6px 14px 8px;
    margin-bottom: 0;
    border-radius: 0px;
    background: rgba(255, 255, 255, 0.82);
    box-shadow:
      0 6px 18px rgba(124, 58, 237, 0.06),
      inset 0 1px 0 rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(16px);
  }
}

.article-edit-toolbar-flags {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 10px;
  margin: 0;
  padding: 5px 10px;
  border-radius: 12px;
  background: linear-gradient(145deg, rgba(139, 92, 246, 0.09) 0%, rgba(255, 255, 255, 0.65) 100%);
  border: 1px solid rgba(139, 92, 246, 0.16);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.9),
    0 2px 8px rgba(124, 58, 237, 0.06);
}

.article-header-edit-flag {
  display: inline-flex;
  align-items: center;
  gap: 6px;

  &__icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 18px;
    height: 18px;
    flex-shrink: 0;
    color: #7c3aed;
    opacity: 0.92;

    svg {
      width: 15px;
      height: 15px;
    }
  }

  &__label {
    font-size: 12px;
    font-weight: 600;
    color: #5b21b6;
    white-space: nowrap;
    letter-spacing: 0.02em;
  }

  &--tags {
    flex: 1 1 220px;
    min-width: 0;
    max-width: 100%;
    display: flex;
    flex-wrap: nowrap;
    align-items: center;
    gap: 6px 8px;

    .article-edit-tags-select {
      flex: 1;
      min-width: 0;
    }
  }

  :deep(.tiny-switch__core) {
    min-width: 36px;
    height: 20px;
  }
}

.article-edit-tags-select {
  min-width: 200px;
  max-width: 360px;

  :deep(.tiny-select.tiny-select--small) {
    display: block;
    width: 100%;
    margin: 0;
    --tv-Select-height: 28px;
    --tv-Select-tags-height: 28px;
    --tv-Select-tag-margin: 2px;
    --tv-Select-tags-padding: 1px 0 1px 4px;
  }

  :deep(.tiny-select.tiny-select--small .tiny-input .tiny-input__suffix-inner) {
    height: 28px;
  }

  :deep(.tiny-select.tiny-select--small .tiny-input__inner) {
    height: 28px;
    min-height: 28px;
    line-height: 28px;
  }

  @media (max-width: 768px) {
    max-width: 100%;
  }
}

.article-title-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 15px;
  position: relative;

  .article-header--editing & {
    gap: 10px;
    margin-bottom: 0;
    align-items: center;
  }
}

.article-actions {
  display: flex;
  gap: 10px;
  flex-shrink: 0;

  .article-header--editing & {
    flex-wrap: wrap;
    justify-content: flex-end;
    align-items: center;
  }

  .article-header--editing & :deep(.tiny-button) {
    height: 30px;
    padding: 0 12px;
    font-size: 13px;
    border-radius: 8px;
    font-weight: 600;
    box-shadow: none;
  }

  .article-header--editing & :deep(.tiny-button--primary) {
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
    border-color: transparent;
    box-shadow: 0 4px 12px rgba(124, 58, 237, 0.18);
  }

  .article-header--editing & :deep(.tiny-button--default),
  .article-header--editing & :deep(.tiny-button:not(.tiny-button--primary)) {
    border-color: rgba(139, 92, 246, 0.18);
    background: rgba(255, 255, 255, 0.9);
    color: #5b21b6;
  }
}

.edit-actions {
  display: flex;
  gap: 10px;
}

.article-content-wrapper {
  display: flex;
  gap: 0;
  position: relative;

  &.article-content-wrapper--editing {
    flex: 1;
    min-height: 0;
  }
}

.article-content {
  flex: 1;
  min-width: 0;
  color: #303133;
  color-scheme: light;

  .article-content-wrapper:not(.article-content-wrapper--editing) & {
    display: flex;
    flex-direction: column;
  }

  .article-content-wrapper:not(.article-content-wrapper--editing) & .article-meta {
    order: 10;
  }

  .article-content-wrapper:not(.article-content-wrapper--editing) & .editor-container,
  .article-content-wrapper:not(.article-content-wrapper--editing) & .empty-content {
    order: 0;
  }

  .article-content-wrapper:not(.article-content-wrapper--editing) & .article-tags--content-footer {
    order: 5;
  }

  .article-content-wrapper--editing & {
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  :deep(img) {
    cursor: pointer;
  }
}

.editor-container {
  min-height: 400px;
  /* border: 1px solid #e4e7ed; */
  border-radius: 4px;
  overflow: hidden;

  .article-content-wrapper--editing & {
    flex: 1;
    min-height: 0;
    height: 100%;
    border-radius: 0px;
    border: 1px solid rgba(139, 92, 246, 0.14);
    background: rgba(255, 255, 255, 0.92);
  }

  .article-content-wrapper--editing &:not(.editor-preview) {
    flex: 1;
    min-height: 0;
    max-height: none;
    display: flex;
    flex-direction: column;
    /* 勿用 overflow:hidden + 大圆角：会裁切 .ql-editor 右下角滚动条，滚到底部时滑块/轨道被挡住 */
    overflow: visible;
  }

  /* FluentEditorV4 根节点与外层同 class，需参与 flex 才不会被 content-area overflow 裁掉底部 */
  .article-content-wrapper--editing &:not(.editor-preview) > :deep(.editor-container) {
    flex: 1;
    min-height: 0;
    min-width: 0;
    display: flex;
    flex-direction: column;
    /* 根节点保持可溢出，mention 等浮层由 FluentEditorV4 处理；纵向裁切在 .fluent-editor-v4-layout */
  }

  .article-content-wrapper--editing &:not(.editor-preview) :deep(.tiny-fluent-editor) {
    height: 100%;
    display: flex;
    flex-direction: column;
    min-height: 0;
  }

  .article-content-wrapper--editing &:not(.editor-preview) :deep(.ql-toolbar),
  .article-content-wrapper--editing &:not(.editor-preview) :deep(.ql-toolbar.ql-snow) {
    position: sticky;
    top: 0;
    z-index: 5;
    padding: 12px 14px;
    border: none;
    border-bottom: 1px solid rgba(139, 92, 246, 0.1);
    background:
      linear-gradient(180deg, rgba(255, 255, 255, 0.96) 0%, rgba(250, 247, 255, 0.96) 100%);
    backdrop-filter: blur(12px);
  }

  .article-content-wrapper--editing &:not(.editor-preview) :deep(.ql-container),
  .article-content-wrapper--editing &:not(.editor-preview) :deep(.ql-container.ql-snow) {
    flex: 1;
    min-height: 0;
    border: none;
    background: transparent;
  }

  .article-content-wrapper--editing &:not(.editor-preview) :deep(.ql-editor) {
    padding: 28px 40px 56px 32px;
    font-size: 15px;
    line-height: 1.8;
    scrollbar-width: thin;
    /* auto：仅内容超出时出现滚动条；不用 scroll + scrollbar-gutter:stable，否则未溢出也会占槽/显滚动条 */
    overflow-y: auto;
    &::-webkit-scrollbar {
      width: 8px;
    }
    &::-webkit-scrollbar-track {
      background: rgba(15, 23, 42, 0.06);
      border-radius: 4px;
    }
    &::-webkit-scrollbar-thumb {
      background: rgba(124, 58, 237, 0.35);
      border-radius: 4px;
    }
    &::-webkit-scrollbar-thumb:hover {
      background: rgba(124, 58, 237, 0.5);
    }
  }

  // 预览模式：隐藏边框和工具栏
  &.editor-preview {
    overflow: visible;
    border: none !important;
    border-radius: 0;
    box-shadow: none !important;
    padding: 0 !important;
    margin: 0 !important;
    
    // 隐藏工具栏 - 使用多种选择器确保覆盖
    :deep(.ql-toolbar),
    :deep(.ql-toolbar.ql-snow),
    :deep([class*="toolbar"]),
    :deep([class*="Toolbar"]) {
      display: none !important;
      visibility: hidden !important;
      height: 0 !important;
      min-height: 0 !important;
      padding: 0 !important;
      margin: 0 !important;
      border: none !important;
      overflow: hidden !important;
    }
    
    // 隐藏编辑器边框 - 覆盖所有可能的边框样式
    :deep(.ql-container),
    :deep(.ql-container.ql-snow),
    :deep([class*="container"]),
    :deep([class*="Container"]) {
      border: none !important;
      border-top: none !important;
      border-bottom: none !important;
      border-left: none !important;
      border-right: none !important;
      box-shadow: none !important;
      outline: none !important;
    }
    
    // 隐藏整个编辑器的边框容器
    :deep(.tiny-fluent-editor),
    :deep(.tiny-fluent-editor > div),
    :deep(.tiny-fluent-editor > .ql-container),
    :deep([class*="fluent-editor"]),
    :deep([class*="FluentEditor"]) {
      border: none !important;
      box-shadow: none !important;
      outline: none !important;
    }
    
    // 确保编辑器内容区域无边框
    :deep(.ql-editor),
    :deep([class*="editor"]) {
      padding: 0 !important;
      border: none !important;
      outline: none !important;
    }
    
    // 隐藏 Quill 编辑器的所有边框相关元素
    :deep(.ql-snow),
    :deep(.ql-snow .ql-toolbar),
    :deep(.ql-snow .ql-container),
    :deep([class*="snow"]) {
      border: none !important;
      outline: none !important;
    }
    
    // 确保编辑器外层容器也无边框 - 使用通配符选择器
    :deep(> *),
    :deep(> * > *) {
      border: none !important;
      outline: none !important;
    }
    
    // 移除所有可能的边框样式（包括内联样式）
    :deep(*) {
      &[style*="border"] {
        border: none !important;
      }
      &[style*="Border"] {
        border: none !important;
      }
    }
    
    // 强制移除所有边框 - 使用更通用的选择器覆盖所有子元素
    :deep(div),
    :deep(span),
    :deep(section),
    :deep(article) {
      border: none !important;
      outline: none !important;
      box-shadow: none !important;
    }

    // 与 FluentEditorV4 一致：恢复任务列表 .ql-ui（通配 span/div 会去掉边框）
    :deep(.ql-editor li[data-list='checked'] > .ql-ui),
    :deep(.ql-editor li[data-list='unchecked'] > .ql-ui),
    :deep(.ql-editor li.checked > .ql-ui),
    :deep(.ql-editor li.unchecked > .ql-ui) {
      display: inline-block !important;
      width: 16px !important;
      height: 16px !important;
      min-width: 16px !important;
      min-height: 16px !important;
      line-height: 14px !important;
      text-align: center !important;
      border: 1px solid #adb0b8 !important;
      color: #777 !important;
      visibility: visible !important;
      opacity: 1 !important;
      box-shadow: none !important;
    }
    :deep(.ql-editor li[data-list='checked'] > .ql-ui),
    :deep(.ql-editor li.checked > .ql-ui) {
      border-color: #5e7ce0 !important;
    }
    /* Quill2 默认 data-list=checked 的 ::before 为 Unicode ☑，会盖住背景 SVG 的白勾；与 li.checked 一致清空后由背景图显示 */
    :deep(.ql-editor li[data-list='checked'] > .ql-ui::before),
    :deep(.ql-editor li.checked > .ql-ui::before) {
      content: '' !important;
    }

    /* 阅读态：白底 + 深色字，避免移动端系统深色模式下继承 :root 浅色字不可见 */
    :deep(.ql-container),
    :deep(.ql-container.ql-snow),
    :deep(.tiny-fluent-editor),
    :deep(.fluent-editor-v4-layout),
    :deep(.fluent-editor-v4-editor-surface) {
      color: #303133;
      background-color: #fff;
      color-scheme: light;
    }

    :deep(.ql-editor) {
      color: #303133 !important;
      background-color: #fff !important;
      -webkit-text-fill-color: currentColor;
      caret-color: #303133;
    }

    :deep(.ql-editor p),
    :deep(.ql-editor li),
    :deep(.ql-editor ol),
    :deep(.ql-editor ul),
    :deep(.ql-editor blockquote),
    :deep(.ql-editor td),
    :deep(.ql-editor th),
    :deep(.ql-editor h1),
    :deep(.ql-editor h2),
    :deep(.ql-editor h3),
    :deep(.ql-editor h4),
    :deep(.ql-editor h5),
    :deep(.ql-editor h6),
    :deep(.ql-editor .ql-file-item span) {
      color: inherit;
    }

    :deep(.ql-editor a),
    :deep(.ql-editor a span) {
      color: var(--primary-color, #8b5cf6);
    }

    :deep(.ql-editor pre),
    :deep(.ql-editor .ql-code-block-container),
    :deep(.ql-editor .hljs),
    :deep(.ql-editor .hljs *) {
      -webkit-text-fill-color: unset;
      color-scheme: dark;
    }
  }
}

.article-title {
  margin: 0 0 15px 0;
  font-size: 28px;
  font-weight: 600;
  color: #333;
  text-align: left;
  cursor: pointer;
  user-select: none;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
  position: relative;

  .article-header--editing & {
    margin: 0;
    font-size: clamp(20px, 2vw, 26px);
    line-height: 1.25;
    letter-spacing: -0.02em;
    color: #1f1147;
  }
  
  &:hover {
    .edit-icon {
      opacity: 1;
    }
  }
  
  .visibility-badge {
    position: absolute;
    top: -10px;
    right: 0;
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 5px 12px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.3px;
    border-radius: 14px;
    white-space: nowrap;
    pointer-events: none;
    box-shadow: 0 3px 8px rgba(0, 0, 0, 0.15), 0 1px 3px rgba(0, 0, 0, 0.1);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    z-index: 10;
    
    .visibility-icon {
      width: 13px;
      height: 13px;
      stroke-width: 2.5;
      flex-shrink: 0;
    }
    
    .visibility-text {
      line-height: 1;
    }
    
    &--1 {
      background: linear-gradient(135deg, #ff4757 0%, #ff3838 50%, #ff1744 100%);
      color: #fff;
      box-shadow: 0 4px 12px rgba(255, 71, 87, 0.4), 0 2px 4px rgba(255, 71, 87, 0.2);
      border-color: rgba(255, 255, 255, 0.3);
      
      .visibility-icon {
        filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.3));
      }
    }
    
    &--2 {
      background: linear-gradient(135deg, #9d4edd 0%, #7b2cbf 50%, #6a1b9a 100%);
      color: #fff;
      box-shadow: 0 4px 12px rgba(157, 78, 221, 0.4), 0 2px 4px rgba(157, 78, 221, 0.2);
      border-color: rgba(255, 255, 255, 0.3);
      
      .visibility-icon {
        filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.3));
      }
    }
    
    &--3 {
      background: linear-gradient(135deg, #06d6a0 0%, #05c78a 50%, #04a777 100%);
      color: #fff;
      box-shadow: 0 4px 12px rgba(6, 214, 160, 0.4), 0 2px 4px rgba(6, 214, 160, 0.2);
      border-color: rgba(255, 255, 255, 0.3);
      
      .visibility-icon {
        filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.3));
      }
    }
  }
  
  .edit-icon {
    flex-shrink: 0;
    opacity: 0;
    transition: opacity 0.2s;
    color: #909399;
    font-size: 14px;
    width: 14px;
    height: 14px;
    cursor: pointer;
    
    &:hover {
      color: #8b5cf6;
    }
  }
}

.article-title-edit {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 15px;

  .article-header--editing & {
    flex: 1;
    gap: 12px;
    margin-bottom: 0;
    padding: 6px;
    border-radius: 18px;
    background: linear-gradient(180deg, rgba(139, 92, 246, 0.08), rgba(139, 92, 246, 0.04));
  }
  
  .title-input {
    flex: 1;
    min-width: 800px;
    max-width: 90%;

    .article-header--editing & {
      min-width: 0;
      max-width: none;
    }
    
    :deep(input) {
      font-size: 28px;
      font-weight: 600;
      color: #333;
      height: auto;
      line-height: 1.5;
      width: 100%;
      padding: 0;

      .article-header--editing & {
        min-height: 40px;
        padding: 8px 12px;
        font-size: 22px;
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.92);
        box-shadow: inset 0 0 0 1px rgba(139, 92, 246, 0.12);
        color: #1f1147;
      }
    }
  }
  
  .title-edit-actions {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-shrink: 0;
    
    .icon-button {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 28px;
      height: 28px;
      cursor: pointer;
      border-radius: 4px;
      transition: background-color 0.2s ease, color 0.2s ease;
      background-color: transparent;

      .article-header--editing & {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.85);
        box-shadow: inset 0 0 0 1px rgba(139, 92, 246, 0.12);
      }
      
      &:hover {
        background-color: #f0f0f0;
      }
      
      svg {
        width: 18px;
        height: 18px;
      }
    }
    
    .icon-button-check {
      color: #67c23a;
      
      &:hover {
        background-color: #e1f3d8;
        color: #67c23a;
      }
    }
    
    .icon-button-cancel {
      color: #f56c6c;
      
      &:hover {
        background-color: #fef0f0;
        color: #f56c6c;
      }
    }
  }
}

.article-meta {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 15px;
  font-size: 14px;
  color: #666;
}

.article-meta__main {
  display: flex;
  flex-direction: column;
  gap: 0;
  flex: 1;
  min-width: min(100%, 280px);
}

.meta-badge-strip {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.meta-badge-strip--after-updated {
  margin-left: 4px;
  padding: 5px 10px;
  border-radius: 14px;
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.92) 0%, rgba(250, 245, 255, 0.95) 100%);
  border: 1px solid rgba(139, 92, 246, 0.14);
  box-shadow:
    0 4px 14px rgba(124, 58, 237, 0.07),
    inset 0 1px 0 rgba(255, 255, 255, 0.95);
}

.meta-text-line {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px 20px;
  line-height: 1.5;
  row-gap: 10px;
}

.meta-right {
  display: flex;
  gap: 20px;
  flex-shrink: 0;
  align-self: center;
}

@media (max-width: 768px) {
  .article-meta {
    flex-direction: column;
    align-items: stretch;
  }

  .meta-right {
    align-self: flex-start;
  }
}

.meta-item {
  display: flex;
  align-items: center;
}

.meta-visibility-badge {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  padding: 5px 12px;
  min-height: 28px;
  box-sizing: border-box;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.3px;
  border-radius: 14px;
  white-space: nowrap;
  box-shadow: 0 3px 8px rgba(0, 0, 0, 0.15), 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  
  .visibility-icon {
    width: 13px;
    height: 13px;
    stroke-width: 2.5;
    flex-shrink: 0;
  }
  
  .visibility-text {
    line-height: 1;
  }
}

.meta-visibility-badge--1 {
  background: linear-gradient(135deg, #ff4757 0%, #ff3838 50%, #ff1744 100%) !important;
  color: #fff !important;
  box-shadow: 0 4px 12px rgba(255, 71, 87, 0.4), 0 2px 4px rgba(255, 71, 87, 0.2) !important;
  border-color: rgba(255, 255, 255, 0.3) !important;
  
  .visibility-icon {
    filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.3));
  }
}

.meta-visibility-badge--2 {
  background: linear-gradient(135deg, #9d4edd 0%, #7b2cbf 50%, #6a1b9a 100%) !important;
  color: #fff !important;
  box-shadow: 0 4px 12px rgba(157, 78, 221, 0.4), 0 2px 4px rgba(157, 78, 221, 0.2) !important;
  border-color: rgba(255, 255, 255, 0.3) !important;
  
  .visibility-icon {
    filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.3));
  }
}

.meta-visibility-badge--3 {
  background: linear-gradient(135deg, #06d6a0 0%, #05c78a 50%, #04a777 100%) !important;
  color: #fff !important;
  box-shadow: 0 4px 12px rgba(6, 214, 160, 0.4), 0 2px 4px rgba(6, 214, 160, 0.2) !important;
  border-color: rgba(255, 255, 255, 0.3) !important;
  
  .visibility-icon {
    filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.3));
  }
}

.meta-flag-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  padding: 5px 12px;
  min-height: 28px;
  box-sizing: border-box;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.3px;
  border-radius: 14px;
  white-space: nowrap;
  border: 1px solid rgba(255, 255, 255, 0.35);
  box-shadow:
    0 2px 8px rgba(124, 58, 237, 0.18),
    inset 0 1px 0 rgba(255, 255, 255, 0.25);
  transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow:
      0 4px 12px rgba(124, 58, 237, 0.22),
      inset 0 1px 0 rgba(255, 255, 255, 0.3);
  }

  &__icon {
    width: 13px;
    height: 13px;
    flex-shrink: 0;
    opacity: 0.95;
  }
}

.meta-flag-badge--original {
  background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 55%, #5b21b6 100%);
  color: #fff;
}

.meta-flag-badge--ai {
  background: linear-gradient(135deg, #22d3ee 0%, #0ea5e9 45%, #6366f1 100%);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.3);

  .meta-flag-badge__icon {
    filter: drop-shadow(0 1px 1px rgba(0, 0, 0, 0.15));
  }
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #666;
  font-size: 13px;
}

.stat-icon {
  width: 16px;
  height: 16px;
  color: #666;
  flex-shrink: 0;
  
  :deep(svg) {
    width: 16px;
    height: 16px;
  }
}

.stat-value {
  color: #333;
  font-weight: 500;
  line-height: 1;
}

.article-actions-bar {
  flex-shrink: 0;
  position: sticky;
  top: 0;
  align-self: flex-start;
  max-height: calc(100vh - 200px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #f9f9f9;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 16px;
  margin-left: 0;
  align-items: center;
  gap: 8px;
  z-index: 200;
  padding: 12px 4px;
  background: #fff;
  border-radius: 12px;
  box-shadow: -2px 0 12px rgba(0, 0, 0, 0.1);
  border: 1px solid #e4e7ed;
  border-right: none;
  transition: right 0.3s ease;
}

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 8px 12px;
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 12px;
  color: #666;
  position: relative;
  min-width: 60px;
  width: 100%;
  outline: none;
  
  &:focus,
  &:active {
    outline: none;
    box-shadow: none;
  }

  &:hover {
    background: #f5f7fa;
    border-color: var(--primary-color, #8b5cf6);
    color: var(--primary-color, #8b5cf6);

    .action-icon {
      color: var(--primary-color, #8b5cf6);
    }
  }

  &.is-active {
    background: rgba(139, 92, 246, 0.1);
    border-color: var(--primary-color, #8b5cf6);
    color: var(--primary-color, #8b5cf6);

    .action-icon {
      color: var(--primary-color, #8b5cf6);
      fill: var(--primary-color, #8b5cf6);
      
      :deep(svg) {
        color: var(--primary-color, #8b5cf6) !important;
        fill: var(--primary-color, #8b5cf6) !important;
      }
    }
  }

  &:disabled {
    opacity: 0.55;
    cursor: not-allowed;
  }

  .action-icon {
    width: 16px;
    height: 16px;
    color: inherit;
    transition: all 0.3s;
    flex-shrink: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;

    :deep(svg) {
      width: 16px;
      height: 16px;
      color: inherit;
      transition: all 0.3s;
    }
  }

  .action-text {
    font-size: 11px;
    font-weight: 500;
    white-space: nowrap;
    text-align: center;
  }

  .action-count {
    position: absolute;
    top: 4px;
    right: 4px;
    font-size: 10px;
    color: #fff;
    background: var(--primary-color, #8b5cf6);
    border-radius: 10px;
    padding: 2px 6px;
    min-width: 18px;
    height: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 500;
    line-height: 1;
  }

  &.is-active .action-count {
    background: var(--primary-color, #8b5cf6);
    color: #fff;
  }
}

.article-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 15px;

  &--content-footer {
    margin-top: 18px;
    margin-bottom: 0;
    flex-wrap: nowrap;
    align-items: flex-start;
    gap: 10px;
  }

  &__lead-icon {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 22px;
    height: 22px;
    margin-top: 3px;
    color: var(--primary-color, #8b5cf6);

    svg {
      width: 18px;
      height: 18px;
    }
  }

  &__chips {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    flex: 1;
    min-width: 0;
  }
}

.tag {
  padding: 4px 12px;
  background-color: #f0f0f0;
  border-radius: 4px;
  font-size: 12px;
  color: #666;

  &--theme {
    color: var(--primary-color, #8b5cf6);
    background: rgba(139, 92, 246, 0.1);
    border: 1px solid rgba(139, 92, 246, 0.28);
    font-weight: 500;
  }
}

.sign-read-banner {
  margin-top: 15px;
  padding: 12px 16px;
  background: linear-gradient(135deg, #f3e8ff 0%, #ede9fe 100%);
  border-radius: 8px;
  border: 1px solid #e9d5ff;

  &.sign-read-banner--status-2 {
    background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
    border-color: #a7f3d0;
  }

  &.sign-read-banner--status-3,
  &.sign-read-banner--status-4 {
    background: #f9fafb;
    border-color: #e5e7eb;
  }
}

.sign-read-status-row {
  display: flex;
  align-items: center;
  gap: 8px;

  .sign-read-status-label {
    font-size: 13px;
    color: #6d28d9;
  }

  .sign-read-status-value {
    font-size: 14px;
    font-weight: 600;
    color: #5b21b6;
  }
}

.sign-read-banner--status-2 .sign-read-status-row {
  .sign-read-status-label { color: #059669; }
  .sign-read-status-value { color: #047857; }
}

.sign-read-banner--status-3 .sign-read-status-row,
.sign-read-banner--status-4 .sign-read-status-row {
  .sign-read-status-label { color: #6b7280; }
  .sign-read-status-value { color: #4b5563; }
}

.sign-read-meta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px 20px;
  margin-top: 8px;
  font-size: 12px;
  color: #6b7280;
}

.sign-read-countdown {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #6d28d9;
  margin-top: 8px;

  .sign-read-label {
    font-size: 14px;
  }

  .sign-read-time {
    font-size: 18px;
    font-weight: 600;
    font-variant-numeric: tabular-nums;
  }
}

.sign-read-time-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 64px;
  padding: 2px 8px;
  margin-right: 8px;
  border-radius: 999px;
  background: rgba(37, 99, 235, 0.08);
  color: #2563eb;
  font-size: 13px;
  font-variant-numeric: tabular-nums;
}

.sign-read-complete {
  display: flex;
  align-items: center;
  margin-top: 8px;
}

.content-text {
  line-height: 1.8;
  color: #333;
  font-size: 15px;

  :deep(p) {
    margin: 0 0 16px 0;
  }

  :deep(h1), :deep(h2), :deep(h3), :deep(h4), :deep(h5), :deep(h6) {
    margin: 24px 0 16px 0;
    font-weight: 600;
    color: #333;
  }

  :deep(ul), :deep(ol) {
    margin: 0 0 16px 0;
    padding-left: 24px;
  }

  :deep(li) {
    margin: 8px 0;
  }

  :deep(code) {
    padding: 2px 6px;
    background-color: #f5f5f5;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 14px;
  }

  :deep(pre) {
    padding: 16px;
    background-color: #f5f5f5;
    border-radius: 6px;
    overflow-x: auto;
    margin: 16px 0;
  }

  :deep(blockquote) {
    margin: 16px 0;
    padding-left: 16px;
    border-left: 4px solid var(--primary-color, #8b5cf6);
    color: #666;
  }
}

.empty-content {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}

.empty-selection {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
  font-size: 16px;
}

.article-error-panel {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 280px;
  padding: 24px;
}

.article-error-card {
  width: 100%;
  max-width: 420px;
  text-align: center;
  padding: 32px 28px;
  border-radius: 16px;
  background: var(--bg-color, #fff);
  box-shadow: 0 4px 24px rgba(139, 92, 246, 0.08);
  border: 1px solid var(--border-color, #e4e7ed);
  transition: box-shadow 0.2s ease;
}

.article-error-card:hover {
  box-shadow: 0 8px 32px rgba(139, 92, 246, 0.12);
}

.article-error-icon-wrap {
  width: 64px;
  height: 64px;
  margin: 0 auto 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.article-error-icon-wrap svg {
  width: 32px;
  height: 32px;
}

.article-error-permission .article-error-icon-lock {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.12) 0%, rgba(139, 92, 246, 0.06) 100%);
  color: var(--primary-color, #8b5cf6);
}

.article-error-not-found .article-error-icon-ghost {
  background: linear-gradient(135deg, rgba(144, 147, 153, 0.15) 0%, rgba(144, 147, 153, 0.06) 100%);
  color: var(--text-color-secondary, #909399);
}

.article-error-heading {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color, #303133);
  margin: 0 0 8px 0;
  line-height: 1.4;
}

.article-error-desc {
  font-size: 14px;
  color: var(--text-color-secondary, #606266);
  margin: 0 0 20px 0;
  line-height: 1.5;
}

.article-apply-trigger-btn {
  margin-bottom: 4px;
}

/* 申请编辑表单 - 展开动画 */
.article-apply-slide-enter-active,
.article-apply-slide-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.article-apply-slide-enter-from,
.article-apply-slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

.article-apply-edit-form {
  margin-top: 20px;
  padding: 20px;
  border-radius: 12px;
  background: var(--bg-color-secondary, #fafafa);
  border: 1px solid var(--border-color, #e4e7ed);
  text-align: left;
}

.article-apply-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 16px;
}

.article-apply-field:last-of-type {
  margin-bottom: 18px;
}

.article-apply-edit-label {
  display: block;
  font-size: 13px;
  color: var(--text-color-secondary, #606266);
  margin-bottom: 8px;
  font-weight: 500;
}

.article-apply-role-select {
  width: 100%;
}

.article-apply-role-select :deep(.tiny-select__wrapper) {
  width: 100%;
}

.article-apply-optional-hint {
  font-size: 12px;
  color: var(--text-color-secondary, #909399);
  font-weight: normal;
  margin-left: 4px;
}

.article-apply-reviewers-select {
  width: 100%;
}

.article-apply-reviewers-select :deep(.tiny-select__wrapper) {
  width: 100%;
}

.article-apply-reviewers-empty {
  font-size: 12px;
  color: var(--text-color-secondary, #909399);
  margin: 4px 0 0 0;
  font-style: italic;
}

.article-apply-edit-remark {
  width: 100%;
  margin: 0;
}

.article-apply-edit-remark :deep(textarea) {
  resize: vertical;
  min-height: 88px;
  border-radius: 8px;
}

.article-apply-edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.article-admins-section {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color, #e4e7ed);
  text-align: left;
}

.article-admins-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.article-admins-icon {
  width: 18px;
  height: 18px;
  color: var(--primary-color, #8b5cf6);
  flex-shrink: 0;
}

.article-admins-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-color, #303133);
  margin: 0;
}

.article-admins-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.article-admin-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border-radius: 10px;
  background: var(--bg-color-secondary, #f5f7fa);
  margin-bottom: 8px;
  font-size: 14px;
  transition: background 0.2s ease;
}

.article-admin-item:last-child {
  margin-bottom: 0;
}

.article-admin-item:hover {
  background: rgba(139, 92, 246, 0.06);
}

.article-admin-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color, #8b5cf6) 0%, #a78bfa 100%);
  color: #fff;
  font-size: 14px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.article-admin-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.article-admin-name {
  color: var(--text-color, #303133);
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.article-admin-email {
  font-size: 12px;
  color: var(--text-color-secondary, #909399);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.article-admins-empty {
  font-size: 14px;
  color: var(--text-color-secondary, #909399);
  margin: 0;
  padding: 12px 0;
  text-align: center;
}

// 阅读区在紧凑/移动端同样强制浅色配色（系统深色模式 + 白底正文）
.article-management-page--compact,
.article-management-page--mobile {
  .content-area:not(.content-area--editing) {
    color: #303133;
    background: #fff;
    color-scheme: light;
  }

  .article-content .editor-container.editor-preview {
    :deep(.ql-editor) {
      color: #303133 !important;
      background-color: #fff !important;
    }
  }
}

// 桌面：元信息仍在标题下方（flex order）
.article-management-page:not(.article-management-page--compact) {
  .article-content .article-meta {
    order: -1;
    margin-top: 0;
    margin-bottom: 15px;
  }
}

// 平板/紧凑：侧栏抽屉
.article-management-page--compact {
  .article-content .article-meta {
    margin-top: 20px;
    margin-bottom: 0;
    padding-top: 16px;
    border-top: 1px solid #ebeef5;
  }

  /* 阅读态：标题已在 content-mobile-toolbar 展示，正文区不再重复标题 */
  .article-header:not(.article-header--editing) {
    .article-title,
    .article-title-edit {
      display: none;
    }
  }

  .tree-sidebar-overlay {
    position: fixed;
    inset: 0;
    z-index: 400;
    background: rgba(15, 23, 42, 0.45);
    backdrop-filter: blur(2px);
  }

  .tree-sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 410;
    width: min(320px, 88vw) !important;
    max-width: 88vw;
    transform: translateX(-100%);
    transition: transform 0.28s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 4px 0 24px rgba(0, 0, 0, 0.14);
    border-right: none;

    &.tree-sidebar--drawer-open {
      transform: translateX(0);
    }
  }

  .content-area {
    width: 100%;
    flex: 1;
    min-width: 0;
    padding: 0;
  }

  .content-mobile-toolbar {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    border-bottom: 1px solid #e4e7ed;
    background: #fff;
    position: sticky;
    top: 0;
    z-index: 30;
    flex-shrink: 0;
  }

  .content-mobile-toolbar__btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    flex-shrink: 0;
    padding: 6px 12px;
    border: 1px solid rgba(139, 92, 246, 0.25);
    border-radius: 8px;
    background: rgba(139, 92, 246, 0.08);
    color: var(--primary-color, #8b5cf6);
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.2s, border-color 0.2s;

    &:hover {
      background: rgba(139, 92, 246, 0.14);
      border-color: rgba(139, 92, 246, 0.4);
    }
  }

  .content-mobile-toolbar__title {
    flex: 1;
    min-width: 0;
    margin: 0;
    font-size: 14px;
    font-weight: 600;
    color: #333;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  &:not(.article-management-page--mobile) .article-detail {
    padding: 0 20px 24px;
  }
}

.tree-drawer-fade-enter-active,
.tree-drawer-fade-leave-active {
  transition: opacity 0.25s ease;
}

.tree-drawer-fade-enter-from,
.tree-drawer-fade-leave-to {
  opacity: 0;
}

.content-mobile-toolbar {
  display: none;
}

// 手机
.article-management-page--mobile {
  height: calc(100vh - 56px);

  .article-detail {
    padding: 0 12px calc(88px + env(safe-area-inset-bottom, 0px));
  }

  .article-header:not(.article-header--editing) .article-title-wrapper {
    display: none;
  }

  .article-header:not(.article-header--editing) .article-actions {
    display: none;
  }

  .article-content-wrapper {
    flex-direction: column;
  }

  // 目录：底部抽屉
  .article-toc-rail {
    position: fixed;
    inset: 0;
    z-index: 500;
    background: rgba(15, 23, 42, 0.45);
    align-items: flex-end;
    justify-content: center;
    padding: 0;
  }

  .article-toc-reveal-enter-active .article-toc--mobile-sheet,
  .article-toc-reveal-leave-active .article-toc--mobile-sheet {
    transition: transform 0.32s cubic-bezier(0.32, 0.72, 0, 1);
  }

  .article-toc-reveal-enter-from .article-toc--mobile-sheet,
  .article-toc-reveal-leave-to .article-toc--mobile-sheet {
    transform: translateY(100%);
  }

  .toc-resizer {
    display: none;
  }

  .article-toc--mobile-sheet {
    position: relative;
    right: auto;
    top: auto;
    bottom: auto;
    width: 100% !important;
    max-width: none;
    max-height: min(72vh, 560px);
    margin: 0;
    padding: 8px 12px 16px;
    padding-bottom: calc(16px + env(safe-area-inset-bottom, 0px));
    border-radius: 16px 16px 0 0;
    border: none;
    border-top: 1px solid rgba(139, 92, 246, 0.12);
    box-shadow: 0 -8px 32px rgba(15, 23, 42, 0.18);
    z-index: 510;

    .toc-sheet-handle {
      width: 40px;
      height: 4px;
      margin: 4px auto 10px;
      border-radius: 999px;
      background: rgba(139, 92, 246, 0.35);
      flex-shrink: 0;
    }

    .toc-header {
      margin-bottom: 10px;
      padding-bottom: 10px;
    }

    .toc-title {
      font-size: 15px;
    }

    .toc-collapse-btn {
      width: 32px;
      height: 32px;
      border-radius: 8px;
      background: rgba(139, 92, 246, 0.08);
      color: var(--primary-color, #8b5cf6);
    }

    .toc-tree-container {
      max-height: calc(min(72vh, 560px) - 72px);
    }

    .toc-tree-node {
      padding: 10px 4px;
      font-size: 14px;
      line-height: 1.4;
    }
  }

  .article-attachments-rail {
    position: fixed;
    inset: 0;
    z-index: 500;
    background: rgba(15, 23, 42, 0.45);
    padding: 12px;
    padding-bottom: calc(12px + env(safe-area-inset-bottom, 0px));
    box-sizing: border-box;
    align-items: flex-end;
    justify-content: center;
  }

  .article-attachments-wrapper,
  .article-attachments {
    width: 100%;
    max-width: none;
    max-height: min(78vh, 640px);
    overflow: auto;
    border-radius: 16px 16px 0 0;
    box-shadow: 0 -8px 32px rgba(0, 0, 0, 0.18);
  }

  // 底部工具栏
  .mobile-actions-backdrop {
    position: fixed;
    inset: 0;
    z-index: 420;
    background: rgba(15, 23, 42, 0.35);
    backdrop-filter: blur(2px);
  }

  .article-actions-bar--mobile {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    top: auto;
    z-index: 430;
    margin: 0;
    padding: 8px 10px;
    padding-bottom: calc(8px + env(safe-area-inset-bottom, 0px));
    flex-direction: column;
    align-items: stretch;
    gap: 0;
    max-width: none;
    max-height: none;
    border: none;
    border-top: 1px solid rgba(139, 92, 246, 0.12);
    border-radius: 16px 16px 0 0;
    background: rgba(255, 255, 255, 0.96);
    backdrop-filter: blur(12px);
    box-shadow: 0 -4px 24px rgba(15, 23, 42, 0.12);

    &.article-actions-bar--concealed {
      opacity: 0;
      pointer-events: none;
      transform: translateY(100%);
      transition: opacity 0.2s ease, transform 0.25s ease;
    }

    &:not(.article-actions-bar--concealed) {
      transition: transform 0.25s ease;
    }

    // 主操作：横向 dock
  }

  .article-actions-bar--mobile:not(.article-actions-bar--expanded) {
    flex-direction: row;
    flex-wrap: nowrap;
    justify-content: space-around;
    gap: 4px;

    .action-btn[data-mobile-tier='sheet'] {
      display: none;
    }

    .action-btn[data-mobile-tier='dock'] {
      flex: 1;
      min-width: 0;
      max-width: 80px;
      padding: 8px 4px;
      border: none;
      background: transparent;
      box-shadow: none;

      .action-text {
        font-size: 10px;
        line-height: 1.2;
        max-width: 100%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }

      .action-icon {
        width: 22px;
        height: 22px;

        :deep(svg) {
          width: 22px;
          height: 22px;
        }
      }

      &.is-active {
        background: rgba(139, 92, 246, 0.12);
        border-radius: 10px;
      }
    }

    .action-btn--more.is-active {
      color: var(--primary-color, #8b5cf6);
    }
  }

  .article-actions-bar--mobile.article-actions-bar--expanded {
    max-height: min(70vh, 480px);
    overflow-x: hidden;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;

    .action-btn[data-mobile-tier='dock'] {
      display: none;
    }

    .action-btn[data-mobile-tier='sheet'] {
      display: flex;
      flex-direction: row;
      justify-content: flex-start;
      align-items: center;
      width: 100%;
      min-width: 0;
      padding: 12px 14px;
      border: none;
      border-bottom: 1px solid #f0f0f0;
      border-radius: 0;
      background: transparent;
      gap: 12px;

      .action-icon {
        width: 20px;
        height: 20px;
        flex-shrink: 0;

        :deep(svg) {
          width: 20px;
          height: 20px;
        }
      }

      .action-text {
        font-size: 14px;
        text-align: left;
        white-space: nowrap;
      }

      &:last-child {
        border-bottom: none;
      }

      &.is-active {
        background: rgba(139, 92, 246, 0.08);
        color: var(--primary-color, #8b5cf6);
      }
    }

    &::before {
      content: '';
      display: block;
      width: 40px;
      height: 4px;
      margin: 2px auto 8px;
      border-radius: 999px;
      background: rgba(139, 92, 246, 0.35);
      flex-shrink: 0;
    }
  }

  .content-area:not(.content-area--editing) {
    padding-bottom: 0;
  }
}

.mobile-actions-fade-enter-active,
.mobile-actions-fade-leave-active {
  transition: opacity 0.22s ease;
}

.mobile-actions-fade-enter-from,
.mobile-actions-fade-leave-to {
  opacity: 0;
}

// 目录栏（分隔条 + 面板）整体进出动画
.article-toc-rail {
  display: flex;
  flex-direction: row;
  flex-shrink: 0;
  align-items: flex-start;
}

.article-toc-reveal-enter-active {
  transition:
    opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1),
    transform 0.38s cubic-bezier(0.34, 1.15, 0.52, 1);
}

.article-toc-reveal-leave-active {
  transition:
    opacity 0.22s cubic-bezier(0.4, 0, 1, 1),
    transform 0.24s cubic-bezier(0.4, 0, 1, 1);
}

.article-toc-reveal-enter-from,
.article-toc-reveal-leave-to {
  opacity: 0;
  transform: translateX(18px);
}

.article-toc-reveal-enter-to,
.article-toc-reveal-leave-from {
  opacity: 1;
  transform: translateX(0);
}

/* 进入编辑态时：目录/附件需立刻消失，避免与 .content-area--editing 全屏切换叠在一起产生抖动 */
.article-toc-edit-leave-active {
  transition: none;
}

// 附件栏进出动画（与目录栏一致的节奏与方向）
.article-attachments-rail {
  flex-shrink: 0;
  align-self: flex-start;
}

.article-attachments-reveal-enter-active {
  transition:
    opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1),
    transform 0.38s cubic-bezier(0.34, 1.15, 0.52, 1);
}

.article-attachments-reveal-leave-active {
  transition:
    opacity 0.22s cubic-bezier(0.4, 0, 1, 1),
    transform 0.24s cubic-bezier(0.4, 0, 1, 1);
}

.article-attachments-reveal-enter-from,
.article-attachments-reveal-leave-to {
  opacity: 0;
  transform: translateX(18px);
}

.article-attachments-reveal-enter-to,
.article-attachments-reveal-leave-from {
  opacity: 1;
  transform: translateX(0);
}

.article-attachments-edit-leave-active {
  transition: none;
}

// 目录分隔条
.toc-resizer {
  width: 6px;
  background: transparent;
  cursor: col-resize;
  position: sticky;
  top: 20px;
  align-self: flex-start;
  height: calc(100vh - 200px);
  flex-shrink: 0;
  z-index: 10;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    background-color: white;
  }
  
  &.resizing {
    background-color: white;
  }
  
  &::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    cursor: col-resize;
  }
  
  .toc-resizer-handle {
    position: absolute;
    left: calc(50% + 3px);
    top: 20px;
    transform: translate(-50%, -50%);
    width: 24px;
    height: 24px;
    border: 1px solid #d3d4d6;
    border-radius: 50%;
    background: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #606266;
    transition: all 0.2s;
    z-index: 11;
    cursor: col-resize;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    
    svg {
      width: 14px;
      height: 14px;
      pointer-events: none;
    }
  }
  
  &:hover .toc-resizer-handle {
    background: #f5f7fa;
    border-color: #8b5cf6;
    color: #8b5cf6;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
  }
  
  &.resizing .toc-resizer-handle {
    background: #f5f7fa;
    border-color: #8b5cf6;
    color: #8b5cf6;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
  }
}

// 文章目录样式
.article-toc {
  flex-shrink: 0;
  position: sticky;
  top: 0;
  align-self: flex-start;
  max-height: calc(100vh - 200px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #f9f9f9;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  padding: 16px;
  margin-left: 0;
  
  .toc-header {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #e4e7ed;
  }
  
  .toc-title {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: #333;
    flex: 1;
  }
  
  .toc-collapse-btn {
    width: 24px;
    height: 24px;
    border: none;
    background: transparent;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #666;
    border-radius: 4px;
    transition: all 0.2s;
    padding: 0;
    flex-shrink: 0;
    outline: none;
    
    &:focus,
    &:active {
      outline: none;
      box-shadow: none;
    }
    
    &:hover {
      background-color: #f0f0f0;
      color: #8b5cf6;
    }
    
    :deep(svg) {
      width: 18px;
      height: 18px;
      stroke-width: 1.5;
    }
  }
  
  .toc-tree-container {
    flex: 1;
    overflow-y: auto;
    overflow-x: hidden;
    text-align: left;
    // 隐藏滚动条但保持滚动功能
    scrollbar-width: none; // Firefox
    -ms-overflow-style: none; // IE/Edge
    
    &::-webkit-scrollbar {
      display: none; // Chrome/Safari/Opera
    }
    
    :deep(.tiny-tree) {
      background: transparent;
      border: none;
    }
    
    :deep(.tiny-tree-node) {
      padding: 2px 0;
    }
    
    :deep(.tiny-tree-node__content) {
      height: auto;
      min-height: 22px;
      padding: 2px 0;
      justify-content: flex-start;
      text-align: left;
    }

    :deep(.tiny-tree-node__label) {
      text-align: left;
      flex: 1;
      min-width: 0;
    }
    
    .toc-tree-node {
      cursor: pointer;
      display: block;
      width: 100%;
      padding: 2px 8px;
      border-radius: 4px;
      transition:
        color 0.2s ease,
        background-color 0.2s ease,
        font-weight 0.15s ease;
      font-size: 14px;
      text-align: left;
      
      &:hover {
        color: #8b5cf6;
      }

      &.is-toc-active {
        color: var(--primary-color, #8b5cf6);
        font-weight: 600;
        background: rgba(139, 92, 246, 0.1);
      }
    }
  }
  
  // 目录空状态
  .toc-empty {
    padding: 40px 20px;
    text-align: center;
    color: #999;
    font-size: 14px;
  }
}

// 目录隐藏时的显示按钮
.toc-show-btn {
  position: sticky;
  top: 20px;
  align-self: flex-start;
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  border-radius: 4px;
  transition: all 0.2s;
  z-index: 100;
  padding: 0;
  flex-shrink: 0;
  margin-top: 0;
  outline: none;
  
  &:focus,
  &:active {
    outline: none;
    box-shadow: none;
  }
  
  &:hover {
    background-color: #f0f0f0;
    color: #8b5cf6;
  }
  
  :deep(svg) {
    width: 18px;
    height: 18px;
    stroke-width: 1.5;
  }
}

// 目录高亮效果
:deep(.toc-highlight) {
  background-color: #fff3cd !important;
  transition: background-color 0.3s;
}
:deep(.blot-formatter__overlay) {
  cursor: pointer;
}
// 美化编辑器中的视频显示
:deep(.ql-video-item) {
  position: relative;
  width: 265px;
  height: 150px;
  margin: 20px auto;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  background: linear-gradient(180deg, #000000 0%, #333333 50%, #ffffff 100%);
  transition: all 0.3s ease;
  
  &:hover {
    cursor: pointer;
  }
  
  video {
    width: 100%;
    height: 100%;
    display: block;
    object-fit: contain;
    border-radius: 12px;
  }
  
  iframe {
    width: 100%;
    height: 100%;
    border: none;
    border-radius: 12px;
  }
}


// 为标题设置滚动偏移（scroll-margin-top）
:deep(.editor-container),
:deep(.ql-editor),
:deep(.article-content) {
  h1, h2, h3, h4, h5, h6 {
    scroll-margin-top: 15px;
  }
}
</style>

<style lang="less">
/* 树节点添加/设置下拉：图标+文案，hover 灰色背景；弹层在 body 故不加 scoped */
.node-add-menu,
.node-settings-menu {
  .tiny-dropdown-item {
    .menu-item-content {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
    }
    .menu-icon {
      flex-shrink: 0;
      width: 16px;
      height: 16px;
      color: #606266;
      svg {
        width: 16px;
        height: 16px;
      }
    }
    &:hover {
      background: #f5f5f5;
    }
  }
}

// 附件区域样式
.article-attachments-wrapper {
  flex-shrink: 0;
  position: sticky;
  top: 0;
  align-self: flex-start;
  max-height: calc(100vh - 200px);
  overflow-y: auto;
  z-index: 150;
  margin-left: 0;
  
  // 隐藏滚动条但保持滚动功能
  scrollbar-width: thin; // Firefox
  -ms-overflow-style: none; // IE/Edge
  
  &::-webkit-scrollbar {
    width: 6px; // Chrome/Safari/Opera
  }
  
  &::-webkit-scrollbar-track {
    background: transparent;
  }
  
  &::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0.2);
    border-radius: 3px;
    
    &:hover {
      background: rgba(0, 0, 0, 0.3);
    }
  }
}

.article-attachments {
  /* margin-top: 32px; */
  padding-top: 24px;
  border: 1px solid #e4e7ed;
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  /* box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05); */
  
  .attachments-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
  }
  
  .attachments-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 18px;
    font-weight: 600;
    color: #333;
    margin: 0;
    
    .attachment-icon {
      width: 20px;
      height: 20px;
      color: #7030a0;
    }
    
    .attachments-count {
      font-size: 14px;
      font-weight: normal;
      color: #666;
    }
  }
  
  .attachments-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 12px;
    
    @media (max-width: 768px) {
      grid-template-columns: 1fr;
    }
  }
  
  .attachment-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    background-color: #f8f9fa;
    border: 1px solid #e4e7ed;
    border-radius: 6px;
    transition: all 0.2s;
    
    &.attachment-previewable {
      cursor: pointer;
    }
    
    &:hover {
      background-color: #fff;
      border-color: #7030a0;
      box-shadow: 0 2px 8px rgba(112, 48, 160, 0.1);
    }
  }
  
  .attachment-icon-wrapper {
    flex-shrink: 0;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #fff;
    border-radius: 6px;
    border: 1px solid #e4e7ed;
  }
  
  .attachment-file-icon {
    font-size: 24px;
  }
  
  .attachment-info {
    flex: 1;
    min-width: 0;
  }
  
  .attachment-name {
    font-size: 14px;
    font-weight: 500;
    color: #333;
    margin-bottom: 4px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  
  .attachment-meta {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 12px;
    color: #666;
  }
  
  .attachment-size {
    color: #999;
  }
  
  .attachment-date {
    color: #999;
  }
  
  .attachment-actions {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .attachment-preview-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    color: #7030a0;
    background-color: #fff;
    border: 1px solid #e4e7ed;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
    padding: 0;
    
    svg {
      width: 16px;
      height: 16px;
    }
    
    &:hover {
      background-color: #7030a0;
      color: #fff;
      border-color: #7030a0;
    }
  }
  
  .attachment-download-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    color: #7030a0;
    background-color: #fff;
    border: 1px solid #e4e7ed;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
    text-decoration: none;
    
    svg {
      width: 16px;
      height: 16px;
    }
    
    &:hover {
      background-color: #7030a0;
      color: #fff;
      border-color: #7030a0;
    }
  }
  
  .attachment-delete-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    color: #f56c6c;
    background-color: #fff;
    border: 1px solid #e4e7ed;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
    padding: 0;
    
    svg {
      width: 16px;
      height: 16px;
    }
    
    &:hover {
      background-color: #f56c6c;
      color: #fff;
      border-color: #f56c6c;
    }
  }
  
  .attachments-empty {
    padding: 40px 20px;
    text-align: center;
    color: #999;
    
    p {
      margin: 0 0 16px 0;
      font-size: 14px;
    }
  }
}

// 附件预览弹窗全屏样式
:deep(.attachment-preview-dialog) {
  // 全屏显示
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  max-width: 100vw !important;
  max-height: 100vh !important;
  margin: 0 !important;
  padding: 0 !important;
  border-radius: 0 !important;
  
  // 对话框主体
  .tiny-dialog-box__wrapper {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    bottom: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    margin: 0 !important;
    padding: 0 !important;
  }
  
  // 对话框内容
  .tiny-dialog-box {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    bottom: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    margin: 0 !important;
    padding: 0 !important;
    border-radius: 0 !important;
    display: flex !important;
    flex-direction: column !important;
  }
  
  // 对话框头部
  .tiny-dialog-box__header {
    flex-shrink: 0;
    padding: 16px 24px;
    border-bottom: 1px solid #e4e7ed;
    background: #fff;
  }
  
  // 对话框主体内容
  .tiny-dialog-box__body {
    flex: 1;
    overflow: auto;
    padding: 0 !important;
    margin: 0 !important;
  }
  
  // 对话框底部（如果有）
  .tiny-dialog-box__footer {
    flex-shrink: 0;
    padding: 16px 24px;
    border-top: 1px solid #e4e7ed;
    background: #fff;
  }
  .tiny-dialog-box__wrapper {
    top: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height: 100vh !important;
    margin: 0 !important;
    padding: 0 !important;
  }
  
  .tiny-dialog-box {
    width: 100% !important;
    height: 100vh !important;
    max-width: 100% !important;
    max-height: 100vh !important;
    margin: 0 !important;
    top: 0 !important;
    left: 0 !important;
    border-radius: 0 !important;
  }
  
  .tiny-dialog-box__header {
    padding: 16px 20px;
    border-bottom: 1px solid #e4e7ed;
  }
  
  .tiny-dialog-box__body {
    height: calc(100vh - 60px) !important;
    padding: 0 !important;
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }
  
  .tiny-dialog-box__footer {
    display: none;
  }
}

// 附件预览布局
.attachment-preview-layout {
  display: flex;
  height: 100%;
  width: 100%;
  overflow: hidden;
}

// 左侧附件列表
.attachment-preview-sidebar {
  width: 320px;
  flex-shrink: 0;
  background: #f8f9fa;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  
  .sidebar-header {
    flex-shrink: 0;
    padding: 16px;
    border-bottom: 1px solid #e4e7ed;
    background: #fff;
    
    .sidebar-title {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 16px;
      font-weight: 600;
      color: #333;
      margin: 0;
      
      .sidebar-icon {
        width: 20px;
        height: 20px;
        color: #7030a0;
      }
      
      .attachments-count {
        font-size: 14px;
        font-weight: normal;
        color: #666;
      }
    }
  }
  
  .sidebar-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    padding: 8px;
  }
  
  .sidebar-content-scrollable {
    flex: 1;
    overflow-y: auto;
    min-height: 0;
    
    // 自定义滚动条
    scrollbar-width: thin;
    -ms-overflow-style: none;
    
    &::-webkit-scrollbar {
      width: 6px;
    }
    
    &::-webkit-scrollbar-track {
      background: transparent;
    }
    
    &::-webkit-scrollbar-thumb {
      background: rgba(0, 0, 0, 0.2);
      border-radius: 3px;
      
      &:hover {
        background: rgba(0, 0, 0, 0.3);
      }
    }
  }
  
  .empty-attachments {
    padding: 40px 20px;
    text-align: center;
    color: #999;
    font-size: 14px;
  }
  
  .attachment-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
    flex: 1;
    min-height: 0;
    overflow-y: auto;
  }
  
  .sidebar-upload-section {
    flex-shrink: 0;
    padding: 12px 8px;
    border-top: 1px solid #e4e7ed;
    background: #fff;
    
    .upload-divider {
      height: 1px;
      background: #e4e7ed;
      margin-bottom: 12px;
    }
    
    .upload-area {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    
    .upload-attachment-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      width: 100%;
      padding: 10px 12px;
      background: #7030a0;
      color: #fff;
      border: none;
      border-radius: 6px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;
      
      &:hover:not(:disabled) {
        background: #5a2580;
      }
      
      &:disabled {
        background: #ccc;
        cursor: not-allowed;
        opacity: 0.6;
      }
      
      .upload-btn-icon {
        width: 16px;
        height: 16px;
      }
    }
    
    .upload-status {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 8px;
      font-size: 12px;
      color: #666;
    }
  }
  
  .attachment-list-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px;
    background: #fff;
    border: 1px solid #e4e7ed;
    border-radius: 6px;
    transition: all 0.2s;
    
    &:hover {
      background: #f5f7fa;
      border-color: #7030a0;
    }
    
    &.active {
      background: rgba(112, 48, 160, 0.1);
      border-color: #7030a0;
      
      .attachment-item-name {
        color: #7030a0;
        font-weight: 600;
      }
    }
    
    .attachment-item-main {
      flex: 1;
      display: flex;
      align-items: center;
      gap: 12px;
      cursor: pointer;
      min-width: 0;
    }
    
    .attachment-item-icon {
      flex-shrink: 0;
      width: 36px;
      height: 36px;
      display: flex;
      align-items: center;
      justify-content: center;
      background: #f8f9fa;
      border-radius: 6px;
      border: 1px solid #e4e7ed;
      
      .attachment-file-icon {
        font-size: 20px;
      }
    }
    
    .attachment-item-info {
      flex: 1;
      min-width: 0;
    }
    
    .attachment-item-name {
      font-size: 14px;
      font-weight: 500;
      color: #333;
      margin-bottom: 4px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    
    .attachment-item-meta {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      color: #666;
    }
    
    .attachment-item-size {
      color: #999;
    }
    
    .attachment-item-actions {
      display: flex;
      align-items: center;
      gap: 4px;
      flex-shrink: 0;
    }
    
    .attachment-action-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 28px;
      height: 28px;
      padding: 0;
      border: none;
      background: transparent;
      border-radius: 4px;
      cursor: pointer;
      color: #666;
      transition: all 0.2s;
      
      &:hover {
        background: #f0f0f0;
        color: #7030a0;
      }
      
      svg {
        width: 16px;
        height: 16px;
      }
    }
  }
}

// 右侧预览内容
.attachment-preview-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #fff;
  
  .office-preview-wrapper {
    position: relative;
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    width: 100%;
    height: 100%;
    min-height: calc(100vh - 120px);
  }

  .excel-preview-wrapper {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    width: 100%;
    height: 100%;
    min-height: calc(100vh - 120px);
    position: relative;

    :deep(.vue-office-excel) {
      flex: 1;
      width: 100%;
      height: 100%;
      overflow: auto;
    }

    :deep(.excel-container) {
      width: 100% !important;
      height: 100% !important;
    }
  }

  .image-preview-container {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    overflow: auto;
    
    :deep(.tiny-image) {
      max-width: 100%;
      max-height: 100%;
    }
    
    :deep(.tiny-image__inner) {
      max-width: 100%;
      max-height: 100%;
    }
    
    :deep(img) {
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
    }
  }
  
  .video-preview-container {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    background: linear-gradient(135deg, #000000 0%, #333333 50%, #ffffff 100%);
    
    video {
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
    }
  }
}

// 图片预览弹窗样式
.image-preview-dialog {
  .image-preview-content {
    width: 100%;
    height: calc(90vh - 100px);
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
    
    :deep(.tiny-image) {
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    :deep(.tiny-image__inner) {
      width: 100%;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    :deep(img) {
      max-width: 100%;
      max-height: 100%;
      object-fit: contain;
    }
  }
  
  .no-preview-selected {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #999;
    
    .empty-icon {
      width: 64px;
      height: 64px;
      margin-bottom: 16px;
      opacity: 0.5;
    }
    
    p {
      font-size: 16px;
      margin: 0;
    }
  }
}

// 文章权限设置样式
.member-management {
  .member-modal-tabs {
    margin-bottom: 16px;
  }

  .member-tab-panel {
    padding-top: 12px;
  }

  .member-role-batch {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .member-role-filter-label {
    font-size: 12px;
    color: var(--text-color-secondary, #909399);
  }

  .member-batch-role-label {
    margin-top: 4px;
  }

  .member-batch-confirm-btn {
    margin-top: 8px;
    align-self: flex-start;
  }

  .member-role-batch-remove .member-batch-remove-btn {
    margin-top: 8px;
    align-self: flex-start;
  }

  .member-role-batch-hint {
    min-height: 120px;
    padding: 20px 16px;
    margin-bottom: 16px;
    border: 1px dashed var(--ti-base-border-color, #dcdfe6);
    border-radius: 8px;
    background: var(--ti-base-bg-color-2, rgba(139, 92, 246, 0.06));
    color: var(--text-color-secondary, #909399);
    font-size: 13px;
    line-height: 1.6;

    p {
      margin: 0;
    }
  }

  .member-search-section {
    margin-bottom: 20px;
  }

  .member-list {
    min-height: 200px;
    max-height: 400px;
    overflow-y: auto;
    margin-bottom: 16px;
  }

  .empty-members {
    text-align: center;
    padding: 40px 20px;
    color: #999;
  }

  .role-badge {
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 500;
    white-space: nowrap;
    display: inline-block;
    border: 1px solid transparent;

    &.role-readonly {
      background-color: #f5f5f5;
      color: #666666;
      border-color: #d9d9d9;
    }

    &.role-editor {
      background-color: #e6f4ff;
      color: #1677ff;
      border-color: #69b1ff;
    }

    &.role-admin {
      background-color: #fff7e6;
      color: #fa8c16;
      border-color: #ffc53d;
    }
  }

  .member-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px;
    border: 1px solid #e4e7ed;
    border-radius: 4px;
    margin-bottom: 8px;

    .member-info {
      display: flex;
      flex-direction: column;
      gap: 6px;
      flex: 1;

      .member-basic {
        display: flex;
        flex-direction: column;
        gap: 4px;
      }

      .member-name {
        font-weight: 500;
        color: #333;
        font-size: 14px;
      }

      .member-email {
        font-size: 12px;
        color: #999;
      }

      .member-meta {
        display: flex;
        align-items: center;
        gap: 12px;
        flex-wrap: wrap;
      }

      .member-role {
        display: inline-flex;
        align-items: center;
      }

      .member-joined {
        font-size: 12px;
        color: #666;
      }
    }

    .member-actions {
      display: flex;
      gap: 8px;
      align-items: center;
    }
  }

  .member-pager-wrap {
    display: flex;
    justify-content: center;
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid #e4e7ed;
  }
}

// 上传附件弹窗样式
.upload-attachment-dialog {
  padding: 0;
  height: 600px;
  display: flex;
  flex-direction: column;
  
  .upload-dialog-layout {
    display: flex;
    flex: 1;
    gap: 0;
    overflow: hidden;
    min-height: 0;
  }
  
  // 左侧附件列表
  .upload-dialog-sidebar {
    width: 350px;
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    border-right: 1px solid #e4e7ed;
    background: #f8f9fa;
    overflow: hidden;
    
    .sidebar-header {
      flex-shrink: 0;
      padding: 16px;
      border-bottom: 1px solid #e4e7ed;
      background: #fff;
    }
    
    .sidebar-content {
      flex: 1;
      overflow-y: auto;
      padding: 12px;
      min-height: 0;
      
      // 自定义滚动条
      scrollbar-width: thin;
      -ms-overflow-style: none;
      
      &::-webkit-scrollbar {
        width: 6px;
      }
      
      &::-webkit-scrollbar-track {
        background: transparent;
      }
      
      &::-webkit-scrollbar-thumb {
        background: rgba(0, 0, 0, 0.2);
        border-radius: 3px;
        
        &:hover {
          background: rgba(0, 0, 0, 0.3);
        }
      }
    }
    
    .empty-attachments {
      padding: 40px 20px;
      text-align: center;
      color: #999;
      font-size: 14px;
    }
  }
  
  // 右侧上传区域
  .upload-dialog-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    padding: 20px;
    overflow-y: auto;
    min-height: 0;
  }
  
  .section-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 16px;
    font-weight: 600;
    color: #333;
    margin: 0 0 16px 0;
    
    .section-icon {
      width: 20px;
      height: 20px;
      color: #7030a0;
    }
    
    .attachments-count {
      font-size: 14px;
      font-weight: normal;
      color: #666;
    }
  }
  
  .existing-attachments-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  .existing-attachment-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 12px;
    background-color: #fff;
    border: 1px solid #e4e7ed;
    border-radius: 6px;
    transition: all 0.2s;
    gap: 8px;
    
    &:hover {
      border-color: #7030a0;
      box-shadow: 0 2px 8px rgba(112, 48, 160, 0.1);
    }
    
    .attachment-item-info {
      display: flex;
      align-items: center;
      gap: 12px;
      flex: 1;
      min-width: 0;
    }
    
    .attachment-icon {
      font-size: 20px;
      flex-shrink: 0;
    }
    
    .attachment-details {
      flex: 1;
      min-width: 0;
    }
    
    .attachment-name {
      font-size: 14px;
      font-weight: 500;
      color: #333;
      margin-bottom: 4px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    
    .attachment-meta {
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 12px;
      color: #999;
    }
    
    .attachment-item-actions {
      display: flex;
      align-items: center;
      gap: 6px;
      flex-shrink: 0;
    }
    
    .attachment-preview-btn-small,
    .attachment-download-btn-small,
    .attachment-delete-btn-small {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 28px;
      height: 28px;
      border: 1px solid #e4e7ed;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.2s;
      padding: 0;
      background-color: #fff;
      
      svg {
        width: 14px;
        height: 14px;
      }
      
      &:hover {
        border-color: #7030a0;
      }
    }
    
    .attachment-preview-btn-small {
      color: #7030a0;
      
      &:hover {
        background-color: #7030a0;
        color: #fff;
      }
    }
    
    .attachment-download-btn-small {
      color: #7030a0;
      text-decoration: none;
      
      &:hover {
        background-color: #7030a0;
        color: #fff;
      }
    }
    
    .attachment-delete-btn-small {
      color: #f56c6c;
      
      &:hover {
        background-color: #f56c6c;
        color: #fff;
        border-color: #f56c6c;
      }
    }
  }
  
  .section-divider {
    height: 1px;
    background-color: #e4e7ed;
    margin: 24px 0;
  }
  
  .upload-section {
    margin-top: 24px;
  }
  
  .upload-dropzone {
    border: 2px dashed #d3d4d6;
    border-radius: 8px;
    padding: 40px 20px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s;
    background-color: #fafafa;
    margin-bottom: 20px;
    
    &:hover {
      border-color: #7030a0;
      background-color: #f5f0ff;
    }
    
    .dropzone-content {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 12px;
    }
    
    .upload-icon {
      width: 48px;
      height: 48px;
      color: #7030a0;
      margin-bottom: 8px;
    }
    
    .dropzone-text {
      margin: 0;
      font-size: 16px;
      font-weight: 500;
      color: #333;
    }
    
    .dropzone-hint {
      margin: 0;
      font-size: 12px;
      color: #999;
    }
  }
  
  .upload-file-list {
    max-height: 400px;
    overflow-y: auto;
    border: 1px solid #e4e7ed;
    border-radius: 6px;
    padding: 12px;
    background-color: #fafafa;
  }
  
  .upload-file-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px;
    background-color: #fff;
    border: 1px solid #e4e7ed;
    border-radius: 6px;
    margin-bottom: 8px;
    transition: all 0.2s;
    
    &:last-child {
      margin-bottom: 0;
    }
    
    &:hover {
      border-color: #7030a0;
      box-shadow: 0 2px 8px rgba(112, 48, 160, 0.1);
    }
    
    .file-item-info {
      display: flex;
      align-items: flex-start;
      gap: 12px;
      flex: 1;
      min-width: 0;
    }
    
    .file-icon {
      font-size: 24px;
      flex-shrink: 0;
    }
    
    .file-details {
      flex: 1;
      min-width: 0;
    }
    
    .file-name {
      font-size: 14px;
      font-weight: 500;
      color: #333;
      margin-bottom: 6px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    
    .file-meta {
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 12px;
      color: #666;
      margin-bottom: 8px;
    }
    
    .file-size {
      color: #999;
    }
    
    .upload-status {
      font-size: 12px;
      
      &.uploading {
        color: #7030a0;
      }
      
      &.success {
        color: #67c23a;
      }
    }
    
    .upload-progress-bar {
      width: 100%;
      height: 4px;
      background-color: #e4e7ed;
      border-radius: 2px;
      overflow: hidden;
      margin-top: 8px;
    }
    
    .upload-progress-fill {
      height: 100%;
      background: linear-gradient(90deg, #7030a0 0%, #9d7ce8 100%);
      border-radius: 2px;
      transition: width 0.3s ease;
    }
    
    .file-remove-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 28px;
      height: 28px;
      color: #f56c6c;
      background-color: #fff;
      border: 1px solid #e4e7ed;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.2s;
      padding: 0;
      flex-shrink: 0;
      
      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
      
      svg {
        width: 14px;
        height: 14px;
      }
      
      &:hover:not(:disabled) {
        background-color: #f56c6c;
        color: #fff;
        border-color: #f56c6c;
      }
    }
  }
}
</style>
