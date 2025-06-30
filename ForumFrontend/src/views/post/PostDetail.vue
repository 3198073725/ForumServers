<template>
  <div class="post-detail-container">
    <!-- 帖子详情卡片 -->
    <el-card class="post-detail-card">
      <div v-if="loading" class="loading-container">
        <el-skeleton :rows="10" animated />
      </div>
      <div v-else>
        <div class="post-header">
          <!-- 非编辑状态下的标题 -->
          <h1 v-if="!isEditing" class="post-title">
            <el-tag v-if="post.is_pinned" size="medium" type="danger">置顶</el-tag>
            <el-tag v-if="post.is_featured" size="medium" type="success">精华</el-tag>
            {{ post.title }}
          </h1>
          <!-- 编辑状态下的标题输入框 -->
          <div v-else class="post-title-edit">
            <el-input v-model="editPostForm.title" placeholder="请输入帖子标题"></el-input>
          </div>

          <div class="post-meta">
            <div class="post-author" @click="goToUserProfile(post.user?.id)" style="cursor: pointer;">
              <el-avatar :size="40" :src="post.user?.avatar_url || ''">
                {{ post.user?.nickname?.charAt(0) || post.user?.username?.charAt(0) || 'U' }}
              </el-avatar>
              <div class="author-info">
                <div class="author-name">{{ post.user?.nickname || post.user?.username }}</div>
                <div class="post-time">发布于 {{ formatDate(post.created_at) }}</div>
              </div>
            </div>
            <div class="post-board" @click="goToBoard">
              <el-icon><Grid /></el-icon>
              <span>{{ post.board?.name }}</span>
            </div>
          </div>
        </div>

        <!-- 非编辑状态下的内容 -->
        <div v-if="!isEditing" class="post-content" v-html="post.content"></div>

        <!-- 编辑状态下的内容输入框 -->
        <div v-else class="post-content-edit">
          <el-input
            v-model="editPostForm.title"
            placeholder="请输入帖子标题"
          ></el-input>
          <rich-text-editor
            v-model="editPostForm.content"
            :disabled="false"
            @change="handleContentChange"
          />
          <!-- 编辑状态下的操作按钮 -->
          <div class="edit-actions">
            <el-button @click="cancelEdit">取消</el-button>
            <el-button type="primary" @click="submitEdit" :loading="editPostSubmitting">提交</el-button>
          </div>
        </div>

        <div class="post-footer">
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
          <div class="post-actions">
            <!-- 帖子作者可见的操作按钮 -->
            <template v-if="isPostAuthor">
              <el-button
                type="primary"
                size="small"
                @click="handleEditPost"
              >
                <el-icon><Edit /></el-icon>
                编辑
              </el-button>
              <el-button
                type="danger"
                size="small"
                @click="handleDeletePost"
              >
                <el-icon><Delete /></el-icon>
                删除
              </el-button>
            </template>

            <!-- 非作者可见的操作按钮 -->
            <template v-else>
              <el-button
                :type="isLiked ? 'primary' : 'default'"
                size="small"
                @click="handleLike"
              >
                <el-icon><Star /></el-icon>
                {{ isLiked ? '已点赞' : '点赞' }}
              </el-button>
              <el-button
                :type="isFavorited ? 'warning' : 'default'"
                size="small"
                @click="handleFavorite"
              >
                <el-icon><Collection /></el-icon>
                {{ isFavorited ? '已收藏' : '收藏' }}
              </el-button>
            </template>

            <!-- 管理员操作下拉菜单 -->
            <el-dropdown v-if="isAdmin" trigger="click" @command="handleCommand">
              <el-button size="small">
                <el-icon><Setting /></el-icon>
                管理
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                <el-dropdown-item command="pin">
                  {{ post.is_pinned ? '取消置顶' : '置顶' }}
                </el-dropdown-item>
                <el-dropdown-item command="feature">
                  {{ post.is_featured ? '取消加精' : '加精' }}
                </el-dropdown-item>
              </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 评论区 -->
    <el-card class="comments-card">
      <div slot="header" class="clearfix">
        <span>评论区 ({{ post.comments_count || 0 }})</span>
      </div>

      <!-- 发表评论 -->
      <div class="comment-form">
        <el-input
          v-model="commentContent"
          type="textarea"
          :rows="3"
          placeholder="发表你的评论..."
          :disabled="!isLogin"
        ></el-input>
        <div class="comment-form-footer">
          <el-button
            type="primary"
            :disabled="!isLogin || !commentContent.trim()"
            @click="submitComment"
          >
            发表评论
          </el-button>
          <div v-if="!isLogin" class="login-tip">
            请先 <router-link :to="{ name: 'Login', query: { redirect: $route.fullPath } }">登录</router-link> 后发表评论
          </div>
        </div>
      </div>

      <!-- 评论列表 -->
      <div v-if="commentsLoading" class="loading-container">
        <el-skeleton :rows="5" animated />
      </div>
      <div v-else-if="comments.length === 0" class="empty-comments">
        <el-icon :size="48"><ChatDotRound /></el-icon>
        <p v-if="isLogin">暂无评论，快来发表第一条评论吧！</p>
        <p v-else>暂无评论，登录后可以发表评论</p>
      </div>
      <div v-else class="comments-list">
        <div v-for="comment in comments" :key="comment.id" class="comment-item">
          <div class="comment-header">
            <div class="comment-user" @click="goToUserProfile(comment.user?.id)" style="cursor: pointer;">
              <el-avatar :size="40" :src="comment.user?.avatar_url || ''">
                {{ comment.user?.nickname?.charAt(0) || comment.user?.username?.charAt(0) || 'U' }}
              </el-avatar>
              <div class="comment-user-info">
                <div class="comment-username">{{ comment.user.nickname || comment.user.username }}</div>
                <div class="comment-time">{{ formatDate(comment.created_at) }}</div>
              </div>
            </div>
            <div class="comment-actions" v-if="canManageComment(comment)">
              <el-button text size="small" @click="handleDeleteComment(comment)">删除</el-button>
            </div>
          </div>
          <div class="comment-content">{{ comment.content }}</div>
          <div class="comment-footer">
            <el-button v-if="isLogin" text size="small" @click="handleReply(comment)">回复</el-button>
          </div>

          <!-- 回复表单 -->
          <div v-if="replyingTo === comment.id" class="reply-form">
            <el-input
              v-model="replyContent"
              type="textarea"
              :rows="2"
              placeholder="回复评论..."
            ></el-input>
            <div class="reply-form-footer">
              <el-button type="primary" size="small" @click="submitReply(comment)" :disabled="!replyContent.trim()">提交回复</el-button>
              <el-button size="small" @click="cancelReply">取消</el-button>
            </div>
          </div>

          <!-- 回复列表 -->
          <div v-if="comment.replies && comment.replies.length > 0" class="replies-list">
            <div v-for="reply in comment.replies" :key="reply.id" class="reply-item">
              <div class="reply-header">
                <div class="reply-user" @click="goToUserProfile(reply.user?.id)" style="cursor: pointer;">
                  <el-avatar :size="30" :src="reply.user?.avatar_url || ''">
                    {{ reply.user?.nickname?.charAt(0) || reply.user?.username?.charAt(0) || 'U' }}
                  </el-avatar>
                  <div class="reply-user-info">
                    <div class="reply-username">{{ reply.user.nickname || reply.user.username }}</div>
                    <div class="reply-time">{{ formatDate(reply.created_at) }}</div>
                  </div>
                </div>
                <div class="reply-actions" v-if="canManageComment(reply)">
                  <el-button text size="small" @click="handleDeleteComment(reply)">删除</el-button>
                </div>
              </div>
              <div class="reply-content">{{ reply.content }}</div>
              <div class="reply-footer">
                <el-button v-if="isLogin" text size="small" @click="handleReply(comment, reply)">回复</el-button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="comments.length > 0" class="pagination-container">
        <el-pagination
          background
          layout="prev, pager, next"
          :total="commentsTotal"
          :page-size="commentsQuery.limit"
          :current-page="commentsQuery.page"
          @update:current-page="val => commentsQuery.page = val"
          @current-change="handleCommentsPageChange"
        >
        </el-pagination>
      </div>
    </el-card>

  </div>
</template>

<script>
import { getPostDetail, likePost, favoritePost, pinPost, featurePost, deletePost, updatePost, getLikeStatus, getFavoriteStatus } from '@/api/post'
import { getPostComments, createComment, replyComment, deleteComment } from '@/api/comment'
import { formatDateTime } from '@/utils/index'
import { mapGetters } from 'vuex'
import RichTextEditor from '@/components/RichTextEditor.vue'

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
  name: 'PostDetail',
  components: {
    RichTextEditor
  },
  data() {
    return {
      loading: false,
      commentsLoading: false,
      post: {},
      isLiked: false,
      isFavorited: false,
      comments: [],
      commentsTotal: 0,
      commentsQuery: {
        page: 1,
        limit: 10
      },
      commentContent: '',
      replyingTo: null,
      replyContent: '',

      forceRefresh: false, // 用于强制刷新评论列表的内部标志

      // 编辑帖子相关
      isEditing: false, // 是否处于编辑状态
      editPostSubmitting: false,
      editPostForm: {
        title: '',
        content: ''
      },
      postRules: {
        title: [
          { required: true, message: '请输入帖子标题', trigger: 'blur' },
          { min: 2, max: 100, message: '标题长度在2到100个字符之间', trigger: 'blur' }
        ],
        content: [
          { required: true, message: '请输入帖子内容', trigger: 'blur' },
          { min: 5, message: '内容至少5个字符', trigger: 'blur' }
        ]
      }
    }
  },
  computed: {
    ...mapGetters([
      'isAuthenticated',
      'isAdmin',
      'userId'
    ]),
    isLogin() {
      return this.$store.getters.isLoggedIn
    },
    isPostAuthor() {
      return this.isLogin && this.post.user && this.post.user.id === this.userId
    },
    canManagePost() {
      return this.isLogin && (
        this.isAdmin ||
        this.isPostAuthor
      )
    }
  },
  created() {
    log('PostDetail组件created，登录状态:', this.isLogin, '认证状态:', this.$store.getters.isLoggedIn)
    const postId = this.$route.params.id
    if (postId) {
      log('准备获取帖子详情和评论，ID:', postId)
      this.fetchPostDetail(postId)
      this.fetchComments(postId)
    } else {
      log('没有帖子ID，跳转到帖子列表')
      this.$router.push({ name: 'PostList' })
    }
  },
  methods: {
    formatDate,

    // 获取帖子详情
    async fetchPostDetail(id) {
      this.loading = true
      try {
        log('组件开始获取帖子详情, ID:', id)
        const response = await getPostDetail(id)
        log('组件收到帖子详情响应:', response)

        // 检查响应是否有效
        if (!response) {
          log('帖子详情响应为空')
          this.post = {}
          return
        }

        // 检查响应中的数据
        if (response.data) {
          log('使用响应中的data字段:', response.data)
          this.post = response.data
        } else if (response.code === 0 || response.status === 0) {
          log('响应成功但没有data字段，尝试使用响应本身')
          // 移除code、status、msg等字段，只保留实际数据
          const { code, status, msg, ...postData } = response
          if (Object.keys(postData).length > 0) {
            this.post = postData
          } else {
            log('响应中没有有效的帖子数据')
            this.$message.error('获取帖子详情失败，请稍后再试')
            this.post = {}
          }
        } else if (typeof response === 'object') {
          log('直接使用响应对象')
          this.post = response
        } else {
          log('无法从响应中提取帖子数据')
          this.$message.error('获取帖子详情失败，请稍后再试')
          this.post = {}
        }
        
        // 确保post对象包含必要的字段
        this.ensurePostFields()
        
        // 检查是否已点赞和收藏
        this.checkLikeAndFavorite()
      } catch (error) {
        log('获取帖子详情失败:', error)
        this.$message.error('获取帖子详情失败，请稍后再试')
        this.post = {}
        // 确保post对象包含必要的字段
        this.ensurePostFields()
      } finally {
        this.loading = false
      }
    },

    // 确保帖子对象包含所有必要的字段
    ensurePostFields() {
      // 确保post是一个对象
      if (!this.post || typeof this.post !== 'object') {
        this.post = {}
      }
      
      // 确保必要的字段存在
      this.post.title = this.post.title || '帖子标题'
      this.post.content = this.post.content || '帖子内容'
      this.post.created_at = this.post.created_at || new Date().toISOString()
      this.post.views = this.post.views || 0
      this.post.likes_count = this.post.likes_count || 0
      this.post.comments_count = this.post.comments_count || 0
      this.post.is_pinned = this.post.is_pinned || false
      this.post.is_featured = this.post.is_featured || false
      
      // 确保board字段存在
      if (!this.post.board || typeof this.post.board !== 'object') {
        this.post.board = { id: 1, name: '默认板块' }
      } else if (typeof this.post.board === 'number') {
        // 如果board只是一个ID，转换为对象
        this.post.board = { id: this.post.board, name: '板块' + this.post.board }
      }
      
      // 确保board.name字段存在
      if (!this.post.board.name) {
        this.post.board.name = '板块' + this.post.board.id
      }
      
      // 确保user字段存在
      if (!this.post.user || typeof this.post.user !== 'object') {
        this.post.user = {
          id: 1,
          username: 'user',
          nickname: '用户',
          avatar_url: ''
        }
      }
      
      // 确保user.nickname字段存在
      if (!this.post.user.nickname) {
        this.post.user.nickname = this.post.user.username || '用户'
      }
    },

    // 检查是否已点赞和收藏
    async checkLikeAndFavorite() {
      if (!this.isLogin) {
        log('未登录用户，设置为未点赞和未收藏状态')
        this.isLiked = false
        this.isFavorited = false
        return
      }

      try {
        // 并行请求点赞和收藏状态
        const [likeResponse, favoriteResponse] = await Promise.all([
          getLikeStatus(this.post.id),
          getFavoriteStatus(this.post.id)
        ]);

        // 更新点赞状态
        this.isLiked = likeResponse.data?.is_liked || false;
        // 更新收藏状态
        this.isFavorited = favoriteResponse.data?.is_favorited || false;

        log('获取状态成功:', {
          isLiked: this.isLiked,
          isFavorited: this.isFavorited
        });
      } catch (error) {
        log('获取点赞/收藏状态失败:', error);
        // 状态获取失败时，默认为未点赞和未收藏
        this.isLiked = false;
        this.isFavorited = false;
      }
    },

    // 获取评论列表
    async fetchComments(postId) {
      // 如果已经在加载中，则不重复加载
      if (this.commentsLoading && !this.forceRefresh) {
        return Promise.resolve()
      }

      this.commentsLoading = true
      log('开始获取评论列表，ID:', postId, '强制刷新:', this.forceRefresh)

      try {
        // 使用API函数的forceRefresh参数
        const response = await getPostComments(postId, this.forceRefresh)
        log('评论列表响应:', response)
        
        // 处理响应
        this.processCommentsResponse(response)
      } catch (error) {
        log('获取评论列表失败:', error)
        // 设置空评论列表
        this.comments = []
        this.commentsTotal = 0
        
        // 未登录用户不显示错误提示
        if (!(error.response && error.response.status === 401)) {
          this.$message.error('获取评论列表失败，请刷新页面重试')
        }
      } finally {
        this.commentsLoading = false
        this.forceRefresh = false // 重置强制刷新标志
        log('评论列表获取完成，重置强制刷新标志')
      }
    },
    
    // 处理评论列表响应
    processCommentsResponse(response) {
      // 如果响应为空，设置空评论列表
      if (!response) {
        log('评论列表响应为空，设置空评论列表')
        this.comments = []
        this.commentsTotal = 0
        return
      }
      
      // 提取评论数据和总数
      let comments = []
      let total = 0
      
      if (response.data && response.data.results) {
        // 标准格式：{data: {results: [...], count: 10}}
        comments = response.data.results
        total = response.data.count || 0
      } else if (response.results) {
        // 直接结果格式：{results: [...], count: 10}
        comments = response.results
        total = response.count || 0
      } else if (Array.isArray(response)) {
        // 数组格式：[...]
        comments = response
        total = response.length
      } else if (response.data && Array.isArray(response.data)) {
        // 数组包装格式：{data: [...]}
        comments = response.data
        total = response.data.length
      } else {
        // 其他情况，设置空评论列表
        log('无法从响应中提取评论数据，设置空评论列表')
        this.comments = []
        this.commentsTotal = 0
        return
      }
      
      // 确保评论数据有效
      comments = comments.filter(comment => comment && typeof comment === 'object')
      
      // 处理评论数据
      this.comments = comments.map(comment => {
        // 确保replies字段存在
        const replies = Array.isArray(comment.replies) ? comment.replies : []
        
        // 确保user字段存在
        const user = comment.user || {
          id: 0,
          username: 'unknown',
          nickname: '未知用户',
          avatar_url: ''
        }
        
        // 返回处理后的评论对象
        return {
          ...comment,
          replies,
          user
        }
      })
      
      this.commentsTotal = total
      
      // 更新帖子评论数
      if (this.post) {
        this.post.comments_count = total
      }
    },

    // 评论分页变化
    handleCommentsPageChange(page) {
      this.commentsQuery.page = page
      this.fetchComments(this.post.id)
    },

    // 前往板块页面
    goToBoard() {
      if (this.post.board && this.post.board.id) {
        this.$router.push({ name: 'BoardDetail', params: { id: this.post.board.id } })
      }
    },

    // 跳转到用户主页
    goToUserProfile(userId) {
      if (userId) {
        this.$router.push({ name: 'UserProfile', params: { id: userId } });
      } else {
        this.$message.warning('无法获取用户信息');
      }
    },

    // 收藏帖子
    async handleFavorite() {
      if (!this.isLogin) {
        this.$message.warning('请先登录')
        this.$router.push({ name: 'Login', query: { redirect: this.$route.fullPath } })
        return
      }

      try {
        console.log('收藏操作开始，当前状态:', this.isFavorited, '帖子ID:', this.post.id);
        
        // 先乐观更新UI状态
        const previousState = this.isFavorited
          this.isFavorited = !this.isFavorited
        
        console.log('调用favoritePost API...');
        const response = await favoritePost(this.post.id)
        console.log('favoritePost API响应:', response);
        
        // 根据API响应更新状态，而不是依赖本地状态
        if (response && response.data && response.data.is_favorited !== undefined) {
          this.isFavorited = response.data.is_favorited;
          console.log('根据API响应更新收藏状态为:', this.isFavorited);
        }
        
          // 使用 Notification 替代 Message
          this.$notify({
            title: this.isFavorited ? '收藏成功' : '已取消收藏',
            message: this.isFavorited ? '帖子已添加到您的收藏列表' : '帖子已从您的收藏列表中移除',
            type: this.isFavorited ? 'success' : 'info',
            position: 'top-right',
            duration: 2000,
            showClose: false,
            customClass: this.isFavorited ? 'favorite-notification success' : 'favorite-notification info'
          })
      } catch (error) {
        console.error('收藏操作失败:', error)
        // 恢复之前的状态
        this.isFavorited = !this.isFavorited
        
        this.$notify.error({
          title: '收藏操作失败',
          message: error.message || '请稍后重试',
          position: 'top-right',
          duration: 3000
        })
        
        // 如果是未登录错误，跳转到登录页
        if (error.response && error.response.status === 401) {
          this.$router.push({ name: 'Login', query: { redirect: this.$route.fullPath } })
        }
      }
    },

    // 点赞帖子
    async handleLike() {
      if (!this.isLogin) {
        this.$message.warning('请先登录')
        this.$router.push({ name: 'Login', query: { redirect: this.$route.fullPath } })
        return
      }

      try {
        const response = await likePost(this.post.id)
        // 更新点赞状态
        this.isLiked = !this.isLiked
        // 更新点赞数
        this.post.likes_count = this.isLiked ? this.post.likes_count + 1 : this.post.likes_count - 1
        // 使用 Notification 替代 Message
        this.$notify({
          title: this.isLiked ? '点赞成功' : '已取消点赞',
          message: this.isLiked ? '感谢您的支持！' : '您已取消点赞',
          type: this.isLiked ? 'success' : 'info',
          position: 'top-right',
          duration: 2000,
          showClose: false,
          customClass: this.isLiked ? 'like-notification success' : 'like-notification info'
        })
      } catch (error) {
        log('点赞操作失败:', error)
        this.$notify.error({
          title: '操作失败',
          message: error.message || '请稍后重试',
          position: 'top-right',
          duration: 3000
        })
        // 如果是未登录错误，跳转到登录页
        if (error.response && error.response.status === 401) {
          this.$router.push({ name: 'Login', query: { redirect: this.$route.fullPath } })
        }
        // 操作失败时恢复原状态
        await this.checkLikeAndFavorite()
      }
    },

    // 帖子管理操作
    async handleCommand(command) {
      switch (command) {
        case 'pin':
          this.handlePinPost()
          break
        case 'feature':
          this.handleFeaturePost()
          break
      }
    }, 
    // 编辑帖子
    handleEditPost() {
      log('开始编辑帖子，原始内容:', {
        title: this.post.title,
        content: this.post.content
      });
      
      // 初始化编辑表单数据
      this.editPostForm = {
        title: this.post.title,
        content: this.post.content
      };
      
      // 切换到编辑状态
      this.isEditing = true;
    },

    // 取消编辑
    cancelEdit() {
      // 退出编辑状态
      this.isEditing = false
      // 重置表单数据
      this.editPostForm.title = this.post.title
      this.editPostForm.content = this.post.content
    },

    // 提交编辑
    async submitEdit() {
      // 表单验证
      if (!this.editPostForm.title.trim()) {
        this.$message.warning('标题不能为空')
        return
      }

      if (!this.editPostForm.content.trim()) {
        this.$message.warning('内容不能为空')
        return
      }

      this.editPostSubmitting = true
      try {
        // 确保发送正确的数据格式
        const postData = {
          title: this.editPostForm.title.trim(),
          content: this.editPostForm.content.trim(),
          board: this.post.board.id // 需要包含板块ID
        }

        log('提交更新帖子数据:', postData)

        const response = await updatePost(this.post.id, postData)

        // 更新当前页面的帖子数据
        this.post.title = this.editPostForm.title
        this.post.content = this.editPostForm.content
        // 更新帖子的更新时间
        if (response.data && response.data.updated_at) {
          this.post.updated_at = response.data.updated_at
        }

        // 退出编辑状态
        this.isEditing = false

        // 显示成功提示
        this.$notify({
          title: '更新成功',
          message: '帖子内容已更新',
          type: 'success',
          position: 'top-right',
          duration: 2000
        })
      } catch (error) {
        console.error('更新帖子失败:', error)
        this.$notify.error({
          title: '更新失败',
          message: error.message || '请稍后重试',
          position: 'top-right',
          duration: 3000
        })
      } finally {
        this.editPostSubmitting = false
      }
    },

    // 删除帖子
    async handleDeletePost() {
      try {
        // 更详细的确认提示
        await this.$confirm(
          '确定要删除这篇帖子吗？删除后将无法恢复，帖子下的所有评论也将被删除。',
          '删除确认',
          {
            confirmButtonText: '确定删除',
            cancelButtonText: '取消',
            type: 'warning',
            distinguishCancelAndClose: true,
            closeOnClickModal: false
          }
        )

        // 显示加载状态
        const loading = this.$loading({
          lock: true,
          text: '正在删除帖子...',
          spinner: 'el-icon-loading',
          background: 'rgba(0, 0, 0, 0.7)'
        })

        try {
          const response = await deletePost(this.post.id)
          loading.close() // 关闭加载状态

          if (response.code === 0) {
            // 不显示任何提示弹窗，直接返回上一级路由
            log('帖子删除成功，正在返回上一级路由...')
            // 返回上一级路由
            this.$router.go(-1)
          } else {
            this.$message.error(response.msg || '删除失败，请稍后重试')
          }
        } catch (err) {
          loading.close() // 确保加载状态被关闭
          log('删除帖子请求失败:', err)
          this.$message.error('删除帖子失败，请检查网络连接')
        }
      } catch (error) {
        // 用户取消删除，不做任何处理
        if (error !== 'cancel') {
          log('删除帖子操作异常:', error)
          this.$message.error('操作异常，请刷新页面后重试')
        }
      }
    },

    // 置顶/取消置顶帖子
    async handlePinPost() {
      try {
        const response = await pinPost(this.post.id)
        if (response.code === 0) {
          this.post.is_pinned = !this.post.is_pinned
          // this.$message.success(response.msg || (this.post.is_pinned ? '置顶成功' : '取消置顶成功')) // 注释掉这行，避免重复显示成功消息
        } else {
          this.$message.error(response.msg || '操作失败')
        }
      } catch (error) {
        log('置顶操作失败:', error)
        this.$message.error('置顶操作失败')
      }
    },

    // 加精/取消加精帖子
    async handleFeaturePost() {
      try {
        const response = await featurePost(this.post.id)
        if (response.code === 0) {
          this.post.is_featured = !this.post.is_featured
          // this.$message.success(response.msg || (this.post.is_featured ? '加精成功' : '取消加精成功')) // 注释掉这行，避免重复显示成功消息
        } else {
          this.$message.error(response.msg || '操作失败')
        }
      } catch (error) {
        log('加精操作失败:', error)
        this.$message.error('加精操作失败')
      }
    },

    // 提交评论
    async submitComment() {
      log('评论提交 - 登录状态检查:', {
        isLogin: this.isLogin,
        storeIsLoggedIn: this.$store.getters.isLoggedIn,
        token: this.$store.state.token,
        userInfo: this.$store.state.user,
        localStorageToken: localStorage.getItem('token'),
        localStorageUserInfo: localStorage.getItem('userInfo')
      })

      // 如果localStorage有token但store中认证状态为false，尝试强制刷新认证状态
      if (!this.isLogin && localStorage.getItem('token')) {
        log('检测到localStorage有token但store认证状态为false，尝试强制刷新认证状态');
        await this.$store.dispatch('getUserInfo');
        // 重新检查登录状态
        log('刷新后的登录状态:', {
          isLogin: this.$store.getters.isLoggedIn,
          token: this.$store.state.token,
          userInfo: this.$store.state.user
        });
      }
      
      if (!this.isLogin) {
        log('未登录状态，无法提交评论')
        this.$message.warning('请先登录')
        this.$router.push({ name: 'Login', query: { redirect: this.$route.fullPath } })
        return
      }

      if (!this.commentContent.trim()) {
        this.$message.warning('评论内容不能为空')
        return
      }

      try {
        log('提交评论数据:', {
          post: this.post.id,
          content: this.commentContent,
          token: this.$store.state.token
        })

        // 确保API请求中包含有效的token
        const token = this.$store.state.token || localStorage.getItem('token');
        if (!token) {
          log('提交评论时没有有效的token');
          this.$message.error('登录状态异常，请重新登录');
          this.$router.push({ name: 'Login', query: { redirect: this.$route.fullPath } });
          return;
        }

        const response = await createComment({
          post: this.post.id,
          content: this.commentContent
        })

        log('评论提交响应:', response)

        if (response && (response.code === 0 || response.status === 0)) {
          // 不显示成功消息
          log('评论发表成功，不显示成功消息')

          // 清空评论内容
          this.commentContent = ''

          // 无论如何，强制刷新评论列表以确保同步
          log('强制刷新评论列表以确保与数据库同步')
          this.forceRefresh = true
          await this.fetchComments(this.post.id)

          // 只有在确认获取到评论数据时，才尝试本地添加
          if (response.data && response.data.id) {
            log('获取到新评论数据，ID:', response.data.id)
            
            // 获取当前用户信息
            const userInfo = this.$store.getters.userInfo
            
            // 构建评论对象
            const newComment = {
              ...response.data,
              id: response.data.id,
              user: userInfo,
              replies: [],
              created_at: response.data.created_at || new Date().toISOString()
            };

            // 将新评论添加到评论列表的开头（如果不在列表中）
            const existingComment = this.comments.find(c => c.id === newComment.id)
            if (!existingComment) {
              this.comments.unshift(newComment);
              log('新评论已添加到列表')
            }
          }
        } else {
          log('评论发表失败，响应:', response)
          this.$message.error(response?.msg || '评论发表失败')
        }
      } catch (error) {
        log('评论发表失败:', error)
        this.$message.error('评论发表失败，请检查网络连接')
        
        // 发生错误时也刷新评论列表
        this.forceRefresh = true
        this.fetchComments(this.post.id)
      }
    },

    // 回复评论
    handleReply(comment, reply = null) {
      if (!this.isLogin) {
        this.$message.warning('请先登录')
        this.$router.push({ name: 'Login', query: { redirect: this.$route.fullPath } })
        return
      }

      this.replyingTo = comment.id
      this.replyContent = reply ? `@${reply.user.nickname || reply.user.username} ` : ''
    },

    // 取消回复
    cancelReply() {
      this.replyingTo = null
      this.replyContent = ''
    },

    // 提交回复
    async submitReply(comment) {
      if (!this.isLogin) {
        this.$message.warning('请先登录')
        this.$router.push({ name: 'Login', query: { redirect: this.$route.fullPath } })
        return
      }

      if (!this.replyContent.trim()) {
        this.$message.warning('回复内容不能为空')
        return
      }

      try {
        log('提交回复数据:', {
          post: this.post.id,
          parent: comment.id,
          content: this.replyContent
        })

        const response = await replyComment(
          this.post.id,
          comment.id,
          this.replyContent
        )

        log('回复提交响应:', response)

        if (response && (response.code === 0 || response.status === 0)) {
          // 清空回复状态
          this.replyingTo = null
          this.replyContent = ''

          // 无论如何，强制刷新评论列表以确保同步
          log('强制刷新评论列表以确保与数据库同步')
          this.forceRefresh = true
          await this.fetchComments(this.post.id)

          // 只有在确认获取到回复数据时，才尝试本地添加
          if (response.data && response.data.id) {
            log('获取到新回复数据，ID:', response.data.id)
            
            // 获取当前用户信息
            const userInfo = this.$store.getters.userInfo
            
            // 构建回复对象
            const newReply = {
              ...response.data,
              id: response.data.id,
              user: userInfo,
              created_at: response.data.created_at || new Date().toISOString()
            };

            // 将新回复添加到对应评论的回复列表（如果不在列表中）
            if (!comment.replies) {
              comment.replies = [];
            }
            
            const existingReply = comment.replies.find(r => r.id === newReply.id)
            if (!existingReply) {
              comment.replies.push(newReply);
              log('新回复已添加到列表')
            }
          }
        } else {
          log('回复发表失败，响应:', response)
          this.$message.error(response?.msg || '回复发表失败')
        }
      } catch (error) {
        log('回复发表失败:', error)
        this.$message.error('回复发表失败，请检查网络连接')
        
        // 发生错误时也刷新评论列表
        this.forceRefresh = true
        this.fetchComments(this.post.id)
      }
    },

    // 判断是否可以管理评论
    canManageComment(comment) {
      return this.isLogin && (
        this.isAdmin ||
        (comment.user && comment.user.id === this.userId)
      )
    },

    // 删除评论
    async handleDeleteComment(comment) {
      try {
        // 打印评论对象，用于调试
        log('要删除的评论对象:', comment)

        // 确保评论对象和ID存在
        if (!comment) {
          this.$message.error('评论数据无效，无法删除')
          return
        }

        // 获取评论ID，支持字符串和数字类型
        const commentId = comment.id ? parseInt(comment.id) : null
        if (!commentId) {
          this.$message.error('评论ID无效，无法删除')
          return
        }

        // 判断是否有回复，提供更详细的确认信息
        const hasReplies = comment.replies && comment.replies.length > 0
        const confirmMessage = hasReplies
          ? `确定要删除这条评论吗？删除后将同时删除该评论下的 ${comment.replies.length} 条回复，且无法恢复。`
          : '确定要删除这条评论吗？删除后将无法恢复。'

        await this.$confirm(confirmMessage, '删除确认', {
          confirmButtonText: '确定删除',
          cancelButtonText: '取消',
          type: 'warning',
          distinguishCancelAndClose: true,
          closeOnClickModal: false
        })

        // 显示加载状态
        const loading = this.$loading({
          lock: true,
          text: '正在删除评论...',
          spinner: 'el-icon-loading',
          background: 'rgba(0, 0, 0, 0.7)'
        })

        try {
          log('发送删除评论请求，ID:', commentId)
          const response = await deleteComment(commentId)
          loading.close() // 关闭加载状态

          // 修改判断条件，同时支持code: 0和status: 0作为成功状态
          if (response.code === 0 || response.status === 0) {
            log('评论删除成功，响应:', response)
            
            // 无论如何，强制刷新评论列表以确保同步
            log('强制刷新评论列表以确保与数据库同步')
            this.forceRefresh = true
            await this.fetchComments(this.post.id)
          } else {
            log('评论删除失败，响应:', response)
            this.$message.error(response.msg || '删除失败，请稍后重试')
            
            // 如果删除失败，也刷新评论列表恢复原状
            this.forceRefresh = true
            await this.fetchComments(this.post.id)
          }
        } catch (error) {
          loading.close()
          log('删除评论失败:', error)
          
          // 如果删除失败，刷新评论列表恢复原状
          this.forceRefresh = true
          await this.fetchComments(this.post.id)
          
          // 根据错误类型显示不同的错误信息
          if (error.response) {
            switch (error.response.status) {
              case 403:
                this.$message.error('您没有权限删除此评论')
                break
              case 404:
                this.$message.error('评论不存在或已被删除')
                break
              default:
                this.$message.error(error.response.data?.msg || '删除失败，请稍后重试')
            }
          } else if (error.request) {
            this.$message.error('网络连接失败，请检查网络后重试')
          } else {
            this.$message.error('删除失败，请稍后重试')
          }
        }
      } catch (error) {
        // 用户取消删除操作
        if (error === 'cancel') {
          return
        }
        log('删除评论操作失败:', error)
        this.$message.error('操作失败，请稍后重试')
      }
    },

    handleContentChange(value) {
      this.post.content = value;
    }
  }
}
</script>

<style scoped>
.post-detail-container {
  padding: 20px;
}

.post-detail-card,
.comments-card {
  margin-bottom: 20px;
}

.loading-container {
  padding: 20px 0;
}

.post-header {
  margin-bottom: 20px;
}

.post-title {
  font-size: 24px;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
}

.post-title .el-tag {
  margin-right: 10px;
}

.post-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.post-author {
  display: flex;
  align-items: center;
}

.author-info {
  margin-left: 10px;
}

.author-name {
  font-weight: bold;
}

.post-time,
.comment-time,
.reply-time {
  font-size: 12px;
  color: #909399;
}

.post-board {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #409EFF;
}

.post-board i {
  margin-right: 5px;
}

.post-content {
  margin-top: 20px;
  line-height: 1.6;
  word-break: break-word;
}

.post-content :deep(img) {
  max-width: 100%;
  height: auto;
  margin: 10px 0;
}

.post-content :deep(p) {
  margin: 10px 0;
}

.post-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin: 10px 0;
}

.post-content :deep(th),
.post-content :deep(td) {
  border: 1px solid #ddd;
  padding: 8px;
}

.post-content :deep(th) {
  background-color: #f5f5f5;
}

.post-content :deep(blockquote) {
  margin: 10px 0;
  padding: 10px 20px;
  border-left: 4px solid #ddd;
  background-color: #f9f9f9;
}

.post-content :deep(pre) {
  background-color: #f5f5f5;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}

.post-content :deep(code) {
  font-family: Consolas, Monaco, 'Andale Mono', monospace;
  background-color: #f5f5f5;
  padding: 2px 4px;
  border-radius: 3px;
}

.post-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 15px;
  border-top: 1px solid #EBEEF5;
}

.post-stats {
  display: flex;
  color: #909399;
}

.post-stats span {
  margin-right: 15px;
  display: flex;
  align-items: center;
}

.post-stats span i {
  margin-right: 5px;
}

.post-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.post-actions .el-button {
  margin-left: 0;
}

.comment-form {
  margin-bottom: 20px;
}

.comment-form-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.login-tip {
  margin-top: 10px;
  color: #909399;
  font-size: 14px;
}

.login-tip a {
  color: #409EFF;
  text-decoration: none;
  font-weight: bold;
}

.login-tip a:hover {
  text-decoration: underline;
}

.empty-comments {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 0;
  color: #909399;
}

.empty-comments i {
  font-size: 48px;
  margin-bottom: 10px;
}

.comments-list {
  margin-bottom: 20px;
}

.comment-item {
  padding: 15px 0;
  border-bottom: 1px solid #EBEEF5;
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.comment-user {
  display: flex;
  align-items: center;
  gap: 10px;
}

.comment-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.comment-content {
  line-height: 1.6;
  margin-bottom: 10px;
  white-space: pre-wrap;
}

.reply-form {
  margin: 10px 0 10px 40px;
}

.reply-form-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
}

.replies-list {
  margin-left: 40px;
  margin-top: 10px;
  padding: 10px;
  background-color: #F5F7FA;
  border-radius: 4px;
}

.reply-item {
  padding: 10px 0;
  border-bottom: 1px solid #EBEEF5;
}

.reply-item:last-child {
  border-bottom: none;
}

.reply-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.reply-user {
  display: flex;
  align-items: center;
  gap: 10px;
}

.reply-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.reply-content {
  line-height: 1.6;
  white-space: pre-wrap;
}

.pagination-container {
  text-align: center;
  margin-top: 20px;
}

/* 编辑相关样式 */
.post-title-edit {
  margin-bottom: 15px;
}

.post-content-edit {
  margin-bottom: 20px;
}

.edit-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 15px;
  gap: 10px;
}
</style>

<style>
/* 收藏消息提示样式 */
.favorite-message {
  min-width: 120px;
  padding: 10px 20px;
  border-radius: 4px;
}

.favorite-message.el-message--success {
  background-color: #f0f9eb;
  border-color: #e1f3d8;
}

.favorite-message.el-message--warning {
  background-color: #fdf6ec;
  border-color: #faecd8;
}

.favorite-message .el-message__icon {
  font-size: 16px;
  margin-right: 8px;
}

.favorite-message .el-message__content {
  font-size: 14px;
  color: #606266;
}

/* 图标样式调整 */
.post-stats .el-icon {
  margin-right: 5px;
  vertical-align: middle;
}

.post-meta .el-icon {
  margin-right: 5px;
  vertical-align: middle;
}

.post-actions .el-button .el-icon {
  margin-right: 5px;
  vertical-align: middle;
}
</style>
