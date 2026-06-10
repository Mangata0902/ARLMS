<template>
  <div class="page">
    <div class="page-header">
      <h1>上传文献</h1>
      <p>上传 PDF 或 DOCX 文献，AI 将自动解析并加入你的知识库，供导师对话使用</p>
    </div>

    <div class="mode-card">
      <h4><el-icon><Setting /></el-icon> 选择上传模式</h4>
      <el-radio-group v-model="taskType" size="large">
        <el-radio-button label="reference">
          <el-icon><Reading /></el-icon> 文献参考（加入 RAG 知识库）
        </el-radio-button>
        <el-radio-button label="revision">
          <el-icon><EditPen /></el-icon> 论文修改（润色 / 降重）
        </el-radio-button>
      </el-radio-group>
      <p class="mode-hint">
        <template v-if="taskType === 'reference'">
          文件将被解析并向量化，AI 导师对话时会自动引用其内容作为参考依据
        </template>
        <template v-else>
          文件将进入论文修改流程，AI 将对你的论文进行润色、降重或结构优化
        </template>
      </p>
    </div>

    <div class="upload-card">
      <el-upload
        class="uploader"
        drag multiple
        :auto-upload="false"
        :on-change="handleAdd"
        :on-remove="handleRemove"
        :file-list="fileList"
        accept=".pdf,.docx,.doc,.txt"
      >
        <div class="upload-inner">
          <el-icon class="upload-icon"><UploadFilled /></el-icon>
          <h3>拖拽文献文件到此处</h3>
          <p>支持 PDF、DOCX、TXT，可批量上传</p>
          <el-button type="primary" plain style="border-radius:20px;margin-top:12px">
            选择文件
          </el-button>
        </div>
      </el-upload>

      <div v-if="fileList.length > 0" class="file-list-area">
        <div class="file-list-header">
          <span>已选择 {{ fileList.length }} 个文件</span>
          <el-button
            type="primary" :loading="loading" @click="uploadAll"
            style="border-radius:20px"
          >
            <el-icon><Upload /></el-icon> 全部上传
          </el-button>
        </div>

        <div v-for="(file, i) in fileList" :key="i" class="file-row">
          <div class="file-icon">
            <el-icon><Document /></el-icon>
          </div>
          <div class="file-info">
            <span class="file-name">{{ file.name }}</span>
            <span class="file-size">{{ (file.size / 1024).toFixed(1) }} KB</span>
          </div>
          <el-tag
            :type="taskType === 'reference' ? 'primary' : 'warning'"
            size="small"
            style="margin-right:8px"
          >
            {{ taskType === 'reference' ? '文献参考' : '论文修改' }}
          </el-tag>
          <div class="file-status">
            <el-tag v-if="file.status === 'done'"            type="success">✓ 上传成功</el-tag>
            <el-tag v-else-if="file.status === 'fail'"       type="danger">✗ 上传失败</el-tag>
            <el-tag v-else-if="file.status === 'uploading'"  type="warning">上传中...</el-tag>
            <el-tag v-else type="info">待上传</el-tag>
          </div>
        </div>
      </div>
    </div>

    <div v-if="uploadSummary" class="summary-card">
      <div class="summary-item success">
        <el-icon><CircleCheckFilled /></el-icon>
        <span>成功 {{ uploadSummary.success }} 个</span>
      </div>
      <div v-if="uploadSummary.fail > 0" class="summary-item fail">
        <el-icon><CircleCloseFilled /></el-icon>
        <span>失败 {{ uploadSummary.fail }} 个</span>
      </div>

      <template v-if="taskType === 'reference'">
        <el-button
          v-if="latestSessionId"
          type="primary" text
          @click="$router.push(`/chat/${latestSessionId}`)"
          class="go-chat-btn"
        >
          进入 AI 导师对话 <el-icon><ArrowRight /></el-icon>
        </el-button>
        <el-button v-else text @click="$router.push('/chat')" class="go-chat-btn">
          去 AI 导师对话 <el-icon><ArrowRight /></el-icon>
        </el-button>
      </template>
      <template v-else>
        <el-button text @click="$router.push('/revision')" class="go-chat-btn">
          去论文修改页面 <el-icon><ArrowRight /></el-icon>
        </el-button>
      </template>
    </div>

    <div class="tips-card">
      <h4><el-icon><InfoFilled /></el-icon> 使用说明</h4>
      <ul>
        <li>上传后，文献内容将自动加入你的个人知识库</li>
        <li>在「AI 导师对话」中提问时，AI 会优先参考你上传的文献</li>
        <li>建议上传与你研究方向相关的核心文献（5-20 篇效果最佳）</li>
        <li>支持中英文文献混合上传</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ingestionAPI, chatAPI } from '../api/index.js'  // ✅ 引入 chatAPI，移除裸 axios

const router = useRouter()

const fileList        = ref([])
const loading         = ref(false)
const uploadSummary   = ref(null)
const taskType        = ref('reference')
const latestSessionId = ref(null)

const handleAdd    = (file) => { fileList.value.push({ ...file, status: 'ready' }) }
const handleRemove = (file) => { fileList.value = fileList.value.filter(f => f.uid !== file.uid) }

const uploadAll = async () => {
  if (fileList.value.length === 0) return
  loading.value = true
  uploadSummary.value = null
  latestSessionId.value = null
  let success = 0, fail = 0

  for (const file of fileList.value) {
    if (file.status === 'done') { success++; continue }
    file.status = 'uploading'

    const formData = new FormData()
    formData.append('file', file.raw)
    formData.append('type', taskType.value)

    try {
      const uploadRes = await ingestionAPI.upload(formData)
      file.status = 'done'
      success++

      // ✅ 拦截器已解包，直接用 uploadRes.file_id，不再需要 uploadRes.data.file_id
      if (taskType.value === 'reference') {
        try {
          const fileId = uploadRes?.file_id ?? uploadRes?.material_id ?? null
          if (fileId) {
            const sessionRes = await chatAPI.createSession({
              title:          file.name,
              active_file_id: fileId
            })
            // ✅ 同样直接取 session_id
            latestSessionId.value = sessionRes?.session_id ?? null
          }
        } catch (sessionErr) {
          console.warn(`会话创建失败（${file.name}）:`, sessionErr)
        }
      }

    } catch {
      file.status = 'fail'
      fail++
    }
  }

  loading.value = false
  uploadSummary.value = { success, fail }
  if (fail === 0) ElMessage.success(`全部上传成功！共 ${success} 个文件`)
  else            ElMessage.warning(`上传完成：${success} 成功，${fail} 失败`)
}
</script>

<style scoped>
.page { padding: 32px; max-width: 800px; margin: 0 auto; }
.page-header { margin-bottom: 28px; }
.page-header h1 { font-size: 26px; font-weight: 800; color: #1e293b; }
.page-header p  { color: #94a3b8; margin-top: 6px; font-size: 14px; }

.mode-card {
  background: #fff; border-radius: 20px; padding: 22px 28px;
  border: 1px solid #eef0f4; margin-bottom: 20px;
}
.mode-card h4 {
  display: flex; align-items: center; gap: 8px;
  font-size: 14px; font-weight: 700; color: #1e293b; margin-bottom: 14px;
}
.mode-hint {
  margin-top: 12px; font-size: 13px; color: #64748b;
  background: #f8f9fc; border-radius: 10px; padding: 10px 14px;
  border-left: 3px solid #2563eb;
}

.upload-card {
  background: #fff; border-radius: 20px; padding: 28px;
  border: 1px solid #eef0f4; margin-bottom: 20px;
}
.uploader { width: 100%; }
.upload-inner { padding: 40px 20px; text-align: center; }
.upload-icon  { font-size: 52px; color: #2563eb; margin-bottom: 14px; }
.upload-inner h3 { font-size: 17px; font-weight: 700; color: #1e293b; margin-bottom: 6px; }
.upload-inner p  { color: #94a3b8; font-size: 13px; }

.file-list-area { margin-top: 20px; border-top: 1px solid #f1f5f9; padding-top: 20px; }
.file-list-header {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 14px; font-size: 13px; color: #64748b; font-weight: 600;
}
.file-row {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 14px; border-radius: 10px; margin-bottom: 8px;
  background: #f8f9fc; border: 1px solid #eef0f4;
}
.file-icon { color: #2563eb; font-size: 20px; }
.file-info { flex: 1; }
.file-name { font-size: 14px; font-weight: 500; color: #1e293b; display: block; }
.file-size { font-size: 12px; color: #94a3b8; }

.summary-card {
  background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 16px;
  padding: 18px 24px; display: flex; align-items: center; gap: 20px;
  margin-bottom: 20px;
}
.summary-item { display: flex; align-items: center; gap: 6px; font-weight: 600; font-size: 14px; }
.summary-item.success { color: #16a34a; }
.summary-item.fail    { color: #dc2626; }
.go-chat-btn { margin-left: auto; color: #2563eb; font-weight: 600; }

.tips-card {
  background: #eff6ff; border: 1px solid #bfdbfe;
  border-radius: 16px; padding: 20px 24px;
}
.tips-card h4 {
  display: flex; align-items: center; gap: 8px;
  font-size: 14px; font-weight: 700; color: #1e40af; margin-bottom: 12px;
}
.tips-card ul { padding-left: 20px; }
.tips-card li { font-size: 13px; color: #1e40af; line-height: 2; }
</style>
