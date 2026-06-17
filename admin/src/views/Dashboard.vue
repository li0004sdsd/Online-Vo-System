<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon user">
              <el-icon :size="32"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_users }}</div>
              <div class="stat-label">总用户数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon poll">
              <el-icon :size="32"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_polls }}</div>
              <div class="stat-label">总投票数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon active">
              <el-icon :size="32"><Connection /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.active_users }}</div>
              <div class="stat-label">活跃用户数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon vote">
              <el-icon :size="32"><Checked /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.total_votes }}</div>
              <div class="stat-label">总投票次数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 24px;">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>投票状态分布</span>
            </div>
          </template>
          <div ref="statusChartRef" class="chart"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>投票详情统计</span>
            </div>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="待审核投票">
              <el-tag type="warning" size="large">{{ stats.pending_polls }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="已通过投票">
              <el-tag type="success" size="large">{{ stats.approved_polls }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="已删除投票">
              <el-tag type="danger" size="large">{{ stats.rejected_polls }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="投票通过率">
              <span style="font-weight: 600; color: #67c23a">
                {{ stats.total_polls > 0 ? ((stats.approved_polls / stats.total_polls) * 100).toFixed(1) : 0 }}%
              </span>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { getDashboardStats } from '@/api/admin'

const stats = ref({
  total_users: 0,
  total_polls: 0,
  active_users: 0,
  pending_polls: 0,
  approved_polls: 0,
  rejected_polls: 0,
  total_votes: 0
})

const statusChartRef = ref(null)
let statusChart = null

async function loadStats() {
  try {
    const data = await getDashboardStats()
    stats.value = data
    await nextTick()
    initChart()
  } catch (error) {
    ElMessage.error('加载统计数据失败')
  }
}

function initChart() {
  if (!statusChartRef.value) return

  if (statusChart) {
    statusChart.dispose()
  }

  statusChart = echarts.init(statusChartRef.value)

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'center'
    },
    series: [
      {
        name: '投票状态',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false,
          position: 'center'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 20,
            fontWeight: 'bold'
          }
        },
        labelLine: {
          show: false
        },
        data: [
          { value: stats.value.pending_polls, name: '待审核', itemStyle: { color: '#e6a23c' } },
          { value: stats.value.approved_polls, name: '已通过', itemStyle: { color: '#67c23a' } },
          { value: stats.value.rejected_polls, name: '已删除', itemStyle: { color: '#f56c6c' } }
        ]
      }
    ]
  }

  statusChart.setOption(option)
}

onMounted(() => {
  loadStats()

  window.addEventListener('resize', () => {
    statusChart?.resize()
  })
})
</script>

<style scoped>
.stat-card {
  text-align: center;
}

.stat-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  padding: 10px 0;
}

.stat-icon {
  width: 70px;
  height: 70px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-icon.user {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-icon.poll {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.stat-icon.active {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.stat-icon.vote {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.stat-info {
  text-align: left;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}

.card-header {
  font-weight: 600;
  font-size: 16px;
}

.chart {
  height: 300px;
}
</style>
