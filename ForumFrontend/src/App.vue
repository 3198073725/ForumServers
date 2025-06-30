<template>
  <div id="app">
    <el-container>
      <el-header>
        <div class="header-content">
          <div class="logo">
            <router-link to="/">论坛系统</router-link>
          </div>
          <div class="nav">
            <el-menu mode="horizontal" :router="true" :default-active="activeRoute">
              <el-menu-item index="/">首页</el-menu-item>
              <el-menu-item index="/boards">板块</el-menu-item>
              <el-menu-item index="/posts">帖子</el-menu-item>
              <el-menu-item index="/ranking">排行榜</el-menu-item>
              <el-menu-item index="/complaints">投诉中心</el-menu-item>
            </el-menu>
          </div>
          <div class="user-actions">
            <template v-if="isLoggedIn">
              <!-- 通知铃铛 -->
              <NotificationBell v-if="notificationsEnabled" />
              
              <!-- 用户头像和下拉菜单 -->
              <el-dropdown trigger="click" @command="handleCommand">
                <div class="user-avatar">
                  <el-avatar :size="32" :src="userAvatar">
                    {{ username && username.substring(0, 1).toUpperCase() }}
                  </el-avatar>
                  <span class="username">{{ user && (user.nickname || user.username) }}</span>
                </div>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                    <el-dropdown-item v-if="isAdmin" command="admin">管理后台</el-dropdown-item>
                    <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </template>
            <template v-else>
              <el-button type="primary" @click="goToLogin">登录</el-button>
              <el-button @click="goToRegister">注册</el-button>
            </template>
          </div>
        </div>
      </el-header>
      
      <el-container class="main-container">
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    
    </el-container>
    
  </div>
</template>

<script>
import { computed, onMounted, ref, provide } from 'vue'
import { useStore } from 'vuex'
import { useRouter, useRoute } from 'vue-router'
import NotificationBell from '@/components/NotificationBell.vue'

import { ElMessage } from 'element-plus'

// 是否启用调试日志
const DEBUG = false;

// 自定义日志函数，可以通过DEBUG开关控制
const log = (...args) => {
  if (DEBUG) {
    console.log(...args);
  }
};

export default {
  name: 'App',
  components: {
    NotificationBell
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    const route = useRoute()
    
    // 登录状态
    const isLoggedIn = computed(() => store.getters.isLoggedIn)
    const isAdmin = computed(() => store.getters.isAdmin)
    const user = computed(() => store.state.user)
    const username = computed(() => store.getters.username)
    const userAvatar = computed(() => store.getters.userAvatar)
    
    // 检查通知功能是否可用
    const notificationsEnabled = ref(true)
    
    // 当前激活的路由
    const activeRoute = computed(() => route.path)
    
    // 路由导航
    const goToLogin = () => router.push('/login')
    const goToRegister = () => router.push('/register')
    
    // 强制刷新认证状态
    const forceRefreshAuthState = async () => {
      log('强制刷新认证状态')
      const token = localStorage.getItem('token')
      if (!token) {
        log('本地存储中没有token，不刷新认证状态')
        return false
      }

      // 同步token到store
      store.commit('setToken', token)
      
      // 尝试同步用户信息
      try {
        const userInfoStr = localStorage.getItem('userInfo')
        if (userInfoStr) {
          const userInfo = JSON.parse(userInfoStr)
          store.commit('setUser', userInfo)
          log('已从localStorage同步用户信息:', userInfo)
        }
      } catch (e) {
        console.error('解析本地用户信息失败:', e)
      }
      
      // 从API获取最新用户信息
      try {
        const userInfo = await store.dispatch('getUserInfo')
        log('已从API更新用户信息:', userInfo)
        return !!userInfo
      } catch (err) {
        console.error('从API获取用户信息失败:', err)
        return false
      }
    }
    
    // 提供给子组件
    provide('forceRefreshAuthState', forceRefreshAuthState)
    
    // 处理下拉菜单命令
    const handleCommand = (command) => {
      let userId;
      
      switch (command) {
        case 'profile':
          // 确保用户ID存在
          userId = user.value?.id || store.state.user?.id;
          if (userId) {
            router.push(`/profile/${userId}`);
          } else {
            console.error('无法获取用户ID');
            ElMessage.error('获取用户信息失败');
          }
          break;

        case 'admin':
          router.push('/admin');
          break;
        case 'logout':
          logout();
          break;
      }
    }
    
    // 登出
    const logout = () => {
      // 登出并重定向到首页
      store.dispatch('logout')
      router.push('/')
    }
    
    onMounted(() => {
      log('App组件加载 - 登录状态:', {
        isLoggedIn: isLoggedIn.value,
        token: store.state.token,
        userInfo: user.value,
        localStorageToken: localStorage.getItem('token'),
        localStorageUserInfo: localStorage.getItem('userInfo')
      })
      
      // 强制刷新用户状态
      const token = localStorage.getItem('token')
      if (token) {
        log('App.vue - 应用启动时发现token，强制刷新用户状态')
        store.commit('setToken', token)
        try {
          const userInfoStr = localStorage.getItem('userInfo')
          if (userInfoStr) {
            const userInfo = JSON.parse(userInfoStr)
            store.commit('setUser', userInfo)
            log('已从localStorage恢复用户信息:', userInfo)
          }
        } catch (e) {
          console.error('解析用户信息失败:', e)
        }
        
        // 请求最新的用户信息
        store.dispatch('getUserInfo')
          .then(userInfo => {
            log('用户信息已从API刷新:', userInfo)
            // 强制触发状态更新
            setTimeout(() => {
              log('强制触发登录状态检查:', {
                isLoggedIn: store.getters.isLoggedIn,
                token: store.state.token,
                userInfo: store.state.user
              })
            }, 100)
          })
          .catch(err => {
            console.error('刷新用户信息失败:', err)
          })
      }
      
      // 检查通知API是否可用
      if (isLoggedIn.value) {
        const token = store.state.token || localStorage.getItem('token');
        if (!token) {
          notificationsEnabled.value = false;
          log('用户登录状态异常，禁用通知功能');
          return;
        }
        
        fetch('http://localhost:8000/api/v1/notifications/', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
          .then(response => {
            notificationsEnabled.value = response.status !== 404
            log('通知功能' + (notificationsEnabled.value ? '可用' : '不可用'))
          })
          .catch(() => {
            notificationsEnabled.value = false
            log('通知功能不可用 - 连接失败')
          })
      } else {
        notificationsEnabled.value = false
        log('用户未登录，禁用通知功能')
      }
    })
    
    return {
      isLoggedIn,
      isAdmin,
      user,
      username,
      userAvatar,
      activeRoute,
      notificationsEnabled,
      goToLogin,
      goToRegister,
      handleCommand
    }
  }
}
</script>

<style>
#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  min-height: 100vh;
}

.el-container {
  min-height: 100vh;
}

.el-header {
  padding: 0;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: fixed;
  width: 100%;
  z-index: 1000;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.logo {
  font-size: 20px;
  font-weight: bold;
}

.logo a {
  color: #409EFF;
  text-decoration: none;
}

.nav {
  flex: 1;
  margin: 0 20px;
}

.nav .el-menu {
  border: none;
  background: transparent;
}

.user-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-avatar {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.username {
  margin-left: 8px;
  font-size: 14px;
}

.main-container {
  padding-top: 60px;
  min-height: calc(100vh - 60px);
  background-color: #f5f7fa;
}

.el-main {
  padding: 20px;
}

.el-footer {
  height: 60px !important;
  background-color: #fff;
  border-top: 1px solid #e4e7ed;
  margin-top: auto;
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
}

/* 修复下拉框宽度问题 */
.el-select {
  min-width: 120px !important;
}

.el-select .el-input {
  width: 100% !important;
}

.el-select-dropdown__item {
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

.el-select-dropdown {
  min-width: 120px !important;
}
</style>