<template>
  <div class="login-container">
    <el-card class="login-card">
      <div class="login-header">
        <h1>投票系统管理后台</h1>
        <p>管理员登录</p>
      </div>
      <el-form :model="form" :rules="rules" ref="loginForm" @submit.prevent="handleLogin">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" prefix-icon="User" size="large" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" prefix-icon="Lock" size="large" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" style="width: 100%" :loading="loading" @click="handleLogin">
            登录
          </el-button>
        </el-form-item>
      </el-form>
      <div class="login-tip">
        <el-alert title="请使用管理员账号登录" type="info" :closable="false" show-icon />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login as loginApi, getUserInfo } from '@/api/auth'
import { setToken, setUser } from '@/utils/auth'

const router = useRouter()
const loginForm = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function handleLogin() {
  try {
    await loginForm.value.validate()
  } catch {
    return
  }

  loading.value = true
  try {
    const tokenData = await loginApi(form)
    setToken(tokenData)

    const userInfo = await getUserInfo()
    if (!userInfo.is_staff) {
      ElMessage.error('该账号没有管理员权限')
      return
    }
    setUser(userInfo)

    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    if (error.response?.status === 401) {
      ElMessage.error('用户名或密码错误')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 420px;
  padding: 20px;
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  font-size: 24px;
  color: #303133;
  margin-bottom: 8px;
}

.login-header p {
  color: #909399;
  font-size: 14px;
}

.login-tip {
  margin-top: 20px;
}
</style>
