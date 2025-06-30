<template>
  <div class="post-list-container">
    <!-- 顶部过滤器 -->
    <el-card class="filter-card">
      <div class="filter-container">
        <div class="filter-item">
          <el-select v-model="listQuery.board" placeholder="选择板块" clearable @change="handleFilter" style="width: 120px;">
            <el-option
              v-for="board in boardOptions"
              :key="board.id"
              :label="board.name"
              :value="board.id"
            >
            </el-option>
          </el-select>
        </div>

        <div class="filter-item">
          <el-select v-model="listQuery.ordering" placeholder="排序方式" @change="handleFilter" style="width: 120px;">
            <el-option label="最新发布" value="-created_at"></el-option>
            <el-option label="最多浏览" value="-views"></el-option>
            <el-option label="最多点赞" value="-likes_count"></el-option>
            <el-option label="最多评论" value="-comments_count"></el-option>
          </el-select>
        </div>

        <div class="filter-item">
          <el-input
            v-model="listQuery.search"
            placeholder="搜索帖子"
            style="width: 200px;"
            clearable
            @keyup.enter="handleFilter"
            @clear="handleFilter"
          >
            <template #append>
              <el-button @click="handleFilter">
                <el-icon><Search /></el-icon>
              </el-button>
            </template>
          </el-input>
        </div>

        <div class="filter-item">
          <el-button type="primary" @click="handleCreatePost">发布新帖</el-button>
        </div>
      </div>
    </el-card>

    <!-- 帖子列表 -->
    <el-card class="post-list-card">
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="10" animated />
      </div>
      <div v-else>
        <div v-if="posts.length === 0" class="empty-posts">
          <el-icon :size="48">
            <Document />
          </el-icon>
          <p>暂无帖子，快来发布第一篇帖子吧！</p>
        </div>
        <div v-else class="post-list">
          <div
            v-for="post in posts"
            :key="post.id"
            class="post-item"
            @click="viewPost(post)"
          >
            <div class="post-title">
              <el-tag v-if="post.is_pinned" size="small" type="danger">置顶</el-tag>
              <el-tag v-if="post.is_featured" size="small" type="success">精华</el-tag>
              <span>{{ post.title }}</span>
            </div>
            <div class="post-meta">
              <div class="post-board">
                <el-icon><Grid /></el-icon>
                <span>{{ post.board_name }}</span>
              </div>
              <div class="post-author" @click.stop="goToUserProfile(post.user?.id)" style="cursor: pointer;">
                <el-icon><User /></el-icon>
                <span>{{ post.user.nickname || post.user.username }}</span>
              </div>
              <div class="post-stats">
                <span>
                  <el-icon><View /></el-icon>
                  {{ post.views }}
                </span>
                <span>
                  <el-icon><Star /></el-icon>
                  {{ post.likes_count }}
                </span>
                <span>
                  <el-icon><ChatDotRound /></el-icon>
                  {{ post.comments_count }}
                </span>
              </div>
              <div class="post-time">{{ formatDate(post.created_at) }}</div>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination
            background
            layout="prev, pager, next"
            :total="total"
            :page-size="listQuery.limit"
            :current-page="listQuery.page"
            @current-change="handlePageChange"
          >
          </el-pagination>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { getPostList } from '@/api/post'
import { getBoardList } from '@/api/board'
import { formatDateTime } from '@/utils/index'
import { mapGetters } from 'vuex'

// 是否启用调试日志
const DEBUG = false;

// 自定义日志函数，可以通过DEBUG开关控制
const log = (...args) => {
  if (DEBUG) {
    console.log(...args);
  }
};

// 格式化日期函数
const formatDate = (date) => {
  return formatDateTime(date)
}

export default {
  name: 'PostList',
  data() {
    return {
      loading: false,
      posts: [],
      total: 0,
      boardOptions: [],
      listQuery: {
        page: 1,
        limit: 10,
        board: null,
        ordering: '-created_at',
        search: ''
      }
    }
  },
  computed: {
    ...mapGetters([
      'isLoggedIn'
    ]),
    isLogin() {
      return this.isLoggedIn
    }
  },
  created() {
    log('PostList组件created，登录状态:', this.isLogin, '认证状态:', this.isAuthenticated)
    this.fetchBoardOptions()
    this.fetchPosts()
  },
  methods: {
    formatDate,

    // 获取板块选项
    async fetchBoardOptions() {
      try {
        const response = await getBoardList()
        if (response.code === 0) {
          this.boardOptions = response.data
        }
      } catch (error) {
        log('获取板块列表失败:', error)
      }
    },

    // 获取帖子列表
    async fetchPosts() {
      this.loading = true
      try {
        const params = {
          page: this.listQuery.page,
          page_size: this.listQuery.limit,
          ordering: this.listQuery.ordering
        }

        if (this.listQuery.board) {
          params.board = this.listQuery.board
        }

        if (this.listQuery.search) {
          params.search = this.listQuery.search
        }

        log('组件开始获取帖子列表，参数:', params)
        const response = await getPostList(params)
        log('组件收到帖子列表响应:', response)
        
        // 处理响应
        this.processPostsResponse(response)
      } catch (error) {
        log('获取帖子列表失败:', error)
        // 设置空列表
        this.posts = []
        this.total = 0
      } finally {
        this.loading = false
      }
    },
    
    // 处理帖子列表响应
    processPostsResponse(response) {
      // 关闭调试日志
      const DEBUG_THIS = false;
      
      // 如果响应为空，设置空帖子列表
      if (!response) {
        if (DEBUG_THIS) console.log('帖子列表响应为空，设置空帖子列表');
        this.posts = [];
        this.total = 0;
        return;
      }
      
      if (DEBUG_THIS) console.log('处理帖子列表响应:', response);
      
      // 提取帖子数据和总数
      let posts = [];
      let total = 0;
      
      try {
      if (response.data && response.data.results) {
        // 标准格式：{data: {results: [...], count: 10}}
          if (DEBUG_THIS) console.log('标准格式响应');
          posts = response.data.results || [];
          total = response.data.count || 0;
      } else if (response.results) {
        // 直接结果格式：{results: [...], count: 10}
          if (DEBUG_THIS) console.log('直接结果格式响应');
          posts = response.results || [];
          total = response.count || 0;
      } else if (Array.isArray(response)) {
        // 数组格式：[...]
          if (DEBUG_THIS) console.log('数组格式响应');
          posts = response;
          total = response.length;
      } else if (response.data && Array.isArray(response.data)) {
        // 数组包装格式：{data: [...]}
          if (DEBUG_THIS) console.log('数组包装格式响应');
          posts = response.data;
          total = response.data.length;
        } else {
          // 其他情况，尝试从响应中提取有用信息
          if (DEBUG_THIS) console.log('无法识别的响应格式，尝试提取数据');
          
          if (response.data && typeof response.data === 'object') {
            // 尝试将data作为单个帖子对象
            if (DEBUG_THIS) console.log('尝试将data作为单个帖子对象');
            posts = [response.data];
            total = 1;
          } else if (typeof response === 'object' && !Array.isArray(response)) {
            // 尝试将整个响应作为单个帖子对象
            if (DEBUG_THIS) console.log('尝试将整个响应作为单个帖子对象');
            posts = [response];
            total = 1;
      } else {
            // 无法提取，使用空数组
            if (DEBUG_THIS) console.log('无法从响应中提取帖子数据，使用空数组');
            this.posts = [];
            this.total = 0;
            return;
          }
        }
        
        // 确保posts是数组
        if (!Array.isArray(posts)) {
          if (DEBUG_THIS) console.log('帖子数据不是数组，使用空数组');
          this.posts = [];
          this.total = 0;
          return;
      }
      
      // 确保帖子数据有效
        posts = posts.filter(post => post && typeof post === 'object');
        
        if (DEBUG_THIS) console.log('过滤后的帖子数据:', posts);
      
      // 确保每个帖子对象包含必要的字段
      posts = posts.map(post => {
        // 确保user字段存在
        const user = post.user || {
          id: 0,
          username: 'unknown',
          nickname: '未知用户',
          avatar_url: ''
          };
        
        // 确保board_name字段存在
          let board_name = post.board_name;
        if (!board_name && post.board) {
          if (typeof post.board === 'object') {
              board_name = post.board.name;
          } else {
              board_name = '板块' + post.board;
          }
        }
        
        // 返回处理后的帖子对象
        return {
          ...post,
          user,
          board_name: board_name || '未知板块',
          title: post.title || '无标题',
          content: post.content || '',
          created_at: post.created_at || new Date().toISOString(),
          views: post.views || 0,
          likes_count: post.likes_count || 0,
          comments_count: post.comments_count || 0,
          is_pinned: post.is_pinned || false,
          is_featured: post.is_featured || false
          };
        });
        
        if (DEBUG_THIS) console.log('最终处理后的帖子数据:', posts);
      
        this.posts = posts;
        this.total = total;
      } catch (error) {
        console.error('处理帖子列表响应时发生错误:', error);
        // 出现错误时，确保显示空列表而不是崩溃
        this.posts = [];
        this.total = 0;
      }
    },

    // 筛选
    handleFilter() {
      this.listQuery.page = 1
      this.fetchPosts()
    },

    // 页码变化
    handlePageChange(page) {
      this.listQuery.page = page
      this.fetchPosts()
    },

    // 查看帖子
    viewPost(post) {
      this.$router.push({ name: 'PostDetail', params: { id: post.id } })
    },

    // 跳转到用户主页
    goToUserProfile(userId) {
      if (userId) {
        this.$router.push({ name: 'UserProfile', params: { id: userId } });
        // 阻止冒泡，避免触发查看帖子
        event.stopPropagation();
      } else {
        this.$message.warning('无法获取用户信息');
      }
    },

    // 创建帖子
    handleCreatePost() {
      log('点击发布新帖按钮, 登录状态:', this.isLogin, '认证状态:', this.isAuthenticated)

      if (!this.isLogin) {
        log('未登录，跳转到登录页面')
        this.$message.warning('请先登录才能发布帖子')
        this.$router.push({ name: 'Login', query: { redirect: '/post/create' } })
        return
      }

      log('已登录，跳转到发帖页面')
      // 清除可能的成功消息提示
      this.$message.closeAll()
      this.$router.push({ name: 'PostCreate' })
    }
  }
}
</script>

<style scoped>
.post-list-container {
  padding: 20px;
}

.filter-card,
.post-list-card {
  margin-bottom: 20px;
}

.filter-container {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}

.filter-item {
  margin-right: 15px;
  margin-bottom: 10px;
}

/* 确保下拉框有足够宽度 */
:deep(.el-select) {
  min-width: 120px;
}

:deep(.el-select .el-input) {
  width: 100%;
}

:deep(.el-select-dropdown__item) {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.loading-container {
  padding: 20px 0;
}

.empty-posts {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  color: #909399;
}

.empty-posts .el-icon {
  margin-bottom: 10px;
}

.post-list {
  margin-bottom: 20px;
}

.post-item {
  padding: 15px;
  border-bottom: 1px solid #EBEEF5;
  cursor: pointer;
  transition: background-color 0.3s;
}

.post-item:hover {
  background-color: #F5F7FA;
}

.post-item:last-child {
  border-bottom: none;
}

.post-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
}

.post-title .el-tag {
  margin-right: 8px;
}

.post-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: #909399;
}

.post-board,
.post-author {
  display: flex;
  align-items: center;
}

.post-board .el-icon,
.post-author .el-icon {
  margin-right: 5px;
}

.post-stats {
  display: flex;
}

.post-stats span {
  margin-right: 15px;
  display: flex;
  align-items: center;
}

.post-stats span .el-icon {
  margin-right: 5px;
}

.pagination-container {
  text-align: center;
  margin-top: 20px;
}
</style>
