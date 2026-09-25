<template>
  <router-view />
  <BottomNav />
</template>

<script setup lang="ts">
import BottomNav from '@/components/BottomNav.vue'
</script>

<style>
:root {
  --primary-color: #1a73e8;
  --primary-light: #e8f0fe;
  --primary-dark: #1558b0;
  --accent-color: #ff9800;
  --bg-color: #f5f7fa;
  --card-bg: #ffffff;
  --text-primary: #1a1a1a;
  --text-secondary: #666666;
  --text-muted: #999999;
  --border-color: #e8e8e8;
  --shadow-sm: 0 1px 4px rgba(0,0,0,0.06);
  --shadow-md: 0 4px 16px rgba(0,0,0,0.08);
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
}
</style>
