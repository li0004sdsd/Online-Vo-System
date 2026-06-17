<template>
  <div class="poll-results-container">
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
      <el-card v-if="results" class="results-card">
        <div class="poll-header">
          <h2 class="poll-title">{{ results.title }}</h2>
          <el-tag type="success" size="large">
            总票数: {{ results.total_votes }}
          </el-tag>
        </div>
        
        <p class="poll-description">{{ results.description || '暂无描述' }}</p>
        
        <div class="results-section">
          <h3 class="section-title">投票结果统计</h3>
          
          <div class="results-list">
            <div
              v-for="(option, index) in sortedOptions"
              :key="option.id"
              class="result-item"
            >
              <div class="result-header">
                <div class="option-info">
                  <el-badge 
                    :value="index + 1" 
                    :type="getBadgeType(index)"
                    class="rank-badge"
                    :hidden="results.total_votes === 0"
                  >
                    <span class="option-text">{{ option.text }}</span>
                  </el-badge>
                  <el-tag 
                    v-if="userVotes.includes(option.id)" 
                    type="success" 
                    size="small"
                    class="voted-tag"
                  >
                    您的选择
                  </el-tag>
                </div>
                <div class="vote-info">
                  <span class="vote-count">{{ option.vote_count }} 票</span>
                  <span class="vote-percentage">
                    {{ getPercentage(option.vote_count) }}%
                  </span>
                </div>
              </div>
              
              <div class="progress-bar">
                <el-progress
                  :percentage="getPercentage(option.vote_count)"
                  :color="getProgressColor(index)"
                  :stroke-width="20"
                  :show-text="false"
                />
              </div>
            </div>
          </div>
          
          <div class="summary-section">
            <el-row :gutter="20">
              <el-col :span="8">
                <div class="stat-card">
                  <div class="stat-icon" style="background: #409eff;">
                    <el-icon><DataAnalysis /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-value">{{ results.total_votes }}</div>
                    <div class="stat-label">总投票数</div>
                  </div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="stat-card">
                  <div class="stat-icon" style="background: #67c23a;">
                    <el-icon><Menu /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-value">{{ results.options.length }}</div>
                    <div class="stat-label">选项数量</div>
                  </div>
                </div>
              </el-col>
              <el-col :span="8">
                <div class="stat-card">
                  <div class="stat-icon" style="background: #e6a23c;">
                    <el-icon><Trophy /></el-icon>
                  </div>
                  <div class="stat-info">
                    <div class="stat-value">{{ winningOption }}</div>
                    <div class="stat-label">领先选项</div>
                  </div>
                </div>
              </el-col>
            </el-row>
          </div>
        </div>
        
        <div class="chart-section" v-if="results.total_votes > 0">
          <h3 class="section-title">可视化图表</h3>
          <div class="chart-container">
            <div class="pie-chart">
              <div 
                v-for="(option, index) in sortedOptions" 
                :key="option.id"
                class="pie-legend"
              >
                <span 
                  class="legend-color" 
                  :style="{ backgroundColor: getProgressColor(index) }"
                ></span>
                <span class="legend-text">{{ option.text }}</span>
                <span class="legend-value">{{ getPercentage(option.vote_count) }}%</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="action-buttons">
          <el-button type="primary" @click="goBack">返回列表</el-button>
          <el-button 
            v-if="!hasVoted && pollId" 
            @click="goToVote"
          >
            去投票
          </el-button>
        </div>
      </el-card>
    </el-main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, DataAnalysis, Menu, Trophy } from '@element-plus/icons-vue'
import { getPollResults, getUserVotes } from '@/api/poll'
import { getUser } from '@/utils/auth'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const results = ref(null)
const userVotes = ref([])
const user = ref(getUser())

const pollId = route.params.id

const fetchResults = async () => {
  try {
    loading.value = true
    results.value = await getPollResults(pollId)
    
    try {
      const votes = await getUserVotes(pollId)
      userVotes.value = votes.map(v => v.option)
    } catch (e) {
      userVotes.value = []
    }
  } catch (error) {
    console.error('获取投票结果失败', error)
  } finally {
    loading.value = false
  }
}

const sortedOptions = computed(() => {
  if (!results.value) return []
  return [...results.value.options].sort((a, b) => b.vote_count - a.vote_count)
})

const hasVoted = computed(() => {
  return userVotes.value.length > 0
})

const winningOption = computed(() => {
  if (!results.value || results.value.total_votes === 0) return '-'
  return sortedOptions.value[0]?.text || '-'
})

const getPercentage = (count) => {
  if (!results.value || results.value.total_votes === 0) return 0
  return ((count / results.value.total_votes) * 100).toFixed(1)
}

const getBadgeType = (index) => {
  if (index === 0) return 'danger'
  if (index === 1) return 'warning'
  if (index === 2) return 'primary'
  return 'info'
}

const getProgressColor = (index) => {
  const colors = ['#f56c6c', '#e6a23c', '#409eff', '#67c23a', '#909399', '#8e44ad']
  return colors[index % colors.length]
}

const goBack = () => {
  router.push('/')
}

const goToVote = () => {
  router.push(`/poll/${pollId}`)
}

onMounted(() => {
  fetchResults()
})
</script>

<style scoped>
.poll-results-container {
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
  max-width: 900px;
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
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
  padding: 20px;
}

.results-card {
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

.poll-description {
  color: #606266;
  font-size: 15px;
  margin-bottom: 30px;
  line-height: 1.6;
}

.section-title {
  font-size: 18px;
  color: #303133;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #ebeef5;
}

.results-list {
  margin-bottom: 30px;
}

.result-item {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #fafafa;
  border-radius: 8px;
  transition: all 0.3s;
}

.result-item:hover {
  background-color: #f5f7fa;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.option-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.rank-badge {
  font-size: 15px;
  font-weight: 500;
}

.option-text {
  color: #303133;
}

.voted-tag {
  margin-left: 5px;
}

.vote-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.vote-count {
  font-weight: 600;
  color: #606266;
}

.vote-percentage {
  font-weight: 700;
  font-size: 18px;
  color: #409eff;
}

.progress-bar {
  margin-top: 5px;
}

.summary-section {
  margin-bottom: 30px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea10 0%, #764ba210 100%);
  border-radius: 8px;
}

.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #303133;
}

.stat-label {
  font-size: 13px;
  color: #909399;
}

.chart-section {
  margin-bottom: 30px;
}

.chart-container {
  display: flex;
  justify-content: center;
}

.pie-chart {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-width: 300px;
}

.pie-legend {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 15px;
  background-color: #fafafa;
  border-radius: 6px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 3px;
  flex-shrink: 0;
}

.legend-text {
  flex: 1;
  color: #606266;
}

.legend-value {
  font-weight: 600;
  color: #303133;
}

.action-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}
</style>
