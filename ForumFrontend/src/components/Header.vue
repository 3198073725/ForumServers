<template>
  <header class="app-header">
    <div class="header-container">
      <div class="logo-container">
        <router-link to="/" class="logo">
          <h1>论坛系统</h1>
        </router-link>
      </div>
      <nav class="main-nav">
        <ul>
          <li>
            <router-link to="/" active-class="active" exact>首页</router-link>
          </li>
          <li>
            <router-link to="/boards" active-class="active">板块</router-link>
          </li>
          <li>
            <router-link to="/ranking" active-class="active">排行榜</router-link>
          </li>
          <li>
            <router-link to="/complaints" active-class="active">投诉</router-link>
          </li>
        </ul>
      </nav>
      <div class="user-area">
        <template v-if="isAuthenticated">
          <div class="user-info" @click="toggleUserMenu">
            <user-avatar :user="userInfo" :size="32" />
            <span class="username">{{ userInfo.nickname || userInfo.username }}</span>
            <el-icon class="dropdown-icon"><arrow-down /></el-icon>
            <div class="user-menu" v-show="showUserMenu">
              <router-link :to="`/profile/${userInfo.id}`">
                <el-icon><user /></el-icon> <span>个人中心</span>
              </router-link>
              <router-link to="/post/create">
                <el-icon><edit /></el-icon> <span>发布帖子</span>
              </router-link>

              <router-link to="/user/settings" v-if="false">
                <el-icon><setting /></el-icon> <span>设置</span>
              </router-link>
              <div v-if="userInfo.role === 'admin'" class="divider"></div>
              <router-link v-if="userInfo.role === 'admin'" to="/admin/dashboard">
                <el-icon><monitor /></el-icon> <span>管理员仪表盘</span>
              </router-link>
              <router-link v-if="userInfo.role === 'admin'" to="/admin/users">
                <el-icon><user /></el-icon> <span>用户管理</span>
              </router-link>
              <div class="divider"></div>
              <a href="javascript:void(0)" @click="handleLogout">
                <el-icon><switch-button /></el-icon> <span>退出登录</span>
              </a>
            </div>
          </div>
        </template>
        <template v-else>
          <router-link to="/login" class="login-btn">登录</router-link>
          <router-link to="/register" class="register-btn">注册</router-link>
        </template>
      </div>
    </div>
  </header>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  User, 
  Setting, 
  Monitor, 
  SwitchButton, 
  ArrowDown,
  Edit
} from '@element-plus/icons-vue'
import { logout } from '../api/user'
import UserAvatar from './UserAvatar.vue'

export default {
  name: 'AppHeader',
  components: {
    UserAvatar,
    User,
    Setting,
    Monitor,
    SwitchButton,
    ArrowDown,
    Edit
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    const showUserMenu = ref(false)

    const isAuthenticated = computed(() => store.getters.isAuthenticated)
    const userInfo = computed(() => store.getters.userInfo)

    const toggleUserMenu = () => {
      showUserMenu.value = !showUserMenu.value
    }

    const handleLogout = async () => {
      try {
        const response = await logout()
        store.dispatch('logout')
        if (window.messageTracker) {
          window.messageTracker.showMessage(response.msg || '退出登录成功', 'success', 'header-logout');
        } else {
          ElMessage({
            message: '退出登录成功',
            type: 'success'
          })
        }
        router.push('/')
      } catch (error) {
        console.error('退出登录失败:', error)
        if (window.messageTracker) {
          window.messageTracker.showMessage('退出登录失败', 'error', 'header-logout-error');
        } else {
          ElMessage({
            message: '退出登录失败',
            type: 'error'
          })
        }
      }
      showUserMenu.value = false
    }

    const closeUserMenu = (event) => {
      if (showUserMenu.value && !event.target.closest('.user-info')) {
        showUserMenu.value = false
      }
    }

    onMounted(() => {
      document.addEventListener('click', closeUserMenu)
    })

    onUnmounted(() => {
      document.removeEventListener('click', closeUserMenu)
    })

    return {
      isAuthenticated,
      userInfo,
      showUserMenu,
      toggleUserMenu,
      handleLogout
    }
  }
}
</script>

<style scoped>
.app-header {
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
  height: 60px; /* 固定高度 */
}

.header-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo-container {
  flex: 0 0 auto;
  width: 100px; /* 固定宽度 */
  text-align: left;
}

.logo {
  text-decoration: none;
  color: #409EFF;
}

.logo h1 {
  margin: 0;
  font-size: 20px;
  white-space: nowrap; /* 防止文字换行 */
}

.main-nav {
  flex: 1;
  margin: 0 20px;
}

.main-nav ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
}

.main-nav li {
  margin-right: 30px;
  height: 60px; /* 固定高度 */
  display: flex;
  align-items: center;
}

.main-nav a {
  text-decoration: none;
  color: #606266;
  font-size: 16px;
  padding: 0;
  position: relative;
  display: inline-block;
  height: 60px;
  line-height: 60px; /* 垂直居中 */
  box-sizing: border-box; /* 确保padding不会增加元素尺寸 */
  width: 100%; /* 确保宽度一致 */
  text-align: center; /* 文本居中 */
}

.main-nav a:hover {
  color: #409EFF;
}

.main-nav a.active {
  color: #409EFF;
  font-weight: 500; /* 使用字体粗细代替可能导致尺寸变化的其他属性 */
}

/* 修改下划线实现方式，使用伪元素，不影响元素尺寸 */
.main-nav a::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: transparent;
  transition: background-color 0.3s;
}

.main-nav a.active::after {
  background-color: #409EFF;
}

.user-area {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  height: 60px; /* 固定高度 */
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  position: relative;
  height: 60px; /* 固定高度 */
}

.username {
  margin: 0 8px;
  font-size: 14px;
  white-space: nowrap; /* 防止文字换行 */
}

.dropdown-icon {
  font-size: 12px;
  width: 12px; /* 固定宽度 */
  height: 12px; /* 固定高度 */
}

.user-menu {
  position: absolute;
  top: 100%;
  right: 0;
  width: 150px;
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 5px 0;
  margin-top: 0; /* 移除可变的边距 */
  z-index: 1001;
}

.user-menu:before {
  content: '';
  position: absolute;
  top: -6px;
  right: 20px;
  width: 12px;
  height: 12px;
  background-color: #fff;
  transform: rotate(45deg);
  box-shadow: -2px -2px 5px rgba(0, 0, 0, 0.05);
}

.user-menu a {
  display: flex;
  align-items: center;
  padding: 8px 15px;
  color: #606266;
  text-decoration: none;
  font-size: 14px;
  position: relative;
  height: 36px; /* 固定高度 */
  box-sizing: border-box; /* 确保padding不会增加元素尺寸 */
}

.user-menu a:hover {
  background-color: #f5f7fa;
}

.user-menu .el-icon {
  margin-right: 8px;
  font-size: 16px;
  width: 16px; /* 固定宽度 */
  height: 16px; /* 固定高度 */
  flex-shrink: 0; /* 防止图标被压缩 */
}

.user-menu a span {
  flex-grow: 1; /* 让文本占据剩余空间 */
  white-space: nowrap; /* 防止文本换行 */
}

.divider {
  height: 1px;
  background-color: #ebeef5;
  margin: 5px 0;
}

.badge {
  position: absolute;
  right: 15px;
  background-color: #f56c6c;
  color: #fff;
  border-radius: 10px;
  padding: 0 6px;
  font-size: 12px;
  height: 18px;
  line-height: 18px;
  text-align: center;
  min-width: 18px;
}

.login-btn,
.register-btn {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  text-decoration: none;
  margin-left: 10px;
  display: inline-block; /* 确保元素尺寸稳定 */
  box-sizing: border-box; /* 确保padding不会增加元素尺寸 */
  height: 36px; /* 固定高度 */
  line-height: 20px; /* 垂直居中 */
  min-width: 60px; /* 最小宽度 */
  text-align: center; /* 文本居中 */
}

.login-btn {
  background-color: #409EFF;
  color: #fff;
}

.login-btn:hover {
  background-color: #66b1ff;
}

.register-btn {
  border: 1px solid #dcdfe6;
  color: #606266;
}

.register-btn:hover {
  border-color: #c6e2ff;
  color: #409EFF;
  background-color: #ecf5ff;
}
</style> 