<template>
  <div class="product-review">
    <el-card>
      <template #header>
        <span>产品审核</span>
        <el-tag type="warning" style="margin-left: 10px;">待审核: {{ pendingCount }}</el-tag>
      </template>

      <el-table :data="products" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="title" label="产品标题" />
        <el-table-column prop="merchant_id" label="商户ID" width="80" />
        <el-table-column prop="industry_id" label="行业ID" width="80" />
        <el-table-column prop="area" label="区域" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="提交时间" width="160">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220">
          <template #default="{ row }">
            <el-button size="small" @click="viewDetail(row)">详情</el-button>
            <el-button
              v-if="row.status === 'pending_review'"
              size="small"
              type="success"
              @click="handleReview(row, 'approve')"
            >通过</el-button>
            <el-button
              v-if="row.status === 'pending_review'"
              size="small"
              type="danger"
              @click="showRejectDialog(row)"
            >驳回</el-button>
            <span v-if="row.reject_reason" style="font-size: 12px; color: #f56c6c;">{{ row.reject_reason }}</span>
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

    <!-- 产品详情弹窗 -->
    <el-dialog v-model="showDetail" title="产品详情" width="600px">
      <el-descriptions :column="2" border v-if="currentProduct">
        <el-descriptions-item label="产品ID">{{ currentProduct.id }}</el-descriptions-item>
        <el-descriptions-item label="商户ID">{{ currentProduct.merchant_id }}</el-descriptions-item>
        <el-descriptions-item label="产品标题" :span="2">{{ currentProduct.title }}</el-descriptions-item>
        <el-descriptions-item label="所属行业">{{ currentProduct.industry_id }}</el-descriptions-item>
        <el-descriptions-item label="所在区域">{{ currentProduct.area }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ currentProduct.contact_phone || '-' }}</el-descriptions-item>
        <el-descriptions-item label="浏览次数">{{ currentProduct.view_count }}</el-descriptions-item>
        <el-descriptions-item label="审核状态">
          <el-tag :type="getStatusType(currentProduct.status)">{{ getStatusText(currentProduct.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="产品简介" :span="2">{{ currentProduct.description || '暂无' }}</el-descriptions-item>
        <el-descriptions-item label="驳回原因" :span="2" v-if="currentProduct.reject_reason">
          <span style="color: #f56c6c;">{{ currentProduct.reject_reason }}</span>
        </el-descriptions-item>
        <el-descriptions-item label="提交时间">{{ formatTime(currentProduct.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="更新时间">{{ formatTime(currentProduct.updated_at) }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="showDetail = false">关闭</el-button>
        <el-button v-if="currentProduct?.status === 'pending_review'" type="success" @click="handleReview(currentProduct, 'approve')">通过</el-button>
        <el-button v-if="currentProduct?.status === 'pending_review'" type="danger" @click="showRejectDialog(currentProduct)">驳回</el-button>
      </template>
    </el-dialog>

    <!-- 驳回弹窗 -->
    <el-dialog v-model="showReject" title="填写驳回原因" width="400px">
      <el-input
        v-model="rejectReason"
        type="textarea"
        :rows="3"
        placeholder="请输入驳回原因"
      />
      <template #footer>
        <el-button @click="showReject = false">取消</el-button>
        <el-button type="danger" @click="confirmReject">确认驳回</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/api'
import { ElMessage } from 'element-plus'

const products = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = 20
const total = ref(0)
const showDetail = ref(false)
const showReject = ref(false)
const rejectReason = ref('')
const rejectingProduct = ref(null)
const currentProduct = ref(null)

const pendingCount = computed(() => products.value.filter(p => p.status === 'pending_review').length)

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
    const params = { page: page.value, page_size: pageSize, status: 'pending_review' }
    const data = await api.get('/admin/products', { params })
    products.value = data.items || []
    total.value = data.total || 0
  } catch (e) {
    console.error('加载产品失败', e)
  } finally {
    loading.value = false
  }
}

function viewDetail(product) {
  currentProduct.value = product
  showDetail.value = true
}

async function handleReview(product, action) {
  try {
    await api.put(`/admin/products/${product.id}/review`, { action })
    ElMessage.success(action === 'approve' ? '已通过' : '已驳回')
    showDetail.value = false
    await loadProducts()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

function showRejectDialog(product) {
  rejectingProduct.value = product
  rejectReason.value = ''
  showReject.value = true
}

async function confirmReject() {
  if (!rejectingProduct.value || !rejectReason.value.trim()) {
    ElMessage.warning('请填写驳回原因')
    return
  }
  try {
    await api.put(`/admin/products/${rejectingProduct.value.id}/review`, {
      action: 'reject',
      reason: rejectReason.value,
    })
    ElMessage.success('已驳回')
    showReject.value = false
    await loadProducts()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

onMounted(() => {
  loadProducts()
})
</script>

<style scoped>
.product-review {
  padding: 0;
}
</style>
