<template>
  <div class="ranking-container">
    <div class="page-header">
      <h1>排行榜</h1>
      <p>查看论坛中最活跃的用户、最热门的帖子和板块</p>
    </div>

    <el-tabs v-model="activeTab" class="ranking-tabs" @tab-click="handleTabChange">
      <el-tab-pane label="用户排行" name="users">
        <div class="ranking-section">
          <div class="section-header">
            <h2>活跃用户排行</h2>
            <el-select v-model="userRankingType" placeholder="排序方式" size="small" @change="handleUserRankingTypeChange">
              <el-option label="发帖数量" value="posts_count" />
              <el-option label="获赞数量" value="likes_received" />
              <el-option label="注册时间" value="join_date" />
            </el-select>
          </div>

          <div class="ranking-list">
            <div v-if="loading.users" class="loading-container">
              <el-skeleton :rows="10" animated />
            </div>
            <el-empty description="暂无数据" v-else-if="!userRanking.length"></el-empty>
            <div v-else class="ranking-items">
              <div v-for="(user, index) in userRanking" :key="user.id" class="ranking-item">
                <div class="rank-number" :class="{ 'top-three': index < 3 }">{{ index + 1 }}</div>
                <div class="user-avatar">
                  <user-avatar :user="user" :size="40" />
                </div>
                <div class="user-info">
                  <div class="user-name">
                    <router-link :to="`/profile/${user.id}`">{{ user.nickname || user.username }}</router-link>
                  </div>
                  <div class="user-stats">
                    <span>
                      <el-icon><Collection /></el-icon> 发帖: {{ user.posts_count || 0 }}
                    </span>
                    <span>
                      <el-icon><StarFilled /></el-icon> 获赞: {{ user.likes_received || 0 }}
                    </span>
                    <span class="register-time">
                      <el-icon><Timer /></el-icon> 注册于: {{ formatDate(user.created_at || user.date_joined) }}
                    </span>
                  </div>
                </div>
                <div class="ranking-value">
                  {{ getRankingValue(user, userRankingType) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="帖子排行" name="posts">
        <div class="ranking-section">
          <div class="section-header">
            <h2>热门帖子排行</h2>
            <el-select v-model="postRankingType" placeholder="排序方式" size="small" @change="handlePostRankingTypeChange">
              <el-option label="浏览量" value="views" />
              <el-option label="评论数" value="comments_count" />
              <el-option label="点赞数" value="likes_count" />
            </el-select>
          </div>

          <div class="ranking-list">
            <div v-if="loading.posts" class="loading-container">
              <el-skeleton :rows="10" animated />
            </div>
            <el-empty description="暂无数据" v-else-if="!postRanking.length"></el-empty>
            <div v-else class="ranking-items">
              <div v-for="(post, index) in postRanking" :key="post.id" class="ranking-item">
                <div class="rank-number" :class="{ 'top-three': index < 3 }">{{ index + 1 }}</div>
                <div class="post-info">
                  <div class="post-title">
                    <router-link :to="`/posts/${post.id}`">{{ post.title }}</router-link>
                    <el-tag size="small" type="success" v-if="post.is_pinned">置顶</el-tag>
                    <el-tag size="small" type="warning" v-if="post.is_featured">精华</el-tag>
                  </div>
                  <div class="post-meta">
                    <span>作者: {{ post.user.nickname || post.user.username }}</span>
                    <span>板块: {{ post.board_name }}</span>
                    <span>发布于: {{ formatDate(post.created_at) }}</span>
                  </div>
                </div>
                <div class="ranking-stats">
                  <div class="stat-item">
                    <el-icon><View /></el-icon> {{ post.views || 0 }}
                  </div>
                  <div class="stat-item">
                    <el-icon><ChatDotRound /></el-icon> {{ post.comments_count || 0 }}
                  </div>
                  <div class="stat-item">
                    <el-icon><Star /></el-icon> {{ post.likes_count || 0 }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>

      <el-tab-pane label="板块排行" name="boards">
        <div class="ranking-section">
          <div class="section-header">
            <h2>热门板块排行</h2>
            <el-select v-model="boardRankingType" placeholder="排序方式" size="small" @change="handleBoardRankingTypeChange">
              <el-option label="帖子数量" value="posts_count" />
              <el-option label="用户数量" value="users_count" />
              <el-option label="总浏览量" value="total_views" />
            </el-select>
          </div>

          <div class="ranking-list">
            <div v-if="loading.boards" class="loading-container">
              <el-skeleton :rows="10" animated />
            </div>
            <el-empty description="暂无数据" v-else-if="!boardRanking.length"></el-empty>
            <div v-else class="ranking-items">
              <div v-for="(board, index) in boardRanking" :key="board.id" class="ranking-item">
                <div class="rank-number" :class="{ 'top-three': index < 3 }">{{ index + 1 }}</div>
                <div class="board-info">
                  <div class="board-name">
                    <router-link :to="`/boards/${board.id}`">{{ board.name }}</router-link>
                  </div>
                  <div class="board-description">
                    {{ board.description }}
                  </div>
                </div>
                <div class="ranking-stats">
                  <div class="stat-item">
                    <el-icon><Document /></el-icon> {{ board.posts_count || 0 }} 帖子
                  </div>
                  <div class="stat-item">
                    <el-icon><User /></el-icon> {{ board.users_count || 0 }} 用户
                  </div>
                  <div class="stat-item">
                    <el-icon><View /></el-icon> {{ board.total_views || 0 }} 浏览
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import { ref, reactive, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { View, ChatDotRound, Star, Document, User, Timer, Collection, StarFilled } from '@element-plus/icons-vue'
import { getHotUsers } from '../api/profile'
import { getPostList } from '../api/post'
import { getHotBoards } from '../api/board'
import { formatDateTime } from '../utils/index'
import UserAvatar from '../components/UserAvatar.vue'

export default {
  name: 'Ranking',
  components: {
    UserAvatar,
    View,
    ChatDotRound,
    Star,
    Document,
    User,
    Timer,
    Collection,
    StarFilled
  },
  setup() {
    const activeTab = ref('users')
    const userRankingType = ref('posts_count')
    const postRankingType = ref('views')
    const boardRankingType = ref('posts_count')

    const userRanking = ref([])
    const postRanking = ref([])
    const boardRanking = ref([])

    const loading = reactive({
      users: false,
      posts: false,
      boards: false
    })

    // 是否启用调试日志
    const DEBUG = false;

    // 自定义日志函数，可以通过DEBUG开关控制
    const log = (...args) => {
      if (DEBUG) {
        console.log(...args);
      }
    };

    // 格式化日期
    const formatDate = (date) => {
      if (!date) return '未知'
      
      try {
        // 对于注册时间，使用更友好的格式
        const dateObj = new Date(date)
        if (isNaN(dateObj.getTime())) return '格式错误'
        
        const now = new Date()
        const diffYears = now.getFullYear() - dateObj.getFullYear()
        
        if (diffYears > 0) {
          // 超过一年显示年月日
          return formatDateTime(date, 'YYYY年MM月DD日')
        } else {
          // 不到一年显示月日和具体时间
          return formatDateTime(date, 'MM月DD日 HH:mm')
        }
      } catch (error) {
        console.error('日期格式化错误:', error)
        return '格式错误'
      }
    }

    // 根据排序类型获取排行值
    const getRankingValue = (item, type) => {
      switch (type) {
        case 'posts_count':
          return `${item.posts_count || 0} 帖子`
        case 'likes_received':
          return `${item.likes_received || 0} 获赞`
        case 'join_date':
          return formatDate(item.created_at || item.date_joined)
        default:
          return item[type] || 0
      }
    }

    // 获取用户排行
    const fetchUserRanking = async () => {
      loading.users = true
      try {
        const response = await getHotUsers(20)
        
        if (response && response.code === 0 && response.data) {
          userRanking.value = response.data
        } else if (response && Array.isArray(response)) {
          userRanking.value = response
        } else if (response && response.status === 0 && response.data) {
          userRanking.value = response.data
        } else {
          console.error('获取用户排行失败:', response ? response.msg : '未知错误')
          userRanking.value = []
        }
        
        // 根据当前选择的排序类型排序
        sortUserRanking()
      } catch (error) {
        console.error('获取用户排行失败:', error)
        ElMessage.error('获取用户排行失败，请稍后再试')
        userRanking.value = []
      } finally {
        loading.users = false
      }
    }

    // 获取帖子排行
    const fetchPostRanking = async () => {
      loading.posts = true
      try {
        const response = await getPostList({
          page: 1,
          page_size: 20,
          ordering: `-${postRankingType.value}`
        })

        if (response && response.count !== undefined) {
          postRanking.value = response.results || []
        } else if (response && response.code === 0 && response.data && response.data.results) {
          postRanking.value = response.data.results || []
        } else if (response && response.code === 0 && Array.isArray(response.data)) {
          postRanking.value = response.data || []
        } else {
          console.error('获取帖子排行失败:', response ? response.msg : '未知错误')
          postRanking.value = []
        }
      } catch (error) {
        console.error('获取帖子排行失败:', error)
        ElMessage.error('获取帖子排行失败，请稍后再试')
        postRanking.value = []
      } finally {
        loading.posts = false
      }
    }

    // 获取板块排行
    const fetchBoardRanking = async () => {
      loading.boards = true
      try {
        const response = await getHotBoards(20)

        if (response && response.status === 0 && response.data) {
          boardRanking.value = response.data
        } else if (response && response.code === 0 && response.data) {
          boardRanking.value = response.data
        } else if (response && Array.isArray(response)) {
          boardRanking.value = response
        } else {
          console.error('获取板块排行失败:', response ? response.msg : '未知错误')
          boardRanking.value = []
        }
        
        // 根据当前选择的排序类型排序
        sortBoardRanking()
      } catch (error) {
        console.error('获取板块排行失败:', error)
        ElMessage.error('获取板块排行失败，请稍后再试')
        boardRanking.value = []
      } finally {
        loading.boards = false
      }
    }

    // 排序用户排行榜
    const sortUserRanking = () => {
      userRanking.value.sort((a, b) => {
        const valueA = a[userRankingType.value] || 0
        const valueB = b[userRankingType.value] || 0
        
        if (userRankingType.value === 'join_date') {
          // 注册时间从早到晚
          const dateA = a.created_at || a.date_joined
          const dateB = b.created_at || b.date_joined
          return new Date(dateA) - new Date(dateB)
        } else {
          // 其他从高到低
          return valueB - valueA
        }
      })
    }

    // 排序板块排行榜
    const sortBoardRanking = () => {
      boardRanking.value.sort((a, b) => {
        const valueA = a[boardRankingType.value] || 0
        const valueB = b[boardRankingType.value] || 0
        return valueB - valueA
      })
    }

    // 用户排行榜排序方式变更
    const handleUserRankingTypeChange = (type) => {
      userRankingType.value = type;
      log('用户排行榜排序方式变更为:', userRankingType.value);
      fetchUserRanking();
    };

    // 帖子排行榜排序方式变更
    const handlePostRankingTypeChange = (type) => {
      postRankingType.value = type;
      log('帖子排行榜排序方式变更为:', postRankingType.value);
      fetchPostRanking();
    };

    // 板块排行榜排序方式变更
    const handleBoardRankingTypeChange = (type) => {
      boardRankingType.value = type;
      log('板块排行榜排序方式变更为:', boardRankingType.value);
      fetchBoardRanking();
    };

    // 标签页切换
    const handleTabChange = (tab) => {
      log('标签页切换为:', tab.props.name);
      // 根据标签页加载对应数据
      switch (tab.props.name) {
        case 'users':
          if (!userRanking.value.length) {
            fetchUserRanking();
          }
          break;
        case 'posts':
          if (!postRanking.value.length) {
            fetchPostRanking();
          }
          break;
        case 'boards':
          if (!boardRanking.value.length) {
            fetchBoardRanking();
          }
          break;
      }
    };

    onMounted(() => {
      // 加载默认标签页的数据
      fetchUserRanking()
    })

    return {
      activeTab,
      userRankingType,
      postRankingType,
      boardRankingType,
      userRanking,
      postRanking,
      boardRanking,
      loading,
      formatDate,
      getRankingValue,
      handleUserRankingTypeChange,
      handlePostRankingTypeChange,
      handleBoardRankingTypeChange,
      handleTabChange
    }
  }
}
</script>

<style scoped>
.ranking-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  margin-bottom: 30px;
  text-align: center;
  position: relative;
}

.page-header::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 3px;
  background: linear-gradient(90deg, #409eff, #67c23a);
  border-radius: 3px;
}

.page-header h1 {
  font-size: 32px;
  color: #303133;
  margin-bottom: 12px;
  font-weight: 600;
}

.page-header p {
  color: #606266;
  font-size: 16px;
  max-width: 600px;
  margin: 0 auto;
}

.ranking-tabs {
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  padding: 25px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 15px;
}

.section-header h2 {
  margin: 0;
  font-size: 22px;
  width: 200px;
  color: #303133;
  position: relative;
  padding-left: 15px;
}

.section-header h2::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 20px;
  background: #409eff;
  border-radius: 2px;
}

.ranking-list {
  margin-top: 25px;
}

.ranking-items {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.ranking-item {
  display: flex;
  align-items: center;
  padding: 18px;
  background-color: #ffffff;
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  border: 1px solid #ebeef5;
  margin-bottom: 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  position: relative;
  overflow: hidden;
  animation: fadeIn 0.5s ease-out forwards;
  animation-delay: calc(0.05s * var(--index, 0));
}

.ranking-item:nth-child(1) { --index: 1; }
.ranking-item:nth-child(2) { --index: 2; }
.ranking-item:nth-child(3) { --index: 3; }
.ranking-item:nth-child(4) { --index: 4; }
.ranking-item:nth-child(5) { --index: 5; }
.ranking-item:nth-child(6) { --index: 6; }
.ranking-item:nth-child(7) { --index: 7; }
.ranking-item:nth-child(8) { --index: 8; }
.ranking-item:nth-child(9) { --index: 9; }
.ranking-item:nth-child(10) { --index: 10; }
.ranking-item:nth-child(n+11) { --index: 11; }

.ranking-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: transparent;
  transition: all 0.3s ease;
}

.ranking-item:hover::before {
  background: linear-gradient(to bottom, #409eff, #67c23a);
}

.ranking-item:hover {
  transform: translateY(-3px) scale(1.01);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
  border-color: #dcdfe6;
}

.rank-number {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background-color: #909399;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-right: 15px;
  font-size: 16px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.rank-number.top-three:nth-child(1) {
  background: linear-gradient(135deg, #f56c6c, #e74c3c);
  font-size: 18px;
}

.rank-number.top-three:nth-child(3n+2) {
  background: linear-gradient(135deg, #e6a23c, #f39c12);
  font-size: 17px;
}

.rank-number.top-three:nth-child(3n+3) {
  background: linear-gradient(135deg, #67c23a, #27ae60);
  font-size: 16px;
}

.user-avatar {
  margin-right: 18px;
  position: relative;
}

.user-avatar::after {
  content: '';
  position: absolute;
  top: -3px;
  left: -3px;
  right: -3px;
  bottom: -3px;
  border-radius: 50%;
  border: 2px solid transparent;
  opacity: 0;
  transition: all 0.3s;
}

.ranking-item:hover .user-avatar::after {
  opacity: 1;
  border-color: #409eff;
}

.user-info, .post-info, .board-info {
  flex: 1;
}

.user-name, .post-title, .board-name {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
}

.user-name a, .post-title a, .board-name a {
  color: #303133;
  text-decoration: none;
  transition: color 0.2s;
}

.user-name a:hover, .post-title a:hover, .board-name a:hover {
  color: #409eff;
}

.user-stats, .post-meta {
  display: flex;
  gap: 15px;
  color: #909399;
  font-size: 13px;
  flex-wrap: wrap;
}

.user-stats span, .post-meta span {
  background-color: #f5f7fa;
  padding: 4px 10px;
  border-radius: 4px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.user-stats span .el-icon, .post-meta span .el-icon {
  font-size: 14px;
}

.user-stats .register-time {
  background-color: #f0f9eb;
  color: #67c23a;
}

.board-description {
  color: #606266;
  font-size: 14px;
  margin-top: 5px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.ranking-value {
  font-weight: bold;
  color: #409eff;
  margin-left: 15px;
  background-color: #ecf5ff;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
  white-space: nowrap;
}

.ranking-stats {
  display: flex;
  gap: 15px;
}

.stat-item {
  display: flex;
  align-items: center;
  color: #606266;
  font-size: 14px;
  background-color: #f5f7fa;
  padding: 4px 10px;
  border-radius: 6px;
  transition: all 0.3s;
}

.stat-item:hover {
  background-color: #ecf5ff;
  color: #409eff;
}

.stat-item .el-icon {
  margin-right: 5px;
  font-size: 16px;
}

.loading-container {
  padding: 30px 0;
}

/* 添加响应式样式 */
@media screen and (max-width: 768px) {
  .ranking-item {
    flex-direction: column;
    align-items: flex-start;
    padding: 15px;
  }
  
  .rank-number {
    margin-bottom: 10px;
  }
  
  .user-avatar {
    margin-bottom: 10px;
  }
  
  .user-stats, .post-meta {
    flex-direction: column;
    gap: 5px;
  }
  
  .ranking-value, .ranking-stats {
    margin-top: 10px;
    margin-left: 0;
  }
}
</style> 