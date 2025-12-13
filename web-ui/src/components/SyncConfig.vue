<script setup>
import { ref, reactive } from 'vue'
import { syncAPI, configAPI } from '../api'

const config = reactive({
  host: '',
  port: 22,
  username: '',
  password: '',
  private_key: '',
  private_key_password: '',
  local_dir: '.',
  remote_dir: '.',
  include_patterns: ['*'],
  exclude_patterns: ['*.pyc', '__pycache__', '.git', 'node_modules', '.env'],
  delete_remote: false,
  preserve_permissions: true,
  auto_add_host_key: false,
  dry_run: false,
  verbose: false,
  follow_symlinks: false,
  backup_remote: false,
})

const authMethod = ref('password')
const loading = ref(false)
const message = ref({ type: '', text: '' })
const testingConnection = ref(false)

const showMessage = (type, text) => {
  message.value = { type, text }
  setTimeout(() => {
    message.value = { type: '', text: '' }
  }, 5000)
}

const testConnection = async () => {
  testingConnection.value = true
  try {
    const params = {
      host: config.host,
      port: config.port,
      username: config.username,
    }
    
    if (authMethod.value === 'password') {
      params.password = config.password
    } else {
      params.private_key = config.private_key
    }
    
    const response = await syncAPI.testConnection(params)
    
    if (response.data.status === 'success') {
      showMessage('success', '✓ 连接测试成功！')
    } else {
      showMessage('error', `✗ 连接失败: ${response.data.message}`)
    }
  } catch (error) {
    showMessage('error', `✗ 连接测试失败: ${error.message}`)
  } finally {
    testingConnection.value = false
  }
}

const startSync = async () => {
  loading.value = true
  try {
    const response = await syncAPI.startSync(config)
    showMessage('success', `✓ 同步任务已启动！任务ID: ${response.data.task_id}`)
    
    // Poll for status
    pollStatus(response.data.task_id)
  } catch (error) {
    showMessage('error', `✗ 启动同步失败: ${error.response?.data?.detail || error.message}`)
  } finally {
    loading.value = false
  }
}

const pollStatus = async (taskId) => {
  const interval = setInterval(async () => {
    try {
      const response = await syncAPI.getStatus(taskId)
      const status = response.data
      
      if (status.status === 'completed') {
        clearInterval(interval)
        showMessage('success', `✓ 同步完成！上传: ${status.stats?.uploaded || 0}, 跳过: ${status.stats?.skipped || 0}`)
      } else if (status.status === 'failed') {
        clearInterval(interval)
        showMessage('error', `✗ 同步失败: ${status.error}`)
      }
    } catch (error) {
      clearInterval(interval)
    }
  }, 2000)
}

const addPattern = (type) => {
  const pattern = prompt(`请输入${type === 'include' ? '包含' : '排除'}模式:`)
  if (pattern) {
    if (type === 'include') {
      config.include_patterns.push(pattern)
    } else {
      config.exclude_patterns.push(pattern)
    }
  }
}

const removePattern = (type, index) => {
  if (type === 'include') {
    config.include_patterns.splice(index, 1)
  } else {
    config.exclude_patterns.splice(index, 1)
  }
}

const loadSavedConfig = async () => {
  try {
    const response = await configAPI.list()
    const configs = response.data
    
    if (configs.length === 0) {
      showMessage('info', 'ℹ 没有保存的配置')
      return
    }
    
    const configName = prompt(`选择配置:\n${configs.map((c, i) => `${i + 1}. ${c.name}`).join('\n')}`)
    if (configName) {
      const loadResponse = await configAPI.load(configName)
      Object.assign(config, loadResponse.data)
      showMessage('success', `✓ 配置 "${configName}" 已加载`)
    }
  } catch (error) {
    showMessage('error', `✗ 加载配置失败: ${error.message}`)
  }
}

const saveConfig = async () => {
  const name = prompt('请输入配置名称:')
  if (name) {
    try {
      await configAPI.save(name, config)
      showMessage('success', `✓ 配置已保存为 "${name}"`)
    } catch (error) {
      showMessage('error', `✗ 保存配置失败: ${error.message}`)
    }
  }
}
</script>

<template>
  <div class="sync-config">
    <h2>同步配置</h2>
    
    <div v-if="message.text" :class="['message', message.type]">
      {{ message.text }}
    </div>

    <div class="config-actions">
      <button @click="loadSavedConfig" class="btn-secondary">📁 加载配置</button>
      <button @click="saveConfig" class="btn-secondary">💾 保存配置</button>
    </div>

    <div class="form-section">
      <h3>连接设置</h3>
      
      <div class="form-group">
        <label>主机地址 *</label>
        <input v-model="config.host" type="text" placeholder="192.168.1.100 或 example.com" />
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>端口</label>
          <input v-model.number="config.port" type="number" />
        </div>
        <div class="form-group">
          <label>用户名 *</label>
          <input v-model="config.username" type="text" />
        </div>
      </div>

      <div class="form-group">
        <label>认证方式</label>
        <select v-model="authMethod">
          <option value="password">密码</option>
          <option value="key">SSH密钥</option>
        </select>
      </div>

      <div v-if="authMethod === 'password'" class="form-group">
        <label>密码</label>
        <input v-model="config.password" type="password" />
      </div>

      <div v-if="authMethod === 'key'">
        <div class="form-group">
          <label>私钥路径</label>
          <input v-model="config.private_key" type="text" placeholder="~/.ssh/id_rsa" />
        </div>
        <div class="form-group">
          <label>私钥密码（如有）</label>
          <input v-model="config.private_key_password" type="password" />
        </div>
      </div>

      <button @click="testConnection" :disabled="testingConnection" class="btn-test">
        {{ testingConnection ? '测试中...' : '🔌 测试连接' }}
      </button>
    </div>

    <div class="form-section">
      <h3>目录设置</h3>
      
      <div class="form-group">
        <label>本地目录 *</label>
        <input v-model="config.local_dir" type="text" placeholder="./my-project" />
      </div>

      <div class="form-group">
        <label>远程目录 *</label>
        <input v-model="config.remote_dir" type="text" placeholder="/var/www/html" />
      </div>
    </div>

    <div class="form-section">
      <h3>文件过滤</h3>
      
      <div class="pattern-group">
        <label>包含模式</label>
        <div class="pattern-list">
          <span v-for="(pattern, index) in config.include_patterns" :key="index" class="pattern-tag">
            {{ pattern }}
            <button @click="removePattern('include', index)">×</button>
          </span>
          <button @click="addPattern('include')" class="btn-add">+ 添加</button>
        </div>
      </div>

      <div class="pattern-group">
        <label>排除模式</label>
        <div class="pattern-list">
          <span v-for="(pattern, index) in config.exclude_patterns" :key="index" class="pattern-tag">
            {{ pattern }}
            <button @click="removePattern('exclude', index)">×</button>
          </span>
          <button @click="addPattern('exclude')" class="btn-add">+ 添加</button>
        </div>
      </div>
    </div>

    <div class="form-section">
      <h3>同步选项</h3>
      
      <div class="options-grid">
        <label class="checkbox-label">
          <input v-model="config.delete_remote" type="checkbox" />
          <span>删除远程多余文件</span>
        </label>

        <label class="checkbox-label">
          <input v-model="config.preserve_permissions" type="checkbox" />
          <span>保留文件权限</span>
        </label>

        <label class="checkbox-label">
          <input v-model="config.backup_remote" type="checkbox" />
          <span>备份远程文件</span>
        </label>

        <label class="checkbox-label">
          <input v-model="config.follow_symlinks" type="checkbox" />
          <span>跟随符号链接</span>
        </label>

        <label class="checkbox-label">
          <input v-model="config.dry_run" type="checkbox" />
          <span>预演模式（不实际执行）</span>
        </label>

        <label class="checkbox-label">
          <input v-model="config.verbose" type="checkbox" />
          <span>详细输出</span>
        </label>

        <label class="checkbox-label">
          <input v-model="config.auto_add_host_key" type="checkbox" />
          <span>自动添加主机密钥</span>
        </label>
      </div>
    </div>

    <div class="form-actions">
      <button @click="startSync" :disabled="loading" class="btn-primary">
        {{ loading ? '同步中...' : '🚀 开始同步' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.sync-config {
  max-width: 800px;
}

h2 {
  color: #333;
  margin-bottom: 1.5rem;
}

h3 {
  color: #555;
  margin-bottom: 1rem;
  font-size: 1.2rem;
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

.message.info {
  background: #d1ecf1;
  color: #0c5460;
  border: 1px solid #bee5eb;
}

.config-actions {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.form-section {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.form-group {
  margin-bottom: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
  font-weight: 500;
}

input[type="text"],
input[type="password"],
input[type="number"],
select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

input:focus,
select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.pattern-group {
  margin-bottom: 1rem;
}

.pattern-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.pattern-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: #667eea;
  color: white;
  padding: 0.5rem 0.75rem;
  border-radius: 20px;
  font-size: 0.9rem;
}

.pattern-tag button {
  background: rgba(255, 255, 255, 0.3);
  border: none;
  color: white;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
}

.pattern-tag button:hover {
  background: rgba(255, 255, 255, 0.5);
}

.btn-add {
  background: transparent;
  border: 2px dashed #667eea;
  color: #667eea;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-add:hover {
  background: rgba(102, 126, 234, 0.1);
}

.options-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
  cursor: pointer;
}

.btn-primary,
.btn-secondary,
.btn-test {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  width: 100%;
  padding: 1rem;
  font-size: 1.1rem;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
}

.btn-secondary:hover {
  background: #667eea;
  color: white;
}

.btn-test {
  background: #28a745;
  color: white;
  margin-top: 0.5rem;
}

.btn-test:hover:not(:disabled) {
  background: #218838;
}

.btn-test:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.form-actions {
  margin-top: 2rem;
}
</style>
