<template>
  <div class="home-container">
    <el-container>
      <el-main>
        <div class="main-content">
          <el-row :gutter="20">
            <el-col :span="18">
              <div class="content-area">
                <div class="welcome-message" v-if="isAuthenticated">
                  <h2>欢迎回来，{{ userInfo?.nickname || userInfo?.username }}！</h2>
                  <p>今天有什么想法要分享吗？</p>
                  <el-button type="primary" @click="goToNewPost">发布新帖</el-button>
                </div>
                <div class="welcome-message" v-else>
                  <h2>欢迎来到论坛系统</h2>
                  <p>这里是一个交流和分享的平台，您可以浏览所有帖子和内容。</p>
                  <p>登录后可以发帖和参与讨论。</p>
                  <el-button type="primary" @click="goToLogin">立即登录</el-button>
                  <el-button @click="goToRegister">注册账号</el-button>
                </div>

                <div class="section-title">
                  <h3>最新帖子</h3>
                  <el-button link @click="goToPostList">查看更多</el-button>
                </div>

                <div class="post-list">
                  <div v-if="loading.posts" class="loading-container">
                    <el-skeleton :rows="5" animated />
                  </div>
                  <el-empty description="暂无帖子" v-else-if="!latestPosts.length"></el-empty>
                  <div v-else>
                    <div v-for="post in latestPosts" :key="post.id" class="post-item">
                      <div class="post-avatar" @click.stop="goToUserProfile(post.user?.id)" style="cursor: pointer;">
                        <el-avatar :size="40" :src="post.user?.avatar_url || ''">
                          {{ post.user?.nickname?.charAt(0) || post.user?.username?.charAt(0) || 'U' }}
                        </el-avatar>
                      </div>
                      <div class="post-content">
                        <div class="post-title">
                          <router-link :to="`/posts/${post.id}`">{{ post.title || '无标题' }}</router-link>
                          <el-tag size="small" type="success" v-if="post.is_pinned">置顶</el-tag>
                          <el-tag size="small" type="warning" v-if="post.is_featured">精华</el-tag>
                        </div>
                        <div class="post-info">
                          <span class="author" @click.stop="goToUserProfile(post.user?.id)" style="cursor: pointer;">{{ post.user?.nickname || post.user?.username || '匿名用户' }}</span>
                          <span class="board">{{ post.board_name || '未分类' }}</span>
                          <span class="time">{{ formatDate(post.created_at || new Date()) }}</span>
                        </div>
                        <div class="post-stats">
                          <span class="views">
                            <el-icon><View /></el-icon> {{ post.views || 0 }}
                          </span>
                          <span class="comments">
                            <el-icon><ChatDotRound /></el-icon> {{ post.comments_count || 0 }}
                          </span>
                          <span class="likes">
                            <el-icon><Star /></el-icon> {{ post.likes_count || 0 }}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </el-col>

            <el-col :span="6">
              <div class="sidebar">
                <div class="sidebar-section">
                  <div class="section-title">
                    <h3>热门板块</h3>
                  </div>
                  <div class="board-list">
                    <div v-if="loading.boards" class="loading-container">
                      <el-skeleton :rows="3" animated />
                    </div>
                    <el-empty description="暂无板块" v-else-if="!hotBoards.length"></el-empty>
                    <div v-else>
                      <div v-for="board in hotBoards" :key="board.id" class="board-item">
                        <router-link :to="`/boards/${board.id}`">{{ board.name }}</router-link>
                        <span class="post-count">{{ board.posts_count }}帖子</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="sidebar-section">
                  <div class="section-title">
                    <h3>热门用户</h3>
                  </div>
                  <div class="user-list">
                    <div v-if="loading.users" class="loading-container">
                      <el-skeleton :rows="3" animated />
                    </div>
                    <el-empty description="暂无用户" v-else-if="!hotUsers.length"></el-empty>
                    <div v-else>
                      <div v-for="user in hotUsers" :key="user.id" class="user-item" @click="goToUserProfile(user.id)" style="cursor: pointer;">
                        <user-avatar :user="user" :size="32" />
                        <span class="user-nickname">{{ user.nickname || user.username }}</span>
                        <span class="post-count">{{ user.posts_count }}帖子</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
      </el-main>

      <el-footer height="60px">
        <div class="footer-content">
          <p>© 2025 论坛系统 - 基于Vue + Django + MySQL的PC端论坛系统</p>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, provide } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'
import { View, ChatDotRound, Star } from '@element-plus/icons-vue'
import { logout } from '../api/user'
import { getHotBoards } from '../api/board'
import { getHotUsers } from '../api/profile'
import { getPostList } from '../api/post'
import { formatDateTime } from '../utils/index'
import UserAvatar from '../components/UserAvatar.vue'

// 是否启用调试日志
const DEBUG = false;

// 自定义日志函数，可以通过DEBUG开关控制
const log = (...args) => {
  if (DEBUG) {
    console.log(...args);
  }
};

export default {
  name: 'Home',
  components: {
    View,
    ChatDotRound,
    Star,
    UserAvatar
  },
  setup() {
    const router = useRouter()
    const store = useStore()

    // 获取认证状态和用户信息
    const isAuthenticated = computed(() => {
      const loggedIn = store.getters.isLoggedIn;
      log('Home组件检查登录状态:', {
        isLoggedIn: loggedIn,
        token: store.state.token,
        user: store.state.user
      });
      return loggedIn;
    })
    const userInfo = computed(() => store.state.user)

    // 判断是否为管理员
    const isAdmin = computed(() => {
      return userInfo.value && userInfo.value.role === 'admin'
    })

    // 数据状态
    const latestPosts = ref([])
    const hotBoards = ref([])
    const hotUsers = ref([])
    const loading = ref({
      posts: false,
      boards: false,
      users: false
    })

    // 格式化日期
    const formatDate = (date) => {
      return formatDateTime(date)
    }

    // 页面跳转方法
    const goToLogin = () => router.push('/login')
    const goToRegister = () => router.push('/register')
    const goToProfile = () => router.push('/profile/me')
    const goToAdminDashboard = () => router.push('/admin/dashboard')
    const goToUserManagement = () => router.push('/admin/users')
    const goToPostList = () => router.push('/posts')
    const goToUserProfile = (userId) => {
      if (userId) {
        router.push(`/profile/${userId}`)
      } else {
        ElMessage.warning('无法获取用户信息')
      }
    }
    const goToNewPost = () => {
      if (!isAuthenticated.value) {
        ElMessage.warning('请先登录才能发布帖子')
        router.push({ name: 'Login', query: { redirect: '/post/create' } })
        return
      }
      
      // 清除可能的成功消息提示
      ElMessage.closeAll()
      router.push('/post/create')
    }

    // 退出登录
    const handleLogout = async () => {
      try {
        const response = await logout()
        store.dispatch('logout')
        // 使用messageTracker替代直接调用ElMessage
        if (window.messageTracker) {
          window.messageTracker.showMessage(response.msg || '退出登录成功', 'success', 'home-logout');
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
          window.messageTracker.showMessage('退出登录失败', 'error', 'home-logout-error');
        } else {
          ElMessage({
            message: '退出登录失败',
            type: 'error'
          })
        }
      }
    }

    // 获取最新帖子
    const fetchLatestPosts = async () => {
      loading.value.posts = true
      try {
        log('开始获取最新帖子...')
        const response = await getPostList({
          page: 1,
          page_size: 5,
          ordering: '-created_at',
          _t: Date.now() // 添加时间戳避免缓存
        })

        log('最新帖子响应:', response)

        if (response && response.count !== undefined && response.results) {
          // 处理DRF分页响应
          log('使用DRF分页响应格式处理最新帖子数据')
          latestPosts.value = response.results || []
        } else if (response && response.code === 0 && response.data) {
          // 处理自定义响应格式
          log('使用自定义响应格式处理最新帖子数据')
          if (response.data.results) {
            latestPosts.value = response.data.results || []
          } else if (Array.isArray(response.data)) {
            latestPosts.value = response.data || []
          }
        } else if (response && response.status === 0 && response.data) {
          // 处理另一种自定义响应格式
          log('使用status=0格式处理最新帖子数据')
          if (response.data.results) {
            latestPosts.value = response.data.results || []
          } else if (Array.isArray(response.data)) {
            latestPosts.value = response.data || []
          }
        } else if (response && Array.isArray(response)) {
          // 直接返回数组的情况
          log('使用数组格式处理最新帖子数据')
          latestPosts.value = response
        } else if (response && Array.isArray(response.results)) {
          // 直接带有results属性的情况
          log('使用带results属性的响应格式处理最新帖子数据')
          latestPosts.value = response.results
        } else {
          console.error('获取最新帖子失败:', response ? response.msg : '未知错误')
          ElMessage.error('获取最新帖子失败，请稍后再试')
          latestPosts.value = []
        }
      } catch (error) {
        console.error('获取最新帖子失败:', error)
        // 使用更友好的错误提示
        if (error.response && error.response.status === 401) {
          log('未登录状态，无法获取帖子列表')
          ElMessage.warning('请登录后查看最新帖子')
        } else {
          ElMessage.error('获取最新帖子失败，请稍后再试')
        }
        latestPosts.value = []
      } finally {
        loading.value.posts = false
      }
    }

    // 提供刷新函数给子组件
    provide('refreshLatestPosts', fetchLatestPosts)

    // 获取热门板块
    const fetchHotBoards = async () => {
      loading.value.boards = true
      try {
        log('开始获取热门板块...')
        const response = await getHotBoards(5)

        log('热门板块响应:', response)

        if (response && response.status === 0 && response.data) {
          // 处理Django REST framework自定义响应格式
          log('使用status=0格式处理热门板块数据')
          hotBoards.value = response.data || []
        } else if (response && response.code === 0 && response.data) {
          // 处理另一种自定义响应格式
          log('使用code=0格式处理热门板块数据')
          hotBoards.value = response.data || []
        } else if (response && Array.isArray(response)) {
          // 直接返回数组的情况
          log('使用数组格式处理热门板块数据')
          hotBoards.value = response
        } else {
          console.error('获取热门板块失败:', response ? response.msg : '未知错误')
          hotBoards.value = [] // 如果获取失败，设置为空数组
        }
      } catch (error) {
        console.error('获取热门板块失败:', error)
        ElMessage.error('获取热门板块失败，请稍后再试')
        hotBoards.value = [] // 如果发生错误，设置为空数组
      } finally {
        loading.value.boards = false
      }
    }

    // 获取热门用户
    const fetchHotUsers = async () => {
      loading.value.users = true
      try {
        log('开始获取热门用户...')
        const response = await getHotUsers(5)

        log('热门用户响应:', response)

        if (response && response.code === 0 && response.data) {
          log('使用code=0格式处理热门用户数据')
          hotUsers.value = response.data || []
        } else if (response && Array.isArray(response)) {
          // 直接返回数组的情况
          log('使用数组格式处理热门用户数据')
          hotUsers.value = response
        } else if (response && response.status === 0 && response.data) {
          // 另一种响应格式
          log('使用status=0格式处理热门用户数据')
          hotUsers.value = response.data || []
        } else {
          console.error('获取热门用户失败:', response ? response.msg : '未知错误')
          hotUsers.value = [] // 如果获取失败，设置为空数组
        }
      } catch (error) {
        console.error('获取热门用户失败:', error)
        ElMessage.error('获取热门用户失败，请稍后再试')
        hotUsers.value = [] // 如果发生错误，设置为空数组
      } finally {
        loading.value.users = false
      }
    }

    // 生命周期钩子
    onMounted(() => {
      log('Home页面加载 - 登录状态:', {
        isAuthenticated: isAuthenticated.value,
        userInfo: userInfo.value,
        storeToken: store.state.token,
        localStorageToken: localStorage.getItem('token'),
        localStorageUserInfo: localStorage.getItem('userInfo')
      })

      // 获取数据
      fetchLatestPosts()
      fetchHotBoards()
      fetchHotUsers()
      
      // 添加定时器，每30秒刷新一次最新帖子
      const refreshTimer = setInterval(() => {
        log('定时刷新最新帖子...')
        fetchLatestPosts()
      }, 30000)

      // 在组件卸载时清除定时器
      onUnmounted(() => {
        if (refreshTimer) {
          clearInterval(refreshTimer)
        }
      })
      
      // 添加重试机制，确保数据加载成功
      setTimeout(() => {
        // 如果首次加载失败，尝试重新加载
        if (latestPosts.value.length === 0 && !loading.value.posts) {
          log('首次加载帖子失败，尝试重新加载...')
          fetchLatestPosts()
        }
      }, 5000)
    })

    return {
      isAuthenticated,
      userInfo,
      isAdmin,
      latestPosts,
      hotBoards,
      hotUsers,
      loading,
      formatDate,
      goToLogin,
      goToRegister,
      goToProfile,
      goToAdminDashboard,
      goToUserManagement,
      goToPostList,
      goToUserProfile,
      goToNewPost,
      handleLogout,
      fetchLatestPosts // 导出刷新函数
    }
  }
}
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.el-container {
  min-height: 100vh;
}

.el-main {
  padding: 20px;
  background-color: #f5f7fa;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
}

.content-area {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.welcome-message {
  background-color: #f0f9ff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  border-left: 4px solid #409eff;
}

.welcome-message h2 {
  margin-top: 0;
  color: #303133;
}

.section-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 10px;
}

.section-title h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
}

.post-list {
  margin-bottom: 20px;
}

.post-item {
  display: flex;
  padding: 15px 0;
  border-bottom: 1px solid #ebeef5;
}

.post-avatar {
  margin-right: 15px;
}

.post-content {
  flex-grow: 1;
}

.post-title {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
}

.post-title a {
  color: #303133;
  text-decoration: none;
  margin-right: 8px;
}

.post-title a:hover {
  color: #409eff;
}

.post-info {
  font-size: 12px;
  color: #909399;
  margin-bottom: 8px;
}

.post-info .author {
  margin-right: 10px;
}

.post-info .board {
  margin-right: 10px;
  background-color: #f0f9ff;
  color: #409eff;
  padding: 2px 6px;
  border-radius: 4px;
}

.post-stats {
  font-size: 12px;
  color: #909399;
  display: flex;
  gap: 15px;
}

.sidebar {
  position: sticky;
  top: 80px;
}

.sidebar-section {
  background-color: #fff;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.board-list, .user-list {
  margin-top: 10px;
}

.board-item, .user-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #ebeef5;
  width: 100%;
}

.board-item a {
  color: #303133;
  text-decoration: none;
  flex-grow: 1;
  margin-right: 10px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.board-item a:hover {
  color: #409eff;
}

.post-count {
  font-size: 12px;
  color: #909399;
  min-width: 45px;
  text-align: right;
}

.user-item {
  gap: 10px;
}

.user-nickname {
  flex-grow: 1;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-right: 10px;
}

.el-footer {
  background-color: #fff;
  border-top: 1px solid #ebeef5;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #909399;
  font-size: 14px;
}
</style>
