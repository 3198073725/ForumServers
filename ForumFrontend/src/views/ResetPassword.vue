<template>
  <div class="reset-password-container">
    <div class="reset-password-box">
      <div class="reset-password-header">
        <h2>重置密码</h2>
      </div>

      <!-- 步骤条 -->
      <el-steps :active="currentStep" finish-status="success" simple>
        <el-step title="邮箱验证" />
        <el-step title="重置密码" />
        <el-step title="重置完成" />
      </el-steps>

      <!-- 步骤1：邮箱验证 -->
      <div v-if="currentStep === 0">
        <el-form
          ref="emailFormRef"
          :model="emailForm"
          :rules="emailRules"
          label-width="100px"
          class="reset-password-form"
          label-position="top"
        >
          <el-form-item label="邮箱" prop="email">
            <el-input
              v-model="emailForm.email"
              placeholder="请输入注册时使用的邮箱"
            >
              <template #prefix>
                <el-icon><Message /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item label="验证码" prop="code">
            <div class="verification-code-container">
              <el-input
                v-model="emailForm.code"
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
            <div class="verification-tip" v-if="emailForm.code">
              验证码有效期为15分钟，请尽快完成验证
            </div>
          </el-form-item>

          <el-form-item>
            <el-button
              type="primary"
              :loading="verifying"
              @click="verifyEmail"
              class="reset-password-button"
            >下一步</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 步骤2：重置密码 -->
      <div v-if="currentStep === 1">
        <el-form
          ref="passwordFormRef"
          :model="passwordForm"
          :rules="passwordRules"
          label-width="100px"
          class="reset-password-form"
          label-position="top"
        >
          <el-form-item label="新密码" prop="newPassword">
            <el-input
              v-model="passwordForm.newPassword"
              type="password"
              placeholder="请输入新密码"
              show-password
            >
              <template #prefix>
                <el-icon><Lock /></el-icon>
              </template>
            </el-input>
          </el-form-item>

          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input
              v-model="passwordForm.confirmPassword"
              type="password"
              placeholder="请再次输入新密码"
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
              :loading="resetting"
              @click="handleResetPassword"
              class="reset-password-button"
            >重置密码</el-button>
            <el-button @click="currentStep = 0" class="reset-password-button-two">上一步</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 步骤3：重置完成 -->
      <div v-if="currentStep === 2" class="reset-password-success">
        <el-result
          icon="success"
          title="密码重置成功"
          sub-title="您的密码已成功重置，现在可以使用新密码登录了"
        >
          <template #extra>
            <el-button type="primary" @click="goToLogin">去登录</el-button>
          </template>
        </el-result>
      </div>

      <div class="reset-password-options" v-if="currentStep < 2">
        <router-link to="/login">返回登录</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Message, Lock, Key } from '@element-plus/icons-vue'
import { sendVerificationCode as sendCode, verifyEmail as verifyCode, resetPassword } from '../api/user'

export default {
  name: 'ResetPassword',
  components: {
    Message,
    Lock,
    Key
  },
  setup() {
    const router = useRouter()
    const currentStep = ref(0)
    const emailFormRef = ref(null)
    const passwordFormRef = ref(null)
    const codeSending = ref(false)
    const verifying = ref(false)
    const resetting = ref(false)
    const countdown = ref(0)
    let countdownTimer = null

    // 邮箱验证表单
    const emailForm = reactive({
      email: '',
      code: ''
    })

    // 密码重置表单
    const passwordForm = reactive({
      newPassword: '',
      confirmPassword: '',
      email: '', // 将从邮箱验证表单中获取
      code: ''   // 将从邮箱验证表单中获取
    })

    // 邮箱验证表单规则
    const emailRules = {
      email: [
        { required: true, message: '请输入邮箱', trigger: 'blur' },
        { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
      ],
      code: [
        { required: true, message: '请输入验证码', trigger: 'blur' },
        { min: 6, max: 6, message: '验证码长度应为6位', trigger: 'blur' }
      ]
    }

    // 密码重置表单规则
    const passwordRules = {
      newPassword: [
        { required: true, message: '请输入新密码', trigger: 'blur' },
        { min: 6, max: 20, message: '密码长度应在6-20个字符之间', trigger: 'blur' }
      ],
      confirmPassword: [
        { required: true, message: '请再次输入新密码', trigger: 'blur' },
        {
          validator: (rule, value, callback) => {
            if (value !== passwordForm.newPassword) {
              callback(new Error('两次输入的密码不一致'))
            } else {
              callback()
            }
          },
          trigger: 'blur'
        }
      ]
    }

    // 发送验证码
    const sendVerificationCode = async () => {
      try {
        // 验证邮箱
        await emailFormRef.value.validateField('email')

        // 显示加载状态
        codeSending.value = true

        // 调用发送验证码API
        await sendCode({
          email: emailForm.email,
          type: 'reset_password'
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

    // 验证邮箱
    const verifyEmail = async () => {
      try {
        // 表单验证
        await emailFormRef.value.validate()

        // 显示加载状态
        verifying.value = true

        // 调用验证邮箱API
        await verifyCode({
          email: emailForm.email,
          code: emailForm.code,
          type: 'reset_password'
        })

        // 将邮箱和验证码传递给密码重置表单
        passwordForm.email = emailForm.email
        passwordForm.code = emailForm.code

        // 进入下一步
        currentStep.value = 1

        ElMessage({
          message: '邮箱验证成功',
          type: 'success'
        })
      } catch (error) {
        console.error('邮箱验证失败:', error)
        ElMessage({
          message: error.message || '邮箱验证失败，请检查验证码是否正确',
          type: 'error'
        })
      } finally {
        verifying.value = false
      }
    }

    // 重置密码处理
    const handleResetPassword = async () => {
      try {
        // 表单验证
        await passwordFormRef.value.validate()

        // 显示加载状态
        resetting.value = true

        // 准备重置密码数据
        const resetPasswordPayload = {
          email: passwordForm.email,
          code: passwordForm.code,
          new_password: passwordForm.newPassword,
          confirm_password: passwordForm.confirmPassword
        }

        // 调用重置密码API
        await resetPassword(resetPasswordPayload)

        // 进入下一步
        currentStep.value = 2

        ElMessage({
          message: '密码重置成功',
          type: 'success'
        })
      } catch (error) {
        console.error('密码重置失败:', error)

        // 处理后端返回的错误信息
        let errorMsg = '密码重置失败，请稍后重试'

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
        resetting.value = false
      }
    }

    // 跳转到登录页
    const goToLogin = () => {
      router.push('/login')
    }

    // 组件销毁前清除定时器
    onBeforeUnmount(() => {
      if (countdownTimer) {
        clearInterval(countdownTimer)
      }
    })

    return {
      currentStep,
      emailFormRef,
      passwordFormRef,
      emailForm,
      passwordForm,
      emailRules,
      passwordRules,
      codeSending,
      verifying,
      resetting,
      countdown,
      sendVerificationCode,
      verifyEmail,
      handleResetPassword,
      goToLogin
    }
  }
}
</script>

<style scoped>
.reset-password-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 20px 0;
}

.reset-password-box {
  width: 500px;
  padding: 40px;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.reset-password-header {
  text-align: center;
  margin-bottom: 20px;
}

.reset-password-header h2 {
  font-weight: 600;
  color: #303133;
  font-size: 24px;
  margin: 0;
}

.reset-password-form {
  margin-top: 30px;
}

.reset-password-form :deep(.el-form-item__label) {
  padding-bottom: 8px;
  font-weight: 500;
}

.reset-password-form :deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px #dcdfe6 inset;
  padding: 1px 15px;
  height: 42px;
  transition: all 0.2s;
}

.reset-password-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #c0c4cc inset;
}

.reset-password-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #409eff inset;
}

.reset-password-form :deep(.el-form-item) {
  margin-bottom: 25px;
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

.reset-password-button {
  width: 100%;
  height: 42px;
  font-size: 16px;
  font-weight: 500;
  margin-top: 10px;
}
.reset-password-button-two {
  width: 100%;
  height: 42px;
  font-size: 16px;
  font-weight: 500;
  margin-top: 10px;
  margin-right: 0px;
  margin-left: 0px;
}
.reset-password-options {
  display: flex;
  justify-content: center;
  margin-top: 20px;
  font-size: 14px;
}

.reset-password-options a {
  color: #409eff;
  text-decoration: none;
  transition: color 0.2s;
}

.reset-password-options a:hover {
  color: #66b1ff;
  text-decoration: underline;
}

.reset-password-success {
  margin-top: 20px;
}

.verification-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
  line-height: 1.4;
}

:deep(.el-steps--simple) {
  margin-top: 20px;
  margin-bottom: 30px;
}

:deep(.el-step__title) {
  font-size: 14px;
  font-weight: 500;
}
</style>
