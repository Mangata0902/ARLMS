<template>
  <div v-if="isBlankLayout" class="blank-layout">
    <router-view />
  </div>

  <div v-else class="layout">
    <!-- 左侧导航栏 -->
    <aside class="sidebar">
      <div class="sidebar-logo">
        <div class="logo-icon">知</div>
        <div class="logo-text-box">
          <div class="logo-title">知己 ScholarMate</div>
          <div class="logo-sub">你的学术陪伴者</div>
        </div>
      </div>

      <div class="new-chat-btn" @click="handleNewChat">
        <el-icon><Plus /></el-icon>
        <span>新建对话</span>
      </div>

      <nav class="nav-menu">
        <div class="nav-section-title">主要功能</div>
        <router-link to="/chat" class="nav-item" active-class="active">
          <el-icon><ChatDotRound /></el-icon><span>AI 导师对话</span>
        </router-link>
        <router-link to="/detection" class="nav-item" active-class="active">
          <el-icon><DocumentChecked /></el-icon><span>论文 AI 检测</span>
        </router-link>
        <router-link to="/revision" class="nav-item" active-class="active">
          <el-icon><EditPen /></el-icon><span>论文修改</span>
        </router-link>

        <div class="nav-section-title" style="margin-top:16px">文献管理</div>
        <router-link to="/ingestion" class="nav-item" active-class="active">
          <el-icon><Upload /></el-icon><span>上传文献</span>
        </router-link>
        <router-link to="/materials" class="nav-item" active-class="active">
          <el-icon><Collection /></el-icon><span>文献库</span>
        </router-link>
        <router-link to="/research" class="nav-item" active-class="active">
          <el-icon><Opportunity /></el-icon><span>选题与大纲</span>
        </router-link>

        <div class="nav-section-title" style="margin-top:16px">设置</div>
        <router-link to="/settings" class="nav-item" active-class="active">
          <el-icon><Setting /></el-icon><span>系统设置</span>
        </router-link>
      </nav>

      <div class="sidebar-slogan">“科研路漫漫，知己一直在。”</div>

      <div class="sidebar-footer">
        <div class="user-avatar">{{ userInitial }}</div>
        <div class="user-info">
          <div class="user-name">{{ userName }}</div>
          <div class="user-role">学术用户</div>
        </div>
        <el-icon class="logout-btn" @click="logout"><SwitchButton /></el-icon>
      </div>
    </aside>

    <!-- 右侧主内容区域：确保这里能渲染出内容 -->
    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from './stores/user.js'
import http from '@/api'
import { ElMessage } from 'element-plus'
// 确保引入了图标，如果你的项目是全局注册的可以忽略
import { Plus, ChatDotRound, DocumentChecked, EditPen, Upload, Collection, Opportunity, Setting, SwitchButton } from '@element-plus/icons-vue'

const route     = useRoute()
const router    = useRouter()
const userStore = useUserStore()

const isBlankLayout = computed(() => route.meta.layout === 'blank')
const userName      = computed(() => userStore.userInfo?.name || '用户')
const userInitial   = computed(() => (userStore.userInfo?.name || 'U')[0].toUpperCase())

const handleNewChat = async () => {
  try {
    const res = await http.post('/sessions', { title: '新对话' })
    router.push(`/chat/${res.session_id}`)
  } catch (e) {
    ElMessage.error('新建会话失败')
  }
}

onMounted(async () => {
  if (localStorage.getItem('token')) {
    try { await userStore.fetchMe() } catch {}
  }
})

const logout = () => {
  userStore.logout()
  router.push('/login')
}
</script>

<style>
/* 重置基础样式 */
* { margin: 0; padding: 0; box-sizing: border-box; }
body, html, #app { height: 100%; width: 100%; }

.layout { display: flex; height: 100vh; width: 100vw; overflow: hidden; }

.sidebar {
  width: 220px; min-width: 220px;
  background: #fff; border-right: 1px solid #eef0f4;
  display: flex; flex-direction: column; padding: 20px 12px;
}
.sidebar-logo { display: flex; align-items: center; gap: 10px; padding: 10px 8px 20px; }
.logo-icon { width: 36px; height: 36px; background: #2563eb; border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; font-weight: 800; font-size: 18px; }
.logo-title { font-weight: 800; font-size: 15px; color: #1e293b; }
.logo-sub { font-size: 11px; color: #94a3b8; }

.new-chat-btn { display: flex; align-items: center; gap: 8px; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 14px; cursor: pointer; color: #475569; font-size: 14px; margin-bottom: 20px; }
.new-chat-btn:hover { background: #f1f5f9; }

.nav-menu { flex: 1; overflow-y: auto; }
.nav-section-title { font-size: 11px; font-weight: 600; color: #94a3b8; text-transform: uppercase; padding: 0 8px; margin-bottom: 4px; }
.nav-item { display: flex; align-items: center; gap: 10px; padding: 9px 10px; border-radius: 8px; color: #475569; font-size: 14px; text-decoration: none; margin-bottom: 2px; }
.nav-item:hover { background: #f1f5f9; }
.nav-item.active { background: #eff6ff; color: #2563eb; font-weight: 600; border-left: 3px solid #2563eb; padding-left: 7px; }

.sidebar-slogan { font-size: 12px; color: #94a3b8; font-style: italic; padding: 15px 12px; text-align: center; border-top: 1px solid #f1f5f9; }
.sidebar-footer { display: flex; align-items: center; gap: 10px; padding: 12px 8px; border-top: 1px solid #eef0f4; }
.user-avatar { width: 34px; height: 34px; background: #2563eb; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 14px; }
.user-info { flex: 1; }
.user-name { font-size: 13px; font-weight: 600; color: #1e293b; }
.user-role { font-size: 11px; color: #94a3b8; }
.logout-btn { color: #94a3b8; cursor: pointer; font-size: 18px; }

/* 核心修复：确保主内容区能显示 */
.main-content { flex: 1; height: 100%; overflow-y: auto; background: #f8f9fc; position: relative; }
</style>
