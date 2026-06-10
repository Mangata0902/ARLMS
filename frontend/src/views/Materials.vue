<template>
  <div class="materials-page">

    <!-- 顶部标题栏 -->
    <div class="page-header">
      <div class="header-left">
        <h1><el-icon><Files /></el-icon> 文献库</h1>
        <p>管理你上传的所有文献，点击「开始对话」可直接跳转到绑定该文献的聊天页</p>
      </div>
      <el-button type="primary" size="large" round @click="$router.push('/ingestion')">
        <el-icon><Upload /></el-icon> 上传新文献
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stat-cards">
      <div class="stat-card">
        <div class="stat-num">{{ total }}</div>
        <div class="stat-label">全部文献</div>
      </div>
      <div class="stat-card">
        <div class="stat-num">{{ localCount }}</div>
        <div class="stat-label">本地上传</div>
      </div>
      <div class="stat-card">
        <div class="stat-num">{{ onlineCount }}</div>
        <div class="stat-label">在线导入</div>
      </div>
    </div>

    <!-- 搜索与筛选 -->
    <div class="toolbar">
      <el-input
        v-model="searchKeyword"
        placeholder="搜索文献标题或作者..."
        clearable
        style="width: 320px"
        @input="handleSearch"
      >
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
      <el-select v-model="filterType" placeholder="全部类型" clearable style="width: 160px" @change="handleSearch">
        <el-option label="全部类型" value="" />
        <el-option label="期刊论文" value="journal" />
        <el-option label="会议论文" value="conference" />
        <el-option label="学位论文" value="thesis" />
        <el-option label="其他" value="other" />
      </el-select>
    </div>

    <!-- 文献列表 -->
    <div class="material-list" v-loading="loading" element-loading-text="加载中...">

      <!-- 空状态 -->
      <div v-if="!loading && filteredMaterials.length === 0" class="empty-state">
        <el-icon class="empty-icon"><FolderOpened /></el-icon>
        <p>暂无文献，点击右上角上传你的第一篇文献</p>
        <el-button type="primary" @click="$router.push('/ingestion')">立即上传</el-button>
      </div>

      <!-- 文献卡片 -->
      <div v-for="m in filteredMaterials" :key="m.material_id" class="material-card">
        <div class="card-left">
          <div class="file-icon" :class="getTypeClass(m.material_type)">
            <el-icon><Document /></el-icon>
          </div>
        </div>

        <div class="card-body">
          <div class="card-title">{{ m.title || '未命名文献' }}</div>
          <div class="card-meta">
            <span v-if="m.author"><el-icon><User /></el-icon> {{ m.author }}</span>
            <span><el-icon><Clock /></el-icon> {{ formatDate(m.created_at) }}</span>
            <el-tag size="small" :type="getTypeTagType(m.material_type)" effect="light">
              {{ getTypeLabel(m.material_type) }}
            </el-tag>
            <el-tag size="small" :type="m.is_local ? 'info' : 'warning'" effect="light">
              {{ m.is_local ? '本地上传' : '在线导入' }}
            </el-tag>
          </div>
        </div>

        <div class="card-actions">
          <el-button type="primary" size="small" round @click="startChat(m)" :loading="m._chatLoading">
            <el-icon><ChatLineSquare /></el-icon> 开始对话
          </el-button>
          <el-button size="small" round @click="goRevision(m)">
            <el-icon><EditPen /></el-icon> 论文修改
          </el-button>
          <el-popconfirm
            :title="`确定删除「${m.title || '该文献'}」吗？`"
            confirm-button-text="确定删除"
            cancel-button-text="取消"
            confirm-button-type="danger"
            width="260"
            @confirm="deleteMaterial(m)"
          >
            <template #reference>
              <el-button size="small" round type="danger" plain :loading="m._deleteLoading">
                <el-icon><Delete /></el-icon> 删除
              </el-button>
            </template>
          </el-popconfirm>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Files, Upload, Search, FolderOpened, Document,
  User, Clock, ChatLineSquare, EditPen, Delete
} from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()

// ===== 状态 =====
const materials       = ref([])
const loading         = ref(false)
const searchKeyword   = ref('')
const filterType      = ref('')

// ===== 统计数据 =====
const total       = computed(() => materials.value.length)
const localCount  = computed(() => materials.value.filter(m => m.is_local).length)
const onlineCount = computed(() => materials.value.filter(m => !m.is_local).length)

// ===== 搜索 + 筛选（纯前端过滤） =====
const filteredMaterials = computed(() => {
  return materials.value.filter(m => {
    const keyword = searchKeyword.value.trim().toLowerCase()
    const matchKeyword = !keyword ||
      (m.title  && m.title.toLowerCase().includes(keyword)) ||
      (m.author && m.author.toLowerCase().includes(keyword))
    const matchType = !filterType.value || m.material_type === filterType.value
    return matchKeyword && matchType
  })
})

const handleSearch = () => {} // 触发 computed 自动响应，无需额外操作

// ===== 加载文献列表 =====
const fetchMaterials = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/v1/materials/')
    materials.value = (res.data.data || []).map(m => ({
      ...m,
      _chatLoading:   false,
      _deleteLoading: false
    }))
  } catch (e) {
    ElMessage.error('加载文献列表失败')
    console.error(e)
  } finally {
    loading.value = false
  }
}

// ===== 删除文献 =====
const deleteMaterial = async (m) => {
  m._deleteLoading = true
  try {
    await axios.delete(`/api/v1/materials/${m.material_id}`)
    ElMessage.success(`「${m.title || '文献'}」已删除`)
    materials.value = materials.value.filter(item => item.material_id !== m.material_id)
  } catch (e) {
    ElMessage.error('删除失败，请稍后重试')
    console.error(e)
  } finally {
    m._deleteLoading = false
  }
}

// ===== 开始对话（创建会话并绑定文献） =====
const startChat = async (m) => {
  m._chatLoading = true
  try {
    const res = await axios.post('/api/v1/sessions', {
      title:          m.title || '新对话',
      active_file_id: m.material_id
    })
    const sessionId = res.data.session_id
    router.push(`/chat/${sessionId}`)
  } catch (e) {
    ElMessage.error('创建对话失败，请稍后重试')
    console.error(e)
  } finally {
    m._chatLoading = false
  }
}

// ===== 跳转论文修改 =====
const goRevision = (m) => {
  router.push({ path: '/revision', query: { material_id: m.material_id, title: m.title } })
}

// ===== 工具函数 =====
const formatDate = (dateStr) => {
  if (!dateStr) return '未知时间'
  const d = new Date(dateStr)
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

const getTypeLabel = (type) => {
  const map = { journal: '期刊论文', conference: '会议论文', thesis: '学位论文', other: '其他' }
  return map[type] || '未知类型'
}

const getTypeTagType = (type) => {
  const map = { journal: 'primary', conference: 'success', thesis: 'warning', other: 'info' }
  return map[type] || 'info'
}

const getTypeClass = (type) => {
  const map = { journal: 'icon-journal', conference: 'icon-conference', thesis: 'icon-thesis', other: 'icon-other' }
  return map[type] || 'icon-other'
}

onMounted(fetchMaterials)
</script>

<style scoped>
.materials-page { padding: 32px; max-width: 1200px; margin: 0 auto; }

/* 顶部标题 */
.page-header {
  display: flex; align-items: flex-start; justify-content: space-between;
  margin-bottom: 28px;
}
.header-left h1 {
  display: flex; align-items: center; gap: 10px;
  font-size: 26px; font-weight: 800; color: #1e293b; margin-bottom: 6px;
}
.header-left p { color: #94a3b8; font-size: 14px; }

/* 统计卡片 */
.stat-cards { display: flex; gap: 16px; margin-bottom: 24px; }
.stat-card {
  flex: 1; background: #fff; border: 1px solid #eef0f4;
  border-radius: 14px; padding: 20px 24px; text-align: center;
}
.stat-num { font-size: 32px; font-weight: 800; color: #2563eb; }
.stat-label { font-size: 13px; color: #94a3b8; margin-top: 4px; }

/* 工具栏 */
.toolbar {
  display: flex; gap: 12px; align-items: center;
  margin-bottom: 20px;
}

/* 空状态 */
.empty-state {
  display: flex; flex-direction: column; align-items: center;
  justify-content: center; padding: 80px 0; gap: 16px;
}
.empty-icon { font-size: 64px; color: #cbd5e1; }
.empty-state p { color: #94a3b8; font-size: 15px; }

/* 文献卡片 */
.material-list { display: flex; flex-direction: column; gap: 12px; }
.material-card {
  display: flex; align-items: center; gap: 16px;
  background: #fff; border: 1px solid #eef0f4; border-radius: 16px;
  padding: 20px 24px; transition: all 0.2s;
}
.material-card:hover { border-color: #bfdbfe; box-shadow: 0 4px 20px rgba(37,99,235,0.08); }

/* 文件图标 */
.file-icon {
  width: 48px; height: 48px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  font-size: 22px; flex-shrink: 0;
}
.icon-journal    { background: #eff6ff; color: #2563eb; }
.icon-conference { background: #f0fdf4; color: #16a34a; }
.icon-thesis     { background: #fffbeb; color: #d97706; }
.icon-other      { background: #f8fafc; color: #64748b; }

/* 卡片内容 */
.card-body { flex: 1; overflow: hidden; }
.card-title {
  font-size: 15px; font-weight: 700; color: #1e293b;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  margin-bottom: 8px;
}
.card-meta {
  display: flex; align-items: center; gap: 12px;
  font-size: 12px; color: #94a3b8; flex-wrap: wrap;
}
.card-meta span { display: flex; align-items: center; gap: 4px; }

/* 操作按钮 */
.card-actions { display: flex; gap: 8px; flex-shrink: 0; }
</style>