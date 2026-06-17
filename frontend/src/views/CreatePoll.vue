<template>
  <div class="create-poll-container">
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
    
    <el-main class="main-content">
      <el-card class="form-card">
        <h2 class="form-title">创建新投票</h2>
        <el-form
          ref="pollForm"
          :model="form"
          :rules="rules"
          label-width="100px"
          class="poll-form"
        >
          <el-form-item label="投票标题" prop="title">
            <el-input v-model="form.title" placeholder="请输入投票标题" maxlength="200" />
          </el-form-item>
          
          <el-form-item label="投票描述" prop="description">
            <el-input
              v-model="form.description"
              type="textarea"
              :rows="3"
              placeholder="请输入投票描述（可选）"
              maxlength="500"
            />
          </el-form-item>
          
          <el-form-item label="投票类型" prop="allow_multiple">
            <el-radio-group v-model="form.allow_multiple">
              <el-radio :label="false">单选</el-radio>
              <el-radio :label="true">多选</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item label="投票选项" prop="options">
            <div class="options-list">
              <div 
                v-for="(option, index) in form.options" 
                :key="index" 
                class="option-item"
              >
                <el-input 
                  v-model="form.options[index]" 
                  :placeholder="`选项 ${index + 1}`"
                  maxlength="200"
                />
                <el-button 
                  type="danger" 
                  size="small" 
                  :icon="Delete"
                  @click="removeOption(index)"
                  :disabled="form.options.length <= 2"
                />
              </div>
            </div>
            <el-button 
              type="primary" 
              size="small" 
              :icon="Plus"
              @click="addOption"
              class="add-option-btn"
            >
              添加选项
            </el-button>
          </el-form-item>
          
          <el-form-item>
            <el-button type="primary" @click="handleSubmit" :loading="loading">
              创建投票
            </el-button>
            <el-button @click="goBack">取消</el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </el-main>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft, Plus, Delete } from '@element-plus/icons-vue'
import { createPoll } from '@/api/poll'
import { getUser } from '@/utils/auth'

const router = useRouter()
const loading = ref(false)
const pollForm = ref(null)
const user = ref(getUser())

const form = reactive({
  title: '',
  description: '',
  allow_multiple: false,
  options: ['', '']
})

const validateOptions = (rule, value, callback) => {
  const filledOptions = form.options.filter(opt => opt.trim() !== '')
  if (filledOptions.length < 2) {
    callback(new Error('至少需要2个有效选项'))
  } else {
    callback()
  }
}

const rules = {
  title: [
    { required: true, message: '请输入投票标题', trigger: 'blur' },
    { min: 2, max: 200, message: '标题长度在 2 到 200 个字符', trigger: 'blur' }
  ],
  allow_multiple: [
    { required: true, message: '请选择投票类型', trigger: 'change' }
  ],
  options: [
    { validator: validateOptions, trigger: 'blur' }
  ]
}

const addOption = () => {
  if (form.options.length < 10) {
    form.options.push('')
  } else {
    ElMessage.warning('最多只能添加10个选项')
  }
}

const removeOption = (index) => {
  if (form.options.length > 2) {
    form.options.splice(index, 1)
  }
}

const handleSubmit = async () => {
  try {
    await pollForm.value.validate()
    
    const filledOptions = form.options.filter(opt => opt.trim() !== '')
    if (filledOptions.length < 2) {
      ElMessage.error('至少需要2个有效选项')
      return
    }
    
    loading.value = true
    
    const submitData = {
      title: form.title,
      description: form.description,
      allow_multiple: form.allow_multiple,
      options: filledOptions
    }
    
    await createPoll(submitData)
    
    ElMessage.success('投票创建成功')
    router.push('/')
  } catch (error) {
    console.error('创建投票失败', error)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/')
}
</script>

<style scoped>
.create-poll-container {
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

.form-card {
  padding: 30px;
}

.form-title {
  text-align: center;
  margin-bottom: 30px;
  color: #303133;
}

.poll-form {
  max-width: 600px;
  margin: 0 auto;
}

.options-list {
  margin-bottom: 15px;
}

.option-item {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.option-item .el-input {
  flex: 1;
}

.add-option-btn {
  width: 100%;
}
</style>
