<template>
  <div class="board-detail-container">
    <!-- 板块信息卡片 -->
    <el-card class="board-info-card">
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="3" animated />
      </div>
      <div v-else class="board-header">
        <div class="board-title">
          <i class="el-icon-s-grid"></i>
          <h2>{{ board.name }}</h2>
        </div>
        <div class="board-description">{{ board.description }}</div>
        <div class="board-meta">
          <span>帖子数: {{ board.posts_count || 0 }}</span>
          <span>创建时间: {{ formatDate(board.created_at) }}</span>
        </div>
        <div class="board-actions">
          <el-button type="primary" @click="handleCreatePost">发布新帖</el-button>
          <el-button v-if="isAdmin" text @click="handleEditBoard">编辑板块</el-button>
        </div>
      </div>
    </el-card>

    <!-- 帖子列表 -->
    <el-card class="post-list-card">
      <template #header>
        <div class="clearfix">
          <span>帖子列表</span>
          <div class="post-filter">
            <el-select v-model="listQuery.ordering" placeholder="排序方式" @change="fetchPosts">
              <el-option label="最新发布" value="-created_at"></el-option>
              <el-option label="最多浏览" value="-views"></el-option>
              <el-option label="最多点赞" value="-likes_count"></el-option>
              <el-option label="最多评论" value="-comments_count"></el-option>
            </el-select>
            <el-input
              v-model="listQuery.search"
              placeholder="搜索帖子"
              style="width: 200px; margin-left: 10px;"
              clearable
              @keyup.enter="fetchPosts"
              @clear="fetchPosts"
            >
              <template #append>
                <el-button icon="el-icon-search" @click="fetchPosts"></el-button>
              </template>
            </el-input>
          </div>
        </div>
      </template>

      <div v-if="postsLoading" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>
      <div v-else>
        <div v-if="posts.length === 0" class="empty-posts">
          <i class="el-icon-document"></i>
          <p>暂无帖子，快来发布第一篇帖子吧！</p>
        </div>
        <div v-else class="post-list">
          <div
            v-for="(post, index) in posts"
            :key="post && post.id || index"
            class="post-item"
            @click="viewPost(post)"
          >
            <div class="post-title">
              <el-tag v-if="post && post.is_pinned" size="small" type="danger">置顶</el-tag>
              <el-tag v-if="post && post.is_featured" size="small" type="success">精华</el-tag>
              <span>{{ post && post.title || '无标题' }}</span>
            </div>
            <div class="post-meta">
              <div class="post-author">
                <i class="el-icon-user"></i>
                <span>{{ (post && post.user && (post.user.nickname || post.user.username)) || '未知用户' }}</span>
              </div>
              <div class="post-stats">
                <span><i class="el-icon-view"></i> {{ post && post.views || 0 }}</span>
                <span><i class="el-icon-star-on"></i> {{ post && post.likes_count || 0 }}</span>
                <span><i class="el-icon-chat-dot-round"></i> {{ post && post.comments_count || 0 }}</span>
              </div>
              <div class="post-time">{{ post && post.created_at ? formatDate(post.created_at) : '未知时间' }}</div>
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

    <!-- 编辑板块对话框 -->
    <el-dialog
      title="编辑板块"
      :visible="dialogVisible"
      width="500px"
    >
      <el-form
        ref="boardForm"
        :model="boardForm"
        :rules="boardRules"
        label-width="80px"
      >
        <el-form-item label="板块名称" prop="name">
          <el-input v-model="boardForm.name" placeholder="请输入板块名称"></el-input>
        </el-form-item>
        <el-form-item label="板块描述" prop="description">
          <el-input
            v-model="boardForm.description"
            type="textarea"
            :rows="4"
            placeholder="请输入板块描述"
          ></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取 消</el-button>
          <el-button type="primary" @click="submitBoardForm">确 定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { getBoardDetail, updateBoard } from '@/api/board'
import { getPostList } from '@/api/post'
import { formatDateTime } from '@/utils/index'
import { mapGetters } from 'vuex'

// 格式化日期函数
const formatDate = (date) => {
  return formatDateTime(date)
}

export default {
  name: 'BoardDetail',
  data() {
    return {
      loading: false,
      postsLoading: false,
      board: {},
      posts: [],
      total: 0,
      listQuery: {
        page: 1,
        limit: 10,
        board: null,
        ordering: '-created_at',
        search: ''
      },
      dialogVisible: false,
      boardForm: {
        name: '',
        description: ''
      },
      boardRules: {
        name: [
          { required: true, message: '请输入板块名称', trigger: 'blur' },
          { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
        ],
        description: [
          { max: 500, message: '长度不能超过 500 个字符', trigger: 'blur' }
        ]
      }
    }
  },
  computed: {
    ...mapGetters([
      'isAdmin',
      'isLoggedIn'
    ]),
    isLogin() {
      return this.isLoggedIn
    }
  },
  created() {
    const boardId = this.$route.params.id
    if (boardId) {
      this.listQuery.board = boardId
      this.fetchBoardDetail(boardId)
      this.fetchPosts()
    } else {
      this.$router.push({ name: 'BoardList' })
    }
  },
  methods: {
    formatDate,

    // 获取板块详情
    async fetchBoardDetail(id) {
      this.loading = true
      try {
        console.log('获取板块详情，ID:', id)
        const response = await getBoardDetail(id)
        console.log('板块详情响应:', response)

        if (response.code === 0 || response.status === 0) {
          this.board = response.data
          console.log('获取到的板块信息:', this.board)
        } else {
          console.error('获取板块详情失败，响应:', response)
          this.$message.error(response.msg || '获取板块详情失败')
        }
      } catch (error) {
        console.error('获取板块详情失败:', error)
        this.$message.error('获取板块详情失败，请检查网络连接或联系管理员')
      } finally {
        this.loading = false
      }
    },

    // 获取帖子列表
    async fetchPosts() {
      this.postsLoading = true
      try {
        const params = {
          page: this.listQuery.page,
          page_size: this.listQuery.limit,
          board: this.listQuery.board,
          ordering: this.listQuery.ordering
        }

        if (this.listQuery.search) {
          params.search = this.listQuery.search
        }

        console.log('获取帖子列表，参数:', params)
        const response = await getPostList(params)
        console.log('帖子列表响应:', response)

        if (response.code === 0 || response.status === 0) {
          // 处理不同的响应格式
          if (response.data.results) {
            // 分页响应
            this.posts = response.data.results
            this.total = response.data.count
          } else if (Array.isArray(response.data)) {
            // 直接返回数组
            this.posts = response.data
            this.total = response.data.length
          } else {
            console.error('帖子列表响应格式不正确:', response)
            this.posts = []
            this.total = 0
          }
          console.log('获取到的帖子列表:', this.posts)
        } else {
          console.error('获取帖子列表失败，响应:', response)
          this.$message.error(response.msg || '获取帖子列表失败')
        }
      } catch (error) {
        console.error('获取帖子列表失败:', error)
        this.$message.error('获取帖子列表失败，请检查网络连接或联系管理员')
      } finally {
        this.postsLoading = false
      }
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

    // 创建帖子
    handleCreatePost() {
      if (!this.isLogin) {
        this.$router.push('/login')
        return
      }
      // 使用 query 参数而不是 params 传递板块ID
      this.$router.push({
        name: 'PostCreate',
        query: { board: this.board.id }
      })
    },

    // 编辑板块
    handleEditBoard() {
      this.boardForm = {
        name: this.board.name,
        description: this.board.description
      }
      this.dialogVisible = true
    },

    // 提交板块表单
    submitBoardForm() {
      this.$refs.boardForm.validate(async (valid) => {
        if (valid) {
          try {
            const response = await updateBoard(this.board.id, this.boardForm)
            if (response.code === 0) {
              this.$message.success(response.msg || '更新成功')
              this.dialogVisible = false
              this.fetchBoardDetail(this.board.id)
            } else {
              this.$message.error(response.msg || '更新失败')
            }
          } catch (error) {
            console.error('更新板块失败:', error)
            this.$message.error('更新板块失败')
          }
        } else {
          return false
        }
      })
    }
  }
}
</script>

<style scoped>
.board-detail-container {
  padding: 20px;
}

.board-info-card,
.post-list-card {
  margin-bottom: 20px;
}

.loading-container {
  padding: 20px 0;
}

.board-header {
  padding: 10px 0;
}

.board-title {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.board-title i {
  font-size: 24px;
  margin-right: 10px;
  color: #409EFF;
}

.board-title h2 {
  margin: 0;
  font-size: 20px;
}

.board-description {
  color: #606266;
  margin-bottom: 15px;
  line-height: 1.5;
}

.board-meta {
  display: flex;
  color: #909399;
  font-size: 14px;
  margin-bottom: 15px;
}

.board-meta span {
  margin-right: 20px;
}

.board-actions {
  display: flex;
  align-items: center;
}

.post-filter {
  float: right;
  display: flex;
  align-items: center;
}

.empty-posts {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  color: #909399;
}

.empty-posts i {
  font-size: 48px;
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

.post-author {
  display: flex;
  align-items: center;
}

.post-author i {
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

.post-stats span i {
  margin-right: 5px;
}

.pagination-container {
  text-align: center;
  margin-top: 20px;
}
</style>
