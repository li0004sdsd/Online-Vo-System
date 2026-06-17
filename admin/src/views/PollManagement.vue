<template>
  <div class="poll-management">
    <el-card shadow="never">
      <div class="card-header">
        <div class="title-section">
          <el-page-header @back="$router.back()" :title="pageTitle">
            <template #content>
              <el-tag v-if="status === 'pending'" type="warning">待审核 {{ polls.length }} 条</el-tag>
              <el-tag v-else type="danger">已删除 {{ polls.length }} 条</el-tag>
            </template>
          </el-page-header>
        </div>
        <div class="action-section">
          <el-input
            v-model="searchText"
            placeholder="搜索投票标题..."
            style="width: 300px"
            clearable
            :prefix-icon="Search"
          />
          <el-button type="primary" @click="loadPolls" :icon="Refresh">
            刷新
          </el-button>
        </div>
      </div>

      <el-table
        :data="filteredPolls"
        v-loading="loading"
        style="width: 100%"
        empty-text="暂无数据"
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column prop="title" label="投票标题" min-width="200">
          <template #default="{ row }">
            <div class="poll-title">
              <span>{{ row.title }}</span>
              <el-tag v-if="row.status === 'pending'" type="warning" size="small" style="margin-left: 8px;">
                待审核
              </el-tag>
              <el-tag v-else-if="row.status === 'approved'" type="success" size="small" style="margin-left: 8px;">
                已通过
              </el-tag>
              <el-tag v-else type="danger" size="small" style="margin-left: 8px;">
                已删除
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="创建者" width="150">
          <template #default="{ row }">
            <div class="creator-info">
              <el-avatar :size="28" style="background-color: #409EFF">
                {{ row.creator?.username?.charAt(0)?.toUpperCase() }}
              </el-avatar>
              <span class="creator-name">{{ row.creator?.username }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="total_votes" label="投票数" width="100" align="center">
          <template #default="{ row }">
            <el-badge :value="row.total_votes" class="badge" />
          </template>
        </el-table-column>
        <el-table-column v-if="status === 'rejected'" label="删除原因" min-width="200">
          <template #default="{ row }">
            <el-tooltip :content="row.reject_reason" placement="top">
              <span class="reject-reason">{{ row.reject_reason || '违规内容' }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" link @click="viewDetail(row)">
              <el-icon><View /></el-icon> 详情
            </el-button>
            <template v-if="status === 'pending'">
              <el-button type="success" link @click="handleApprove(row)">
                <el-icon><Check /></el-icon> 通过
              </el-button>
              <el-button type="danger" link @click="handleReject(row)">
                <el-icon><Close /></el-icon> 删除
              </el-button>
            </template>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="detailVisible" title="投票详情" width="600px">
      <div v-if="currentPoll" class="poll-detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="投票标题">
            {{ currentPoll.title }}
          </el-descriptions-item>
          <el-descriptions-item label="投票描述">
            {{ currentPoll.description || '无' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建者">
            {{ currentPoll.creator?.username }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDate(currentPoll.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="投票类型">
            {{ currentPoll.allow_multiple ? '多选' : '单选' }}
          </el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="getStatusTagType(currentPoll.status)">
              {{ currentPoll.status_display }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item v-if="currentPoll.reject_reason" label="删除原因">
            <span style="color: #f56c6c;">{{ currentPoll.reject_reason }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="投票选项">
            <div class="options-list">
              <div v-for="option in currentPoll.options" :key="option.id" class="option-item">
                <span class="option-text">{{ option.text }}</span>
                <el-tag size="small" type="info">{{ option.vote_count }} 票</el-tag>
              </div>
            </div>
          </el-descriptions-item>
        </el-descriptions>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="detailVisible = false">关闭</el-button>
          <template v-if="status === 'pending' && currentPoll?.status === 'pending'">
            <el-button type="success" @click="handleApprove(currentPoll)">
              通过审核
            </el-button>
            <el-button type="danger" @click="handleReject(currentPoll)">
              删除违规
            </el-button>
          </template>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Refresh, View, Check, Close } from '@element-plus/icons-vue'
import { getPollList, approvePoll, rejectPoll } from '@/api/admin'

const route = useRoute()

const status = computed(() => route.meta.status || 'pending')
const pageTitle = computed(() => route.meta.title || '投票管理')

const polls = ref([])
const loading = ref(false)
const searchText = ref('')
const detailVisible = ref(false)
const currentPoll = ref(null)

const filteredPolls = computed(() => {
  if (!searchText.value) return polls.value
  return polls.value.filter(p =>
    p.title.toLowerCase().includes(searchText.value.toLowerCase())
  )
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function getStatusTagType(s) {
  if (s === 'pending') return 'warning'
  if (s === 'approved') return 'success'
  return 'danger'
}

async function loadPolls() {
  loading.value = true
  try {
    const data = await getPollList(status.value)
    polls.value = data
  } catch (error) {
    ElMessage.error('加载投票列表失败')
  } finally {
    loading.value = false
  }
}

async function viewDetail(poll) {
  currentPoll.value = poll
  detailVisible.value = true
}

async function handleApprove(poll) {
  try {
    await ElMessageBox.confirm(
      `确定要通过投票「${poll.title}」的审核吗？`,
      '审核通过',
      {
        confirmButtonText: '确定通过',
        cancelButtonText: '取消',
        type: 'success'
      }
    )
    await approvePoll(poll.id)
    ElMessage.success('投票已通过审核')
    loadPolls()
    if (detailVisible.value) {
      detailVisible.value = false
    }
  } catch {}
}

async function handleReject(poll) {
  try {
    const { value: reason } = await ElMessageBox.prompt(
      `请输入删除「${poll.title}」的原因`,
      '删除违规投票',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        inputPlaceholder: '请输入违规原因',
        inputValue: '违规内容检测',
        type: 'warning'
      }
    )
    await rejectPoll(poll.id, reason)
    ElMessage.success('投票已删除')
    loadPolls()
    if (detailVisible.value) {
      detailVisible.value = false
    }
  } catch {}
}

onMounted(() => {
  loadPolls()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
}

.title-section {
  flex: 1;
}

.action-section {
  display: flex;
  gap: 12px;
  align-items: center;
}

.poll-title {
  display: flex;
  align-items: center;
}

.creator-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.creator-name {
  font-size: 14px;
  color: #303133;
}

.badge :deep(.el-badge__content) {
  position: static;
  transform: none;
  font-size: 14px;
  background-color: #ecf5ff;
  color: #409eff;
  border: 1px solid #d9ecff;
}

.reject-reason {
  display: inline-block;
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: #f56c6c;
}

.poll-detail {
  padding: 10px 0;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.option-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.option-text {
  font-size: 14px;
  color: #303133;
}

.dialog-footer {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}
</style>
