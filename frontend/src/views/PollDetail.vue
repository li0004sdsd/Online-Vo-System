<template>
  <div class="poll-detail-container">
    <el-header class="header">
      <div class="header-content">
        <h1 class="logo" @click="goBack" style="cursor: pointer;">
          <el-icon><ArrowLeft /></el-icon>
          返回
        </h1>
        <div class="user-info">
          <span class="username">{{ user?.username }}</span>
        </div>
      </div>
    </el-header>
    
    <el-main class="main-content" v-loading="loading">
      <el-card v-if="poll" class="detail-card">
        <div class="poll-header">
          <h2 class="poll-title">{{ poll.title }}</h2>
          <div class="poll-tags">
            <el-tag :type="poll.is_active ? 'success' : 'info'" size="small">
              {{ poll.is_active ? '进行中' : '已结束' }}
            </el-tag>
            <el-tag :type="poll.allow_multiple ? 'warning' : ''" size="small">
              {{ poll.allow_multiple ? '多选' : '单选' }}
            </el-tag>
          </div>
        </div>
        
        <p class="poll-description">{{ poll.description || '暂无描述' }}</p>
        
        <div class="poll-meta">
          <span class="meta-item">
            <el-icon><User /></el-icon>
            创建者: {{ poll.creator.username }}
          </span>
          <span class="meta-item">
            <el-icon><Calendar /></el-icon>
            创建时间: {{ formatDate(poll.created_at) }}
          </span>
          <span class="meta-item">
            <el-icon><DataAnalysis /></el-icon>
            总票数: {{ poll.total_votes }}
          </span>
        </div>
        
        <div class="vote-section">
          <h3 class="section-title">请选择您的选项：</h3>
          
          <div class="options-list">
            <div
              v-for="option in poll.options"
              :key="option.id"
              class="option-item"
              :class="{
                'selected': selectedOptions.includes(option.id),
                'disabled': poll.has_voted || !poll.is_active,
                'voted': poll.user_votes?.includes(option.id)
              }"
              @click="toggleOption(option.id)"
            >
              <el-icon v-if="poll.allow_multiple" class="option-icon">
                <Check v-if="selectedOptions.includes(option.id) || poll.user_votes?.includes(option.id)" />
                <Box v-else />
              </el-icon>
              <el-icon v-else class="option-icon">
                <CircleCheck v-if="selectedOptions.includes(option.id) || poll.user_votes?.includes(option.id)" />
                <CircleClose v-else />
              </el-icon>
              <span class="option-text">{{ option.text }}</span>
              <el-tag 
                v-if="poll.user_votes?.includes(option.id)" 
                type="success" 
                size="small"
                class="voted-tag"
              >
                您的选择
              </el-tag>
            </div>
          </div>
          
          <div class="vote-actions">
            <el-button 
              v-if="!poll.has_voted && poll.is_active"
              type="primary" 
              :disabled="selectedOptions.length === 0"
              :loading="voting"
              @click="submitVote"
            >
              提交投票
            </el-button>
            <el-button 
              v-else-if="poll.has_voted"
              type="success"
              @click="goToResults"
            >
              查看投票结果
            </el-button>
            <el-button 
              v-else
              type="info"
              disabled
            >
              投票已结束
            </el-button>
            <el-button @click="goBack">返回列表</el-button>
          </div>
        </div>
      </el-card>
    </el-main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, User, Calendar, DataAnalysis, Check, Box, CircleCheck, CircleClose } from '@element-plus/icons-vue'
import { getPollDetail, vote } from '@/api/poll'
import { getUser } from '@/utils/auth'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const voting = ref(false)
const poll = ref(null)
const selectedOptions = ref([])
const user = ref(getUser())

const pollId = route.params.id

const fetchPollDetail = async () => {
  try {
    loading.value = true
    poll.value = await getPollDetail(pollId)
    
    if (poll.value.user_votes && poll.value.user_votes.length > 0) {
      selectedOptions.value = [...poll.value.user_votes]
    }
  } catch (error) {
    console.error('获取投票详情失败', error)
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

const toggleOption = (optionId) => {
  if (poll.value.has_voted || !poll.value.is_active) {
    return
  }
  
  if (poll.value.allow_multiple) {
    const index = selectedOptions.value.indexOf(optionId)
    if (index > -1) {
      selectedOptions.value.splice(index, 1)
    } else {
      selectedOptions.value.push(optionId)
    }
  } else {
    selectedOptions.value = [optionId]
  }
}

const submitVote = async () => {
  if (selectedOptions.value.length === 0) {
    ElMessage.warning('请至少选择一个选项')
    return
  }
  
  try {
    await ElMessageBox.confirm(
      `确定要提交您的投票吗？${!poll.value.allow_multiple ? '（单选投票提交后不可更改）' : ''}`,
      '确认投票',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    voting.value = true
    const res = await vote(pollId, selectedOptions.value)
    
    ElMessage.success('投票成功')
    poll.value.has_voted = true
    poll.value.user_votes = [...selectedOptions.value]
    poll.value.total_votes = res.results.total_votes
  } catch (error) {
    if (error !== 'cancel') {
      console.error('投票失败', error)
    }
  } finally {
    voting.value = false
  }
}

const goBack = () => {
  router.push('/')
}

const goToResults = () => {
  router.push(`/results/${pollId}`)
}

onMounted(() => {
  fetchPollDetail()
})
</script>

<style scoped>
.poll-detail-container {
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
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.logo {
  margin: 0;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 5px;
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
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
  padding: 20px;
}

.detail-card {
  padding: 30px;
}

.poll-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.poll-title {
  margin: 0;
  font-size: 24px;
  color: #303133;
  flex: 1;
  margin-right: 15px;
}

.poll-tags {
  display: flex;
  gap: 8px;
}

.poll-description {
  color: #606266;
  font-size: 15px;
  margin-bottom: 20px;
  line-height: 1.6;
}

.poll-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 30px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 8px;
  color: #909399;
  font-size: 14px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.vote-section {
  border-top: 1px solid #ebeef5;
  padding-top: 20px;
}

.section-title {
  font-size: 18px;
  color: #303133;
  margin-bottom: 20px;
}

.options-list {
  margin-bottom: 25px;
}

.option-item {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  margin-bottom: 12px;
  border: 2px solid #dcdfe6;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  background-color: white;
}

.option-item:hover:not(.disabled) {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.option-item.selected:not(.disabled) {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.option-item.voted {
  border-color: #67c23a;
  background-color: #f0f9eb;
}

.option-item.disabled {
  cursor: not-allowed;
  opacity: 0.8;
}

.option-icon {
  margin-right: 12px;
  font-size: 20px;
  color: #909399;
}

.selected .option-icon,
.voted .option-icon {
  color: #409eff;
}

.voted .option-icon {
  color: #67c23a;
}

.option-text {
  flex: 1;
  font-size: 15px;
  color: #303133;
}

.voted-tag {
  margin-left: 10px;
}

.vote-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
}
</style>
