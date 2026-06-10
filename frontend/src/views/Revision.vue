<template>
  <div class="revision-page">

    <!-- 顶部标题 -->
    <div class="page-header">
      <h1><el-icon><EditPen /></el-icon> 论文修改助手</h1>
      <p>上传你的论文，AI 将根据你选择的模式进行润色、降重或结构优化</p>
    </div>

    <div class="revision-layout">

      <!-- 左侧：设置面板 -->
      <div class="setting-panel">

        <!-- 修改模式选择 -->
        <div class="panel-card">
          <h4><el-icon><Setting /></el-icon> 修改模式</h4>
          <el-radio-group v-model="revisionMode" class="mode-group">
            <el-radio-button label="polish">
              <el-icon><MagicStick /></el-icon> 润色优化
            </el-radio-button>
            <el-radio-button label="reduce">
              <el-icon><Scissor /></el-icon> 降重改写
            </el-radio-button>
            <el-radio-button label="structure">
              <el-icon><Grid /></el-icon> 结构优化
            </el-radio-button>
            <el-radio-button label="grammar">
              <el-icon><Check /></el-icon> 语法检查
            </el-radio-button>
          </el-radio-group>
          <p class="mode-desc">{{ modeDescMap[revisionMode] }}</p>
        </div>

        <!-- 写作风格 -->
        <div class="panel-card">
          <h4><el-icon><Notebook /></el-icon> 写作风格</h4>
          <el-select v-model="writingStyle" style="width:100%">
            <el-option label="学术正式（期刊论文）" value="academic" />
            <el-option label="简洁清晰（会议论文）" value="concise" />
            <el-option label="中文母语化" value="native_chinese" />
            <el-option label="英文学术化" value="english_academic" />
          </el-select>
        </div>

        <!-- 额外要求 -->
        <div class="panel-card">
          <h4><el-icon><ChatLineSquare /></el-icon> 额外要求（可选）</h4>
          <el-input
            v-model="extraRequirement"
            type="textarea"
            :autosize="{ minRows: 3, maxRows: 6 }"
            placeholder="例如：保留专业术语、不改变原意、重点修改第三章..."
          />
        </div>

        <!-- 提交按钮 -->
        <el-button
          type="primary" size="large" style="width:100%;border-radius:12px"
          :loading="loading" :disabled="!inputText.trim()"
          @click="submitRevision"
        >
          <el-icon><MagicStick /></el-icon>
          {{ loading ? 'AI 修改中...' : '开始修改' }}
        </el-button>

      </div>

      <!-- 右侧：输入 / 输出区域 -->
      <div class="editor-panel">

        <!-- 输入区 -->
        <div class="editor-card">
          <div class="editor-header">
            <span class="editor-label">原文输入</span>
            <div class="editor-actions">
              <el-button text size="small" @click="inputText = ''">
                <el-icon><Delete /></el-icon> 清空
              </el-button>
              <el-button text size="small" @click="pasteFromClipboard">
                <el-icon><DocumentCopy /></el-icon> 粘贴
              </el-button>
            </div>
          </div>
          <el-input
            v-model="inputText"
            type="textarea"
            :autosize="{ minRows: 12, maxRows: 20 }"
            placeholder="请在此粘贴你需要修改的论文段落或全文..."
            class="editor-textarea"
          />
          <div class="word-count">字数：{{ inputText.length }} 字</div>
        </div>

        <!-- 输出区 -->
        <div class="editor-card output-card" v-if="outputText || loading">
          <div class="editor-header">
            <span class="editor-label">
              修改结果
              <el-tag size="small" type="success" style="margin-left:8px">
                {{ modeTagMap[revisionMode] }}
              </el-tag>
            </span>
            <div class="editor-actions">
              <el-button text size="small" @click="copyOutput" :disabled="!outputText">
                <el-icon><CopyDocument /></el-icon> 复制
              </el-button>
              <el-button text size="small" @click="clearOutput" :disabled="!outputText">
                <el-icon><RefreshLeft /></el-icon> 重置
              </el-button>
            </div>
          </div>

          <!-- 流式输出内容 -->
          <div class="output-content" ref="outputRef">
            <span v-if="loading && !outputText" class="typing">
              <span></span><span></span><span></span>
            </span>
            <span v-else class="output-text">{{ outputText }}</span>
          </div>

          <div v-if="outputText" class="word-count">
            修改后字数：{{ outputText.length }} 字
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import {
  EditPen, Setting, MagicStick, Scissor, Grid, Check,
  Notebook, ChatLineSquare, Delete, DocumentCopy,
  CopyDocument, RefreshLeft
} from '@element-plus/icons-vue'
import axios from 'axios'

// ===== 状态 =====
const revisionMode     = ref('polish')
const writingStyle     = ref('academic')
const extraRequirement = ref('')
const inputText        = ref('')
const outputText       = ref('')
const loading          = ref(false)
const outputRef        = ref(null)

// ===== 模式描述映射 =====
const modeDescMap = {
  polish:    '对论文进行语言润色，提升表达流畅度与学术规范性，保留原意不变',
  reduce:    '对论文进行同义改写，降低重复率，保持逻辑连贯，适合查重前处理',
  structure: '分析论文结构合理性，给出章节调整、逻辑优化建议，并提供修改版本',
  grammar:   '逐句检查语法错误、标点规范、用词准确性，并给出修正版本'
}

const modeTagMap = {
  polish:    '润色优化',
  reduce:    '降重改写',
  structure: '结构优化',
  grammar:   '语法检查'
}

// ===== 粘贴剪贴板 =====
const pasteFromClipboard = async () => {
  try {
    const text = await navigator.clipboard.readText()
    inputText.value = text
    ElMessage.success('已粘贴剪贴板内容')
  } catch {
    ElMessage.warning('请手动粘贴（Ctrl+V）')
  }
}

// ===== 复制输出 =====
const copyOutput = async () => {
  try {
    await navigator.clipboard.writeText(outputText.value)
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败，请手动选中复制')
  }
}

// ===== 清空输出 =====
const clearOutput = () => {
  outputText.value = ''
}

// ===== 滚动输出区到底部 =====
const scrollOutput = async () => {
  await nextTick()
  if (outputRef.value) {
    outputRef.value.scrollTop = outputRef.value.scrollHeight
  }
}

// ===== 提交修改（流式请求） =====
const submitRevision = async () => {
  if (!inputText.value.trim()) return
  loading.value = true
  outputText.value = ''

  try {
    const response = await fetch('/api/v1/revision/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        content: inputText.value,
        mode: revisionMode.value,
        style: writingStyle.value,
        extra: extraRequirement.value
      })
    })

    if (!response.ok) throw new Error('请求失败')

    const reader = response.body.getReader()
    const decoder = new TextDecoder('utf-8')

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value, { stream: true })
      const lines = chunk.split('\n')

      for (const line of lines) {
        if (!line.startsWith('data:')) continue
        const data = line.replace('data:', '').trim()
        if (data === '[DONE]') break

        try {
          const parsed = JSON.parse(data)
          if (parsed.content) {
            outputText.value += parsed.content
            await scrollOutput()
          }
          if (parsed.error) {
            ElMessage.error(parsed.error)
          }
        } catch {
          // 忽略非 JSON 行
        }
      }
    }

    ElMessage.success('修改完成！')
  } catch (e) {
    ElMessage.error('修改请求失败，请稍后重试')
    console.error(e)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.revision-page { padding: 32px; max-width: 1400px; margin: 0 auto; }

.page-header { margin-bottom: 28px; }
.page-header h1 {
  display: flex; align-items: center; gap: 10px;
  font-size: 26px; font-weight: 800; color: #1e293b;
}
.page-header p { color: #94a3b8; margin-top: 6px; font-size: 14px; }

.revision-layout { display: flex; gap: 24px; align-items: flex-start; }

/* 左侧设置面板 */
.setting-panel { width: 280px; min-width: 280px; display: flex; flex-direction: column; gap: 16px; }
.panel-card {
  background: #fff; border-radius: 16px; padding: 18px 20px;
  border: 1px solid #eef0f4;
}
.panel-card h4 {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; font-weight: 700; color: #1e293b; margin-bottom: 14px;
}
.mode-group { display: flex; flex-direction: column; gap: 8px; width: 100%; }
.mode-group :deep(.el-radio-button__inner) { width: 100%; text-align: left; border-radius: 8px !important; }
.mode-desc {
  margin-top: 10px; font-size: 12px; color: #64748b;
  background: #f8f9fc; border-radius: 8px; padding: 8px 10px;
  line-height: 1.6; border-left: 3px solid #2563eb;
}

/* 右侧编辑器 */
.editor-panel { flex: 1; display: flex; flex-direction: column; gap: 20px; }
.editor-card {
  background: #fff; border-radius: 16px; padding: 20px;
  border: 1px solid #eef0f4;
}
.editor-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 12px;
}
.editor-label { font-size: 13px; font-weight: 700; color: #1e293b; }
.editor-textarea :deep(.el-textarea__inner) {
  border: none; box-shadow: none; background: #f8f9fc;
  border-radius: 10px; font-size: 14px; line-height: 1.8; padding: 14px;
}
.word-count { text-align: right; font-size: 12px; color: #94a3b8; margin-top: 8px; }

.output-card { border-color: #bbf7d0; background: #f0fdf4; }
.output-content {
  min-height: 200px; max-height: 500px; overflow-y: auto;
  background: #fff; border-radius: 10px; padding: 14px;
  font-size: 14px; line-height: 1.8; color: #1e293b; white-space: pre-wrap;
}
.output-text { white-space: pre-wrap; }

/* 打字动画 */
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
</style>