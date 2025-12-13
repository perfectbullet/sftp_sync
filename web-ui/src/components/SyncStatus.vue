<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { syncAPI } from '../api'

const tasks = ref([])
const loading = ref(false)
let refreshInterval = null

const statusColors = {
  pending: '#ffc107',
  running: '#17a2b8',
  completed: '#28a745',
  failed: '#dc3545',
}

const statusIcons = {
  pending: '⏳',
  running: '🔄',
  completed: '✅',
  failed: '❌',
}

const loadTasks = async () => {
  loading.value = true
  try {
    const response = await syncAPI.listTasks()
    tasks.value = response.data.sort((a, b) => 
      new Date(b.started_at) - new Date(a.started_at)
    )
  } catch (error) {
    console.error('Failed to load tasks:', error)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

const formatDuration = (startedAt, completedAt) => {
  if (!startedAt || !completedAt) return '-'
  const start = new Date(startedAt)
  const end = new Date(completedAt)
  const duration = (end - start) / 1000 // seconds
  
  if (duration < 60) {
    return `${Math.round(duration)}秒`
  } else if (duration < 3600) {
    return `${Math.round(duration / 60)}分钟`
  } else {
    return `${Math.round(duration / 3600)}小时`
  }
}

onMounted(() => {
  loadTasks()
  // Auto refresh every 3 seconds
  refreshInterval = setInterval(loadTasks, 3000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<template>
  <div class="sync-status">
    <div class="header">
      <h2>同步任务状态</h2>
      <button @click="loadTasks" :disabled="loading" class="btn-refresh">
        {{ loading ? '刷新中...' : '🔄 刷新' }}
      </button>
    </div>

    <div v-if="tasks.length === 0" class="empty-state">
      <p>📭 暂无同步任务</p>
      <p class="hint">在"同步配置"标签中启动第一个同步任务</p>
    </div>

    <div v-else class="tasks-list">
      <div v-for="task in tasks" :key="task.task_id" class="task-card">
        <div class="task-header">
          <div class="task-title">
            <span class="status-icon" :style="{ color: statusColors[task.status] }">
              {{ statusIcons[task.status] }}
            </span>
            <span class="task-id">{{ task.task_id }}</span>
          </div>
          <span class="status-badge" :style="{ 
            background: statusColors[task.status],
            color: 'white'
          }">
            {{ task.status === 'pending' ? '等待中' :
               task.status === 'running' ? '运行中' :
               task.status === 'completed' ? '已完成' : '失败' }}
          </span>
        </div>

        <div class="task-info">
          <div class="info-row">
            <span class="label">开始时间:</span>
            <span class="value">{{ formatDate(task.started_at) }}</span>
          </div>
          
          <div v-if="task.completed_at" class="info-row">
            <span class="label">完成时间:</span>
            <span class="value">{{ formatDate(task.completed_at) }}</span>
          </div>
          
          <div v-if="task.completed_at" class="info-row">
            <span class="label">用时:</span>
            <span class="value">{{ formatDuration(task.started_at, task.completed_at) }}</span>
          </div>

          <div v-if="task.stats" class="stats">
            <div class="stat-item">
              <span class="stat-label">上传:</span>
              <span class="stat-value success">{{ task.stats.uploaded || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">跳过:</span>
              <span class="stat-value">{{ task.stats.skipped || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">删除:</span>
              <span class="stat-value warning">{{ task.stats.deleted || 0 }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">错误:</span>
              <span class="stat-value error">{{ task.stats.errors || 0 }}</span>
            </div>
          </div>

          <div v-if="task.error" class="error-message">
            <strong>错误:</strong> {{ task.error }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sync-status {
  max-width: 900px;
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

.tasks-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.task-card {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.task-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.task-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.status-icon {
  font-size: 1.5rem;
}

.task-id {
  font-weight: 600;
  color: #333;
  font-family: monospace;
}

.status-badge {
  padding: 0.4rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}

.task-info {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.info-row {
  display: flex;
  align-items: center;
}

.label {
  color: #666;
  min-width: 100px;
  font-weight: 500;
}

.value {
  color: #333;
}

.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 1rem;
  margin-top: 0.5rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 6px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-label {
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 0.25rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #333;
}

.stat-value.success {
  color: #28a745;
}

.stat-value.warning {
  color: #ffc107;
}

.stat-value.error {
  color: #dc3545;
}

.error-message {
  padding: 1rem;
  background: #f8d7da;
  color: #721c24;
  border-radius: 6px;
  border: 1px solid #f5c6cb;
}

.error-message strong {
  display: block;
  margin-bottom: 0.5rem;
}
</style>
