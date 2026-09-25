<template>
  <div class="user-manage">
    <el-card>
      <template #header>
        <span>用户管理</span>
      </template>

      <el-form :inline="true" style="margin-bottom: 16px;">
        <el-form-item label="角色">
          <el-select v-model="filterRole" placeholder="全部" clearable style="width: 120px;">
            <el-option label="普通用户" value="user" />
            <el-option label="会员商户" value="merchant" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadUsers">筛选</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="users" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="nickname" label="昵称" />
        <el-table-column prop="role" label="角色" width="100">
          <template #default="{ row }">
            <el-tag :type="getRoleType(row.role)">{{ getRoleText(row.role) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="phone_masked" label="手机号" width="120" />
        <el-table-column prop="is_disabled" label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_disabled ? 'danger' : 'success'">
              {{ row.is_disabled ? '禁用' : '正常' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="160">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-select v-model="row.tempRole" size="small" style="width: 90px; margin-right: 8px;" @change="(val) => changeRole(row, val)">
              <el-option label="普通用户" value="user" />
              <el-option label="会员商户" value="merchant" />
              <el-option label="管理员" value="admin" />
            </el-select>
            <el-button
              size="small"
              :type="row.is_disabled ? 'success' : 'danger'"
              @click="toggleDisable(row)"
            >
              {{ row.is_disabled ? '启用' : '禁用' }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        style="margin-top: 20px; justify-content: flex-end;"
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="loadUsers"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'
import { ElMessage } from 'element-plus'

const users = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = 20
const total = ref(0)
const filterRole = ref('')

function getRoleType(role) {
  const map = { user: '', merchant: 'warning', admin: 'danger' }
  return map[role] || 'info'
}

function getRoleText(role) {
  const map = { visitor: '游客', user: '普通用户', merchant: '会员商户', admin: '管理员' }
  return map[role] || role
}

function formatTime(time) {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN')
}

async function loadUsers() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize }
    if (filterRole.value) params.role = filterRole.value
    const data = await api.get('/admin/users', { params })
    users.value = (data.items || []).map(u => ({ ...u, tempRole: u.role }))
    total.value = data.total || 0
  } catch (e) {
    console.error('加载用户失败', e)
  } finally {
    loading.value = false
  }
}

async function changeRole(user, newRole) {
  try {
    await api.put(`/admin/users/${user.id}/role`, { role: newRole })
    user.role = newRole
    ElMessage.success('角色已更新')
  } catch (e) {
    ElMessage.error('操作失败')
    loadUsers()
  }
}

async function toggleDisable(user) {
  try {
    await api.put(`/admin/users/${user.id}/disable`, { is_disabled: !user.is_disabled })
    user.is_disabled = !user.is_disabled
    ElMessage.success(user.is_disabled ? '已禁用' : '已启用')
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<style scoped>
.user-manage {
  padding: 0;
}
</style>
