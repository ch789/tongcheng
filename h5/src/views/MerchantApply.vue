<template>
  <div class="merchant-apply-page">
    <van-nav-bar title="商户入驻申请" left-arrow @click-left="$router.back()" />

    <van-form @submit="handleSubmit">
      <van-cell-group inset>
        <van-field
          v-model="form.shop_name"
          name="shop_name"
          label="商户名称"
          placeholder="请输入商户名称"
          required
          :rules="[{ required: true, message: '请输入商户名称' }]"
        />
        <van-field
          v-model="form.industry_name"
          name="industry_name"
          label="所属行业"
          placeholder="请选择所属行业"
          is-link
          required
          :rules="[{ required: true, message: '请选择所属行业' }]"
          @click="showIndustryPicker = true"
        />
        <van-field
          v-model="form.area"
          name="area"
          label="所在区域"
          placeholder="请选择所在区域"
          is-link
          required
          :rules="[{ required: true, message: '请选择所在区域' }]"
          @click="showAreaPicker = true"
        />
        <van-field
          v-model="form.contact_phone"
          name="contact_phone"
          label="联系电话"
          placeholder="请输入联系电话"
          type="tel"
          required
        />
        <van-field
          v-model="form.address"
          name="address"
          label="经营地址"
          placeholder="请输入经营地址"
        />
        <van-field
          v-model="form.description"
          name="description"
          label="简介"
          placeholder="请输入商户简介"
          type="textarea"
          rows="3"
        />
      </van-cell-group>

      <div style="margin: 16px;">
        <van-uploader
          v-model="licenseFiles"
          :max-count="1"
          accept="image/*"
          :http-request="handleCustomUpload"
        >
          <div class="upload-tip">上传营业执照（可选）</div>
        </van-uploader>
      </div>

      <div style="padding: 0 16px 16px;">
        <van-button type="primary" block native-type="submit" :loading="submitting">
          提交申请
        </van-button>
      </div>
    </van-form>

    <!-- 行业选择器 -->
    <van-popup v-model:show="showIndustryPicker" position="bottom" round>
      <van-picker
        :columns="industryOptions"
        @confirm="onIndustryConfirm"
        @cancel="showIndustryPicker = false"
      />
    </van-popup>

    <!-- 区域选择器 -->
    <van-popup v-model:show="showAreaPicker" position="bottom" round>
      <van-picker
        :columns="areaOptions"
        @confirm="onAreaConfirm"
        @cancel="showAreaPicker = false"
      />
    </van-popup>

    <!-- 已有申请状态展示 -->
    <van-cell-group inset v-if="existingApp">
      <van-cell title="申请状态" :value="getStatusText(existingApp.status)" />
      <van-cell title="商户名称" :value="existingApp.shop_name" />
      <van-cell title="所属行业" :value="existingApp.industry_name || '-'" />
      <van-cell title="所在区域" :value="existingApp.area || '-'" />
      <van-cell v-if="existingApp.reject_reason" title="驳回原因" :value="existingApp.reject_reason" />
    </van-cell-group>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showFailToast } from 'vant'
import { applyMerchant, getMyMerchant } from '@/api/users'
import { uploadImage } from '@/api/upload'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const submitting = ref(false)
const licenseFiles = ref<any[]>([])
const existingApp = ref<any>(null)
const showIndustryPicker = ref(false)
const showAreaPicker = ref(false)

const form = ref({
  shop_name: '',
  industry_name: '',
  area: '',
  contact_phone: '',
  address: '',
  description: '',
})

const industryOptions = [
  { text: '餐饮美食', value: '餐饮美食' },
  { text: '装修建材', value: '装修建材' },
  { text: '家政服务', value: '家政服务' },
  { text: '教育培训', value: '教育培训' },
  { text: '法律服务', value: '法律服务' },
  { text: '医疗健康', value: '医疗健康' },
  { text: '汽车服务', value: '汽车服务' },
  { text: '商贸批发', value: '商贸批发' },
  { text: '休闲娱乐', value: '休闲娱乐' },
  { text: '房产服务', value: '房产服务' },
  { text: '美容美发', value: '美容美发' },
  { text: '物流快递', value: '物流快递' },
]

const areaOptions = [
  { text: '南开区', value: '南开区' },
  { text: '河西区', value: '河西区' },
  { text: '滨海新区', value: '滨海新区' },
  { text: '和平区', value: '和平区' },
  { text: '河北区', value: '河北区' },
  { text: '红桥区', value: '红桥区' },
  { text: '东丽区', value: '东丽区' },
  { text: '西青区', value: '西青区' },
]

function getStatusText(status: string) {
  const map: Record<string, string> = {
    pending_review: '待审核',
    approved: '已通过',
    rejected: '已驳回',
  }
  return map[status] || status
}

async function loadMyApplication() {
  try {
    const res = await getMyMerchant()
    if (res) {
      existingApp.value = res
      form.value.shop_name = res.shop_name || ''
      form.value.industry_name = res.industry_name || ''
      form.value.area = res.area || ''
      form.value.contact_phone = res.contact_phone || ''
      form.value.address = res.address || ''
      form.value.description = res.description || ''
    }
  } catch (e) {
    // 未登录或无申请记录，忽略
  }
}

function onIndustryConfirm({ selectedOptions }: any) {
  if (selectedOptions && selectedOptions.length > 0) {
    form.value.industry_name = selectedOptions[0].value
  }
  showIndustryPicker.value = false
}

function onAreaConfirm({ selectedOptions }: any) {
  if (selectedOptions && selectedOptions.length > 0) {
    form.value.area = selectedOptions[0].value
  }
  showAreaPicker.value = false
}

async function handleCustomUpload(options: any) {
  const { file, onSuccess, onError } = options
  try {
    const res = await uploadImage(file as File)
    if (res.compressed) showFailToast('图片已自动压缩')
    onSuccess(res)
  } catch (e: any) {
    showFailToast(e?.response?.data?.detail || '上传失败，请重试')
    onError(e)
  }
}

async function handleSubmit() {
  if (!userStore.isLoggedIn) {
    showToast('请先登录')
    router.push('/login')
    return
  }
  if (!form.value.shop_name || !form.value.industry_name || !form.value.area || !form.value.contact_phone) {
    showToast('请填写完整信息')
    return
  }

  submitting.value = true
  try {
    const payload = {
      shop_name: form.value.shop_name,
      industry_name: form.value.industry_name,
      area: form.value.area,
      contact_phone: form.value.contact_phone,
      address: form.value.address,
      description: form.value.description,
      business_license: licenseFiles.value[0]?.url || licenseFiles.value[0]?.link,
    }
    await applyMerchant(payload)
    showToast('申请已提交，等待审核')
    setTimeout(() => router.push('/profile'), 1500)
  } catch (error: any) {
    showToast(error?.detail || '提交失败，请重试')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadMyApplication()
})
</script>

<style scoped>
.merchant-apply-page {
  min-height: 100vh;
  background: #f7f8fa;
}

.upload-tip {
  width: 100%;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f7f8fa;
  border: 1px dashed #ddd;
  border-radius: 8px;
  color: #999;
  font-size: 14px;
}
</style>
