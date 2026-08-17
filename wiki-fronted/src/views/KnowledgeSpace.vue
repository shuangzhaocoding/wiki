<template>
  <div class="knowledge-space-page">
        <div class="content-header">
          <div class="header-left">
            <h1 class="content-title">{{ translate('knowledge.knowledgeSpace') }}</h1>
          </div>
          <div class="header-actions">
            <!-- 搜索框 -->
            <tiny-input
              v-model="searchKeyword"
              :placeholder="translate('knowledgeBase.searchPlaceholder')"
              clearable
              @input="handleSearch"
              @keyup.enter="handleSearch"
              class="search-input"
            >
              <template #prefix>
                <component :is="TinyIconSearch" class="search-icon" />
              </template>
            </tiny-input>
            <!-- 视图切换按钮 -->
            <tiny-button 
              :plain="viewMode === 'table'"
              @click="handleViewModeChange"
              :title="viewMode === 'card' ? translate('knowledgeBase.switchToTable') : translate('knowledgeBase.switchToCard')"
            >
              <component v-if="viewMode === 'card'" :is="TinyIconTable" style="margin-right: 4px;" />
              <svg v-else viewBox="0 0 1024 1024" width="16" height="16" fill="currentColor" style="margin-right: 4px; display: inline-block; vertical-align: middle;">
                <path d="M128 128h256v256H128V128zm0 320h256v256H128V448zm0 320h256v256H128V768zm320-640h448v256H448V128zm0 320h448v256H448V448zm0 320h448v256H448V768z"/>
              </svg>
              {{ viewMode === 'card' ? translate('knowledgeBase.tableView') : translate('knowledgeBase.cardView') }}
            </tiny-button>
            <tiny-button type="primary" @click="showCreateModal = true">
              {{ translate('knowledgeBase.create') }}
            </tiny-button>
          </div>
        </div>

        <!-- 筛选 Tab -->
        <div class="filter-section">
          <tiny-tabs v-model="activeFilter" @click="handleFilterChange">
            <tiny-tab-item :key="'all'" :title="translate('knowledgeBase.filter.all')" name="all"></tiny-tab-item>
            <tiny-tab-item :key="'created'" :title="translate('knowledgeBase.filter.created')" name="created"></tiny-tab-item>
            <tiny-tab-item :key="'joined'" :title="translate('knowledgeBase.filter.joined')" name="joined"></tiny-tab-item>
            <tiny-tab-item :key="'invited'" :title="translate('knowledgeBase.filter.invited')" name="invited"></tiny-tab-item>
          </tiny-tabs>
        </div>

        <!-- 知识库列表 -->
        <div class="knowledge-base-list" :class="{ 'is-table-view': viewMode === 'table' }">
          <div v-if="loading" class="loading-wrapper">
            <LoadingSpinner :absolute="false" />
          </div>
          <div v-if="listTotal === 0 && !loading" class="empty-state">
            <p>{{ translate('knowledgeBase.empty') }}</p>
          </div>
          <!-- 卡片视图 -->
          <template v-else-if="viewMode === 'card'">
            <div
              v-for="kb in knowledgeBases"
              :key="kb.id"
              class="knowledge-base-card"
              @click="goToArticleManagement(kb.id)"
            >
              <div class="card-body">
                <div class="card-top">
                  <div class="card-icon" aria-hidden="true">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75">
                      <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
                      <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
                      <path d="M8 7h8M8 11h6" />
                    </svg>
                  </div>
                  <div class="card-head-main">
                    <h3 class="card-title" :title="kb.name">{{ kb.name }}</h3>
                    <div class="card-badges">
                      <span class="visibility-badge" :class="getVisibilityClass(kb.visibility)">
                        {{ getVisibilityText(kb.visibility) }}
                      </span>
                      <span
                        v-if="kb.my_role !== undefined && kb.my_role !== null"
                        class="role-badge"
                        :class="getRoleClass(kb.my_role)"
                      >
                        {{ getRoleText(kb.my_role) }}
                      </span>
                    </div>
                  </div>
                </div>

                <ul v-if="kb.team_space_name || kb.owner_name || kb.created_at" class="card-meta">
                  <li v-if="kb.team_space_name" class="card-meta-item">
                    <span class="meta-label">{{ translate('knowledgeBase.teamSpace') }}</span>
                    <span
                      v-if="kb.team_space_id"
                      class="meta-value meta-link"
                      @click.stop="goToTeamSpace(kb.team_space_name)"
                    >{{ kb.team_space_name }}</span>
                    <span v-else class="meta-value">{{ kb.team_space_name }}</span>
                  </li>
                  <li v-if="kb.owner_name" class="card-meta-item">
                    <span class="meta-label">{{ translate('knowledgeBase.owner') }}</span>
                    <span class="meta-value" :title="kb.owner_name">{{ kb.owner_name }}</span>
                  </li>
                  <li v-if="kb.created_at" class="card-meta-item">
                    <span class="meta-label">{{ translate('knowledgeBase.createdAt') }}</span>
                    <span class="meta-value">{{ formatCardDate(kb.created_at) }}</span>
                  </li>
                </ul>
              </div>

              <div class="card-footer" @click.stop>
                <div class="card-actions">
                  <button type="button" class="card-action-chip" @click="handleViewKB(kb)">
                    {{ translate('knowledgeBase.view') }}
                  </button>
                  <button type="button" class="card-action-chip" @click="handleEditKB(kb)">
                    {{ translate('knowledgeBase.edit') }}
                  </button>
                  <tiny-dropdown trigger="click" placement="bottom-end">
                    <template #default>
                      <button
                        type="button"
                        class="card-action-chip card-action-more"
                        :title="translate('knowledgeBase.moreActions')"
                      >
                        ···
                      </button>
                    </template>
                    <template #dropdown>
                      <tiny-dropdown-menu>
                        <tiny-dropdown-item @click="handleManageMembers(kb)">
                          {{ translate('knowledgeBase.manageMembers') }}
                        </tiny-dropdown-item>
                        <tiny-dropdown-item @click="openTagManage(kb)">
                          {{ translate('knowledgeBase.tagManage') }}
                        </tiny-dropdown-item>
                        <tiny-dropdown-item @click="handleApplyPermission(kb)">
                          {{ translate('knowledgeBase.applyPermission') }}
                        </tiny-dropdown-item>
                        <tiny-dropdown-item @click="showPermissionModal = true">
                          {{ translate('knowledgeBase.permissionManage') }}
                        </tiny-dropdown-item>
                        <tiny-dropdown-item class="table-dropdown-item-danger" @click="handleDeleteKB(kb)">
                          {{ translate('knowledgeBase.delete') }}
                        </tiny-dropdown-item>
                      </tiny-dropdown-menu>
                    </template>
                  </tiny-dropdown>
                </div>
              </div>
            </div>
          </template>
          <!-- 表格视图 -->
          <div v-else-if="viewMode === 'table'" class="table-view">
            <tiny-grid
              :data="knowledgeBases"
              :loading="loading"
              border
              highlight-hover-row
              width="100%"
              class="knowledge-base-grid"
              show-header
            >
              <tiny-grid-column field="name" :title="translate('knowledgeBase.name')" :label="translate('knowledgeBase.name')" min-width="140" align="left">
                <template #default="{ row }">
                  <span class="table-name-link" @click.stop="goToArticleManagement(row.id)">{{ row.name }}</span>
                </template>
              </tiny-grid-column>
              <tiny-grid-column  field="team_space_name" :title="translate('knowledgeBase.teamSpace')" :label="translate('knowledgeBase.teamSpace')" min-width="140" align="left" show-overflow="tooltip">
                <template #default="{ row }">
                  <span v-if="row.team_space_name && row.team_space_id" class="table-team-space-link" @click.stop="goToTeamSpace(row.team_space_name)">
                    {{ row.team_space_name }}
                  </span>
                  <span v-else>—</span>
                </template>
              </tiny-grid-column>
              <tiny-grid-column field="description" :title="translate('knowledgeBase.description')" :label="translate('knowledgeBase.description')" min-width="180" show-overflow="tooltip" align="left"></tiny-grid-column>
              <tiny-grid-column field="visibility" :title="translate('knowledgeBase.visibility')" :label="translate('knowledgeBase.visibility')" width="100" align="center">
                <template #default="{ row }">
                  <span class="visibility-badge" :class="getVisibilityClass(row.visibility)">
                    {{ getVisibilityText(row.visibility) }}
                  </span>
                </template>
              </tiny-grid-column>
              <tiny-grid-column field="my_role" :title="translate('knowledgeBase.myRole')" :label="translate('knowledgeBase.myRole')" width="100" align="center">
                <template #default="{ row }">
                  <span class="role-badge" :class="getRoleClass(row.my_role)">
                    {{ getRoleText(row.my_role) }}
                  </span>
                </template>
              </tiny-grid-column>
              <tiny-grid-column field="owner_name" :title="translate('knowledgeBase.owner')" :label="translate('knowledgeBase.owner')" width="120" align="left" show-overflow="tooltip">
                <template #default="{ row }">
                  {{ row.owner_name || '—' }}
                </template>
              </tiny-grid-column>
              <tiny-grid-column field="created_at" :title="translate('knowledgeBase.createdAt')" :label="translate('knowledgeBase.createdAt')" width="120" align="center">
                <template #default="{ row }">
                  {{ formatDate(row.created_at) }}
                </template>
              </tiny-grid-column>
              <tiny-grid-column :title="translate('knowledgeBase.actions')" :label="translate('knowledgeBase.actions')" width="240" min-width="200" align="center" fixed="right">
                <template #default="{ row }">
                  <div class="table-actions" @click.stop>
                    <button type="button" class="table-action-btn" @click="handleViewKB(row)">
                      {{ translate('knowledgeBase.view') }}
                    </button>
                    <button type="button" class="table-action-btn" @click="handleEditKB(row)">
                      {{ translate('knowledgeBase.edit') }}
                    </button>
                    <tiny-dropdown trigger="click" placement="bottom-end">
                      <template #default>
                        <button type="button" class="table-action-btn table-action-more" :title="translate('knowledgeBase.moreActions')">
                          ···
                        </button>
                      </template>
                      <template #dropdown>
                        <tiny-dropdown-menu>
                          <tiny-dropdown-item @click="handleManageMembers(row)">
                            {{ translate('knowledgeBase.manageMembers') }}
                          </tiny-dropdown-item>
                          <tiny-dropdown-item @click="openTagManage(row)">
                            {{ translate('knowledgeBase.tagManage') }}
                          </tiny-dropdown-item>
                          <tiny-dropdown-item @click="handleApplyPermission(row)">
                            {{ translate('knowledgeBase.applyPermission') }}
                          </tiny-dropdown-item>
                          <tiny-dropdown-item @click="showPermissionModal = true">
                            {{ translate('knowledgeBase.permissionManage') }}
                          </tiny-dropdown-item>
                          <tiny-dropdown-item class="table-dropdown-item-danger" @click="handleDeleteKB(row)">
                            {{ translate('knowledgeBase.delete') }}
                          </tiny-dropdown-item>
                        </tiny-dropdown-menu>
                      </template>
                    </tiny-dropdown>
                  </div>
                </template>
              </tiny-grid-column>
            </tiny-grid>
          </div>
          <div v-if="!loading && listTotal > 0" class="knowledge-list-pager-wrap">
            <tiny-pager
              :current-page="listCurrentPage"
              :page-size="listPageSize"
              :total="listTotal"
              :page-sizes="[10, 20, 30, 40, 50]"
              layout="total, sizes, prev, pager, next"
              :hide-on-single-page="true"
              @page-change="onListPageChange"
              @size-change="onListSizeChange"
            />
          </div>
        </div>

    <!-- 申请权限弹窗 -->
    <tiny-dialog-box
      v-model:visible="showApplyModal"
      :title="translate('knowledgeBase.applyPermission')"
      width="500px"
      @close="handleApplyModalClose"
    >
      <tiny-form
        ref="applyFormRef"
        :model="applyForm"
        label-width="100px"
      >
        <tiny-form-item :label="translate('article.applyRoleLabel')">
          <tiny-select
            v-model="applyForm.role"
            :placeholder="translate('article.applyRolePlaceholder')"
            style="width: 100%;"
          >
            <tiny-option
              v-for="option in applyRoleOptions"
              :key="option.value"
              :label="translate(option.labelKey)"
              :value="option.value"
            />
          </tiny-select>
        </tiny-form-item>
        <tiny-form-item :label="translate('article.applyReviewersLabel')">
          <tiny-select
            v-model="applyForm.reviewer_ids"
            multiple
            :placeholder="translate('article.applyReviewersPlaceholder')"
            style="width: 100%;"
            :disabled="adminsLoading || admins.length === 0"
          >
            <tiny-option
              v-for="admin in admins"
              :key="admin.id"
              :label="admin.username"
              :value="admin.id"
            />
          </tiny-select>
          <p v-if="admins.length === 0 && !adminsLoading" style="margin-top: 8px; color: var(--text-color-secondary, #909399); font-size: 12px;">
            {{ translate('article.noAdminsForReview') }}
          </p>
        </tiny-form-item>
        <tiny-form-item :label="translate('article.remarkLabel')">
          <tiny-input
            v-model="applyForm.message"
            type="textarea"
            :rows="4"
            :placeholder="translate('article.applyEditRemarkPlaceholder')"
          />
        </tiny-form-item>
      </tiny-form>
      <template #footer>
        <tiny-button @click="showApplyModal = false">
          {{ translate('common.cancel') }}
        </tiny-button>
        <tiny-button type="primary" :loading="applySubmitting" @click="handleSubmitApply">
          {{ translate('article.submitApplyEdit') }}
        </tiny-button>
      </template>
    </tiny-dialog-box>

    <!-- 创建知识库弹窗 -->
    <tiny-dialog-box
      v-model:visible="showCreateModal"
      :title="translate('knowledgeBase.create')"
      width="500px"
    >
      <tiny-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="100px"
      >
        <tiny-form-item 
          v-if="!teamSpaceId" 
          :label="translate('knowledgeBase.teamSpace')" 
          prop="team_space_id"
        >
          <tiny-select 
            v-model="createForm.team_space_id" 
            :placeholder="translate('knowledgeBase.teamSpacePlaceholder')"
          >
            <tiny-option 
              v-for="space in teamSpaces" 
              :key="space.id" 
              :label="space.name" 
              :value="space.id" 
            />
          </tiny-select>
        </tiny-form-item>
        <tiny-form-item :label="translate('knowledgeBase.name')" prop="name">
          <tiny-input
            v-model="createForm.name"
            :placeholder="translate('knowledgeBase.namePlaceholder')"
          />
        </tiny-form-item>
        <tiny-form-item :label="translate('knowledgeBase.description')" prop="description">
          <tiny-input
            v-model="createForm.description"
            type="textarea"
            :rows="4"
            :placeholder="translate('knowledgeBase.descriptionPlaceholder')"
          />
        </tiny-form-item>
        <tiny-form-item :label="translate('knowledgeBase.visibility')" prop="visibility">
          <tiny-select v-model="createForm.visibility" :placeholder="translate('knowledgeBase.visibilityPlaceholder')">
            <tiny-option :label="translate('knowledgeBase.visibility.private')" :value="1" />
            <tiny-option :label="translate('knowledgeBase.visibility.member')" :value="2" />
            <tiny-option :label="translate('knowledgeBase.visibility.public')" :value="3" />
          </tiny-select>
        </tiny-form-item>
      </tiny-form>
      <template #footer>
        <tiny-button @click="handleCancelCreate">{{ translate('common.cancel') }}</tiny-button>
        <tiny-button type="primary" :loading="creating" @click="handleCreate">{{ translate('common.confirm') }}</tiny-button>
      </template>
    </tiny-dialog-box>

    <!-- 编辑知识库弹窗 -->
    <tiny-dialog-box
      v-model:visible="showEditModal"
      :title="translate('knowledgeBase.edit')"
      width="500px"
    >
      <tiny-form
        ref="editFormRef"
        :model="editForm"
        :rules="createRules"
        label-width="100px"
      >
        <tiny-form-item :label="translate('knowledgeBase.name')" prop="name">
          <tiny-input
            v-model="editForm.name"
            :placeholder="translate('knowledgeBase.namePlaceholder')"
          />
        </tiny-form-item>
        <tiny-form-item :label="translate('knowledgeBase.description')" prop="description">
          <tiny-input
            v-model="editForm.description"
            type="textarea"
            :rows="4"
            :placeholder="translate('knowledgeBase.descriptionPlaceholder')"
          />
        </tiny-form-item>
        <tiny-form-item :label="translate('knowledgeBase.visibility')" prop="visibility">
          <tiny-select v-model="editForm.visibility" :placeholder="translate('knowledgeBase.visibilityPlaceholder')">
            <tiny-option :label="translate('knowledgeBase.visibility.private')" :value="1" />
            <tiny-option :label="translate('knowledgeBase.visibility.member')" :value="2" />
            <tiny-option :label="translate('knowledgeBase.visibility.public')" :value="3" />
          </tiny-select>
        </tiny-form-item>
      </tiny-form>
      <template #footer>
        <tiny-button @click="showEditModal = false">{{ translate('common.cancel') }}</tiny-button>
        <tiny-button type="primary" :loading="updating" @click="handleUpdate">{{ translate('common.confirm') }}</tiny-button>
      </template>
    </tiny-dialog-box>

    <!-- 查看知识库详情弹窗 -->
    <tiny-dialog-box
      v-model:visible="showViewModal"
      :title="translate('knowledgeBase.view')"
      width="500px"
    >
      <div class="kb-detail" v-if="viewingKB">
        <div class="detail-item">
          <label class="detail-label">{{ translate('knowledgeBase.name') }}:</label>
          <span class="detail-value">{{ viewingKB.name }}</span>
        </div>
        <div class="detail-item">
          <label class="detail-label">{{ translate('knowledgeBase.description') }}:</label>
          <span class="detail-value">{{ viewingKB.description || '-' }}</span>
        </div>
        <div class="detail-item">
          <label class="detail-label">{{ translate('knowledgeBase.visibility') }}:</label>
          <span class="detail-value">
            <span class="visibility-badge" :class="getVisibilityClass(viewingKB.visibility)">
              {{ getVisibilityText(viewingKB.visibility) }}
            </span>
          </span>
        </div>
        <div class="detail-item">
          <label class="detail-label">{{ translate('knowledgeBase.myRole') }}:</label>
          <span class="detail-value">
            <span v-if="viewingKB.my_role !== undefined && viewingKB.my_role !== null" class="role-badge" :class="getRoleClass(viewingKB.my_role)">
              {{ getRoleText(viewingKB.my_role) }}
            </span>
            <span v-else>—</span>
          </span>
        </div>
        <div class="detail-item">
          <label class="detail-label">{{ translate('knowledgeBase.owner') }}:</label>
          <span class="detail-value">{{ viewingKB.owner_name || '—' }}</span>
        </div>
        <div v-if="viewingKB.created_at" class="detail-item">
          <label class="detail-label">{{ translate('knowledgeBase.createdAt') }}:</label>
          <span class="detail-value">{{ formatDate(viewingKB.created_at) }}</span>
        </div>
      </div>
      <template #footer>
        <tiny-button @click="showViewModal = false">{{ translate('common.close') }}</tiny-button>
      </template>
    </tiny-dialog-box>

    <!-- 权限说明弹窗 -->
    <tiny-dialog-box
      v-model:visible="showPermissionModal"
      :title="translate('knowledgeBase.permissionDialogTitle')"
      width="560px"
    >
      <div class="permission-dialog-content">
        <table class="permission-table">
          <thead>
            <tr>
              <th>{{ translate('knowledgeBase.permission.action') }}</th>
              <th>{{ translate('knowledgeBase.member.role.readonly') }}</th>
              <th>{{ translate('knowledgeBase.member.role.editor') }}</th>
              <th>{{ translate('knowledgeBase.member.role.admin') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>{{ translate('knowledgeBase.permission.viewKB') }}</td>
              <td><span class="perm-yes">✓</span></td>
              <td><span class="perm-yes">✓</span></td>
              <td><span class="perm-yes">✓</span></td>
            </tr>
            <tr>
              <td>{{ translate('knowledgeBase.permission.viewArticle') }}</td>
              <td><span class="perm-yes">✓</span></td>
              <td><span class="perm-yes">✓</span></td>
              <td><span class="perm-yes">✓</span></td>
            </tr>
            <tr>
              <td>{{ translate('knowledgeBase.permission.editKB') }}</td>
              <td><span class="perm-no">—</span></td>
              <td><span class="perm-yes">✓</span></td>
              <td><span class="perm-yes">✓</span></td>
            </tr>
            <tr>
              <td>{{ translate('knowledgeBase.permission.editArticle') }}</td>
              <td><span class="perm-no">—</span></td>
              <td><span class="perm-yes">✓</span></td>
              <td><span class="perm-yes">✓</span></td>
            </tr>
            <tr>
              <td>{{ translate('knowledgeBase.permission.deleteArticle') }}</td>
              <td><span class="perm-no">—</span></td>
              <td><span class="perm-yes">✓</span></td>
              <td><span class="perm-yes">✓</span></td>
            </tr>
            <tr>
              <td>{{ translate('knowledgeBase.manageMembers') }}</td>
              <td><span class="perm-no">—</span></td>
              <td><span class="perm-no">—</span></td>
              <td><span class="perm-yes">✓</span></td>
            </tr>
            <tr>
              <td>{{ translate('knowledgeBase.delete') }}</td>
              <td><span class="perm-no">—</span></td>
              <td><span class="perm-no">—</span></td>
              <td><span class="perm-yes">✓</span></td>
            </tr>
          </tbody>
        </table>
      </div>
      <template #footer>
        <tiny-button @click="showPermissionModal = false">{{ translate('common.close') }}</tiny-button>
      </template>
    </tiny-dialog-box>

    <!-- 权限设置弹窗 -->
    <tiny-dialog-box
      v-model:visible="showMemberModal"
      :title="translate('knowledgeBase.manageMembers')"
      width="700px"
      @update:visible="handleMemberModalClose"
      :close-on-click-modal="false"
    >
      <div class="member-management">
        <tiny-tabs v-model="memberActiveTab" class="member-modal-tabs">
          <tiny-tab-item :title="translate('teamSpace.member.tabByUser')" name="user">
            <div class="member-tab-panel">
              <tiny-input
                v-model="memberSearchKeyword"
                :placeholder="translate('knowledgeBase.member.searchPlaceholder')"
                clearable
                @input="handleMemberSearch"
                @keyup.enter="handleMemberSearch"
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
                v-model="memberFilterRoleIds"
                multiple
                filterable
                :placeholder="translate('teamSpace.member.filterRolePlaceholder')"
                style="width: 100%"
              >
                <tiny-option
                  v-for="role in memberFilterRoles"
                  :key="role.id"
                  :label="role.name"
                  :value="role.id"
                />
              </tiny-select>
              <span class="member-role-filter-label member-batch-role-label">{{ translate('knowledgeBase.member.unifiedKbRole') }}</span>
              <tiny-select
                v-model="memberBatchKbRole"
                :placeholder="translate('knowledgeBase.member.unifiedKbRole')"
                style="width: 100%"
              >
                <tiny-option :label="translate('knowledgeBase.member.role.readonly')" :value="0" />
                <tiny-option :label="translate('knowledgeBase.member.role.editor')" :value="1" />
                <tiny-option :label="translate('knowledgeBase.member.role.admin')" :value="2" />
              </tiny-select>
              <tiny-button
                type="primary"
                class="member-batch-confirm-btn"
                :loading="memberBatchAdding"
                :disabled="memberFilterRoleIds.length === 0"
                @click="handleConfirmKbBatchAddByRoles"
              >
                {{ translate('teamSpace.member.batchAddConfirm') }}
              </tiny-button>
            </div>
          </tiny-tab-item>
          <tiny-tab-item :title="translate('teamSpace.member.tabBatchRemove')" name="batchRemove">
            <div class="member-tab-panel member-role-batch member-role-batch-remove">
              <span class="member-role-filter-label">{{ translate('teamSpace.member.filterByRoles') }}</span>
              <tiny-select
                v-model="memberRemoveRoleIds"
                multiple
                filterable
                :placeholder="translate('teamSpace.member.filterRolePlaceholder')"
                style="width: 100%"
              >
                <tiny-option
                  v-for="role in memberFilterRoles"
                  :key="role.id"
                  :label="role.name"
                  :value="role.id"
                />
              </tiny-select>
              <tiny-button
                type="danger"
                plain
                class="member-batch-remove-btn"
                :loading="memberBatchRemoving"
                :disabled="memberRemoveRoleIds.length === 0"
                @click="handleConfirmKbBatchRemoveByRoles"
              >
                {{ translate('teamSpace.member.batchRemoveConfirm') }}
              </tiny-button>
            </div>
          </tiny-tab-item>
        </tiny-tabs>

        <template v-if="memberActiveTab === 'user'">
          <div class="member-list">
            <LoadingSpinner v-if="memberLoading" />
            <div v-else-if="memberUsers.length === 0" class="empty-members">
              {{ translate('knowledgeBase.member.empty') }}
            </div>
            <div v-else>
              <div v-for="user in memberUsers" :key="user.id" class="member-item">
                <div class="member-info">
                  <div class="member-basic">
                    <span class="member-name">{{ user.username || `User ${user.user_id ?? user.id}` }}</span>
                    <span v-if="user.email" class="member-email">{{ user.email }}</span>
                  </div>
                  <div v-if="user.is_member" class="member-meta">
                    <span v-if="user.role !== undefined && user.role !== null" class="member-role">
                      <span class="role-badge" :class="getRoleClass(user.role)">{{ getRoleText(user.role) }}</span>
                    </span>
                    <span v-if="user.joined_at" class="member-joined">
                      {{ translate('knowledgeBase.member.joinedAt') }}: {{ formatDate(user.joined_at) }}
                    </span>
                  </div>
                </div>
                <div v-if="user.is_member" class="member-actions">
                  <tiny-button size="small" type="danger" @click="handleRemoveMember(user)">
                    {{ translate('knowledgeBase.member.remove') }}
                  </tiny-button>
                  <tiny-dropdown trigger="click" placement="bottom-end" border :title="translate('knowledgeBase.member.changeTo')">
                    <template #dropdown>
                      <tiny-dropdown-menu>
                        <tiny-dropdown-item @click="handleChangeMemberRole(user, 0)">
                          {{ translate('knowledgeBase.member.role.readonly') }}
                        </tiny-dropdown-item>
                        <tiny-dropdown-item @click="handleChangeMemberRole(user, 1)">
                          {{ translate('knowledgeBase.member.role.editor') }}
                        </tiny-dropdown-item>
                        <tiny-dropdown-item @click="handleChangeMemberRole(user, 2)">
                          {{ translate('knowledgeBase.member.role.admin') }}
                        </tiny-dropdown-item>
                      </tiny-dropdown-menu>
                    </template>
                  </tiny-dropdown>
                </div>
                <div v-else class="member-actions">
                  <tiny-dropdown trigger="click" placement="bottom-end" border :title="translate('knowledgeBase.member.addAs')">
                    <template #dropdown>
                      <tiny-dropdown-menu>
                        <tiny-dropdown-item @click="handleAddMemberWithRole(user, 0)">
                          {{ translate('knowledgeBase.member.role.readonly') }}
                        </tiny-dropdown-item>
                        <tiny-dropdown-item @click="handleAddMemberWithRole(user, 1)">
                          {{ translate('knowledgeBase.member.role.editor') }}
                        </tiny-dropdown-item>
                        <tiny-dropdown-item @click="handleAddMemberWithRole(user, 2)">
                          {{ translate('knowledgeBase.member.role.admin') }}
                        </tiny-dropdown-item>
                      </tiny-dropdown-menu>
                    </template>
                  </tiny-dropdown>
                </div>
              </div>
            </div>
          </div>
          <div v-if="!memberLoading && memberUsers.length > 0" class="member-pager-wrap">
            <tiny-pager
              :current-page="memberCurrentPage"
              :page-size="memberPageSize"
              :total="memberTotal"
              :page-sizes="[10, 20, 50]"
              layout="total, sizes, prev, pager, next"
              :hide-on-single-page="true"
              @page-change="onMemberPageChange"
              @size-change="onMemberSizeChange"
            />
          </div>
        </template>
        <div v-else-if="memberActiveTab === 'role'" class="member-role-batch-hint">
          <p>{{ translate('teamSpace.member.batchAddByRoleHint') }}</p>
        </div>
        <div v-else class="member-role-batch-hint">
          <p>{{ translate('teamSpace.member.batchRemoveTabHint') }}</p>
        </div>
      </div>
    </tiny-dialog-box>

    <!-- 知识库标签管理 -->
    <tiny-dialog-box
      v-model:visible="showTagModal"
      :title="tagModalTitle"
      width="640px"
      class="kb-tag-manage-dialog"
      @close="handleTagModalClose"
    >
      <div class="kb-tag-manage">
        <div class="kb-tag-toolbar">
          <tiny-input
            v-model="tagKeyword"
            clearable
            :placeholder="translate('knowledgeBase.tagSearchPlaceholder')"
            class="kb-tag-search"
            @input="handleTagKeywordInput"
            @clear="fetchTagList"
          />
          <tiny-button :loading="tagLoading" @click="fetchTagList">
            {{ translate('common.refresh') }}
          </tiny-button>
        </div>
        <div v-if="canManageKbTags(tagManagingKb)" class="kb-tag-add-row">
          <tiny-input
            v-model="tagCreateName"
            :placeholder="translate('knowledgeBase.tagNamePlaceholder')"
            maxlength="50"
            show-word-limit
            class="kb-tag-add-name"
          />
          <tiny-input
            v-model="tagCreateColor"
            :placeholder="translate('knowledgeBase.tagColorPlaceholder')"
            maxlength="20"
            class="kb-tag-add-color"
          />
          <tiny-button type="primary" :loading="tagCreateSubmitting" @click="handleCreateTag">
            {{ translate('knowledgeBase.tagAddSubmit') }}
          </tiny-button>
        </div>
        <div class="kb-tag-list-wrap">
          <LoadingSpinner v-if="tagLoading" :absolute="false" />
          <p v-else-if="tagList.length === 0" class="kb-tag-empty">{{ translate('knowledgeBase.tagEmpty') }}</p>
          <ul v-else class="kb-tag-list">
            <li v-for="tag in tagList" :key="tag.id" class="kb-tag-row">
              <span
                class="kb-tag-swatch"
                :style="{ background: tag.color && /^#|rgb/i.test(tag.color) ? tag.color : (tag.color || '#c4b5fd') }"
                :title="tag.color || ''"
              />
              <span class="kb-tag-name">{{ tag.name }}</span>
              <div class="kb-tag-row-actions">
                <template v-if="canManageKbTags(tagManagingKb)">
                  <tiny-button size="small" @click="openEditTag(tag)">{{ translate('knowledgeBase.tagEdit') }}</tiny-button>
                  <tiny-button size="small" type="danger" plain @click="handleDeleteTag(tag)">{{ translate('knowledgeBase.tagDelete') }}</tiny-button>
                </template>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </tiny-dialog-box>

    <tiny-dialog-box
      v-model:visible="showTagEditModal"
      :title="translate('knowledgeBase.tagEditTitle')"
      width="480px"
      @close="resetTagEditForm"
    >
      <tiny-form label-width="88px">
        <tiny-form-item :label="translate('knowledgeBase.tagName')">
          <tiny-input v-model="tagEditForm.name" maxlength="50" show-word-limit />
        </tiny-form-item>
        <tiny-form-item :label="translate('knowledgeBase.tagColor')">
          <tiny-input v-model="tagEditForm.color" :placeholder="translate('knowledgeBase.tagColorPlaceholder')" maxlength="20" />
        </tiny-form-item>
      </tiny-form>
      <template #footer>
        <tiny-button @click="showTagEditModal = false">{{ translate('common.cancel') }}</tiny-button>
        <tiny-button type="primary" :loading="tagEditSaving" @click="submitTagEdit">{{ translate('common.save') }}</tiny-button>
      </template>
    </tiny-dialog-box>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Button as TinyButton, DialogBox as TinyDialogBox, Form as TinyForm, FormItem as TinyFormItem, Input as TinyInput, Select as TinySelect, Option as TinyOption, Grid as TinyGrid, GridColumn as TinyGridColumn, Dropdown as TinyDropdown, DropdownMenu as TinyDropdownMenu, DropdownItem as TinyDropdownItem, Pager as TinyPager, TinyTabs, TinyTabItem } from '@opentiny/vue'
import { IconSearch, IconListMode } from '@opentiny/vue-icon'
import {
  knowledgeBaseApi,
  type KnowledgeBase,
  type KnowledgeBaseMemberSearchItem,
  type KnowledgeBaseMemberSearchParams,
  type KnowledgeBaseFilterParams,
  type KnowledgeBaseListResponse,
  type KnowledgeBaseTag
} from '../api/knowledgeBase'
import { roleApi, type Role } from '../api/role'
import { teamSpaceApi, type TeamSpace } from '../api/teamSpace'
import { applicationApi, RESOURCE_TYPE as APPLICATION_RESOURCE_TYPE } from '../api/application'
import { permissionApi, type ResourceAdminItem } from '../api/permission'
import { t } from '../i18n'
import { Modal } from '@opentiny/vue'
import { useLocaleStore } from '../stores/locale'
// @ts-ignore
import LoadingSpinner from '../components/LoadingSpinner.vue'

const route = useRoute()
const router = useRouter()
const localeStore = useLocaleStore()

const TinyIconSearch = IconSearch()
const TinyIconTable = IconListMode()

// 视图模式本地缓存 key
const VIEW_MODE_STORAGE_KEY = 'knowledgeBase_viewMode'

// 从本地缓存读取视图模式
const loadViewModeFromStorage = (): 'card' | 'table' => {
  try {
    const saved = localStorage.getItem(VIEW_MODE_STORAGE_KEY)
    if (saved === 'card' || saved === 'table') {
      return saved
    }
  } catch (error) {
    console.warn('Failed to load view mode from storage:', error)
  }
  return 'card' // 默认值
}

// 保存视图模式到本地缓存
const saveViewModeToStorage = (mode: 'card' | 'table') => {
  try {
    localStorage.setItem(VIEW_MODE_STORAGE_KEY, mode)
  } catch (error) {
    console.warn('Failed to save view mode to storage:', error)
  }
}

// 视图模式
const viewMode = ref<'card' | 'table'>(loadViewModeFromStorage())

// 处理视图模式切换
const handleViewModeChange = () => {
  const newMode = viewMode.value === 'card' ? 'table' : 'card'
  viewMode.value = newMode
  saveViewModeToStorage(newMode)
}

// 获取团队空间ID（可选）
const getTeamSpaceIdFromRoute = (): number | null => {
  const id = route.params.teamSpaceId
  return id && !isNaN(Number(id)) ? Number(id) : null
}
const teamSpaceId = ref<number | null>(getTeamSpaceIdFromRoute())
const teamSpace = ref<TeamSpace | null>(null)
const teamSpaces = ref<TeamSpace[]>([]) // 用于创建时选择团队空间

// 数据
const loading = ref(false)
const knowledgeBases = ref<KnowledgeBase[]>([])
const listCurrentPage = ref(1)
const listPageSize = ref(10)
const listTotal = ref(0)

// 筛选相关
const activeFilter = ref<'all' | 'created' | 'joined'>('all')

// 搜索相关
const searchKeyword = ref('')
let searchTimer: ReturnType<typeof setTimeout> | null = null

// 处理筛选切换
const handleFilterChange = () => {
  listCurrentPage.value = 1
  fetchKnowledgeBases()
}

// 创建表单
const showCreateModal = ref(false)
const creating = ref(false)
const createFormRef = ref()
const createForm = ref({
  team_space_id: null as number | null,
  name: '',
  description: '',
  visibility: 3
})

// 编辑表单
const showEditModal = ref(false)
const updating = ref(false)
const editFormRef = ref()
const editingKBId = ref<number | null>(null)
const editForm = ref({
  name: '',
  description: '',
  visibility: 3
})

// 查看详情
const showViewModal = ref(false)
const viewingKB = ref<KnowledgeBase | null>(null)

// 申请权限
const showApplyModal = ref(false)
const applySubmitting = ref(false)
const applyFormRef = ref()
const applyingKBId = ref<number | null>(null)
const admins = ref<ResourceAdminItem[]>([])
const adminsLoading = ref(false)
const applyForm = ref({
  role: 1, // 默认编辑者
  reviewer_ids: [] as number[],
  message: ''
})
const applyRoleOptions = [
  { value: 0, labelKey: 'article.role.readonly' },
  { value: 1, labelKey: 'article.role.editor' },
  { value: 2, labelKey: 'article.role.admin' }
] as const

// 权限说明弹窗
const showPermissionModal = ref(false)

// 权限设置
const showMemberModal = ref(false)
const managingKBId = ref<number | null>(null)
const memberUsers = ref<KnowledgeBaseMemberSearchItem[]>([])
const memberLoading = ref(false)
const memberSearchKeyword = ref('')
const memberCurrentPage = ref(1)
const memberPageSize = ref(10)
const memberTotal = ref(0)
let memberSearchTimer: ReturnType<typeof setTimeout> | null = null

const memberActiveTab = ref<'user' | 'role' | 'batchRemove'>('user')
const memberFilterRoleIds = ref<number[]>([])
const memberRemoveRoleIds = ref<number[]>([])
const memberFilterRoles = ref<Role[]>([])
const memberBatchKbRole = ref(1)
const memberBatchAdding = ref(false)
const memberBatchRemoving = ref(false)

// 知识库标签（OpenAPI: GET/POST /knowledge-bases/{kb_id}/tags，GET/PUT/DELETE .../tags/{tag_id}）
const showTagModal = ref(false)
const tagManagingKb = ref<KnowledgeBase | null>(null)
const tagList = ref<KnowledgeBaseTag[]>([])
const tagLoading = ref(false)
const tagKeyword = ref('')
let tagSearchTimer: ReturnType<typeof setTimeout> | null = null
const tagCreateName = ref('')
const tagCreateColor = ref('')
const tagCreateSubmitting = ref(false)
const showTagEditModal = ref(false)
const tagEditSaving = ref(false)
const tagEditForm = ref({ id: 0, name: '', color: '' })

// 表单验证规则
const createRules = computed(() => ({
  team_space_id: teamSpaceId.value ? [] : [
    { required: true, message: () => translate('knowledgeBase.teamSpaceRequired'), trigger: 'change' }
  ],
  name: [
    { required: true, message: () => translate('knowledgeBase.nameRequired'), trigger: 'blur' }
  ]
}))

// 响应式翻译函数
const translate = (key: string, params?: Record<string, string>) => {
  void localeStore.localeKey
  return t(key, params)
}

/** 编辑者/管理员可增删改；只读仅可查看列表 */
const canManageKbTags = (kb: KnowledgeBase | null): boolean => {
  if (!kb) return false
  const r = kb.my_role
  if (r === undefined || r === null) return true
  return r >= 1
}

const tagModalTitle = computed(() => {
  void localeStore.localeKey
  const kb = tagManagingKb.value
  if (!kb) return translate('knowledgeBase.tagManage')
  return `${translate('knowledgeBase.tagManage')} — ${kb.name}`
})

const openTagManage = (kb: KnowledgeBase) => {
  tagManagingKb.value = kb
  tagKeyword.value = ''
  tagCreateName.value = ''
  tagCreateColor.value = ''
  showTagModal.value = true
  fetchTagList()
}

const handleTagModalClose = () => {
  tagManagingKb.value = null
  tagKeyword.value = ''
  tagList.value = []
}

const fetchTagList = async () => {
  const kb = tagManagingKb.value
  if (!kb) return
  try {
    tagLoading.value = true
    const kw = tagKeyword.value.trim()
    tagList.value = await knowledgeBaseApi.listKnowledgeBaseTags(kb.id, {
      keyword: kw || null
    })
  } catch (error: any) {
    Modal.message({
      message: error.message || translate('knowledgeBase.tagFetchError'),
      status: 'error'
    })
    tagList.value = []
  } finally {
    tagLoading.value = false
  }
}

const handleTagKeywordInput = () => {
  if (tagSearchTimer) clearTimeout(tagSearchTimer)
  tagSearchTimer = setTimeout(() => {
    fetchTagList()
  }, 400)
}

const handleCreateTag = async () => {
  const kb = tagManagingKb.value
  if (!kb || !canManageKbTags(kb)) return
  const name = tagCreateName.value.trim()
  if (!name) {
    Modal.message({
      message: translate('knowledgeBase.tagNameRequired'),
      status: 'warning'
    })
    return
  }
  try {
    tagCreateSubmitting.value = true
    const colorRaw = tagCreateColor.value.trim()
    await knowledgeBaseApi.createKnowledgeBaseTag(kb.id, {
      name,
      color: colorRaw ? colorRaw : null
    })
    Modal.message({
      message: translate('knowledgeBase.tagCreateSuccess'),
      status: 'success'
    })
    tagCreateName.value = ''
    tagCreateColor.value = ''
    await fetchTagList()
  } catch (error: any) {
    Modal.message({
      message: error.message || translate('knowledgeBase.tagCreateError'),
      status: 'error'
    })
  } finally {
    tagCreateSubmitting.value = false
  }
}

const openEditTag = (tag: KnowledgeBaseTag) => {
  tagEditForm.value = {
    id: tag.id,
    name: tag.name,
    color: tag.color ?? ''
  }
  showTagEditModal.value = true
}

const resetTagEditForm = () => {
  tagEditForm.value = { id: 0, name: '', color: '' }
}

const submitTagEdit = async () => {
  const kb = tagManagingKb.value
  if (!kb || !canManageKbTags(kb)) return
  const name = tagEditForm.value.name.trim()
  if (!name) {
    Modal.message({
      message: translate('knowledgeBase.tagNameRequired'),
      status: 'warning'
    })
    return
  }
  try {
    tagEditSaving.value = true
    const c = tagEditForm.value.color.trim()
    await knowledgeBaseApi.updateKnowledgeBaseTag(kb.id, tagEditForm.value.id, {
      name,
      color: c === '' ? '' : c
    })
    Modal.message({
      message: translate('knowledgeBase.tagUpdateSuccess'),
      status: 'success'
    })
    showTagEditModal.value = false
    resetTagEditForm()
    await fetchTagList()
  } catch (error: any) {
    Modal.message({
      message: error.message || translate('knowledgeBase.tagUpdateError'),
      status: 'error'
    })
  } finally {
    tagEditSaving.value = false
  }
}

const handleDeleteTag = (tag: KnowledgeBaseTag) => {
  const kb = tagManagingKb.value
  if (!kb || !canManageKbTags(kb)) return
  Modal.confirm({
    title: translate('knowledgeBase.tagDeleteConfirm'),
    message: translate('knowledgeBase.tagDeleteMessage', { name: tag.name }),
    status: 'warning'
  })
    .then((result: string) => {
      if (result === 'confirm') {
        void deleteTagExec(kb.id, tag.id)
      }
    })
    .catch(() => {})
}

const deleteTagExec = async (kbId: number, tagId: number) => {
  try {
    await knowledgeBaseApi.deleteKnowledgeBaseTag(kbId, tagId)
    Modal.message({
      message: translate('knowledgeBase.tagDeleteSuccess'),
      status: 'success'
    })
    await fetchTagList()
  } catch (error: any) {
    Modal.message({
      message: error.message || translate('knowledgeBase.tagDeleteError'),
      status: 'error'
    })
  }
}

// 获取团队空间列表（用于创建时选择）
const fetchTeamSpaces = async () => {
  try {
    const response = await teamSpaceApi.getTeamSpaces()
    // 处理不同的返回格式
    if (Array.isArray(response)) {
      // 如果直接返回数组
      teamSpaces.value = response
    } else if (response && typeof response === 'object' && 'items' in response) {
      // 如果返回对象，包含 items 字段
      teamSpaces.value = (response as { items: TeamSpace[] }).items || []
    } else if (response && typeof response === 'object' && 'data' in response) {
      // 如果返回对象，包含 data.items 字段（根据用户提供的返回值格式）
      const data = (response as { data: { items: TeamSpace[] } }).data
      teamSpaces.value = data?.items || []
    } else {
      teamSpaces.value = []
    }
  } catch (error: any) {
    console.error('获取团队空间列表失败:', error)
    teamSpaces.value = []
  }
}

// 获取团队空间信息
const fetchTeamSpace = async () => {
  if (!teamSpaceId.value) return
  try {
    const space = await teamSpaceApi.getTeamSpace(teamSpaceId.value)
    teamSpace.value = space
  } catch (error: any) {
    Modal.message({
      message: error.message || translate('teamSpace.viewError'),
      status: 'error'
    })
  }
}

// 获取知识库列表
const fetchKnowledgeBases = async () => {
  try {
    loading.value = true
    
    // 构建筛选参数
    const params: KnowledgeBaseFilterParams = {
      team_space_id: teamSpaceId.value
    }
    
    // 根据选中的筛选类型设置 filter_type 参数
    if (activeFilter.value !== 'all') {
      params.filter_type = activeFilter.value
    }
    
    // 如果有搜索关键词，设置 keyword 参数（所有tab都可以使用）
    if (searchKeyword.value.trim()) {
      params.keyword = searchKeyword.value.trim()
    }

    params.page = listCurrentPage.value
    params.page_size = listPageSize.value
    
    const response = await knowledgeBaseApi.getKnowledgeBases(params)
    
    // 处理响应：可能是数组或对象
    if (Array.isArray(response)) {
      knowledgeBases.value = response
      listTotal.value = response.length
    } else if (response && typeof response === 'object' && 'items' in response) {
      const listRes = response as KnowledgeBaseListResponse
      knowledgeBases.value = listRes.items || []
      listTotal.value = listRes.total ?? listRes.items?.length ?? 0
    } else {
      knowledgeBases.value = []
      listTotal.value = 0
    }

    const maxPage = Math.max(1, Math.ceil(listTotal.value / listPageSize.value))
    if (listCurrentPage.value > maxPage && listTotal.value > 0) {
      listCurrentPage.value = maxPage
      await fetchKnowledgeBases()
      return
    }
  } catch (error: any) {
    Modal.message({
      message: error.message || translate('knowledgeBase.fetchError'),
      status: 'error'
    })
    knowledgeBases.value = []
    listTotal.value = 0
  } finally {
    loading.value = false
  }
}

// 创建知识库
const handleCreate = async () => {
  if (!createFormRef.value) return
  
  await createFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      // 确定使用的团队空间ID
      const finalTeamSpaceId = teamSpaceId.value || createForm.value.team_space_id
      if (!finalTeamSpaceId) {
        Modal.message({
          message: translate('knowledgeBase.teamSpaceRequired'),
          status: 'error'
        })
        return
      }
      
      try {
        creating.value = true
        await knowledgeBaseApi.createKnowledgeBase({
          team_space_id: finalTeamSpaceId,
          name: createForm.value.name,
          description: createForm.value.description || null,
          visibility: createForm.value.visibility
        })
        Modal.message({
          message: translate('knowledgeBase.createSuccess'),
          status: 'success'
        })
        showCreateModal.value = false
        resetCreateForm()
        await fetchKnowledgeBases()
      } catch (error: any) {
        Modal.message({
          message: error.message || translate('knowledgeBase.createError'),
          status: 'error'
        })
      } finally {
        creating.value = false
      }
    }
  })
}

// 取消创建
const handleCancelCreate = () => {
  resetCreateForm()
  showCreateModal.value = false
}

// 重置创建表单
const resetCreateForm = () => {
  createForm.value = {
    team_space_id: teamSpaceId.value,
    name: '',
    description: '',
    visibility: 1
  }
  createFormRef.value?.resetFields()
}

// 查看知识库详情
const handleViewKB = async (kb: KnowledgeBase) => {
  try {
    const detail = await knowledgeBaseApi.getKnowledgeBase(kb.id)
    // 如果详情接口没有返回 owner_name 和 my_role，从列表数据中保留
    viewingKB.value = {
      ...detail,
      owner_name: detail.owner_name || kb.owner_name || null,
      my_role: detail.my_role !== undefined && detail.my_role !== null ? detail.my_role : (kb.my_role !== undefined && kb.my_role !== null ? kb.my_role : null)
    }
    showViewModal.value = true
  } catch (error: any) {
    Modal.message({
      message: error.message || translate('knowledgeBase.viewError'),
      status: 'error'
    })
  }
}

// 编辑知识库
const handleEditKB = (kb: KnowledgeBase) => {
  editingKBId.value = kb.id
  editForm.value = {
    name: kb.name,
    description: kb.description || '',
    visibility: kb.visibility
  }
  showEditModal.value = true
}

// 更新知识库
const handleUpdate = async () => {
  if (!editFormRef.value || !editingKBId.value) return
  
  await editFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      try {
        updating.value = true
        await knowledgeBaseApi.updateKnowledgeBase(editingKBId.value!, {
          name: editForm.value.name,
          description: editForm.value.description || null,
          visibility: editForm.value.visibility
        })
        Modal.message({
          message: translate('knowledgeBase.updateSuccess'),
          status: 'success'
        })
        showEditModal.value = false
        await fetchKnowledgeBases()
      } catch (error: any) {
        Modal.message({
          message: error.message || translate('knowledgeBase.updateError'),
          status: 'error'
        })
      } finally {
        updating.value = false
      }
    }
  })
}

// 删除知识库
const handleDeleteKB = (kb: KnowledgeBase) => {
  Modal.confirm({
    title: translate('knowledgeBase.deleteConfirm'),
    message: translate('knowledgeBase.deleteMessage', { name: kb.name }),
    status: 'warning'
  }).then((result: String) => {
    if (result === 'confirm') {
      deleteKB(kb.id)
    }
  }).catch(() => {
    // 用户取消
  })
}

const deleteKB = async (kbId: number) => {
  try {
    await knowledgeBaseApi.deleteKnowledgeBase(kbId)
    Modal.message({
      message: translate('knowledgeBase.deleteSuccess'),
      status: 'success'
    })
    await fetchKnowledgeBases()
  } catch (error: any) {
    Modal.message({
      message: error.message || translate('knowledgeBase.deleteError'),
      status: 'error'
    })
  }
}

// 处理搜索（防抖）
const handleSearch = () => {
  // 清除之前的定时器
  if (searchTimer) {
    clearTimeout(searchTimer)
  }
  // 防抖后发送API请求
  searchTimer = setTimeout(() => {
    listCurrentPage.value = 1
    fetchKnowledgeBases()
  }, 500)
}

const onListPageChange = (e: { currentPage: number; pageSize?: number }) => {
  listCurrentPage.value = e.currentPage
  if (e.pageSize !== undefined) {
    listPageSize.value = e.pageSize
  }
  fetchKnowledgeBases()
}

const onListSizeChange = (e: { currentPage: number; pageSize: number }) => {
  listPageSize.value = e.pageSize
  listCurrentPage.value = 1
  fetchKnowledgeBases()
}

// 获取可见性文本
const getVisibilityText = (visibility: number) => {
  if (visibility === 1) {
    return translate('knowledgeBase.visibility.private')
  } else if (visibility === 2) {
    return translate('knowledgeBase.visibility.member')
  } else if (visibility === 3) {
    return translate('knowledgeBase.visibility.public')
  } else {
    return translate('knowledgeBase.visibility.public')
  }
}

// 获取可见性样式类
const getVisibilityClass = (visibility: number) => {
  if (visibility === 1) {
    return 'private'
  } else if (visibility === 2) {
    return 'member'
  } else if (visibility === 3) {
    return 'public'
  } else {
    return 'public'
  }
}

const getDateLocale = () => {
  const localeMap: Record<string, string> = {
    zh: 'zh-CN',
    en: 'en-US',
    ko: 'ko-KR',
    de: 'de-DE',
    ja: 'ja-JP',
    fr: 'fr-FR'
  }
  return localeMap[localeStore.currentLocale] || 'zh-CN'
}

// 格式化日期
const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  try {
    return new Date(dateStr).toLocaleString(getDateLocale())
  } catch {
    return dateStr
  }
}

// 卡片展示用短日期
const formatCardDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  try {
    return new Date(dateStr).toLocaleDateString(getDateLocale())
  } catch {
    return dateStr
  }
}

// 获取角色文本：0-只读，1-编辑者，2-管理员
const getRoleText = (role?: number) => {
  if (role === undefined || role === null) {
    return '-'
  }
  if (role === 0) {
    return translate('knowledgeBase.member.role.readonly')
  } else if (role === 1) {
    return translate('knowledgeBase.member.role.editor')
  } else if (role === 2) {
    return translate('knowledgeBase.member.role.admin')
  }
  return '-'
}

// 获取角色样式类：0-只读，1-编辑者，2-管理员
const getRoleClass = (role?: number) => {
  if (role === undefined || role === null) {
    return ''
  }
  if (role === 0) {
    return 'role-readonly'
  } else if (role === 1) {
    return 'role-editor'
  } else if (role === 2) {
    return 'role-admin'
  }
  return ''
}

// 获取成员用户列表
const fetchMemberUsers = async () => {
  if (!managingKBId.value) return
  
  try {
    memberLoading.value = true
    
    const params: KnowledgeBaseMemberSearchParams = {
      knowledge_base_id: managingKBId.value,
      page: memberCurrentPage.value,
      page_size: memberPageSize.value
    }

    if (memberSearchKeyword.value.trim()) {
      params.keyword = memberSearchKeyword.value.trim()
    }

    const response = await knowledgeBaseApi.searchKnowledgeBaseMembers(params)
    memberUsers.value = response.items || []
    memberTotal.value = response.total || 0
  } catch (error: any) {
    Modal.message({
      message: error.message || translate('knowledgeBase.member.fetchError'),
      status: 'error'
    })
    memberUsers.value = []
    memberTotal.value = 0
  } finally {
    memberLoading.value = false
  }
}

const loadMemberFilterRoles = async () => {
  try {
    const res = await roleApi.getRoles({ page: 1, page_size: 100, status: 1 })
    memberFilterRoles.value = res.items || []
  } catch {
    memberFilterRoles.value = []
  }
}

// 管理成员
const handleManageMembers = async (kb: KnowledgeBase) => {
  managingKBId.value = kb.id
  memberActiveTab.value = 'user'
  memberSearchKeyword.value = ''
  memberFilterRoleIds.value = []
  memberRemoveRoleIds.value = []
  memberBatchKbRole.value = 1
  memberCurrentPage.value = 1
  memberPageSize.value = 10
  showMemberModal.value = true
  await loadMemberFilterRoles()
  await fetchMemberUsers()
}

watch(memberActiveTab, () => {
  if (!showMemberModal.value) return
  memberCurrentPage.value = 1
  if (memberActiveTab.value === 'user') {
    fetchMemberUsers()
  } else {
    memberUsers.value = []
    memberTotal.value = 0
  }
})

// 弹窗关闭处理
const handleMemberModalClose = (visible: boolean) => {
  if (!visible) {
    memberUsers.value = []
    memberActiveTab.value = 'user'
    memberSearchKeyword.value = ''
    memberFilterRoleIds.value = []
    memberRemoveRoleIds.value = []
    memberBatchKbRole.value = 1
    memberCurrentPage.value = 1
    memberTotal.value = 0
    if (memberSearchTimer) {
      clearTimeout(memberSearchTimer)
      memberSearchTimer = null
    }
  }
}

const handleConfirmKbBatchAddByRoles = async () => {
  if (!managingKBId.value) return
  if (memberFilterRoleIds.value.length === 0) {
    Modal.message({
      message: translate('teamSpace.member.batchAddSelectRolesFirst'),
      status: 'warning'
    })
    return
  }
  memberBatchAdding.value = true
  try {
    await knowledgeBaseApi.addKnowledgeBaseMember(managingKBId.value, {
      role_ids: [...memberFilterRoleIds.value],
      role: Number(memberBatchKbRole.value)
    })
    Modal.message({
      message: translate('teamSpace.member.batchAddSuccess'),
      status: 'success'
    })
    memberActiveTab.value = 'user'
    memberCurrentPage.value = 1
    await fetchMemberUsers()
  } catch (e: any) {
    Modal.message({
      message: e?.message || translate('teamSpace.member.batchAddError'),
      status: 'error'
    })
  } finally {
    memberBatchAdding.value = false
  }
}

const handleConfirmKbBatchRemoveByRoles = () => {
  if (!managingKBId.value) return
  if (memberRemoveRoleIds.value.length === 0) {
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
      memberBatchRemoving.value = true
      try {
        await knowledgeBaseApi.batchRemoveKnowledgeBaseMembers(managingKBId.value!, {
          role_ids: [...memberRemoveRoleIds.value]
        })
        Modal.message({
          message: translate('teamSpace.member.batchRemoveSuccess'),
          status: 'success'
        })
        memberActiveTab.value = 'user'
        memberCurrentPage.value = 1
        await fetchMemberUsers()
      } catch (e: any) {
        Modal.message({
          message: e?.message || translate('teamSpace.member.batchRemoveError'),
          status: 'error'
        })
      } finally {
        memberBatchRemoving.value = false
      }
    })
    .catch(() => {})
}

// 成员搜索（防抖）
const handleMemberSearch = () => {
  if (memberSearchTimer) {
    clearTimeout(memberSearchTimer)
  }
  
  memberSearchTimer = setTimeout(() => {
    memberCurrentPage.value = 1
    fetchMemberUsers()
  }, 500)
}

// 成员分页变化
const onMemberPageChange = (e: { currentPage: number; pageSize?: number }) => {
  memberCurrentPage.value = e.currentPage
  if (e.pageSize !== undefined) {
    memberPageSize.value = e.pageSize
  }
  fetchMemberUsers()
}

// 成员每页数量变化
const onMemberSizeChange = (e: { currentPage: number; pageSize: number }) => {
  memberPageSize.value = e.pageSize
  memberCurrentPage.value = 1
  fetchMemberUsers()
}

// 直接添加成员并设置角色（通过下拉菜单）
const handleAddMemberWithRole = async (user: KnowledgeBaseMemberSearchItem, role: number) => {
  if (!managingKBId.value) return
  
  const userId = user.user_id ?? user.id
  
  try {
    await knowledgeBaseApi.addKnowledgeBaseMember(managingKBId.value!, {
      user_id: userId,
      role: role
    })
    Modal.message({
      message: translate('knowledgeBase.member.addSuccess'),
      status: 'success'
    })
    await fetchMemberUsers()
  } catch (error: any) {
    Modal.message({
      message: error.message || translate('knowledgeBase.member.addError'),
      status: 'error'
    })
  }
}

// 修改成员角色
const handleChangeMemberRole = async (user: KnowledgeBaseMemberSearchItem, role: number) => {
  if (!managingKBId.value) return
  
  const userId = user.user_id ?? user.id
  
  try {
    await knowledgeBaseApi.updateKnowledgeBaseMemberRole(managingKBId.value!, userId, role)
    Modal.message({
      message: translate('knowledgeBase.member.roleChangeSuccess'),
      status: 'success'
    })
    await fetchMemberUsers()
  } catch (error: any) {
    Modal.message({
      message: error.message || translate('knowledgeBase.member.roleChangeError'),
      status: 'error'
    })
  }
}

// 移除成员
const handleRemoveMember = (user: KnowledgeBaseMemberSearchItem) => {
  if (!managingKBId.value) return
  
  const userId = user.user_id ?? user.id
  
  Modal.confirm({
    title: translate('knowledgeBase.member.removeConfirm'),
    message: translate('knowledgeBase.member.removeMessage', { name: user.username || `User ${userId}` }),
    status: 'warning'
  }).then(async () => {
    try {
      await knowledgeBaseApi.removeKnowledgeBaseMember(managingKBId.value!, userId)
      Modal.message({
        message: translate('knowledgeBase.member.removeSuccess'),
        status: 'success'
      })
      await fetchMemberUsers()
    } catch (error: any) {
      Modal.message({
        message: error.message || translate('knowledgeBase.member.removeError'),
        status: 'error'
      })
    }
  }).catch(() => {
    // 用户取消
  })
}

// 申请权限
const handleApplyPermission = async (kb: KnowledgeBase) => {
  applyingKBId.value = kb.id
  applyForm.value = {
    role: 1,
    reviewer_ids: [],
    message: ''
  }
  showApplyModal.value = true
  await fetchAdmins(kb.id)
}

// 获取管理员列表
const fetchAdmins = async (kbId: number) => {
  adminsLoading.value = true
  admins.value = []
  try {
    const list = await permissionApi.getResourceAdmins(APPLICATION_RESOURCE_TYPE.KNOWLEDGE_BASE, kbId)
    admins.value = Array.isArray(list) ? list : []
  } catch (e) {
    console.error('获取管理员列表失败:', e)
    admins.value = []
  } finally {
    adminsLoading.value = false
  }
}

// 提交申请
const handleSubmitApply = async () => {
  if (!applyingKBId.value) return
  applySubmitting.value = true
  try {
    await applicationApi.applyForResource({
      resource_type: APPLICATION_RESOURCE_TYPE.KNOWLEDGE_BASE,
      resource_id: applyingKBId.value,
      applied_role: applyForm.value.role,
      message: applyForm.value.message.trim() || null,
      reviewer_ids: applyForm.value.reviewer_ids.length > 0 ? applyForm.value.reviewer_ids : null
    })
    Modal.message({
      message: translate('article.applyEditSuccess'),
      status: 'success'
    })
    showApplyModal.value = false
    handleApplyModalClose()
  } catch (e: any) {
    Modal.message({
      message: e?.message || translate('article.applyEditError'),
      status: 'error'
    })
  } finally {
    applySubmitting.value = false
  }
}

// 关闭申请弹窗
const handleApplyModalClose = () => {
  applyingKBId.value = null
  applyForm.value = {
    role: 1,
    reviewer_ids: [],
    message: ''
  }
  admins.value = []
}

// 跳转到文章管理页面
const goToArticleManagement = (knowledgeBaseId: number) => {
  router.push(`/articles/${knowledgeBaseId}`)
}

// 跳转到团队空间页面
const goToTeamSpace = (teamSpaceName: string) => {
  router.push({
    path: '/knowledge/team-spaces',
    query: {
      name: teamSpaceName
    }
  })
}

// 初始化
onMounted(() => {
  // 检查路由查询参数中的搜索关键词
  const searchParam = route.query.name as string | undefined
  if (searchParam && searchParam.trim()) {
    searchKeyword.value = searchParam.trim()
  }
  
  if (teamSpaceId.value) {
    fetchTeamSpace()
  } else {
    fetchTeamSpaces() // 如果没有团队空间ID，获取团队空间列表用于创建时选择
  }
  
  // fetchKnowledgeBases 会自动使用 searchKeyword.value，所以先设置搜索关键词再调用
  fetchKnowledgeBases()
})
</script>

<style scoped lang="less">
.knowledge-space-page {
  width: 100%;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  gap: 16px;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.search-input {
  width: 300px;
  flex-shrink: 0;
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

.team-space-name {
  margin: 4px 0 0 0;
  font-size: 14px;
  color: #666;
}

.filter-section {
  margin-bottom: 24px;
  background: #fff;
  padding: 0;
  border-radius: 8px;
}

.content-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

.knowledge-base-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
  width: 100%;

  // 表格视图时，使用块级布局
  &.is-table-view {
    display: block;
  }

  .knowledge-list-pager-wrap {
    grid-column: 1 / -1;
    display: flex;
    justify-content: center;
    margin-top: 8px;
    padding-top: 16px;
    border-top: 1px solid rgba(100, 64, 180, 0.12);
  }
}

.table-view {
  background: #fff;
  border-radius: 8px;
  overflow-x: auto;
  box-sizing: border-box;

  // 确保表格宽度铺满
  :deep(.tiny-grid) {
    width: 100% !important;
  }

  :deep(.tiny-grid__wrapper) {
    width: 100% !important;
  }

  // 表头样式
  :deep(.tiny-grid thead),
  :deep(.tiny-grid .tiny-grid-header) {
    display: table-header-group !important;
  }

  :deep(.tiny-grid th),
  :deep(.tiny-grid thead th),
  :deep(.tiny-grid .tiny-grid-header th),
  :deep(.tiny-grid .tiny-grid-header__column) {
    font-weight: 600 !important;
    font-size: 13px !important;
    color: #303133 !important;
    background: #fafafa !important;
    padding: 12px 10px !important;
    border-bottom: 1px solid #e4e7ed !important;
    display: table-cell !important;
    visibility: visible !important;
    opacity: 1 !important;
    text-align: left;
  }

  // 表体样式
  :deep(.tiny-grid tbody td),
  :deep(.tiny-grid .tiny-grid-body td) {
    padding: 10px !important;
    font-size: 13px !important;
    color: #606266 !important;
  }

  :deep(.tiny-grid tbody tr:hover td),
  :deep(.tiny-grid .tiny-grid-row:hover td) {
    background-color: #f5f7fa !important;
  }

  .table-name-link {
    color: var(--primary-color, #8b5cf6);
    cursor: pointer;
    transition: color 0.2s;
    text-decoration: none;

    &:hover {
      color: var(--primary-color, #7c3aed);
      text-decoration: underline;
    }
  }

  .table-team-space-link {
    color: var(--primary-color, #8b5cf6);
    cursor: pointer;
    transition: color 0.2s;
    text-decoration: none;

    &:hover {
      color: var(--primary-color, #7c3aed);
      text-decoration: underline;
    }
  }

  .table-actions {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    justify-content: center;
    align-items: center;
    row-gap: 6px;
  }

  .table-action-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-height: 28px;
    padding: 4px 8px;
    border: none;
    border-radius: 4px;
    background: transparent;
    color: #606266;
    font-size: 12px;
    line-height: 1.2;
    white-space: nowrap;
    outline: none;
    cursor: pointer;
    transition: color 0.2s, background-color 0.2s;

    &:hover {
      color: var(--primary-color, #8b5cf6);
      background-color: rgba(139, 92, 246, 0.08);
    }

    &.table-action-btn-danger {
      color: #f56c6c;

      &:hover {
        color: #f56c6c;
        background-color: #fef0f0;
      }
    }

    &:focus {
      outline: none;
      box-shadow: none;
    }

    &:focus-visible {
      outline: none;
      box-shadow: none;
    }
  }

  .table-action-more {
    color: var(--primary-color, #8b5cf6);
    font-weight: 500;
    letter-spacing: 2px;
    padding: 4px 10px;

    &:hover {
      color: var(--primary-color, #7c3aed);
      background-color: rgba(139, 92, 246, 0.1);
    }
  }

  :deep(.tiny-dropdown-menu .tiny-dropdown-item.table-dropdown-item-danger) {
    color: #f56c6c;

    &:hover {
      color: #f56c6c;
      background-color: #fef0f0;
    }
  }
}

.loading-wrapper {
  grid-column: 1 / -1;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 60px 20px;
  color: #999;
}

.knowledge-base-card {
  position: relative;
  display: flex;
  flex-direction: column;
  min-height: 168px;
  padding: 0;
  border: 1px solid color-mix(in srgb, var(--primary-color, #8b5cf6) 14%, #e4e7ed);
  border-radius: 14px;
  cursor: pointer;
  background: var(--bg-color, #fff);
  overflow: hidden;
}

.card-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 18px 20px 12px;
  min-width: 0;
}

.card-top {
  display: flex;
  gap: 14px;
  align-items: flex-start;
}

.card-icon {
  flex-shrink: 0;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  color: var(--primary-color, #7c3aed);
  background: color-mix(in srgb, var(--primary-color, #8b5cf6) 12%, transparent);

  svg {
    width: 22px;
    height: 22px;
  }
}

.card-head-main {
  flex: 1;
  min-width: 0;
}

.card-title {
  margin: 0 0 8px;
  font-size: 17px;
  font-weight: 600;
  color: var(--text-color, #303133);
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}

.card-meta {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.card-meta-item {
  display: flex;
  align-items: baseline;
  gap: 8px;
  font-size: 12px;
  line-height: 1.5;
  min-width: 0;
}

.meta-label {
  flex-shrink: 0;
  color: var(--text-color-secondary, #909399);
}

.meta-value {
  flex: 1;
  min-width: 0;
  color: var(--text-color, #606266);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.meta-link {
  color: var(--primary-color, #8b5cf6);
  cursor: pointer;

  &:hover {
    color: var(--primary-color, #7c3aed);
    text-decoration: underline;
  }
}

.role-badge {
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 500;
  white-space: nowrap;
  display: inline-block;

  &.role-readonly {
    background-color: #f0f2f5;
    color: #606266;
  }

  &.role-editor {
    background-color: #e6f7ff;
    color: #1890ff;
  }

  &.role-admin {
    background-color: #fff7e6;
    color: #fa8c16;
  }
}

.visibility-badge {
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 500;
  white-space: nowrap;

  &.private {
    background-color: #fef0f0;
    color: #f56c6c;
  }

  &.member {
    background-color: #fff7e6;
    color: #e6a23c;
  }

  &.public {
    background-color: #f0f9ff;
    color: #67c23a;
  }
}

.card-footer {
  margin-top: auto;
  padding: 10px 14px 14px;
  border-top: 1px solid color-mix(in srgb, var(--primary-color, #8b5cf6) 8%, #f0f0f0);
  background: color-mix(in srgb, var(--primary-color, #8b5cf6) 4%, var(--bg-color-secondary, #fafafa));
}

.kb-detail {
  .detail-item {
    display: flex;
    margin-bottom: 20px;
    align-items: flex-start;

    .detail-label {
      font-weight: 500;
      color: #333;
      width: 100px;
      flex-shrink: 0;
    }

    .detail-value {
      flex: 1;
      color: #666;
      word-break: break-word;
    }
  }
}

.card-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px;
}

.card-action-chip {
  padding: 6px 12px;
  border: 1px solid color-mix(in srgb, var(--primary-color, #8b5cf6) 18%, #e4e7ed);
  border-radius: 8px;
  background: var(--bg-color, #fff);
  cursor: pointer;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-color, #606266);

  &:hover {
    color: var(--primary-color, #8b5cf6);
    border-color: color-mix(in srgb, var(--primary-color, #8b5cf6) 45%, #e4e7ed);
    background: color-mix(in srgb, var(--primary-color, #8b5cf6) 8%, transparent);
  }

  &:focus {
    outline: none;
    box-shadow: none;
  }

  &:focus-visible {
    outline: 2px solid color-mix(in srgb, var(--primary-color, #8b5cf6) 50%, transparent);
    outline-offset: 1px;
  }
}

.card-action-more {
  min-width: 36px;
  padding: 6px 10px;
  color: var(--primary-color, #8b5cf6);
  letter-spacing: 2px;

  &:hover {
    color: var(--primary-color, #7c3aed);
  }
}

.permission-dialog-content {
  padding: 8px 0;
}

.permission-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;

  th, td {
    padding: 10px 12px;
    text-align: center;
    border-bottom: 1px solid #e4e7ed;
  }

  th {
    background: #f5f7fa;
    color: #333;
    font-weight: 500;
  }

  td:first-child {
    text-align: left;
    color: #606266;
  }

  .perm-yes {
    color: var(--primary-color, #8b5cf6);
    font-weight: 500;
  }

  .perm-no {
    color: #c0c4cc;
  }
}

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

.kb-tag-manage {
  min-height: 200px;
}

.kb-tag-toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 14px;
  align-items: center;

  .kb-tag-search {
    flex: 1;
    min-width: 180px;
  }
}

.kb-tag-add-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 16px;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  background: rgba(139, 92, 246, 0.06);
  border: 1px dashed rgba(139, 92, 246, 0.35);

  .kb-tag-add-name {
    flex: 1;
    min-width: 160px;
  }

  .kb-tag-add-color {
    width: 160px;
    min-width: 120px;
  }
}

.kb-tag-list-wrap {
  position: relative;
  min-height: 120px;
}

.kb-tag-empty {
  text-align: center;
  color: var(--text-color-secondary, #909399);
  padding: 32px 16px;
  margin: 0;
}

.kb-tag-list {
  list-style: none;
  margin: 0;
  padding: 0;
  max-height: 360px;
  overflow-y: auto;
}

.kb-tag-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border: 1px solid var(--ti-base-border-color, #e4e7ed);
  border-radius: 8px;
  margin-bottom: 8px;
  transition: border-color 0.2s, box-shadow 0.2s;

  &:hover {
    border-color: rgba(139, 92, 246, 0.45);
    box-shadow: 0 2px 8px rgba(139, 92, 246, 0.08);
  }
}

.kb-tag-swatch {
  width: 14px;
  height: 14px;
  border-radius: 4px;
  flex-shrink: 0;
  border: 1px solid rgba(0, 0, 0, 0.08);
}

.kb-tag-name {
  flex: 1;
  min-width: 0;
  font-weight: 500;
  color: var(--ti-base-text-color, #303133);
  word-break: break-word;
}

.kb-tag-row-actions {
  flex-shrink: 0;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .knowledge-base-list {
    grid-template-columns: 1fr;
  }

  .content-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .kb-tag-add-row {
    flex-direction: column;
    align-items: stretch;

    .kb-tag-add-color {
      width: 100%;
    }
  }
}
</style>
