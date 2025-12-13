<script setup>
import { ref, onMounted } from 'vue'
import { configAPI } from '../api'

const configs = ref([])
const loading = ref(false)
const message = ref({ type: '', text: '' })

const showMessage = (type, text) => {
  message.value = { type, text }
  setTimeout(() => {
    message.value = { type: '', text: '' }
  }, 5000)
}

const loadConfigs = async () => {
  loading.value = true
  try {
    const response = await configAPI.list()
    configs.value = response.data.sort((a, b) => 
      new Date(b.modified_at) - new Date(a.modified_at)
    )
  } catch (error) {
    showMessage('error', `✗ 加载配置失败: ${error.message}`)
  } finally {
    loading.value = false
  }
}

const deleteConfig = async (name) => {
  if (!confirm(`确定要删除配置 "${name}" 吗？`)) {
    return
  }
  
  try {
    await configAPI.delete(name)
    showMessage('success', `✓ 配置 "${name}" 已删除`)
    await loadConfigs()
  } catch (error) {
    showMessage('error', `✗ 删除配置失败: ${error.message}`)
  }
}

const viewConfig = async (name) => {
  try {
    const response = await configAPI.load(name)
    const config = response.data
    
    // Format config as JSON
    const formatted = JSON.stringify(config, null, 2)
    
    // Show in alert for now (could be a modal in production)
    alert(`配置 "${name}":\n\n${formatted}`)
  } catch (error) {
    showMessage('error', `✗ 查看配置失败: ${error.message}`)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  loadConfigs()
})
</script>

<template>
  <div class="config-manager">
    <div class="header">
      <h2>配置管理</h2>
      <button @click="loadConfigs" :disabled="loading" class="btn-refresh">
        {{ loading ? '刷新中...' : '🔄 刷新' }}
      </button>
    </div>

    <div v-if="message.text" :class="['message', message.type]">
      {{ message.text }}
    </div>

    <div v-if="configs.length === 0" class="empty-state">
      <p>📁 暂无保存的配置</p>
      <p class="hint">在"同步配置"标签中保存配置后，可在此处管理</p>
    </div>

    <div v-else class="configs-grid">
      <div v-for="config in configs" :key="config.name" class="config-card">
        <div class="config-header">
          <div class="config-icon">📄</div>
          <div class="config-name">{{ config.name }}</div>
        </div>
        
        <div class="config-info">
          <div class="info-item">
            <span class="info-label">修改时间:</span>
            <span class="info-value">{{ formatDate(config.modified_at) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">路径:</span>
            <span class="info-value path">{{ config.path }}</span>
          </div>
        </div>

        <div class="config-actions">
          <button @click="viewConfig(config.name)" class="btn-action btn-view">
            👁️ 查看
          </button>
          <button @click="deleteConfig(config.name)" class="btn-action btn-delete">
            🗑️ 删除
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.config-manager {
  max-width: 1000px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

h2 {
  color: #333;
  margin: 0;
}

.btn-refresh {
  padding: 0.75rem 1.5rem;
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-refresh:hover:not(:disabled) {
  background: #667eea;
  color: white;
}

.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.message {
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  font-weight: 500;
}

.message.success {
  background: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.empty-state p {
  font-size: 1.2rem;
  color: #666;
  margin: 0.5rem 0;
}

.empty-state .hint {
  font-size: 1rem;
  color: #999;
}

.configs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.config-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  display: flex;
  flex-direction: column;
}

.config-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.15);
}

.config-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.config-icon {
  font-size: 2rem;
}

.config-name {
  font-size: 1.2rem;
  font-weight: 600;
  color: #333;
  word-break: break-word;
}

.config-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-label {
  font-size: 0.85rem;
  color: #666;
  font-weight: 500;
}

.info-value {
  font-size: 0.9rem;
  color: #333;
}

.info-value.path {
  font-family: monospace;
  font-size: 0.8rem;
  color: #666;
  word-break: break-all;
}

.config-actions {
  display: flex;
  gap: 0.75rem;
}

.btn-action {
  flex: 1;
  padding: 0.75rem;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-view {
  background: #667eea;
  color: white;
}

.btn-view:hover {
  background: #5568d3;
  transform: translateY(-2px);
}

.btn-delete {
  background: #dc3545;
  color: white;
}

.btn-delete:hover {
  background: #c82333;
  transform: translateY(-2px);
}
</style>
