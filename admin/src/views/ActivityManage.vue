<template>
  <div class="activity-manage">
    <el-card>
      <template #header>
        <span>活动管理</span>
        <el-button type="primary" size="small" style="float: right;" @click="showAddDialog = true">
          创建活动
        </el-button>
      </template>

      <el-table :data="activities" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="活动标题" />
        <el-table-column prop="start_time" label="开始时间" width="160">
          <template #default="{ row }">{{ formatTime(row.start_time) }}</template>
        </el-table-column>
        <el-table-column prop="end_time" label="结束时间" width="160">
          <template #default="{ row }">{{ formatTime(row.end_time) }}</template>
        </el-table-column>
        <el-table-column prop="location" label="地点" show-overflow-tooltip />
        <el-table-column prop="max_participants" label="人数上限" width="100">
          <template #default="{ row }">{{ row.max_participants === 0 ? '不限' : row.max_participants }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="250">
          <template #default="{ row }">
            <el-button size="small" @click="editActivity(row)">编辑</el-button>
            <el-button size="small" type="primary" @click="viewRegistrations(row)">报名</el-button>
            <el-button
              size="small"
              :type="row.status === 'off_shelf' ? 'success' : 'danger'"
              @click="changeStatus(row)"
            >
              改状态
            </el-button>
            <el-button size="small" type="danger" @click="deleteActivity(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        style="margin-top: 20px; justify-content: flex-end;"
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="loadActivities"
      />
    </el-card>

    <!-- 新增/编辑活动弹窗 -->
    <el-dialog v-model="showAddDialog" :title="editingActivity ? '编辑活动' : '创建活动'" width="600px">
      <el-form :model="activityForm" label-width="100px">
        <el-form-item label="活动标题" required>
          <el-input v-model="activityForm.title" placeholder="请输入活动标题" />
        </el-form-item>
        <el-form-item label="活动封面">
          <el-upload
            :http-request="handleCustomUpload"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :limit="1"
          >
            <el-button size="small">选择图片</el-button>
          </el-upload>
        </el-form-item>
        <el-form-item label="开始时间" required>
          <el-date-picker v-model="activityForm.start_time" type="datetime" placeholder="选择开始时间" />
        </el-form-item>
        <el-form-item label="结束时间" required>
          <el-date-picker v-model="activityForm.end_time" type="datetime" placeholder="选择结束时间" />
        </el-form-item>
        <el-form-item label="活动地点">
          <el-input v-model="activityForm.location" placeholder="请输入活动地点" />
        </el-form-item>
        <el-form-item label="活动详情">
          <el-input v-model="activityForm.content" type="textarea" :rows="5" placeholder="请输入活动详情" />
        </el-form-item>
        <el-form-item label="人数上限">
          <el-input-number v-model="activityForm.max_participants" :min="0" :max="9999" />
          <span style="margin-left: 8px; color: #999; font-size: 12px;">0 表示不限</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <!-- 报名记录弹窗 -->
    <el-dialog v-model="showRegDialog" title="报名记录" width="800px">
      <el-table :data="registrations" stripe>
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="phone" label="联系电话" width="120" />
        <el-table-column prop="register_type" label="类型" width="80">
          <template #default="{ row }">{{ row.register_type === 'personal' ? '个人' : '商户' }}</template>
        </el-table-column>
        <el-table-column prop="area" label="区域" width="100" />
        <el-table-column prop="interest" label="意向内容" show-overflow-tooltip />
        <el-table-column prop="remark" label="备注" show-overflow-tooltip />
        <el-table-column prop="registered_at" label="报名时间" width="160">
          <template #default="{ row }">{{ formatTime(row.registered_at) }}</template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="exportRegistrations">导出 Excel</el-button>
        <el-button @click="showRegDialog = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 活动状态设置弹窗 -->
    <el-dialog v-model="showStatusDialog" title="修改活动状态" width="420px">
      <el-radio-group v-model="statusForm.status">
        <el-radio label="upcoming">未开始（即将开始）</el-radio>
        <el-radio label="registering">报名中（进行中）</el-radio>
        <el-radio label="ended">已结束</el-radio>
        <el-radio label="off_shelf">已下架</el-radio>
      </el-radio-group>
      <template #footer>
        <el-button @click="showStatusDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmStatus">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { uploadImage } from '@/utils/upload'

const router = useRouter()
const activities = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = 20
const total = ref(0)
const showAddDialog = ref(false)
const editingActivity = ref(null)
const saving = ref(false)
const showRegDialog = ref(false)
const registrations = ref([])
const currentActivity = ref(null)
const showStatusDialog = ref(false)
const statusForm = ref({ id: null, status: '' })

const activityForm = ref({
  title: '',
  cover_image: '',
  start_time: '',
  end_time: '',
  location: '',
  content: '',
  max_participants: 0,
})

function getStatusType(status) {
  const map = { upcoming: 'info', registering: 'success', ended: 'danger', off_shelf: 'info' }
  return map[status] || 'info'
}

function getStatusText(status) {
  const map = { upcoming: '未开始', registering: '报名中', ended: '已结束', off_shelf: '已下架' }
  return map[status] || status
}

function formatTime(time) {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN')
}

async function loadActivities() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize }
    const data = await api.get('/admin/activities', { params })
    activities.value = data.items || []
    total.value = data.total || 0
  } catch (e) {
    console.error('加载活动失败', e)
  } finally {
    loading.value = false
  }
}

function editActivity(activity) {
  editingActivity.value = activity
  activityForm.value = {
    title: activity.title,
    cover_image: activity.cover_image,
    start_time: activity.start_time,
    end_time: activity.end_time,
    location: activity.location,
    content: activity.content,
    max_participants: activity.max_participants,
  }
  showAddDialog.value = true
}

async function handleSave() {
  if (!activityForm.value.title) {
    ElMessage.warning('请填写活动标题')
    return
  }
  saving.value = true
  try {
    if (editingActivity.value) {
      await api.put(`/admin/activities/${editingActivity.value.id}`, activityForm.value)
      ElMessage.success('更新成功')
    } else {
      await api.post('/admin/activities', activityForm.value)
      ElMessage.success('创建成功')
    }
    showAddDialog.value = false
    editingActivity.value = null
    await loadActivities()
  } catch (e) {
    ElMessage.error('操作失败')
  } finally {
    saving.value = false
  }
}

async function changeStatus(activity) {
  // 改为弹出状态下拉框，可切到真实枚举（未开始/报名中/已结束/下架）
  showStatusDialog.value = true
  statusForm.value = { id: activity.id, status: activity.status }
}

async function confirmStatus() {
  const { id, status } = statusForm.value
  try {
    await api.put(`/admin/activities/${id}`, { status })
    ElMessage.success('状态已更新为：' + getStatusText(status))
    showStatusDialog.value = false
    await loadActivities()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

async function deleteActivity(id) {
  try {
    await ElMessageBox.confirm('确定要删除该活动吗？', '提示', { type: 'warning' })
    await api.delete(`/admin/activities/${id}`)
    ElMessage.success('删除成功')
    await loadActivities()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

async function viewRegistrations(activity) {
  currentActivity.value = activity
  try {
    const data = await api.get(`/admin/activities/${activity.id}/registrations`)
    registrations.value = data
  } catch (e) {
    console.error('加载报名记录失败', e)
  }
  showRegDialog.value = true
}

function exportRegistrations() {
  if (!currentActivity.value) return
  const token = localStorage.getItem('token')
  // 使用 fetch + blob 下载，避免 Token 暴露在 URL 和日志中
  fetch(`/api/admin/export/registrations?activity_id=${currentActivity.value.id}`, {
    headers: { 'Authorization': `Bearer ${token}` },
  })
    .then(res => {
      if (!res.ok) throw new Error('导出失败')
      return res.blob()
    })
    .then(blob => {
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `活动报名数据_${currentActivity.value.id}.xlsx`
      a.click()
      URL.revokeObjectURL(url)
    })
    .catch(() => {
      ElMessage.error('导出失败，请重试')
    })
}

async function handleCustomUpload({ file }) {
  try {
    const res = await uploadImage(file)
    ElMessage.success(res.compressed ? '图片已自动压缩并上传' : '上传成功')
    handleUploadSuccess(res)
  } catch (e) {
    ElMessage.error(e?.response?.data?.detail || '上传失败，请重试')
  }
}

function handleUploadSuccess(response) {
  activityForm.value.cover_image = response.url || response.path
}

function handleUploadError() {
  ElMessage.error('上传失败，请重试')
}

onMounted(() => {
  loadActivities()
})
</script>

<style scoped>
.activity-manage {
  padding: 0;
}
</style>
