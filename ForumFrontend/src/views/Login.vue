<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h2>用户登录</h2>
      </div>
      <el-form
        ref="formRef"
        :model="loginForm"
        :rules="loginRules"
        label-width="80px"
        class="login-form"
        label-position="top"
      >
        <el-form-item label="账号" prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="请输入账号"
          >
            <template #prefix>
              <el-icon><User /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="请输入密码"
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
            @click="handleLogin"
            class="login-button"
          >登录</el-button>
        </el-form-item>
        <div class="login-options">
          <router-link to="/register">没有账号？立即注册</router-link>
          <router-link to="/reset-password">忘记密码？</router-link>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { User, Lock } from '@element-plus/icons-vue'
import { login, getUserInfo } from '../api/user'

// 是否启用调试日志
const DEBUG = false;

// 自定义日志函数，可以通过DEBUG开关控制
const log = (...args) => {
  if (DEBUG) {
    console.log(...args);
  }
};

export default {
  name: 'Login',
  components: {
    User,
    Lock
  },
  setup() {
    const router = useRouter()
    const store = useStore()
    const formRef = ref(null)
    const loading = ref(false)

    // 表单数据
    const loginForm = reactive({
      username: '',
      password: ''
    })

    // 表单验证规则
    const loginRules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 3, max: 50, message: '用户名长度应在3-50个字符之间', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, max: 20, message: '密码长度应在6-20个字符之间', trigger: 'blur' }
      ]
    }

    // 登录处理
    const handleLogin = async () => {
      try {
        // 表单验证
        await formRef.value.validate()

        // 显示加载状态
        loading.value = true

        // 调用登录API
        const response = await login(loginForm)
        log('登录响应:', response)

        // 检查响应中是否包含错误信息
        if (response.status !== 0 && response.status !== 200) {
          throw new Error(response.msg || '登录失败')
        }

        // 处理不同的响应格式
        let token, userInfo

        log('原始响应结构:', JSON.stringify(response))

        // 实际API返回的数据结构可能是 { status: 0, msg: "登录成功", data: { token: "...", user_info: {...} } }
        if (response.data) {
          // 如果响应中有data字段
          log('处理data字段:', response.data)
          if (response.data.token) {
            token = response.data.token
            userInfo = response.data.user_info || response.data.userInfo || response.data.user
          } else if (response.data.access) {
            // JWT格式响应嵌套在data中
            token = response.data.access
            userInfo = response.data.user || { username: loginForm.username }
          }
        } else if (response.token) {
          // 直接在响应根级别有token
          token = response.token
          userInfo = response.user_info || response.userInfo || response.user
        } else if (response.access) {
          // JWT格式的响应
          token = response.access
          // 如果没有用户信息，创建一个简单的用户对象
          userInfo = response.user || { username: loginForm.username }
        }

        // 确保用户信息至少包含id字段
        if (!userInfo?.id && loginForm.username) {
          // 如果没有id但有username，调用API获取完整用户信息
          try {
            const userResponse = await getUserInfo();
            if (userResponse && userResponse.data) {
              userInfo = userResponse.data;
            }
          } catch (err) {
            console.error('获取用户信息失败:', err);
          }
        }

        if (!token) {
          throw new Error('登录失败：服务器响应中没有找到token')
        }

        log('解析后的token和用户信息:', { token, userInfo })

        // 登录成功，保存token和用户信息
        log('开始调用Vuex store登录动作')
        try {
          await store.dispatch('login', { token, userInfo })
          log('Vuex store登录动作执行成功')
        } catch (err) {
          console.error('Vuex store登录动作失败:', err)
        }
        
        log('开始保存到localStorage')
        // 为确保一致性，也直接保存到localStorage
        localStorage.setItem('token', token)
        localStorage.setItem('userInfo', JSON.stringify(userInfo))
        log('localStorage保存成功')
        
        // 检查是否有重定向路径
        const redirect = router.currentRoute.value.query.redirect || '/'
        log('登录成功，准备跳转到:', redirect)
        
        // 确保路由已准备好
        setTimeout(() => {
          // 用户已经登录，直接执行跳转
          log('执行跳转:', redirect)
          log('当前路由信息:', router.currentRoute.value)
          log('存储状态:', {
            token: store.state.token,
            user: store.state.user,
            isLoggedIn: store.getters.isLoggedIn
          })
          log('localStorage状态:', {
            token: localStorage.getItem('token'),
            userInfo: localStorage.getItem('userInfo')
          })
          
          // 直接执行跳转
          router.push(redirect).catch(err => {
            console.error('路由跳转失败:', err)
            // 如果跳转失败，尝试跳转到首页
            router.push('/')
          })
        }, 100)
      } catch (error) {
        console.error('登录失败:', error)

        // 处理后端返回的错误信息
        let errorMsg = '登录失败，请检查用户名和密码'

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

        // 使用全局的messageTracker来显示错误消息
        if (window.messageTracker) {
          window.messageTracker.showMessage(errorMsg, 'error', 'login-component-error');
        } else {
          // 如果全局对象不可用，再使用ElMessage
          import('element-plus').then(({ ElMessage }) => {
            ElMessage({
              message: errorMsg,
              type: 'error',
              dangerouslyUseHTMLString: true
            });
          });
        }
      } finally {
        loading.value = false
      }
    }

    return {
      loginForm,
      formRef,
      loginRules,
      loading,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
  padding: 20px 0;
}

.login-box {
  width: 400px;
  padding: 40px;
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  font-weight: 600;
  color: #303133;
  font-size: 24px;
  margin: 0;
}

.login-form {
  margin-top: 20px;
}

.login-form :deep(.el-form-item__label) {
  padding-bottom: 8px;
  font-weight: 500;
}

.login-form :deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px #dcdfe6 inset;
  padding: 1px 15px;
  height: 42px;
  transition: all 0.2s;
}

.login-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #c0c4cc inset;
}

.login-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #409eff inset;
}

.login-form :deep(.el-form-item) {
  margin-bottom: 25px;
}

.login-button {
  width: 100%;
  height: 42px;
  font-size: 16px;
  font-weight: 500;
  margin-top: 10px;
}

.login-options {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 20px;
  font-size: 14px;
}

.login-options a {
  color: #409eff;
  text-decoration: none;
  transition: color 0.2s;
}

.login-options a:hover {
  color: #66b1ff;
  text-decoration: underline;
}
</style>
