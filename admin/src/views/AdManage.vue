<template>
  <div class="ad-manage">
    <el-card>
      <template #header>
        <span>广告轮播管理</span>
        <el-button type="primary" size="small" style="float: right;" @click="showAddDialog = true">
          新增广告
        </el-button>
      </template>

      <el-table :data="ads" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="广告标题" />
        <el-table-column label="图片" width="120">
          <template #default="{ row }">
            <el-image
              :src="row.image"
              style="width: 100px; height: 60px;"
              fit="cover"
            />
          </template>
        </el-table-column>
        <el-table-column prop="link" label="跳转链接" show-overflow-tooltip />
        <el-table-column prop="sort_order" label="排序" width="80" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'warning'">
              {{ row.status === 'active' ? '已投放' : '待审核' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="merchant_name" label="申请商户" width="120" />
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="editAd(row)">编辑</el-button>
            <el-button
              size="small"
              :type="row.status === 'inactive' ? 'success' : 'danger'"
              @click="toggleStatus(row)"
            >
              {{ row.status === 'inactive' ? '启用' : '禁用' }}
            </el-button>
            <el-button size="small" type="danger" @click="deleteAd(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showAddDialog" :title="editingAd ? '编辑广告' : '新增广告'" width="500px">
      <el-form :model="adForm" label-width="100px">
        <el-form-item label="广告标题">
          <el-input v-model="adForm.title" placeholder="请输入广告标题" />
        </el-form-item>
        <el-form-item label="广告图片">
          <el-upload
            :http-request="handleCustomUpload"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :limit="1"
          >
            <el-button size="small">选择图片</el-button>
          </el-upload>
        </el-form-item>
        <el-form-item label="跳转链接">
          <el-input v-model="adForm.link" placeholder="请输入跳转链接" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="adForm.sort_order" :min="0" :max="99" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { uploadImage } from '@/utils/upload'

const ads = ref([])
const loading = ref(false)
const showAddDialog = ref(false)
const editingAd = ref(null)
const saving = ref(false)

const adForm = ref({ title: '', image: '', link: '', sort_order: 0 })

async function loadAds() {
  loading.value = true
  try {
    const data = await api.get('/admin/ads')
    ads.value = data
  } catch (e) {
    console.error('加载广告失败', e)
  } finally {
    loading.value = false
  }
}

function editAd(ad) {
  editingAd.value = ad
  adForm.value = { ...ad }
  showAddDialog.value = true
}

async function handleSave() {
  if (!adForm.value.title || !adForm.value.image) {
    ElMessage.warning('请填写完整信息')
    return
  }
  saving.value = true
  try {
    if (editingAd.value) {
      await api.put(`/admin/ads/${editingAd.value.id}`, adForm.value)
      ElMessage.success('更新成功')
    } else {
      await api.post('/admin/ads', adForm.value)
      ElMessage.success('添加成功')
    }
    showAddDialog.value = false
    editingAd.value = null
    adForm.value = { title: '', image: '', link: '', sort_order: 0 }
    await loadAds()
  } catch (e) {
    ElMessage.error('操作失败')
  } finally {
    saving.value = false
  }
}

async function toggleStatus(ad) {
  try {
    await api.put(`/admin/ads/${ad.id}`, { status: ad.status === 'inactive' ? 'active' : 'inactive' })
    ad.status = ad.status === 'inactive' ? 'active' : 'inactive'
    ElMessage.success(ad.status === 'active' ? '已启用' : '已禁用')
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

async function deleteAd(id) {
  try {
    await ElMessageBox.confirm('确定要删除该广告吗？', '提示', { type: 'warning' })
    await api.delete(`/admin/ads/${id}`)
    ElMessage.success('删除成功')
    await loadAds()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
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
  adForm.value.image = response.url || response.path
}

function handleUploadError() {
  ElMessage.error('上传失败，请重试')
}

onMounted(() => {
  loadAds()
})
</script>

<style scoped>
.ad-manage {
  padding: 0;
}
</style>
