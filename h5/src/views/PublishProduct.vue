<template>
  <div class="publish-product-page">
    <van-nav-bar title="发布产品" left-arrow @click-left="$router.back()" />

    <van-form @submit="handleSubmit">
      <van-cell-group inset>
        <van-field
          v-model="form.title"
          name="title"
          label="产品标题"
          placeholder="请输入产品标题"
          required
          :rules="[{ required: true, message: '请输入产品标题' }]"
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
          v-model="form.description"
          name="description"
          label="产品简介"
          placeholder="请输入产品简介"
          type="textarea"
          rows="3"
        />
      </van-cell-group>

      <div style="margin: 16px;">
        <van-uploader
          v-model="imageFiles"
          :max-count="5"
          accept="image/*"
          :http-request="handleCustomUpload"
        >
          <div class="upload-tip">上传产品图片（可选）</div>
        </van-uploader>
      </div>

      <div style="padding: 0 16px 16px;">
        <van-button type="primary" block native-type="submit" :loading="submitting">
          提交审核
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showToast, showFailToast } from 'vant'
import { createProduct, getIndustries } from '@/api/products'
import { uploadImage } from '@/api/upload'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const submitting = ref(false)
const imageFiles = ref<any[]>([])
const showIndustryPicker = ref(false)
const showAreaPicker = ref(false)
const industries = ref<any[]>([])

const form = ref({
  title: '',
  industry_name: '',
  area: '',
  contact_phone: '',
  description: '',
})

const industryOptions = ref<{ text: string; value: string }[]>([])
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

async function loadIndustries() {
  try {
    industries.value = await getIndustries()
    industryOptions.value = industries.value.map((ind: any) => ({
      text: ind.name,
      value: ind.name,
    }))
  } catch (e) {
    console.error('加载行业失败', e)
  }
}

function onIndustryConfirm(event: any) {
  const options = event?.selectedOptions
  if (options && options.length > 0) {
    form.value.industry_name = options[0].value
  }
  showIndustryPicker.value = false
}

function onAreaConfirm(event: any) {
  const options = event?.selectedOptions
  if (options && options.length > 0) {
    form.value.area = options[0].value
  }
  showAreaPicker.value = false
}

async function handleCustomUpload(options: any) {
  const { file, onProgress, onSuccess, onError } = options
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
  if (!form.value.title || !form.value.industry_name || !form.value.area || !form.value.contact_phone) {
    showToast('请填写完整信息')
    return
  }

  submitting.value = true
  try {
    // 找到行业ID
    const industry = industries.value.find((i: any) => i.name === form.value.industry_name)
    const payload = {
      title: form.value.title,
      description: form.value.description,
      images: imageFiles.value.map((f: any) => f.url || f.response?.url || '').filter(Boolean),
      industry_id: industry?.id || 0,
      area: form.value.area,
      contact_phone: form.value.contact_phone,
    }
    await createProduct(payload)
    showToast('提交成功，等待审核')
    setTimeout(() => router.push('/my-products'), 1500)
  } catch (error: any) {
    showToast(error?.detail || '提交失败，请重试')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  loadIndustries()
})
</script>

<style scoped>
.publish-product-page {
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
