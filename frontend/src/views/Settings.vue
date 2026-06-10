<template>
  <div class="settings-page">
    <div class="settings-header">
      <h1>系统设置</h1>
      <p>管理你的账户信息与偏好设置</p>
    </div>

    <div class="settings-content">
      <el-card class="settings-card">
        <template #header>
          <div class="card-header">
            <span>账户信息</span>
          </div>
        </template>
        <el-form label-width="100px">
          <el-form-item label="当前账号">
            <el-input v-model="email" disabled />
          </el-form-item>
          <el-form-item label="修改密码">
            <el-input type="password" placeholder="输入新密码" />
          </el-form-item>
          <el-button type="primary">保存修改</el-button>
        </el-form>
      </el-card>

      <el-card class="settings-card" style="margin-top: 20px;">
        <template #header>
          <div class="card-header">
            <span>系统偏好</span>
          </div>
        </template>
        <el-form label-width="100px">
          <el-form-item label="自动保存">
            <el-switch v-model="autoSave" />
          </el-form-item>
          <el-form-item label="主题模式">
            <el-radio-group v-model="theme">
              <el-radio label="light">浅色模式</el-radio>
              <el-radio label="dark">深色模式</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const email = ref('admin@admin.com')
const autoSave = ref(true)
const theme = ref('light')
</script>

<style scoped>
.settings-page { padding: 32px; max-width: 800px; }
.settings-header { margin-bottom: 30px; }
.settings-header h1 { font-size: 24px; color: #1e293b; }
.settings-header p { color: #94a3b8; margin-top: 8px; }
.settings-card { border-radius: 12px; }
.card-header { font-weight: 600; }
</style>