<template>
  <el-container class="layout-container">
    <el-aside width="220px" class="aside">
      <div class="logo">
        <el-icon :size="28"><DataBoard /></el-icon>
        <span>投票管理系统</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="menu"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        router
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataBoard /></el-icon>
          <span>数据看板</span>
        </el-menu-item>
        <el-sub-menu index="polls">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>投票管理</span>
          </template>
          <el-menu-item index="/polls/pending">
            <el-icon><DocumentChecked /></el-icon>
            <span>审核投票</span>
            <el-badge v-if="pendingCount > 0" :value="pendingCount" class="badge" />
          </el-menu-item>
          <el-menu-item index="/polls/rejected">
            <el-icon><Delete /></el-icon>
            <span>删除违规投票</span>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <span class="title">{{ currentTitle }}</span>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="32" style="background-color: #409EFF">{{ user?.username?.charAt(0)?.toUpperCase() }}</el-avatar>
              <span class="username">{{ user?.username }}</span>
              <el-tag size="small" type="warning" effect="dark">管理员</el-tag>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUser, removeToken } from '@/utils/auth'
import { getPollList } from '@/api/admin'

const route = useRoute()
const router = useRouter()

const user = ref(getUser())
const pendingCount = ref(0)

const activeMenu = computed(() => route.path)
const currentTitle = computed(() => route.meta?.title || '管理后台')

function handleCommand(command) {
  if (command === 'logout') {
    ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }).then(() => {
      removeToken()
      ElMessage.success('已退出登录')
      router.push('/login')
    }).catch(() => {})
  }
}

async function loadPendingCount() {
  try {
    const data = await getPollList('pending')
    pendingCount.value = data.length
  } catch {}
}

onMounted(() => {
  loadPendingCount()
})

watch(
  () => route.path,
  () => {
    loadPendingCount()
  }
)
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.aside {
  background-color: #304156;
  color: #fff;
  overflow: hidden;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  font-size: 18px;
  font-weight: bold;
  color: #fff;
  border-bottom: 1px solid #1f2d3d;
}

.menu {
  border-right: none;
}

.menu :deep(.el-menu-item) {
  height: 50px;
  line-height: 50px;
}

.menu :deep(.el-sub-menu__title) {
  height: 50px;
  line-height: 50px;
}

.badge {
  margin-left: 10px;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.header-left .title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.username {
  color: #303133;
  font-size: 14px;
}

.main {
  background-color: #f0f2f5;
  padding: 24px;
}
</style>
