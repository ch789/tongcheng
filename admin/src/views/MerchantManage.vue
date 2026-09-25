<template>
  <div class="merchant-manage">
    <el-card>
      <template #header><span>商户入驻审核</span></template>

      <el-table :data="merchants" stripe v-loading="loading">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="user_nickname" label="申请人" width="120" />
        <el-table-column prop="shop_name" label="商户名称" />
        <el-table-column prop="industry_name" label="所属行业" width="100" />
        <el-table-column prop="area" label="所在区域" width="100" />
        <el-table-column prop="contact_phone" label="联系电话" width="120" />
        <el-table-column prop="address" label="经营地址" show-overflow-tooltip />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ getStatusText(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="applied_at" label="申请时间" width="160">
          <template #default="{ row }">{{ formatTime(row.applied_at) }}</template>
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
    </el-card>

    <!-- 商户详情弹窗 -->
    <el-dialog v-model="showDetail" title="商户申请详情" width="600px">
      <el-descriptions :column="2" border v-if="currentMerchant">
        <el-descriptions-item label="申请ID">{{ currentMerchant.id }}</el-descriptions-item>
        <el-descriptions-item label="用户ID">{{ currentMerchant.user_id }}</el-descriptions-item>
        <el-descriptions-item label="商户名称" :span="2">{{ currentMerchant.shop_name }}</el-descriptions-item>
        <el-descriptions-item label="所属行业">{{ currentMerchant.industry_name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="所在区域">{{ currentMerchant.area || '-' }}</el-descriptions-item>
        <el-descriptions-item label="联系电话">{{ currentMerchant.contact_phone }}</el-descriptions-item>
        <el-descriptions-item label="经营地址" :span="2">{{ currentMerchant.address || '暂无' }}</el-descriptions-item>
        <el-descriptions-item label="商户简介" :span="2">{{ currentMerchant.description || '暂无' }}</el-descriptions-item>
        <el-descriptions-item label="营业执照">
          <el-image
            v-if="currentMerchant.business_license"
            :src="currentMerchant.business_license"
            :preview-src-list="[currentMerchant.business_license]"
            style="width: 100px; height: 100px;"
            fit="cover"
          />
          <span v-else>暂未上传</span>
        </el-descriptions-item>
        <el-descriptions-item label="申请状态">
          <el-tag :type="getStatusType(currentMerchant.status)">{{ getStatusText(currentMerchant.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="申请时间">{{ formatTime(currentMerchant.applied_at) }}</el-descriptions-item>
        <el-descriptions-item label="驳回原因" :span="2" v-if="currentMerchant.reject_reason">
          <span style="color: #f56c6c;">{{ currentMerchant.reject_reason }}</span>
        </el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="showDetail = false">关闭</el-button>
        <el-button v-if="currentMerchant?.status === 'pending_review'" type="success" @click="handleReview(currentMerchant, 'approve')">通过</el-button>
        <el-button v-if="currentMerchant?.status === 'pending_review'" type="danger" @click="showRejectDialog(currentMerchant)">驳回</el-button>
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
import { ref, onMounted } from 'vue'
import api from '@/api'
import { ElMessage } from 'element-plus'

const merchants = ref([])
const loading = ref(false)
const showDetail = ref(false)
const showReject = ref(false)
const rejectReason = ref('')
const rejectingMerchant = ref(null)
const currentMerchant = ref(null)

function getStatusType(status) {
  const map = { pending_review: 'warning', approved: 'success', rejected: 'danger' }
  return map[status] || 'info'
}

function getStatusText(status) {
  const map = { pending_review: '待审核', approved: '已通过', rejected: '已驳回' }
  return map[status] || status
}

function formatTime(time) {
  if (!time) return ''
  return new Date(time).toLocaleString('zh-CN')
}

async function loadMerchants() {
  loading.value = true
  try {
    const data = await api.get('/admin/merchants')
    merchants.value = data
  } catch (e) {
    console.error('加载商户申请失败', e)
  } finally {
    loading.value = false
  }
}

function viewDetail(merchant) {
  currentMerchant.value = merchant
  showDetail.value = true
}

async function handleReview(merchant, action) {
  try {
    await api.put(`/admin/merchants/${merchant.id}/review`, { action })
    ElMessage.success(action === 'approve' ? '已通过' : '已驳回')
    showDetail.value = false
    await loadMerchants()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

function showRejectDialog(merchant) {
  rejectingMerchant.value = merchant
  rejectReason.value = ''
  showReject.value = true
}

async function confirmReject() {
  if (!rejectingMerchant.value || !rejectReason.value.trim()) {
    ElMessage.warning('请填写驳回原因')
    return
  }
  try {
    await api.put(`/admin/merchants/${rejectingMerchant.value.id}/review`, {
      action: 'reject',
      reason: rejectReason.value,
    })
    ElMessage.success('已驳回')
    showReject.value = false
    await loadMerchants()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

onMounted(() => {
  loadMerchants()
})
</script>

<style scoped>
.merchant-manage {
  padding: 0;
}
</style>
