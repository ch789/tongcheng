<template>
  <div class="home-manage">
    <el-card>
      <template #header>首页内容设置</template>
      <el-form :model="form" label-width="100px">
        <el-form-item label="平台Slogan">
          <el-input
            v-model="form.slogan"
            type="textarea"
            :rows="3"
            placeholder="请输入平台宣传语，如：团结同乡资源，服务在外老乡"
          />
        </el-form-item>
        <el-form-item label="首页公告">
          <el-input
            v-model="form.announcement"
            type="textarea"
            :rows="3"
            placeholder="请输入首页公告内容"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSave">保存设置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card style="margin-top: 20px;">
      <template #header>
        <span>轮播广告</span>
        <el-button type="primary" size="small" style="float: right;" @click="showAddAd = true">新增广告</el-button>
      </template>
      <el-table :data="ads" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="标题" />
        <el-table-column label="图片">
          <template #default="{ row }">
            <el-image
              :src="row.image"
              style="width: 60px; height: 40px;"
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
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="editAd(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteAd(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑广告弹窗 -->
    <el-dialog v-model="showAddAd" :title="editingAd ? '编辑广告' : '新增广告'" width="500px">
      <el-form :model="adForm" label-width="100px">
        <el-form-item label="广告标题">
          <el-input v-model="adForm.title" placeholder="请输入广告标题" />
        </el-form-item>
        <el-form-item label="广告图片">
          <el-upload
            :http-request="handleCustomUpload"
            list-type="picture-card"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :limit="1"
          >
            <el-icon v-if="!adForm.image"><Plus /></el-icon>
            <img v-else :src="adForm.image" class="el-upload-list__item-thumbnail" />
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
        <el-button @click="showAddAd = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSaveAd">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import api from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { uploadImage } from '@/utils/upload'

const form = ref({ slogan: '', announcement: '' })
const ads = ref([])
const showAddAd = ref(false)
const editingAd = ref(null)
const adForm = ref({ title: '', image: '', link: '', sort_order: 0 })
const saving = ref(false)

onMounted(async () => {
  await loadHomeContent()
  await loadAds()
})

async function loadHomeContent() {
  try {
    const data = await api.get('/admin/home')
    form.value.slogan = data.slogan || ''
    form.value.announcement = data.announcement || ''
  } catch (e) {
    console.error('加载首页内容失败', e)
  }
}

async function loadAds() {
  try {
    const data = await api.get('/admin/ads')
    ads.value = data
  } catch (e) {
    console.error('加载广告失败', e)
  }
}

async function handleSave() {
  saving.value = true
  try {
    await api.put('/admin/home', form.value)
    ElMessage.success('保存成功')
  } catch (e) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

function editAd(ad) {
  editingAd.value = ad
  adForm.value = { ...ad }
  showAddAd.value = true
}

async function handleSaveAd() {
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
    showAddAd.value = false
    editingAd.value = null
    adForm.value = { title: '', image: '', link: '', sort_order: 0 }
    await loadAds()
  } catch (e) {
    ElMessage.error('操作失败')
  } finally {
    saving.value = false
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
</script>

<style scoped>
.home-manage {
  padding: 0;
}
</style>
