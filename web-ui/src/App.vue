<script setup>
import { ref } from 'vue'
import SyncConfig from './components/SyncConfig.vue'
import SyncStatus from './components/SyncStatus.vue'
import ConfigManager from './components/ConfigManager.vue'

const currentTab = ref('sync')
</script>

<template>
  <div class="app">
    <header>
      <h1>🚀 SFTP Sync 管理界面</h1>
      <p>同步本地代码到远程服务器</p>
    </header>

    <nav class="tabs">
      <button 
        :class="{ active: currentTab === 'sync' }" 
        @click="currentTab = 'sync'"
      >
        同步配置
      </button>
      <button 
        :class="{ active: currentTab === 'status' }" 
        @click="currentTab = 'status'"
      >
        同步状态
      </button>
      <button 
        :class="{ active: currentTab === 'configs' }" 
        @click="currentTab = 'configs'"
      >
        配置管理
      </button>
    </nav>

    <main class="content">
      <SyncConfig v-if="currentTab === 'sync'" />
      <SyncStatus v-if="currentTab === 'status'" />
      <ConfigManager v-if="currentTab === 'configs'" />
    </main>

    <footer>
      <p>SFTP Sync v1.0.0 | <a href="https://github.com/perfectbullet/sftp_sync" target="_blank">GitHub</a></p>
    </footer>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  text-align: center;
}

header h1 {
  margin: 0;
  font-size: 2.5rem;
  font-weight: 700;
}

header p {
  margin: 0.5rem 0 0 0;
  opacity: 0.9;
  font-size: 1.1rem;
}

.tabs {
  display: flex;
  gap: 0;
  background: #f5f5f5;
  padding: 0;
  border-bottom: 2px solid #ddd;
}

.tabs button {
  flex: 1;
  padding: 1rem 2rem;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  color: #666;
  transition: all 0.3s ease;
  border-bottom: 3px solid transparent;
}

.tabs button:hover {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
}

.tabs button.active {
  color: #667eea;
  background: white;
  border-bottom-color: #667eea;
}

.content {
  flex: 1;
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
}

footer {
  background: #333;
  color: white;
  text-align: center;
  padding: 1rem;
  margin-top: auto;
}

footer a {
  color: #667eea;
  text-decoration: none;
}

footer a:hover {
  text-decoration: underline;
}
</style>

