<template>
  <div class="page">
    <div class="page-header">
      <h1>选题与大纲生成</h1>
      <p>输入研究方向，AI 自动为你生成完整的论文选题建议与结构大纲</p>
    </div>

    <div class="input-card">
      <div class="form-row">
        <div class="form-item">
          <label>研究领域 <span class="required">*</span></label>
          <el-input v-model="form.field" placeholder="例如：计算机视觉、金融科技、教育心理学..." size="large" />
        </div>
        <div class="form-item">
          <label>学历层次</label>
          <el-select v-model="form.degree" size="large" style="width:100%">
            <el-option label="本科毕业论文" value="本科" />
            <el-option label="硕士学位论文" value="硕士" />
            <el-option label="博士学位论文" value="博士" />
          </el-select>
        </div>
      </div>
      <div class="form-item" style="margin-top:16px">
        <label>补充说明（可选）</label>
        <el-input
          v-model="form.description"
          type="textarea" :rows="3"
          placeholder="例如：希望结合深度学习方法，研究方向偏应用型..."
        />
      </div>
      <el-button
        type="primary" size="large" class="generate-btn"
        :loading="loading" @click="generate"
      >
        <el-icon><MagicStick /></el-icon>
        {{ loading ? 'AI 生成中...' : '生成选题与大纲' }}
      </el-button>
    </div>

    <div v-if="result" class="result-area">
      <div class="result-card">
        <div class="result-card-header">
          <el-icon class="header-icon topic-icon"><Opportunity /></el-icon>
          <h3>推荐选题</h3>
          <el-button text size="small" @click="copyText(result.topic)">
            <el-icon><CopyDocument /></el-icon> 复制
          </el-button>
        </div>
        <div class="topic-box">{{ result.topic }}</div>
      </div>

      <div class="result-card">
        <div class="result-card-header">
          <el-icon class="header-icon outline-icon"><List /></el-icon>
          <h3>论文大纲</h3>
          <el-button text size="small" @click="copyText(result.outline)">
            <el-icon><CopyDocument /></el-icon> 复制
          </el-button>
        </div>
        <div class="outline-content">
          <pre>{{ result.outline }}</pre>
        </div>
      </div>

      <div v-if="result.suggestions" class="result-card">
        <div class="result-card-header">
          <el-icon class="header-icon suggest-icon"><Promotion /></el-icon>
          <h3>研究建议</h3>
        </div>
        <p class="suggestion-text">{{ result.suggestions }}</p>
      </div>

      <el-button class="regenerate-btn" @click="generate" :loading="loading">
        <el-icon><Refresh /></el-icon> 重新生成
      </el-button>
    </div>

    <div v-else-if="!loading" class="empty-state">
      <el-icon><EditPen /></el-icon>
      <p>填写研究领域后，点击生成按钮</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { researchAPI } from '../api/index.js'

const loading = ref(false)
const result  = ref(null)
const form    = ref({ field: '', degree: '硕士', description: '' })

const generate = async () => {
  if (!form.value.field.trim()) return ElMessage.warning('请输入研究领域')
  loading.value = true
  result.value  = null
  try {
    const res = await researchAPI.generate(form.value)
    // ✅ 拦截器已解包，直接用 res 而非 res.data
    result.value = res
  } catch (e) {
    ElMessage.error(e.response?.data?.detail || '生成失败，请重试')
  } finally {
    loading.value = false
  }
}

const copyText = (text) => {
  navigator.clipboard.writeText(text)
  ElMessage.success('已复制到剪贴板')
}
</script>

<style scoped>
.page { padding: 32px; max-width: 900px; margin: 0 auto; }
.page-header { margin-bottom: 28px; }
.page-header h1 { font-size: 26px; font-weight: 800; color: #1e293b; }
.page-header p  { color: #94a3b8; margin-top: 6px; font-size: 14px; }

.input-card {
  background: #fff; border-radius: 20px; padding: 28px;
  border: 1px solid #eef0f4; margin-bottom: 28px;
}
.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.form-item label {
  display: block; font-size: 13px; font-weight: 600;
  color: #475569; margin-bottom: 8px;
}
.required { color: #ef4444; }

.generate-btn {
  margin-top: 20px; border-radius: 12px;
  padding: 0 32px; height: 46px; font-size: 15px; font-weight: 600;
}

.result-area { display: flex; flex-direction: column; gap: 20px; }
.result-card {
  background: #fff; border-radius: 16px; padding: 24px;
  border: 1px solid #eef0f4;
}
.result-card-header {
  display: flex; align-items: center; gap: 10px; margin-bottom: 16px;
}
.result-card-header h3 { font-size: 16px; font-weight: 700; color: #1e293b; flex: 1; }
.header-icon { font-size: 20px; padding: 6px; border-radius: 8px; }
.topic-icon   { background: #eff6ff; color: #2563eb; }
.outline-icon { background: #f0fdf4; color: #16a34a; }
.suggest-icon { background: #fffbeb; color: #d97706; }

.topic-box {
  background: #eff6ff; border-radius: 10px; padding: 16px 20px;
  font-size: 16px; font-weight: 600; color: #1e40af; line-height: 1.6;
}
.outline-content {
  background: #f8f9fc; border-radius: 10px; padding: 16px 20px;
  max-height: 400px; overflow-y: auto;
}
.outline-content pre {
  font-family: inherit; font-size: 14px; color: #334155;
  line-height: 1.8; white-space: pre-wrap;
}
.suggestion-text { font-size: 14px; color: #475569; line-height: 1.8; }

.regenerate-btn {
  align-self: flex-start; border-radius: 10px;
  color: #64748b; border-color: #e2e8f0;
}

.empty-state {
  text-align: center; padding: 80px 20px; color: #cbd5e1;
}
.empty-state .el-icon { font-size: 64px; margin-bottom: 16px; }
.empty-state p { font-size: 15px; }
</style>
