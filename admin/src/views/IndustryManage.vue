<template>
  <div class="industry-manage">
    <el-card>
      <template #header>
        <span>行业字典管理</span>
        <el-button type="primary" size="small" style="float: right;" @click="showAddDialog = true">
          新增行业
        </el-button>
      </template>

      <el-table :data="industries" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="行业名称" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button size="small" type="danger" @click="deleteIndustry(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showAddDialog" title="新增行业" width="400px">
      <el-input v-model="newName" placeholder="请输入行业名称" />
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleAdd">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const industries = ref([])
const loading = ref(false)
const showAddDialog = ref(false)
const newName = ref('')
const saving = ref(false)

async function loadIndustries() {
  loading.value = true
  try {
    const data = await api.get('/admin/industries')
    industries.value = data
  } catch (e) {
    console.error('加载行业失败', e)
  } finally {
    loading.value = false
  }
}

async function handleAdd() {
  if (!newName.value.trim()) {
    ElMessage.warning('请输入行业名称')
    return
  }
  saving.value = true
  try {
    await api.post('/admin/industries', { name: newName.value })
    ElMessage.success('添加成功')
    showAddDialog.value = false
    newName.value = ''
    await loadIndustries()
  } catch (e) {
    ElMessage.error('添加失败，可能已存在同名行业')
  } finally {
    saving.value = false
  }
}

async function deleteIndustry(id) {
  try {
    await ElMessageBox.confirm('确定要删除该行业吗？相关产品可能受影响。', '提示', { type: 'warning' })
    // 注意：当前 API 没有提供删除行业接口，这里仅作展示
    ElMessage.info('删除功能暂未开放')
  } catch (e) {
    if (e !== 'cancel') {}
  }
}

onMounted(() => {
  loadIndustries()
})
</script>

<style scoped>
.industry-manage {
  padding: 0;
}
</style>
