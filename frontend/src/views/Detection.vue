<template>
  <div class="page">
    <div class="page-header">
      <h1>论文 AI 检测</h1>
      <p>上传论文文件，基于 DeepSeek 模型深度分析 AI 生成概率并提供降重建议</p>
    </div>

    <!-- 上传区域（未检测时） -->
    <div v-if="!result" class="upload-section">
      <el-upload
        class="upload-dragger"
        drag
        :auto-upload="false"
        :on-change="handleFileChange"
        accept=".pdf,.docx,.doc,.txt"
        :show-file-list="false"
      >
        <div class="upload-inner">
          <el-icon class="upload-icon"><UploadFilled /></el-icon>
          <h3>拖拽论文文件到此处</h3>
          <p>支持 PDF、DOCX、TXT，最大 20MB</p>
          <el-button type="primary" class="select-btn">选择文件</el-button>
        </div>
      </el-upload>

      <div v-if="selectedFile" class="file-preview">
        <el-icon><Document /></el-icon>
        <span>{{ selectedFile.name }}</span>
        <el-tag type="info">{{ (selectedFile.size / 1024).toFixed(1) }} KB</el-tag>
        <el-button type="primary" :loading="loading" @click="startDetect" class="detect-btn">
          开始检测
        </el-button>
      </div>
    </div>

    <!-- 检测结果 -->
    <div v-else class="result-section">
      <div class="result-grid">
        <!-- 左侧：评分卡 -->
        <div class="score-card">
          <h3>检测结果</h3>
          <div class="score-circle-wrap">
            <svg viewBox="0 0 120 120" class="score-svg">
              <circle cx="60" cy="60" r="50" fill="none" stroke="#f1f5f9" stroke-width="10"/>
              <circle
                cx="60" cy="60" r="50" fill="none"
                :stroke="scoreColor" stroke-width="10"
                stroke-linecap="round"
                :stroke-dasharray="314"
                :stroke-dashoffset="314 * (1 - result.ai_score)"
                transform="rotate(-90 60 60)"
                style="transition: stroke-dashoffset 1s ease"
              />
            </svg>
            <div class="score-text">
              <span class="score-num">{{ result.percentage }}</span>
              <span class="score-label">AI 概率</span>
            </div>
          </div>
          <div class="risk-badge" :class="riskClass">{{ result.level }}</div>
          <div class="score-meta">
            <div class="meta-item">
              <span class="meta-label">检测段落</span>
              <span class="meta-val">{{ result.chunks_checked }} / {{ result.total_chunks }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">总字符数</span>
              <span class="meta-val">{{ result.total_chars?.toLocaleString() }}</span>
            </div>
          </div>
          <el-button class="download-btn" @click="downloadReport" :loading="downloading">
            <el-icon><Download /></el-icon> 下载 PDF 报告
          </el-button>
          <el-button text class="recheck-btn" @click="reset">重新检测</el-button>
        </div>

        <!-- 右侧：降重建议 -->
        <div class="suggestions-panel">
          <div class="panel-header">
            <h3>逐句降重建议</h3>
            <el-tag type="danger">发现 {{ totalSuggestions }} 处疑似 AI 片段</el-tag>
          </div>

          <div v-if="totalSuggestions === 0" class="no-suggestion">
            <el-icon><CircleCheckFilled /></el-icon>
            <p>未发现明显 AI 特征，文本较为自然</p>
          </div>

          <div
            v-for="(sug, i) in allSuggestions" :key="i"
            class="suggestion-card"
          >
            <div class="sug-original">
              <div class="sug-label original-label">
                <el-icon><Warning /></el-icon> AI 疑似原文
              </div>
              <p>{{ sug.original }}</p>
            </div>
            <div class="sug-arrow"><el-icon><Bottom /></el-icon></div>
            <div class="sug-revised">
              <div class="sug-label revised-label">
                <el-icon><CircleCheck /></el-icon> 参考改写
              </div>
              <p>{{ sug.revised_version }}</p>
              <div class="sug-tip">{{ sug.suggestion }}</div>
            </div>
          </div>

          <!-- 总体建议 -->
          <div class="overall-advice" v-if="result.conclusion">
            <el-icon><Promotion /></el-icon>
            <div>
              <div class="advice-title">总体降重方针</div>
              <p>{{ result.conclusion }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { detectionAPI } from '../api/index.js'

const selectedFile = ref(null)
const loading      = ref(false)
const downloading  = ref(false)
const result       = ref(null)
const recordId     = ref(null)

const handleFileChange = (file) => { selectedFile.value = file.raw }

const allSuggestions = computed(() => {
  if (!result.value?.chunk_details) return []
  return result.value.chunk_details.flatMap(c => c.rewrite_suggestions || [])
})
const totalSuggestions = computed(() => allSuggestions.value.length)

const scoreColor = computed(() => {
  const s = result.value?.ai_score || 0
  if (s < 0.3) return '#22c55e'
  if (s < 0.6) return '#f59e0b'
  if (s < 0.8) return '#ef4444'
  return '#dc2626'
})

const riskClass = computed(() => {
  const s = result.value?.ai_score || 0
  if (s < 0.3) return 'risk-low'
  if (s < 0.6) return 'risk-mid'
  return 'risk-high'
})

const startDetect = async () => {
  if (!selectedFile.value) return
  loading.value = true
  const formData = new FormData()
  formData.append('file', selectedFile.value)
  try {
    const res = await detectionAPI.detect(formData)
    // ✅ 拦截器已解包，直接用 res 而非 res.data
    result.value   = res
    recordId.value = res.record_id
    ElMessage.success('检测完成！')
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '检测失败，请重试')
  } finally {
    loading.value = false
  }
}

const downloadReport = async () => {
  if (!recordId.value) return
  downloading.value = true
  try {
    const res = await detectionAPI.getReport(recordId.value)
    // ✅ getReport 设置了 responseType: 'blob'，拦截器返回的是 res.data（二进制）
    // 注意：blob 类型拦截器返回的仍是 res.data，因为 blob 本身就是 data
    const url  = URL.createObjectURL(new Blob([res], { type: 'application/pdf' }))
    const link = document.createElement('a')
    link.href = url
    link.download = `AI检测报告_${recordId.value}.pdf`
    link.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    ElMessage.error('报告下载失败')
  } finally {
    downloading.value = false
  }
}

const reset = () => { result.value = null; selectedFile.value = null }
</script>

<style scoped>
.page { padding: 32px; max-width: 1200px; margin: 0 auto; }
.page-header { margin-bottom: 32px; }
.page-header h1 { font-size: 26px; font-weight: 800; color: #1e293b; }
.page-header p  { color: #94a3b8; margin-top: 6px; font-size: 14px; }

.upload-section { display: flex; flex-direction: column; align-items: center; gap: 20px; }
.upload-dragger { width: 100%; max-width: 640px; }
.upload-inner   { padding: 60px 40px; text-align: center; }
.upload-icon    { font-size: 56px; color: #2563eb; margin-bottom: 16px; }
.upload-inner h3 { font-size: 18px; font-weight: 700; color: #1e293b; margin-bottom: 8px; }
.upload-inner p  { color: #94a3b8; margin-bottom: 20px; }
.select-btn     { border-radius: 20px; }

.file-preview {
  display: flex; align-items: center; gap: 12px;
  background: #fff; border: 1px solid #e2e8f0;
  border-radius: 12px; padding: 14px 20px;
}
.detect-btn { margin-left: auto; border-radius: 20px; }

.result-grid { display: grid; grid-template-columns: 280px 1fr; gap: 24px; }

.score-card {
  background: #fff; border-radius: 20px; padding: 28px 24px;
  border: 1px solid #eef0f4; display: flex; flex-direction: column;
  align-items: center; gap: 16px; position: sticky; top: 24px;
  align-self: start;
}
.score-card h3 { font-size: 16px; font-weight: 700; color: #1e293b; align-self: flex-start; }

.score-circle-wrap { position: relative; width: 160px; height: 160px; }
.score-svg { width: 100%; height: 100%; }
.score-text {
  position: absolute; inset: 0; display: flex;
  flex-direction: column; align-items: center; justify-content: center;
}
.score-num   { font-size: 32px; font-weight: 900; color: #1e293b; }
.score-label { font-size: 12px; color: #94a3b8; }

.risk-badge {
  padding: 6px 18px; border-radius: 20px; font-weight: 700; font-size: 14px;
}
.risk-low  { background: #f0fdf4; color: #16a34a; }
.risk-mid  { background: #fffbeb; color: #d97706; }
.risk-high { background: #fef2f2; color: #dc2626; }

.score-meta { width: 100%; display: flex; flex-direction: column; gap: 8px; }
.meta-item  { display: flex; justify-content: space-between; font-size: 13px; }
.meta-label { color: #94a3b8; }
.meta-val   { font-weight: 600; color: #1e293b; }

.download-btn {
  width: 100%; border-radius: 10px; background: #1e293b;
  color: white; border: none; height: 42px;
}
.download-btn:hover { background: #334155; }
.recheck-btn { color: #94a3b8; font-size: 13px; }

.suggestions-panel { display: flex; flex-direction: column; gap: 16px; }
.panel-header { display: flex; align-items: center; justify-content: space-between; }
.panel-header h3 { font-size: 18px; font-weight: 700; color: #1e293b; }

.no-suggestion {
  text-align: center; padding: 60px; color: #22c55e;
  background: #f0fdf4; border-radius: 16px;
}
.no-suggestion .el-icon { font-size: 48px; margin-bottom: 12px; }

.suggestion-card {
  background: #fff; border: 1px solid #eef0f4;
  border-radius: 16px; padding: 20px; display: flex;
  flex-direction: column; gap: 12px;
}
.sug-label {
  display: flex; align-items: center; gap: 6px;
  font-size: 11px; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.08em; margin-bottom: 8px;
}
.original-label { color: #f59e0b; }
.revised-label  { color: #22c55e; }
.sug-original p { background: #fffbeb; padding: 12px; border-radius: 8px; font-size: 14px; color: #92400e; line-height: 1.6; }
.sug-revised  p { background: #f0fdf4; padding: 12px; border-radius: 8px; font-size: 14px; color: #166534; line-height: 1.6; }
.sug-tip { font-size: 12px; color: #94a3b8; margin-top: 8px; }
.sug-arrow { text-align: center; color: #cbd5e1; font-size: 18px; }

.overall-advice {
  display: flex; gap: 14px; align-items: flex-start;
  background: #eff6ff; border-radius: 14px; padding: 18px;
  border: 1px solid #bfdbfe;
}
.overall-advice .el-icon { font-size: 22px; color: #2563eb; margin-top: 2px; }
.advice-title { font-weight: 700; color: #1e40af; margin-bottom: 6px; }
.overall-advice p { font-size: 14px; color: #1e40af; line-height: 1.6; }
</style>
