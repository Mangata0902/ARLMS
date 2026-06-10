<template>
  <div class="chat-container">
    <!-- 左侧历史侧边栏 -->
    <div class="sidebar">
      <div class="sidebar-header">
        <span class="sidebar-title">历史对话</span>
      </div>
      <div class="session-list" v-loading="loadingSessions">
        <div v-if="sessions.length === 0 && !loadingSessions" class="session-empty">暂无历史对话</div>
        <div
          v-for="s in sessions" :key="s.session_id"
          class="session-item"
          :class="{ active: s.session_id === currentSessionId }"
          @click="switchSession(s.session_id)"
        >
          <el-icon class="session-icon"><ChatLineSquare /></el-icon>
          <div class="session-info">
            <span class="session-title">{{ s.title || '新对话' }}</span>
            <span class="session-preview">{{ s.last_message || '暂无消息' }}</span>
          </div>
          <el-button link class="del-btn" @click.stop="deleteSession(s.session_id)">
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
      </div>
    </div>

    <!-- 右侧聊天主区域 -->
    <div class="chat-page">
      <div class="chat-topbar">
        <span class="model-name">学术导师 AI <el-icon><ArrowDown /></el-icon></span>
        <div v-if="lockedMaterial" class="locked-doc-hint">
          <el-icon><Document /></el-icon>
          <span>当前文献：{{ lockedMaterial }}</span>
          <el-icon class="unlock-btn" title="解除文献绑定" @click="unlockMaterial"><Close /></el-icon>
        </div>
        <div class="topbar-right">
          <el-tag type="warning" effect="light" class="upgrade-tag">✦ 升级到完整版</el-tag>
        </div>
      </div>

      <div class="chat-body" ref="chatBodyRef">
        <!-- 欢迎页 -->
        <div v-if="messages.length === 0 && !loadingMessages" class="chat-welcome">
          <div class="welcome-icon">✦</div>
          <h2>{{ greeting }}</h2>
          <p>我是你的学术导师 AI，可以帮你分析文献、生成大纲、解答学术问题</p>
          <div class="quick-cards">
            <div class="quick-card" @click="quickAsk('帮我分析一篇文献的研究方法')">
              <el-icon><Document /></el-icon>
              <div><div class="card-title">文献分析</div><div class="card-desc">深度解析文献研究方法与结论</div></div>
            </div>
            <div class="quick-card" @click="quickAsk('帮我生成一个关于机器学习的论文大纲')">
              <el-icon><EditPen /></el-icon>
              <div><div class="card-title">大纲生成</div><div class="card-desc">快速生成结构化论文大纲</div></div>
            </div>
            <div class="quick-card" @click="quickAsk('解释一下什么是RAG技术')">
              <el-icon><Reading /></el-icon>
              <div><div class="card-title">学术问答</div><div class="card-desc">解答各类学术概念与问题</div></div>
            </div>
          </div>
        </div>

        <div v-if="loadingMessages" class="loading-messages">
          <el-icon class="is-loading"><Loading /></el-icon> 加载历史消息中...
        </div>

        <div v-for="(msg, i) in messages" :key="i" class="message-row" :class="msg.role">
          <div class="msg-avatar" v-if="msg.role === 'assistant'">✦</div>
          <div class="msg-bubble" :class="msg.role">
            <span v-if="msg.loading" class="typing"><span></span><span></span><span></span></span>
            <span v-else>{{ msg.content }}</span>
          </div>
          <div class="msg-avatar user-av" v-if="msg.role === 'user'">我</div>
        </div>
      </div>

      <div class="chat-input-area">
        <div class="input-box">
          <el-input
            v-model="inputText" type="textarea" :autosize="{ minRows: 1, maxRows: 4 }"
            placeholder="问我任何学术问题..." resize="none" @keydown.enter.exact.prevent="sendMessage"
          />
          <div class="input-actions">
            <el-button text @click="$router.push('/ingestion')"><el-icon><Paperclip /></el-icon> 上传文献</el-button>
            <el-button type="primary" circle :disabled="!inputText.trim() || loading" @click="sendMessage">
              <el-icon><Top /></el-icon>
            </el-button>
          </div>
        </div>
        <p class="input-tip">学术导师 AI 以你上传的文献为知识库进行回答</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, watch, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  ChatLineSquare, ArrowDown, Document, Close,
  EditPen, Reading, Paperclip, Top, Loading, Delete
} from '@element-plus/icons-vue'
import http from '@/api'

const route  = useRoute()
const router = useRouter()

const messages          = ref([])
const inputText         = ref('')
const loading           = ref(false)
const chatBodyRef       = ref(null)
const sessions          = ref([])
const currentSessionId  = ref(null)
const activeFileId      = ref(null)
const loadingSessions   = ref(false)
const loadingMessages   = ref(false)
const creatingSession   = ref(false)
const lockedMaterial    = ref(null)

const scrollToBottom = async () => {
  await nextTick()
  if (chatBodyRef.value) chatBodyRef.value.scrollTop = chatBodyRef.value.scrollHeight
}

const quickAsk = (text) => {
  inputText.value = text
  sendMessage()
}

const fetchSessions = async () => {
  loadingSessions.value = true
  try {
    const res = await http.get('/sessions')
    sessions.value = res.data || []
  } catch (e) {
    console.error('加载历史会话失败', e)
  } finally {
    loadingSessions.value = false
  }
}

const loadMessages = async (sessionId) => {
  if (!sessionId) return
  loadingMessages.value = true
  messages.value = []
  try {
    const res = await http.get(`/history?session_id=${sessionId}`)
    messages.value = (res.data || []).map(m => ({ role: m.role, content: m.content, loading: false }))
    await scrollToBottom()
  } catch (e) {
    console.error('加载历史消息失败', e)
  } finally {
    loadingMessages.value = false
  }
}

const loadSessionDetail = async (sessionId) => {
  if (!sessionId) {
    lockedMaterial.value = null
    activeFileId.value   = null
    return
  }
  try {
    const res = await http.get(`/sessions/${sessionId}`)
    const session = res
    if (session?.material_info?.title) {
      lockedMaterial.value = session.material_info.title
      activeFileId.value   = session.material_info.material_id
    } else if (session?.active_file_id) {
      activeFileId.value   = session.active_file_id
      lockedMaterial.value = `文献 #${session.active_file_id}`
    }
  } catch (e) {
    console.error('加载会话详情失败', e)
  }
}

const unlockMaterial = async () => {
  if (!currentSessionId.value) return
  try {
    await http.patch(`/sessions/${currentSessionId.value}`, { clear_file: true })
    lockedMaterial.value = null
    activeFileId.value   = null
    ElMessage.success('已解除文献绑定')
  } catch (e) {
    ElMessage.error('解除绑定失败')
  }
}

const switchSession = (sessionId) => {
  if (sessionId === currentSessionId.value) return
  router.push(`/chat/${sessionId}`)
}

const greeting = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '深夜了，还在忙吗？'
  if (hour < 12) return '早安！今天也是充满灵感的一天。'
  if (hour < 18) return '下午好，知己时刻准备着。'
  return '晚上好，今晚我们一起攻克哪部分内容？'
})



// ===== 删除会话 =====
const deleteSession = async (sessionId) => {
  try {
    await http.delete(`/sessions/${sessionId}`)
    ElMessage.success('已删除')
    await fetchSessions()
    if (currentSessionId.value == sessionId) {
      currentSessionId.value = null
      messages.value = []
      router.push('/chat')
    }
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

// ===== 发送消息（流式版本）=====
const sendMessage = async () => {
  const text = inputText.value.trim()
  if (!text || loading.value) return

  // 若无会话，先自动新建
  if (!currentSessionId.value) {
    creatingSession.value = true
    try {
      const res = await http.post('/sessions', { title: text.slice(0, 20) })
      // ✅ 拦截器已解包，直接用 res.session_id
      currentSessionId.value = res.session_id
      router.replace(`/chat/${currentSessionId.value}`)
      await fetchSessions()
    } catch {
      ElMessage.error('创建会话失败，请重试')
      creatingSession.value = false
      return
    }
    creatingSession.value = false
  }

  // 添加用户消息 & 占位 AI 消息
  messages.value.push({ role: 'user', content: text })
  inputText.value = ''
  loading.value = true
  messages.value.push({ role: 'assistant', content: '', loading: true })
  await scrollToBottom()

  try {
    const payload = {
      user_message: text,
      session_id:   currentSessionId.value,
      ...(activeFileId.value ? { material_id: activeFileId.value } : {})
    }

    const token = localStorage.getItem('token')
    const response = await fetch('/api/v1/chat/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(payload)
    })

    if (!response.ok) throw new Error(`HTTP 错误：${response.status}`)

    const reader  = response.body.getReader()
    const decoder = new TextDecoder('utf-8')

    messages.value[messages.value.length - 1].loading = false

    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop()

      for (const line of lines) {
        const trimmed = line.trim()
        if (!trimmed || !trimmed.startsWith('data: ')) continue

        const dataStr = trimmed.slice(6)
        if (dataStr === '[DONE]') continue

        try {
          const data = JSON.parse(dataStr)
          if (data.content) {
            messages.value[messages.value.length - 1].content += data.content
            await scrollToBottom()
          }
        } catch {
          // 忽略解析失败的行
        }
      }
    }

    fetchSessions()

  } catch (e) {
    console.error('流式请求失败', e)
    messages.value[messages.value.length - 1] = {
      role: 'assistant',
      content: '抱歉，请求失败，请稍后重试。',
      loading: false
    }
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}

// ===== 监听路由变化 =====
watch(
  () => route.params.session_id,
  async (newId) => {
    currentSessionId.value = newId || null
    messages.value = []
    await Promise.all([
      loadMessages(newId),
      loadSessionDetail(newId)
    ])
  }
)

// ===== 初始化 =====
onMounted(async () => {
  const sid = route.params.session_id || null
  currentSessionId.value = sid
  await Promise.all([
    fetchSessions(),
    loadMessages(sid),
    loadSessionDetail(sid)
  ])
})
</script>

<style scoped>
.chat-container { display: flex; height: 100vh; overflow: hidden; }

.sidebar {
  width: 260px; min-width: 260px;
  background: #f8fafc; border-right: 1px solid #eef0f4;
  display: flex; flex-direction: column; padding: 16px 12px;
}
.sidebar-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #eef0f4;
}
.sidebar-title { font-size: 14px; font-weight: 700; color: #1e293b; }
.session-list { flex: 1; overflow-y: auto; }
.session-empty { text-align: center; color: #94a3b8; font-size: 13px; padding: 30px 0; }
.session-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px; border-radius: 10px; cursor: pointer;
  margin-bottom: 4px; transition: background 0.15s; position: relative;
}
.session-item:hover { background: #e2e8f0; }
.session-item.active { background: #dbeafe; }
.session-item.active .session-title { color: #2563eb; }
.session-icon { color: #94a3b8; font-size: 16px; flex-shrink: 0; }
.session-item.active .session-icon { color: #2563eb; }
.session-info { flex: 1; overflow: hidden; padding-right: 20px; }
.session-title {
  display: block; font-size: 13px; font-weight: 600; color: #1e293b;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.session-preview {
  display: block; font-size: 11px; color: #94a3b8;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.del-btn {
  position: absolute; right: 8px;
  opacity: 0; transition: opacity 0.2s; color: #94a3b8;
}
.session-item:hover .del-btn { opacity: 1; }
.del-btn:hover { color: #f56c6c; }

.chat-page { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.chat-topbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 16px 32px; background: #fff; border-bottom: 1px solid #eef0f4; flex-shrink: 0;
}
.model-name {
  display: flex; align-items: center; gap: 6px;
  font-weight: 700; font-size: 15px; color: #1e293b; cursor: pointer;
}
.locked-doc-hint {
  display: flex; align-items: center; gap: 6px;
  font-size: 12px; color: #2563eb; background: #eff6ff;
  border: 1px solid #bfdbfe; border-radius: 20px; padding: 4px 12px;
}
.unlock-btn { cursor: pointer; color: #93c5fd; margin-left: 2px; transition: color 0.15s; }
.unlock-btn:hover { color: #ef4444; }
.upgrade-tag { cursor: pointer; font-size: 13px; }

.chat-body {
  flex: 1; overflow-y: auto; padding: 32px;
  display: flex; flex-direction: column; gap: 20px;
}
.loading-messages {
  display: flex; align-items: center; justify-content: center;
  gap: 8px; color: #94a3b8; font-size: 14px; padding: 40px 0;
}
.chat-welcome {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; justify-content: center; text-align: center; padding: 60px 20px;
}
.welcome-icon {
  width: 64px; height: 64px; background: #2563eb; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  color: white; font-size: 28px; margin-bottom: 20px;
}
.chat-welcome h2 { font-size: 28px; font-weight: 800; color: #1e293b; margin-bottom: 10px; }
.chat-welcome p  { color: #94a3b8; font-size: 15px; margin-bottom: 40px; }
.quick-cards { display: flex; gap: 16px; flex-wrap: wrap; justify-content: center; }
.quick-card {
  display: flex; align-items: flex-start; gap: 12px;
  background: #fff; border: 1px solid #e2e8f0; border-radius: 14px;
  padding: 18px 20px; width: 200px; cursor: pointer; transition: all 0.2s; text-align: left;
}
.quick-card:hover { border-color: #2563eb; box-shadow: 0 4px 20px rgba(37,99,235,0.1); }
.quick-card .el-icon { font-size: 22px; color: #2563eb; margin-top: 2px; }
.card-title { font-weight: 600; font-size: 14px; color: #1e293b; }
.card-desc  { font-size: 12px; color: #94a3b8; margin-top: 4px; line-height: 1.4; }

.message-row { display: flex; align-items: flex-start; gap: 12px; }
.message-row.user { flex-direction: row-reverse; }
.msg-avatar {
  width: 34px; height: 34px; min-width: 34px; background: #2563eb;
  border-radius: 50%; display: flex; align-items: center;
  justify-content: center; color: white; font-size: 14px; font-weight: 700;
}
.user-av { background: #64748b; }
.msg-bubble {
  max-width: 65%; padding: 14px 18px; border-radius: 16px;
  font-size: 14px; line-height: 1.7; white-space: pre-wrap;
}
.msg-bubble.assistant { background: #fff; border: 1px solid #eef0f4; color: #1e293b; }
.msg-bubble.user { background: #2563eb; color: white; border-radius: 16px 16px 4px 16px; }

.typing { display: flex; gap: 4px; padding: 4px 0; }
.typing span {
  width: 7px; height: 7px; background: #94a3b8;
  border-radius: 50%; animation: bounce 1.2s infinite;
}
.typing span:nth-child(2) { animation-delay: 0.2s; }
.typing span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); }
  30%           { transform: translateY(-6px); }
}

.chat-input-area {
  padding: 20px 32px 24px; background: #fff;
  border-top: 1px solid #eef0f4; flex-shrink: 0;
}
.input-box {
  background: #f8f9fc; border: 1px solid #e2e8f0; border-radius: 14px; padding: 12px 16px;
}
.input-box :deep(.el-textarea__inner) {
  background: transparent; border: none; box-shadow: none; font-size: 14px; color: #1e293b; padding: 0;
}
.input-actions {
  display: flex; justify-content: space-between; align-items: center; margin-top: 10px;
}
.input-tip { text-align: center; font-size: 12px; color: #cbd5e1; margin-top: 10px; }
</style>
