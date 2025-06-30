<template>
  <div class="register-container">
    <div class="register-box">
      <div class="register-header">
        <h2>用户注册</h2>
      </div>
      <el-form
        ref="formRef"
        :model="registerForm"
        :rules="registerRules"
        label-width="80px"
        class="register-form"
        label-position="top"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="registerForm.username"
            placeholder="请输入用户名"
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="registerForm.email"
            placeholder="请输入邮箱"
          >
            <template #prefix>
              <el-icon><Message /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="验证码" prop="code">
          <div class="verification-code-container">
            <el-input
              v-model="registerForm.code"
              placeholder="请输入验证码"
              maxlength="6"
            >
              <template #prefix>
                <el-icon><Key /></el-icon>
              </template>
            </el-input>
            <el-button
              type="primary"
              :disabled="codeSending || countdown > 0"
              @click="sendVerificationCode"
            >
              {{ countdown > 0 ? `${countdown}秒后重新发送` : '获取验证码' }}
            </el-button>
          </div>
          <div class="verification-tip" v-if="registerForm.code">
            验证码有效期为15分钟，请尽快完成验证
          </div>
        </el-form-item>
        <el-form-item label="昵称" prop="nickname">
          <el-input
            v-model="registerForm.nickname"
            placeholder="请输入昵称"
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            placeholder="请输入密码"
            show-password
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            show-password
          >
            <template #prefix>
              <el-icon><Lock /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            @click="handleRegister"
            class="register-button"
          >注册</el-button>
        </el-form-item>
        <div class="register-options">
          <router-link to="/login">已有账号？立即登录</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Message, Lock, Key } from '@element-plus/icons-vue'
import { sendVerificationCode as sendCode, registerWithVerification } from '../api/user'

export default {
  name: 'Register',
  components: {
    User,
    Message,
    Lock,
    Key
  },
  setup() {
    const router = useRouter()
    const formRef = ref(null)
    const loading = ref(false)
    const codeSending = ref(false)
    const countdown = ref(0)
    let countdownTimer = null

    // 表单数据
    const registerForm = reactive({
      username: '',
      email: '',
      nickname: '',
      password: '',
      confirmPassword: '',
      code: ''
    })

    // 表单验证规则
    const registerRules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 50, message: '用户名长度应在3-50个字符之间', trigger: 'blur' }
      ],
      email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
      ],
      nickname: [
        { required: true, message: '请输入昵称', trigger: 'blur' },
        { min: 2, max: 50, message: '昵称长度应在2-50个字符之间', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, max: 20, message: '密码长度应在6-20个字符之间', trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, message: '请再次输入密码', trigger: 'blur' },
        {
          validator: (rule, value, callback) => {
            if (value !== registerForm.password) {
              callback(new Error('两次输入的密码不一致'))
            } else {
              callback()
            }
          },
          trigger: 'blur'
        }
      ],
      code: [
        { required: true, message: '请输入验证码', trigger: 'blur' },
        { min: 6, max: 6, message: '验证码长度应为6位', trigger: 'blur' }
      ]
    }

    // 发送验证码
    const sendVerificationCode = async () => {
      try {
        // 验证邮箱
        await formRef.value.validateField('email')

        // 显示加载状态
        codeSending.value = true

        // 调用发送验证码API
        await sendCode({
          email: registerForm.email,
          type: 'register'
        })

        // 开始倒计时
        countdown.value = 60
        countdownTimer = setInterval(() => {
          countdown.value--
          if (countdown.value <= 0) {
            clearInterval(countdownTimer)
          }
        }, 1000)

        ElMessage({
          message: '验证码已发送，请查收邮件',
          type: 'success'
        })
      } catch (error) {
        console.error('发送验证码失败:', error)
        ElMessage({
          message: error.message || '发送验证码失败，请稍后重试',
          type: 'error'
        })
      } finally {
        codeSending.value = false
      }
    }

    // 注册处理
    const handleRegister = async () => {
      try {
        // 表单验证
        await formRef.value.validate()

        // 显示加载状态
        loading.value = true

        // 准备注册数据
        const registerPayload = {
          username: registerForm.username,
          email: registerForm.email,
          nickname: registerForm.nickname,
          password: registerForm.password,
          confirm_password: registerForm.confirmPassword,
          code: registerForm.code
        }

        // 调用带验证码的注册API
        await registerWithVerification(registerPayload)

        ElMessage({
          message: '注册成功，请登录',
          type: 'success'
        })

        // 跳转到登录页
        router.push('/login')
      } catch (error) {
        console.error('注册失败:', error)

        // 处理后端返回的错误信息
        let errorMsg = '注册失败，请检查输入信息'

        if (error.response && error.response.data) {
          const responseData = error.response.data

          if (responseData.msg && typeof responseData.msg === 'object') {
            // 处理字段错误
            const fieldErrors = []
            for (const field in responseData.msg) {
              if (Array.isArray(responseData.msg[field])) {
                fieldErrors.push(`${field}: ${responseData.msg[field].join(', ')}`)
              } else {
                fieldErrors.push(`${field}: ${responseData.msg[field]}`)
              }
            }
            if (fieldErrors.length > 0) {
              errorMsg = fieldErrors.join('\n')
            }
          } else if (responseData.msg) {
            errorMsg = responseData.msg
          }
        } else if (error.message) {
          errorMsg = error.message
        }

        ElMessage({
          message: errorMsg,
          type: 'error',
          dangerouslyUseHTMLString: true
        })
      } finally {
        loading.value = false
      }
    }

    // 组件销毁前清除定时器
    onBeforeUnmount(() => {
      if (countdownTimer) {
        clearInterval(countdownTimer)
      }
    })

    return {
      registerForm,
      formRef,
      registerRules,
      loading,
      codeSending,
      countdown,
      sendVerificationCode,
      handleRegister
    }
  }
}
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 20px 0;
}

.register-box {
  width: 450px;
  padding: 40px;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.register-header {
  text-align: center;
  margin-bottom: 30px;
}

.register-header h2 {
  font-weight: 600;
  color: #303133;
  font-size: 24px;
  margin: 0;
}

.register-form {
  margin-top: 20px;
}

.register-form :deep(.el-form-item__label) {
  padding-bottom: 8px;
  font-weight: 500;
}

.register-form :deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px #dcdfe6 inset;
  padding: 1px 15px;
  height: 42px;
  transition: all 0.2s;
}

.register-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #c0c4cc inset;
}

.register-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #409eff inset;
}

.register-form :deep(.el-form-item) {
  margin-bottom: 25px;
}

.register-button {
  width: 100%;
  height: 42px;
  font-size: 16px;
  font-weight: 500;
  margin-top: 10px;
}

.register-options {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  font-size: 14px;
}

.register-options a {
  color: #409eff;
  text-decoration: none;
  transition: color 0.2s;
}

.register-options a:hover {
  color: #66b1ff;
  text-decoration: underline;
}

.verification-code-container {
  display: flex;
  gap: 10px;
}

.verification-code-container .el-input {
  flex: 1;
}

.verification-code-container :deep(.el-button) {
  height: 42px;
  padding: 0 15px;
  white-space: nowrap;
}

.verification-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
  line-height: 1.4;
}
</style>
