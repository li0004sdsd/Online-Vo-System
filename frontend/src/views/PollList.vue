<template>
  <div class="poll-list-container">
    <el-header class="header">
      <div class="header-content">
        <h1 class="logo">在线投票系统</h1>
        <div class="user-info">
          <span class="username">{{ user?.username }}</span>
          <el-button type="danger" size="small" @click="handleLogout">退出登录</el-button>
        </div>
      </div>
    </el-header>
    
    <el-main class="main-content">
      <div class="action-bar">
        <el-button type="primary" @click="goToCreate">
          <el-icon><Plus /></el-icon>
          创建投票
        </el-button>
      </div>
      
      <div class="poll-list" v-loading="loading">
        <el-empty v-if="polls.length === 0 && !loading" description="暂无投票" />
        <el-card 
          v-for="poll in polls" 
          :key="poll.id" 
          class="poll-card"
          shadow="hover"
        >
          <div class="poll-header">
            <h3 class="poll-title">{{ poll.title }}</h3>
            <el-tag :type="poll.is_active ? 'success' : 'info'" size="small">
              {{ poll.is_active ? '进行中' : '已结束' }}
            </el-tag>
          </div>
          
          <p class="poll-description">{{ poll.description || '暂无描述' }}</p>
          
          <div class="poll-meta">
            <span class="meta-item">
              <el-icon><User /></el-icon>
              {{ poll.creator.username }}
            </span>
            <span class="meta-item">
              <el-icon><Calendar /></el-icon>
              {{ formatDate(poll.created_at) }}
            </span>
            <span class="meta-item">
              <el-icon><DataAnalysis /></el-icon>
              {{ poll.total_votes }} 票
            </span>
            <span class="meta-item">
              <el-tag :type="poll.allow_multiple ? 'warning' : ''" size="small">
                {{ poll.allow_multiple ? '多选' : '单选' }}
              </el-tag>
            </span>
          </div>
          
          <div class="poll-actions">
            <el-button 
              type="success" 
              size="small" 
              @click="goToResults(poll.id)"
            >
              查看结果
            </el-button>
            <el-button 
              v-if="!poll.has_voted && poll.is_active"
              type="primary" 
              size="small" 
              @click="goToDetail(poll.id)"
            >
              去投票
            </el-button>
            <el-button 
              v-else-if="poll.has_voted"
              type="info" 
              size="small" 
              disabled
            >
              已投票
            </el-button>
            <el-button 
              v-else
              type="info" 
              size="small" 
              disabled
            >
              已结束
            </el-button>
          </div>
        </el-card>
      </div>
    </el-main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, User, Calendar, DataAnalysis } from '@element-plus/icons-vue'
import { getPollList } from '@/api/poll'
import { getUser, removeToken } from '@/utils/auth'

const router = useRouter()
const loading = ref(false)
const polls = ref([])
const user = ref(getUser())

const fetchPolls = async () => {
  try {
    loading.value = true
    polls.value = await getPollList()
  } catch (error) {
    console.error('获取投票列表失败', error)
  } finally {
    loading.value = false
  }
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const goToCreate = () => {
  router.push('/create')
}

const goToDetail = (id) => {
  router.push(`/poll/${id}`)
}

const goToResults = (id) => {
  router.push(`/results/${id}`)
}

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    removeToken()
    ElMessage.success('已退出登录')
    router.push('/login')
  } catch (error) {
    // 用户取消操作
  }
}

onMounted(() => {
  fetchPolls()
})
</script>

<style scoped>
.poll-list-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0;
  height: 60px;
  display: flex;
  align-items: center;
}

.header-content {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.logo {
  margin: 0;
  font-size: 20px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.username {
  font-size: 14px;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  padding: 20px;
}

.action-bar {
  margin-bottom: 20px;
}

.poll-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.poll-card {
  transition: transform 0.3s, box-shadow 0.3s;
}

.poll-card:hover {
  transform: translateY(-5px);
}

.poll-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.poll-title {
  margin: 0;
  font-size: 18px;
  color: #303133;
  flex: 1;
  margin-right: 10px;
}

.poll-description {
  color: #606266;
  font-size: 14px;
  margin-bottom: 15px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.poll-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 15px;
  color: #909399;
  font-size: 13px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.poll-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}
</style>
