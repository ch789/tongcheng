<template>
  <div class="product-list">
    <el-card>
      <template #header>
        <span>全部产品</span>
        <div style="float: right;">
          <el-button type="primary" size="small" @click="handleAdd" style="margin-right: 10px;">新增产品</el-button>
          <el-input v-model="searchKeyword" placeholder="搜索产品..." style="width: 200px; margin-right: 10px;" clearable />
          <el-button type="primary" @click="loadProducts">搜索</el-button>
        </div>
      </template>

      <el-form :inline="true" style="margin-bottom: 16px;">
        <el-form-item label="行业">
          <el-select v-model="filterIndustry" placeholder="全部" clearable style="width: 120px;">
            <el-option v-for="ind in industries" :key="ind.id" :label="ind.name" :value="ind.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="区域">
          <el-select v-model="filterArea" placeholder="全部" clearable style="width: 120px;">
            <el-option v-for="a in areas" :key="a" :label="a" :value="a" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filterStatus" placeholder="全部" clearable style="width: 100px;">
            <el-option label="待审核" value="pending_review" />
            <el-option label="已通过" value="approved" />
            <el-option label="已驳回" value="rejected" />
            <el-option label="已下架" value="off_shelf" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadProducts">筛选</el-button>
          <el-button @click="resetFilter">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="products" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="产品标题" />
        <el-table-column prop="merchant_name" label="商户" width="100" />
        <el-table-column prop="industry_name" label="行业" width="100" />
        <el-table-column prop="area" label="区域" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="view_count" label="浏览" width="70" />
        <el-table-column prop="created_at" label="创建时间" width="160">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="220">
          <template #default="{ row }">
            <el-button size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button
              v-if="row.status === 'approved'"
              size="small"
              type="warning"
              @click="offShelf(row)"
            >下架</el-button>
            <el-button
              v-if="row.status === 'off_shelf'"
              size="small"
              type="success"
              @click="onShelf(row)"
            >上架</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        style="margin-top: 20px; justify-content: flex-end;"
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="loadProducts"
      />
    </el-card>

    <!-- 新增/编辑弹窗 -->
    <el-dialog v-model="showDialog" :title="editingProduct ? '编辑产品' : '新增产品'" width="600px">
      <el-form :model="productForm" label-width="100px" ref="formRef">
        <el-form-item label="产品标题" prop="title" required>
          <el-input v-model="productForm.title" placeholder="请输入产品标题" />
        </el-form-item>
        <el-form-item label="所属行业" prop="industry_id" required>
          <el-select v-model="productForm.industry_id" placeholder="请选择行业" style="width: 100%;">
            <el-option v-for="ind in industries" :key="ind.id" :label="ind.name" :value="ind.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="所在区域" prop="area" required>
          <el-select v-model="productForm.area" placeholder="请选择区域" style="width: 100%;">
            <el-option v-for="a in areas" :key="a" :label="a" :value="a" />
          </el-select>
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="productForm.contact_phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="产品图片">
          <el-upload
            :http-request="handleCustomUpload"
            list-type="picture-card"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :limit="5"
            :on-remove="handleRemove"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
        </el-form-item>
        <el-form-item label="产品简介">
          <el-input v-model="productForm.description" type="textarea" :rows="4" placeholder="请输入产品简介" />
        </el-form-item>
        <el-form-item label="审核状态">
          <el-select v-model="productForm.status" style="width: 100%;">
            <el-option label="待审核" value="pending_review" />
            <el-option label="已通过" value="approved" />
            <el-option label="已驳回" value="rejected" />
            <el-option label="已下架" value="off_shelf" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="productForm.status === 'rejected'" label="驳回原因">
          <el-input v-model="productForm.reject_reason" type="textarea" :rows="2" placeholder="请输入驳回原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showDialog = false">取消</el-button>
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

const products = ref([])
const industries = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = 20
const total = ref(0)
const showDialog = ref(false)
const saving = ref(false)
const editingProduct = ref(null)
const formRef = ref(null)

const searchKeyword = ref('')
const filterIndustry = ref(null)
const filterArea = ref('')
const filterStatus = ref('')

const areas = ['南开区', '河西区', '滨海新区', '和平区', '河北区', '红桥区', '东丽区', '西青区']

const productForm = ref({
  title: '',
  description: '',
  images: [],
  industry_id: null,
  area: '',
  contact_phone: '',
  status: 'approved',
  reject_reason: '',
})

function getStatusType(status) {
  const map = { pending_review: 'warning', approved: 'success', rejected: 'danger', off_shelf: 'info' }
  return map[status] || 'info'
}

function getStatusText(status) {
  const map = { pending_review: '待审核', approved: '已通过', rejected: '已驳回', off_shelf: '已下架' }
  return map[status] || status
}

function formatTime(time) {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN')
}

async function loadProducts() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize }
    if (searchKeyword.value) params.keyword = searchKeyword.value
    if (filterIndustry.value) params.industry_id = Number(filterIndustry.value)
    if (filterArea.value) params.area = filterArea.value
    if (filterStatus.value) params.status = filterStatus.value
    const data = await api.get('/admin/products', { params })
    products.value = data.items || []
    total.value = data.total || 0
  } catch (e) {
    console.error('加载产品失败', e)
  } finally {
    loading.value = false
  }
}

function resetFilter() {
  searchKeyword.value = ''
  filterIndustry.value = null
  filterArea.value = ''
  filterStatus.value = ''
  page.value = 1
  loadProducts()
}

function handleAdd() {
  editingProduct.value = null
  productForm.value = {
    title: '',
    description: '',
    images: [],
    industry_id: null,
    area: '',
    contact_phone: '',
    status: 'approved',
    reject_reason: '',
  }
  showDialog.value = true
}

function handleEdit(product) {
  editingProduct.value = product
  productForm.value = {
    title: product.title || '',
    description: product.description || '',
    images: product.images || [],
    industry_id: product.industry_id || null,
    area: product.area || '',
    contact_phone: product.contact_phone || '',
    status: product.status || 'approved',
    reject_reason: product.reject_reason || '',
  }
  showDialog.value = true
}

async function handleSave() {
  if (!productForm.value.title || !productForm.value.industry_id || !productForm.value.area) {
    ElMessage.warning('请填写必填项')
    return
  }
  saving.value = true
  try {
    const payload = {
      title: productForm.value.title,
      description: productForm.value.description,
      images: productForm.value.images,
      industry_id: Number(productForm.value.industry_id),
      area: productForm.value.area,
      contact_phone: productForm.value.contact_phone,
      status: productForm.value.status,
      reject_reason: productForm.value.reject_reason,
    }
    if (editingProduct.value) {
      await api.put(`/admin/products/${editingProduct.value.id}`, payload)
      ElMessage.success('更新成功')
    } else {
      await api.post('/admin/products', payload)
      ElMessage.success('创建成功')
    }
    showDialog.value = false
    editingProduct.value = null
    await loadProducts()
  } catch (e) {
    ElMessage.error('操作失败')
  } finally {
    saving.value = false
  }
}

async function handleDelete(id) {
  try {
    await ElMessageBox.confirm('确定要删除该产品吗？此操作不可恢复。', '提示', { type: 'warning' })
    await api.delete(`/admin/products/${id}`)
    ElMessage.success('删除成功')
    await loadProducts()
  } catch (e) {
    if (e !== 'cancel') ElMessage.error('删除失败')
  }
}

async function offShelf(product) {
  try {
    await api.put(`/admin/products/${product.id}/review`, { action: 'off_shelf' })
    product.status = 'off_shelf'
    ElMessage.success('已下架')
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

async function onShelf(product) {
  try {
    await api.put(`/admin/products/${product.id}/review`, { action: 'on_shelf' })
    product.status = 'approved'
    ElMessage.success('已上架')
  } catch (e) {
    ElMessage.error('操作失败')
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
  productForm.value.images.push(response.url || response.path)
}

function handleUploadError() {
  ElMessage.error('上传失败，请重试')
}

function handleRemove(file, fileList) {
  productForm.value.images = fileList.map(f => f.url || f.response?.url || f.response?.path).filter(Boolean)
}

async function loadIndustries() {
  try {
    const data = await api.get('/admin/industries')
    industries.value = data
  } catch (e) {
    console.error('加载行业失败', e)
  }
}

onMounted(() => {
  loadProducts()
  loadIndustries()
})
</script>

<style scoped>
.product-list {
  padding: 0;
}
</style>
