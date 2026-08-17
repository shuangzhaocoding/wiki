<template>
  <div class="tree-container">
    <h2>TinyTree 节点操作示例</h2>
    
    <div class="tree-wrapper">
      <tiny-tree
        ref="treeRef"
        :data="treeData"
        :props="defaultProps"
        node-key="id"
        default-expand-all
        :highlight-current="true"
        @node-click="handleNodeClick"
      >
        <template #default="{ node, data }">
          <span class="tree-node">
            <span>{{ node.label }}</span>
            <span class="node-actions">
              <span
                class="action-icon"
                title="前插入"
                @click.stop="handleInsertBefore(data)"
              >
                <svg viewBox="0 0 1024 1024" width="16" height="16" fill="currentColor">
                  <path d="M512 192l-192 192h128v256h128V384h128L512 192z"/>
                  <path d="M192 704h640v64H192z"/>
                </svg>
              </span>
              <span
                class="action-icon"
                title="后插入"
                @click.stop="handleInsertAfter(data)"
              >
                <svg viewBox="0 0 1024 1024" width="16" height="16" fill="currentColor">
                  <path d="M512 832l192-192H576V384H448v256H320L512 832z"/>
                  <path d="M192 256h640v64H192z"/>
                </svg>
              </span>
              <span
                class="action-icon action-icon-success"
                title="插入子节点"
                @click.stop="handleInsertChild(data)"
              >
                <svg viewBox="0 0 1024 1024" width="16" height="16" fill="currentColor">
                  <path d="M512 192a32 32 0 0 1 32 32v256h256a32 32 0 1 1 0 64H544v256a32 32 0 1 1-64 0V544H224a32 32 0 1 1 0-64h256V224a32 32 0 0 1 32-32z"/>
                </svg>
              </span>
              <span
                class="action-icon action-icon-warning"
                title="修改名称"
                @click.stop="handleEditNode(data)"
              >
                <svg viewBox="0 0 1024 1024" width="16" height="16" fill="currentColor">
                  <path d="M832 512a32 32 0 1 1 64 0v352a32 32 0 0 1-32 32H160a32 32 0 0 1-32-32V160a32 32 0 0 1 32-32h352a32 32 0 0 1 0 64H192v640h640V512z"/>
                  <path d="M469.952 554.24l45.248-45.248 141.888 141.888-45.248 45.248zM832 128a32 32 0 0 1 9.408 62.592l-9.408 1.408-192 192a32 32 0 0 1-45.248-45.248L786.752 128H832z"/>
                </svg>
              </span>
              <span
                class="action-icon action-icon-danger"
                title="删除"
                @click.stop="handleDeleteNode(data)"
              >
                <svg viewBox="0 0 1024 1024" width="16" height="16" fill="currentColor">
                  <path d="M352 192V128a32 32 0 0 1 32-32h256a32 32 0 0 1 32 32v64h192a32 32 0 1 1 0 64H224a32 32 0 1 1 0-64h128zM256 320v512a64 64 0 0 0 64 64h384a64 64 0 0 0 64-64V320H256z m128 128a32 32 0 0 1 64 0v384a32 32 0 1 1-64 0V448z m192 0a32 32 0 0 1 64 0v384a32 32 0 1 1-64 0V448z"/>
                </svg>
              </span>
            </span>
          </span>
        </template>
      </tiny-tree>
    </div>

    <!-- 编辑节点名称对话框 -->
    <tiny-dialog-box
      v-model="editDialogVisible"
      title="修改节点名称"
      width="400px"
    >
      <tiny-input
        v-model="editNodeName"
        placeholder="请输入节点名称"
        @keyup.enter="confirmEditNode"
      />
      <template #footer>
        <tiny-button @click="editDialogVisible = false">取消</tiny-button>
        <tiny-button type="primary" @click="confirmEditNode">确定</tiny-button>
      </template>
    </tiny-dialog-box>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Tree as TinyTree, Button as TinyButton, DialogBox as TinyDialogBox, Input as TinyInput } from '@opentiny/vue'

interface TreeNode {
  id: string
  label: string
  children?: TreeNode[]
}

const treeRef = ref()
const currentNode = ref<TreeNode | null>(null)
const editDialogVisible = ref(false)
const editNodeName = ref('')
const editingNode = ref<TreeNode | null>(null)

const defaultProps = {
  children: 'children',
  label: 'label'
}

// 初始树数据
const treeData = ref<TreeNode[]>([
  {
    id: '1',
    label: '一级节点 1',
    children: [
      {
        id: '1-1',
        label: '二级节点 1-1'
      },
      {
        id: '1-2',
        label: '二级节点 1-2'
      }
    ]
  },
  {
    id: '2',
    label: '一级节点 2',
    children: [
      {
        id: '2-1',
        label: '二级节点 2-1'
      }
    ]
  },
  {
    id: '3',
    label: '一级节点 3'
  }
])

// 节点点击事件
const handleNodeClick = (data: TreeNode) => {
  currentNode.value = data
}

// 前插入节点
const handleInsertBefore = (data: TreeNode) => {
  if (!treeRef.value) return
  
  const tree = treeRef.value
  // 使用 TinyTree 的 getNode 方法获取节点
  const node = tree.getNode(data.id)
  
  if (!node) return
  
  const newNode: TreeNode = {
    id: `new-${Date.now()}`,
    label: `新节点（前插入）`
  }
  
  // 使用 TinyTree 的 insertBefore 方法
  if (typeof tree.insertBefore === 'function') {
    tree.insertBefore(newNode, node)
  } else {
    // 如果方法不存在，直接操作数据
    const parent = node.parent
    const children = parent ? parent.data.children || parent.data : treeData.value
    const index = children.findIndex((item: TreeNode) => item.id === data.id)
    if (index !== -1) {
      children.splice(index, 0, newNode)
    }
  }
  
  currentNode.value = newNode
}

// 后插入节点
const handleInsertAfter = (data: TreeNode) => {
  if (!treeRef.value) return
  
  const tree = treeRef.value
  // 使用 TinyTree 的 getNode 方法获取节点
  const node = tree.getNode(data.id)
  
  if (!node) return
  
  const newNode: TreeNode = {
    id: `new-${Date.now()}`,
    label: `新节点（后插入）`
  }
  
  // 使用 TinyTree 的 insertAfter 方法
  if (typeof tree.insertAfter === 'function') {
    tree.insertAfter(newNode, node)
  } else {
    // 如果方法不存在，直接操作数据
    const parent = node.parent
    const children = parent ? parent.data.children || parent.data : treeData.value
    const index = children.findIndex((item: TreeNode) => item.id === data.id)
    if (index !== -1) {
      children.splice(index + 1, 0, newNode)
    }
  }
  
  currentNode.value = newNode
}

// 插入子节点
const handleInsertChild = (data: TreeNode) => {
  if (!treeRef.value) return
  
  const tree = treeRef.value
  // 使用 TinyTree 的 getNode 方法获取节点
  const node = tree.getNode(data.id)
  
  if (!node) return
  
  const newNode: TreeNode = {
    id: `new-${Date.now()}`,
    label: `子节点`
  }
  
  // 使用 TinyTree 的 append 方法插入子节点
  if (typeof tree.append === 'function') {
    tree.append(newNode, node)
  } else {
    // 如果方法不存在，直接操作数据
    if (!node.data.children) {
      node.data.children = []
    }
    node.data.children.push(newNode)
  }
  
  currentNode.value = newNode
}

// 编辑节点名称
const handleEditNode = (data: TreeNode) => {
  editingNode.value = data
  editNodeName.value = data.label
  editDialogVisible.value = true
}

// 确认修改节点名称
const confirmEditNode = () => {
  if (!treeRef.value || !editingNode.value) return
  
  const tree = treeRef.value
  // 使用 TinyTree 的 getNode 方法获取节点
  const node = tree.getNode(editingNode.value.id)
  
  if (!node) return
  
  // 使用 TinyTree 的 updateKeyChildren 方法更新节点
  if (typeof tree.updateKeyChildren === 'function') {
    node.data.label = editNodeName.value
    tree.updateKeyChildren(editingNode.value.id, node.data)
  } else {
    // 如果方法不存在，直接更新数据
    node.data.label = editNodeName.value
    if (editingNode.value) {
      editingNode.value.label = editNodeName.value
    }
  }
  
  editDialogVisible.value = false
  editingNode.value = null
  editNodeName.value = ''
}

// 删除节点
const handleDeleteNode = (data: TreeNode) => {
  if (!treeRef.value) return
  
  const tree = treeRef.value
  // 使用 TinyTree 的 getNode 方法获取节点
  const node = tree.getNode(data.id)
  
  if (!node) return
  
  // 使用 TinyTree 的 remove 方法删除节点
  if (typeof tree.remove === 'function') {
    tree.remove(data.id)
  } else {
    // 如果方法不存在，直接操作数据
    const parent = node.parent
    const children = parent ? parent.data.children || parent.data : treeData.value
    const index = children.findIndex((item: TreeNode) => item.id === data.id)
    if (index !== -1) {
      children.splice(index, 1)
    }
  }
  
  currentNode.value = null
}
</script>

<style scoped lang="less">
.tree-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

h2 {
  margin-bottom: 20px;
  color: #333;
}

.tree-wrapper {
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 20px;
  background-color: #fff;
  min-height: 400px;
}

.tree-node {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding-right: 10px;
}

.node-actions {
  display: flex;
  gap: 8px;
  margin-left: 10px;
  opacity: 0;
  transition: opacity 0.2s;
  align-items: center;
}

.tree-node:hover .node-actions {
  opacity: 1;
}

.action-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  padding: 4px;
  border-radius: 4px;
  cursor: pointer;
  color: #409eff;
  transition: all 0.2s;
  background-color: transparent;
}

.action-icon:hover {
  background-color: #ecf5ff;
  color: #409eff;
  transform: scale(1.1);
}

.action-icon-success {
  color: #67c23a;
}

.action-icon-success:hover {
  background-color: #f0f9ff;
  color: #67c23a;
}

.action-icon-warning {
  color: #e6a23c;
}

.action-icon-warning:hover {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.action-icon-danger {
  color: #f56c6c;
}

.action-icon-danger:hover {
  background-color: #fef0f0;
  color: #f56c6c;
}

.action-icon svg {
  width: 16px;
  height: 16px;
}

:deep(.tiny-tree-node__content) {
  height: auto;
  min-height: 26px;
}

:deep(.tiny-tree-node__content:hover) {
  background-color: #f5f7fa;
}
</style>
