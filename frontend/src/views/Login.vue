<template>
  <div class="login-page">
    <div class="login-card">
      <!-- Logo -->
      <div class="login-logo">
        <div class="logo-icon">✦</div>
        <span>学术导师 AI</span>
      </div>
      <h2 class="login-title">{{ isLogin ? '欢迎回来' : '创建账号' }}</h2>
      <p class="login-sub">{{ isLogin ? '登录以继续使用学术导师 AI' : '注册后即可开始使用' }}</p>

      <el-form :model="form" class="login-form">
        <el-form-item v-if="!isLogin">
          <el-input v-model="form.name" placeholder="你的姓名" size="large" prefix-icon="User" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.email" placeholder="邮箱地址" size="large" prefix-icon="Message" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" placeholder="密码" size="large" prefix-icon="Lock" show-password />
        </el-form-item>
        <el-button
          type="primary" size="large" class="login-btn"
          :loading="loading" @click="handleSubmit"
        >
          {{ isLogin ? '登 录' : '注 册' }}
        </el-button>
      </el-form>

      <p class="login-switch">
        {{ isLogin ? '还没有账号？' : '已有账号？' }}
        <span @click="isLogin = !isLogin">{{ isLogin ? '立即注册' : '去登录' }}</span>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { authAPI } from '../api/index.js'

const router  = useRouter()
const isLogin = ref(true)
const loading = ref(false)
const form    = ref({ name: '', email: '', password: '' })

const handleSubmit = async () => {
  if (!form.value.email || !form.value.password) {
    return ElMessage.warning('请填写邮箱和密码')
  }
  loading.value = true
  try {
    if (isLogin.value) {
      // 登录：发送 JSON 格式，字段名与后端 LoginRequest 一致
      const res = await authAPI.login({
        email: form.value.email,
        password: form.value.password
      })
      localStorage.setItem('token', res.access_token)
      ElMessage.success('登录成功！')
    } else {
      // 注册
      await authAPI.register({
        name: form.value.name,
        email: form.value.email,
        password: form.value.password
      })
      ElMessage.success('注册成功，请登录')
      isLogin.value = true
      return
    }
    router.push('/chat')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '操作失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh; background: linear-gradient(135deg, #eff6ff 0%, #f8f9fc 100%);
  display: flex; align-items: center; justify-content: center;
}
.login-card {
  background: #fff; border-radius: 20px; padding: 48px 40px;
  width: 420px; box-shadow: 0 20px 60px rgba(37,99,235,0.1);
}
.login-logo {
  display: flex; align-items: center; gap: 10px;
  font-size: 18px; font-weight: 700; color: #1e293b; margin-bottom: 28px;
}
.logo-icon {
  width: 36px; height: 36px; background: #2563eb; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  color: white; font-size: 18px;
}
.login-title { font-size: 26px; font-weight: 800; color: #1e293b; }
.login-sub   { color: #94a3b8; font-size: 14px; margin: 6px 0 28px; }
.login-form  { display: flex; flex-direction: column; gap: 4px; }
.login-btn   { width: 100%; margin-top: 8px; height: 46px; font-size: 16px; border-radius: 10px; }
.login-switch { text-align: center; margin-top: 20px; color: #94a3b8; font-size: 14px; }
.login-switch span { color: #2563eb; cursor: pointer; font-weight: 600; }
.login-switch span:hover { text-decoration: underline; }
</style>