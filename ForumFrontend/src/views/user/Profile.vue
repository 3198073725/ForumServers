<template>
  <div class="profile-container">
    <el-row :gutter="20">
      <!-- 左侧用户信息卡片 -->
      <el-col :span="6">
        <el-card class="profile-card">
          <div v-if="loading" class="loading-container">
            <el-skeleton :rows="5" animated />
          </div>
          <div v-else class="user-info">
            <div class="avatar-container">
              <user-avatar :user="userProfile" :size="100" />
            </div>
            <h2 class="username">{{ userProfile.nickname || userProfile.username }}</h2>
            <div class="user-meta">
              <div class="meta-item">
                <el-icon><User /></el-icon>
                <span>{{ userProfile.username }}</span>
              </div>
              <div class="meta-item">
                <el-icon><Message /></el-icon>
                <span>{{ userProfile.email }}</span>
              </div>
              <div class="meta-item">
                <el-icon><Calendar /></el-icon>
                <span>注册于 {{ formatDate(userProfile.created_at) }}</span>
              </div>
              <div class="meta-item">
                <el-icon><Timer /></el-icon>
                <span>最后登录 {{ formatDate(userProfile.last_login) }}</span>
              </div>
            </div>

            <div class="user-stats">
              <div class="stat-item">
                <div class="stat-value">{{ userStats.posts_count || 0 }}</div>
                <div class="stat-label">帖子</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ userStats.comments_count || 0 }}</div>
                <div class="stat-label">评论</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ userStats.favorites_count || 0 }}</div>
                <div class="stat-label">收藏</div>
              </div>
            </div>

            <div v-if="isCurrentUser" class="user-actions">
              <el-button type="primary" @click="showEditProfileDialog">编辑资料</el-button>
              <el-button @click="showChangePasswordDialog" class="user-actions-button">修改密码</el-button>
            </div>
            

          </div>
        </el-card>
      </el-col>

      <!-- 右侧内容区域 -->
      <el-col :span="18">
        <el-card class="content-card">
          <el-tabs v-model="activeTab" @tab-click="handleTabClick">
            <el-tab-pane label="我的帖子" name="posts">
              <div v-if="postsLoading" class="loading-container">
                <el-skeleton :rows="5" animated />
              </div>
              <div v-else-if="posts.length === 0" class="empty-container">
                <el-empty description="暂无帖子" />
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

                <!-- 分页 -->
                <div v-if="posts.length > 0" class="pagination-container">
                  <el-pagination
                    background
                    layout="prev, pager, next"
                    :total="postsTotal"
                    :page-size="postsQuery.limit"
                    :current-page="postsQuery.page"
                    @update:current-page="handlePostsPageChange"
                  >
                  </el-pagination>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="我的评论" name="comments">
              <div v-if="commentsLoading" class="loading-container">
                <el-skeleton :rows="5" animated />
              </div>
              <div v-else-if="comments.length === 0" class="empty-container">
                <el-empty description="暂无评论" />
              </div>
              <div v-else class="comment-list">
                <div
                  v-for="comment in comments"
                  :key="comment.id"
                  class="comment-item"
                >
                  <div class="comment-content">{{ comment.content }}</div>
                  <div class="comment-meta">
                    <div class="comment-post" @click="viewPost({ id: comment.post })">
                      <el-icon><Document /></el-icon>
                      <span>查看原帖</span>
                    </div>
                    <div class="comment-time">{{ formatDate(comment.created_at) }}</div>
                  </div>
                </div>

                <!-- 分页 -->
                <div v-if="comments.length > 0" class="pagination-container">
                  <el-pagination
                    background
                    layout="prev, pager, next"
                    :total="commentsTotal"
                    :page-size="commentsQuery.limit"
                    :current-page="commentsQuery.page"
                    @update:current-page="handleCommentsPageChange"
                  >
                  </el-pagination>
                </div>
              </div>
            </el-tab-pane>

            <el-tab-pane label="我的收藏" name="favorites">
              <div v-if="favoritesLoading" class="loading-container">
                <el-skeleton :rows="5" animated />
              </div>
              <div v-else-if="favorites.length === 0" class="empty-container">
                <el-empty description="暂无收藏" />
              </div>
              <div v-else class="favorite-list">
                <div
                  v-for="favorite in favorites"
                  :key="favorite.id"
                  class="favorite-item"
                  @click="viewPost(favorite.post)"
                >
                  <div class="post-title">
                    <el-tag v-if="favorite.post.is_pinned" size="small" type="danger">置顶</el-tag>
                    <el-tag v-if="favorite.post.is_featured" size="small" type="success">精华</el-tag>
                    <span>{{ favorite.post.title }}</span>
                  </div>
                  <div class="post-meta">
                    <div class="post-author">
                      <el-icon><User /></el-icon>
                      <span>{{ favorite.post.user.nickname || favorite.post.user.username }}</span>
                    </div>
                    <div class="post-board">
                      <el-icon><Grid /></el-icon>
                      <span>{{ favorite.post.board_name }}</span>
                    </div>
                    <div class="post-stats">
                      <span>
                        <el-icon><View /></el-icon>
                        {{ favorite.post.views }}
                      </span>
                      <span>
                        <el-icon><Star /></el-icon>
                        {{ favorite.post.likes_count }}
                      </span>
                      <span>
                        <el-icon><ChatDotRound /></el-icon>
                        {{ favorite.post.comments_count }}
                      </span>
                    </div>
                    <div class="post-time">{{ formatDate(favorite.created_at) }}</div>
                  </div>
                </div>

                <!-- 分页 -->
                <div v-if="favorites.length > 0" class="pagination-container">
                  <el-pagination
                    background
                    layout="prev, pager, next"
                    :total="favoritesTotal"
                    :page-size="favoritesQuery.limit"
                    :current-page="favoritesQuery.page"
                    @update:current-page="handleFavoritesPageChange"
                  >
                  </el-pagination>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>

    <!-- 编辑资料对话框 -->
    <el-dialog
      title="编辑个人资料"
      v-model="editProfileDialogVisible"
      width="500px"
      destroy-on-close
    >
      <div class="simple-form">
        <div class="form-item">
          <label>昵称：</label>
          <input
            type="text"
            v-model="nicknameInput"
            placeholder="请输入昵称"
            class="simple-input"
          >
        </div>

        <div class="form-item">
          <label>头像：</label>
          <div class="avatar-preview">
            <user-avatar :user="{nickname: nicknameInput, username: userProfile.username, avatar_url: avatarUrlInput}" :size="80" />
          </div>
          <div class="upload-options">
            <el-upload
              class="avatar-uploader"
              action="#"
              :http-request="handleAvatarUpload"
              :show-file-list="false"
              :before-upload="beforeAvatarUpload"
            >
              <el-button type="primary" size="small">上传头像</el-button>
            </el-upload>
            <div class="url-input">
              <p class="hint-text">或者直接输入图片URL：</p>
              <input
                type="text"
                v-model="avatarUrlInput"
                placeholder="请输入头像URL"
                class="simple-input"
              >
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editProfileDialogVisible = false">取 消</el-button>
          <el-button type="primary" @click="submitProfileForm" :loading="submitting">确 定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 修改密码对话框 -->
    <el-dialog
      title="修改密码"
      v-model="changePasswordDialogVisible"
      width="500px"
      destroy-on-close
    >
      <form class="simple-form" @submit.prevent="submitPasswordForm">
        <div class="form-item">
          <label>当前密码：</label>
          <input
            type="password"
            v-model="passwordForm.old_password"
            placeholder="请输入当前密码"
            class="simple-input"
            name="old_password"
            autocomplete="current-password"
          >
        </div>
        <div class="form-item">
          <label>新密码：</label>
          <input
            type="password"
            v-model="passwordForm.new_password"
            placeholder="请输入新密码"
            class="simple-input"
            name="new_password"
            autocomplete="new-password"
          >
        </div>
        <div class="form-item">
          <label>确认新密码：</label>
          <input
            type="password"
            v-model="passwordForm.confirm_password"
            placeholder="请再次输入新密码"
            class="simple-input"
            name="confirm_password"
            autocomplete="new-password"
          >
        </div>
      </form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="changePasswordDialogVisible = false">取 消</el-button>
          <el-button type="primary" @click="submitPasswordForm" :loading="submitting">确 定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { computed, onMounted, toRefs, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { ElMessage } from 'element-plus'
import { formatDateTime } from '@/utils/index'
import UserAvatar from '@/components/UserAvatar.vue'
import {
  getUserProfile,
  getUserById,
  updateUserProfile,
  getUserPosts,
  getUserComments,
  getUserFavorites,
  uploadAvatar,
  changePassword
} from '@/api/profile'

// 格式化日期函数
const formatDate = (date) => {
  return formatDateTime(date)
}

export default {
  name: 'UserProfile',
  components: {
    UserAvatar
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const store = useStore()

    // 状态
    const state = reactive({
      loading: false,
      userProfile: {},
      userStats: {
        posts_count: 0,
        comments_count: 0,
        favorites_count: 0
      },
      activeTab: 'posts',

      // 帖子相关
      postsLoading: false,
      posts: [],
      postsTotal: 0,
      postsQuery: {
        page: 1,
        limit: 10
      },

      // 评论相关
      commentsLoading: false,
      comments: [],
      commentsTotal: 0,
      commentsQuery: {
        page: 1,
        limit: 10
      },

      // 收藏相关
      favoritesLoading: false,
      favorites: [],
      favoritesTotal: 0,
      favoritesQuery: {
        page: 1,
        limit: 10
      },

      // 编辑资料相关
      editProfileDialogVisible: false,
      // 使用简单的变量存储表单数据
      nicknameInput: '',
      avatarUrlInput: '',
      // 保留原来的表单对象以兼容其他代码
      profileForm: {
        nickname: '',
        avatar_url: ''
      },
      profileRules: {
        nickname: [
          { max: 50, message: '昵称不能超过50个字符', trigger: 'blur' }
        ]
      },
      uploadHeaders: {
        Authorization: `Bearer ${localStorage.getItem('token')}`
      },
      submitting: false,
      imageUploading: false,

      // 修改密码相关
      changePasswordDialogVisible: false,
      passwordForm: {
        old_password: '',
        new_password: '',
        confirm_password: ''
      },
      passwordRules: {
        old_password: [
          { required: true, message: '请输入当前密码', trigger: 'blur' }
        ],
        new_password: [
          { required: true, message: '请输入新密码', trigger: 'blur' },
          { min: 6, message: '密码长度不能少于6个字符', trigger: 'blur' }
        ],
        confirm_password: [
          { required: true, message: '请再次输入新密码', trigger: 'blur' },
          {
            validator: (rule, value, callback) => {
              if (value !== state.passwordForm.new_password) {
                callback(new Error('两次输入的密码不一致'))
              } else {
                callback()
              }
            },
            trigger: 'blur'
          }
        ]
      }
    })

    // 计算属性
    const userId = computed(() => route.params.id || 'me')
    const isCurrentUser = computed(() => !route.params.id || route.params.id === 'me' || route.params.id === store.getters.userId.toString())

    // 从查询参数中获取激活的标签页
    if (route.query.tab && ['posts', 'comments', 'favorites'].includes(route.query.tab)) {
      state.activeTab = route.query.tab
    }

    // 获取用户信息
    const fetchUserProfile = async () => {
      state.loading = true
      try {
        // 检查本地存储的token
        const token = localStorage.getItem('token')
        console.log('获取用户信息前的token:', token)

        let response
        if (userId.value === 'me' || !userId.value) {
          console.log('获取当前用户信息')
          response = await getUserProfile()
        } else {
          console.log('获取指定用户信息:', userId.value)
          response = await getUserById(userId.value)
        }

        console.log('用户信息响应:', response)

        // 处理不同的响应格式
        if (response.code === 0) {
          state.userProfile = response.data
        } else if (response.id) {
          // 直接返回了用户对象
          state.userProfile = response
        } else {
          ElMessage.error('获取用户信息失败: 响应格式不正确')
          console.error('响应格式不正确:', response)
          return
        }

        // 初始化编辑表单
        if (!state.profileForm) {
          state.profileForm = {
            nickname: state.userProfile.nickname || '',
            avatar_url: state.userProfile.avatar_url || ''
          }
        } else {
          state.profileForm.nickname = state.userProfile.nickname || ''
          state.profileForm.avatar_url = state.userProfile.avatar_url || ''
        }
      } catch (error) {
        console.error('获取用户信息失败:', error)
        ElMessage.error('获取用户信息失败')
      } finally {
        state.loading = false
      }
    }

    // 获取用户帖子
    const fetchUserPosts = async () => {
      state.postsLoading = true
      try {
        // 检查本地存储的token
        const token = localStorage.getItem('token')
        console.log('获取用户帖子前的token:', token)

        const response = await getUserPosts(userId.value)
        console.log('用户帖子响应:', response)

        // 处理不同的响应格式
        if (response.code === 0 && response.data) {
          // 标准格式响应
          state.posts = response.data.results || []
          state.postsTotal = response.data.count || 0
          state.userStats.posts_count = response.data.count || 0
        } else if (response.results) {
          // DRF分页响应格式
          state.posts = response.results || []
          state.postsTotal = response.count || 0
          state.userStats.posts_count = response.count || 0
        } else if (Array.isArray(response)) {
          // 直接返回数组
          state.posts = response
          state.postsTotal = response.length
          state.userStats.posts_count = response.length
        } else {
          // 其他格式
          console.error('响应格式不正确:', response)
          ElMessage.error('获取用户帖子失败: 响应格式不正确')
          return
        }
      } catch (error) {
        console.error('获取用户帖子失败:', error)
        ElMessage.error('获取用户帖子失败')
      } finally {
        state.postsLoading = false
      }
    }

    // 获取用户评论
    const fetchUserComments = async () => {
      state.commentsLoading = true
      try {
        console.log('开始获取用户评论，用户ID:', userId.value)
        const response = await getUserComments(userId.value)
        console.log('用户评论响应:', response)

        // 处理不同的响应格式
        if (response.code === 0 && response.data) {
          // 标准格式响应
          console.log('标准格式响应，评论数据:', response.data)
          state.comments = response.data.results || []
          state.commentsTotal = response.data.count || 0
          state.userStats.comments_count = response.data.count || 0
        } else if (response.results) {
          // DRF分页响应格式
          console.log('DRF分页响应格式，评论数据:', response.results)
          state.comments = response.results || []
          state.commentsTotal = response.count || 0
          state.userStats.comments_count = response.count || 0
        } else if (Array.isArray(response)) {
          // 直接返回数组
          console.log('直接返回数组格式，评论数据:', response)
          state.comments = response
          state.commentsTotal = response.length
          state.userStats.comments_count = response.length
        } else {
          // 其他格式
          console.error('响应格式不正确:', response)
          ElMessage.error('获取用户评论失败: 响应格式不正确')
          return
        }
        
        // 打印获取到的评论数据
        console.log('最终获取到的评论数据:', state.comments)
        console.log('评论总数:', state.commentsTotal)
      } catch (error) {
        console.error('获取用户评论失败:', error)
        ElMessage.error('获取用户评论失败')
      } finally {
        state.commentsLoading = false
      }
    }

    // 获取用户收藏
    const fetchUserFavorites = async () => {
      state.favoritesLoading = true
      try {
        const response = await getUserFavorites(userId.value)
        console.log('用户收藏响应:', response)

        // 处理不同的响应格式
        if (response.code === 0 && response.data) {
          // 标准格式响应
          state.favorites = response.data.results || []
          state.favoritesTotal = response.data.count || 0
          state.userStats.favorites_count = response.data.count || 0
        } else if (response.results) {
          // DRF分页响应格式
          state.favorites = response.results || []
          state.favoritesTotal = response.count || 0
          state.userStats.favorites_count = response.count || 0
        } else if (Array.isArray(response)) {
          // 直接返回数组
          state.favorites = response
          state.favoritesTotal = response.length
          state.userStats.favorites_count = response.length
        } else {
          // 其他格式
          console.error('响应格式不正确:', response)
          ElMessage.error('获取用户收藏失败: 响应格式不正确')
          return
        }
      } catch (error) {
        console.error('获取用户收藏失败:', error)
        ElMessage.error('获取用户收藏失败')
      } finally {
        state.favoritesLoading = false
      }
    }

    // 处理标签页切换
    const handleTabClick = (tab) => {
      state.activeTab = tab.name

      if (tab.name === 'posts' && state.posts.length === 0) {
        fetchUserPosts()
      } else if (tab.name === 'comments' && state.comments.length === 0) {
        fetchUserComments()
      } else if (tab.name === 'favorites' && state.favorites.length === 0) {
        fetchUserFavorites()
      }
    }

    // 处理帖子分页变化
    const handlePostsPageChange = (page) => {
      console.log('帖子分页变化:', page)
      state.postsQuery.page = page
      fetchUserPosts()
    }

    // 处理评论分页变化
    const handleCommentsPageChange = (page) => {
      console.log('评论分页变化:', page)
      state.commentsQuery.page = page
      fetchUserComments()
    }

    // 处理收藏分页变化
    const handleFavoritesPageChange = (page) => {
      console.log('收藏分页变化:', page)
      state.favoritesQuery.page = page
      fetchUserFavorites()
    }

    // 查看帖子
    const viewPost = (post) => {
      router.push({ name: 'PostDetail', params: { id: post.id } })
    }

    // 显示编辑资料对话框
    const showEditProfileDialog = () => {
      try {
        console.log('点击编辑资料按钮')

        // 设置输入框的初始值
        state.nicknameInput = state.userProfile?.nickname || ''
        state.avatarUrlInput = state.userProfile?.avatar_url || ''

        // 同时也设置原来的表单对象，以兼容其他代码
        state.profileForm.nickname = state.userProfile?.nickname || ''
        state.profileForm.avatar_url = state.userProfile?.avatar_url || ''

        console.log('设置表单数据:', {
          nicknameInput: state.nicknameInput,
          avatarUrlInput: state.avatarUrlInput
        })

        // 更新上传头部以确保使用最新的token
        state.uploadHeaders = {
          Authorization: `Bearer ${localStorage.getItem('token')}`
        }

        // 显示对话框
        state.editProfileDialogVisible = true
      } catch (error) {
        console.error('显示编辑资料对话框出错:', error)
        ElMessage.error('显示编辑资料对话框出错')
      }
    }

    // 头像上传前的验证
    const beforeAvatarUpload = (file) => {
      state.imageUploading = true
      const isImage = file.type.startsWith('image/')
      const isLt2M = file.size / 1024 / 1024 < 2

      if (!isImage) {
        ElMessage.error('头像必须是图片格式!')
        state.imageUploading = false
        return false
      }
      if (!isLt2M) {
        ElMessage.error('头像大小不能超过 2MB!')
        state.imageUploading = false
        return false
      }
      return true
    }

    // 处理头像上传
    const handleAvatarUpload = async (options) => {
      const { file } = options
      state.imageUploading = true

      try {
        console.log('开始上传头像，文件信息:', {
          name: file.name,
          type: file.type,
          size: file.size
        })

        // 创建FormData
        const formData = new FormData()
        formData.append('file', file)

        // 检查token
        const token = localStorage.getItem('token')
        console.log('上传头像前的token:', token)

        // 调用上传API
        console.log('调用上传API，URL:', '/api/v1/users/profile/me/avatar/')
        const response = await uploadAvatar(formData)
        console.log('头像上传响应:', response)

        if (response.status === 0 || response.code === 0) {
          // 更新两个地方的头像地址
          const avatarUrl = response.data?.avatar_url || ''
          console.log('获取到的头像URL:', avatarUrl)
          state.avatarUrlInput = avatarUrl
          state.profileForm.avatar_url = avatarUrl

          // 立即更新用户信息中的头像
          // 确保头像 URL 是完整的
          const fullAvatarUrl = avatarUrl.startsWith('http') ? avatarUrl : `http://localhost:8000${avatarUrl}`
          console.log('完整的头像 URL:', fullAvatarUrl)
          state.userProfile.avatar_url = fullAvatarUrl

          // 更新Vuex中的用户信息
          store.dispatch('updateUserInfo', {
            ...store.getters.userInfo,
            avatar_url: fullAvatarUrl
          })

          // 自动保存用户资料
          // 注意：保存到后端的头像 URL 应该保持原样，不需要完整路径
          updateUserProfile({
            nickname: state.nicknameInput || state.userProfile.nickname || '',
            avatar_url: avatarUrl  // 使用原始的相对路径
          }).then(response => {
            console.log('自动保存用户资料响应:', response)
          }).catch(error => {
            console.error('自动保存用户资料失败:', error)
          })

          ElMessage.success('头像上传成功')
        } else {
          console.error('头像上传失败，响应:', response)
          ElMessage.error(response.msg || '头像上传失败')
        }
      } catch (error) {
        console.error('头像上传失败:', error)
        // 显示更详细的错误信息
        if (error.response) {
          console.error('错误响应:', error.response)
          ElMessage.error(`头像上传失败: ${error.response.status} ${error.response.statusText}`)
        } else if (error.request) {
          console.error('请求未收到响应:', error.request)
          ElMessage.error('头像上传失败: 服务器未响应')
        } else {
          console.error('请求配置错误:', error.message)
          ElMessage.error(`头像上传失败: ${error.message}`)
        }
      } finally {
        state.imageUploading = false
      }
    }

    // 提交编辑资料表单
    const submitProfileForm = async () => {
      try {
        console.log('提交编辑资料表单')
        console.log('表单数据:', {
          nicknameInput: state.nicknameInput,
          avatarUrlInput: state.avatarUrlInput
        })

        state.submitting = true

        // 准备要提交的数据
        const formData = {
          nickname: state.nicknameInput || '',
          avatar_url: state.avatarUrlInput || ''
        }

        try {
          // 先关闭对话框，避免用户等待
          state.editProfileDialogVisible = false

          const response = await updateUserProfile(formData)
          console.log('更新用户资料响应:', response)

          // 刷新用户信息，以确保显示最新数据
          await fetchUserProfile()

          // 更新Vuex中的用户信息
          store.dispatch('updateUserInfo', {
            ...store.getters.userInfo,
            nickname: formData.nickname,
            avatar_url: formData.avatar_url
          })

          // 显示成功消息
          ElMessage.success('个人资料更新成功')
        } catch (apiError) {
          console.error('调用API更新用户资料失败:', apiError)

          // 尝试刷新用户信息，查看是否实际更新成功
          await fetchUserProfile()

          // 显示错误消息
          ElMessage.error('个人资料更新失败，请刷新页面查看最新状态')
        }
      } catch (error) {
        console.error('个人资料更新失败:', error)
        ElMessage.error('个人资料更新失败')
        // 关闭对话框
        state.editProfileDialogVisible = false
      } finally {
        state.submitting = false
      }
    }

    // 显示修改密码对话框
    const showChangePasswordDialog = () => {
      state.changePasswordDialogVisible = true
      state.passwordForm = {
        old_password: '',
        new_password: '',
        confirm_password: ''
      }
    }

    // 提交修改密码表单
    const submitPasswordForm = async () => {
      try {
        console.log('提交修改密码表单')

        // 确保表单数据存在
        if (!state.passwordForm) {
          ElMessage.error('密码表单数据不存在')
          return
        }

        // 验证密码
        if (!state.passwordForm.old_password) {
          ElMessage.error('请输入当前密码')
          return
        }

        if (!state.passwordForm.new_password) {
          ElMessage.error('请输入新密码')
          return
        }

        if (state.passwordForm.new_password !== state.passwordForm.confirm_password) {
          ElMessage.error('两次输入的密码不一致')
          return
        }

        // 密码长度验证
        if (state.passwordForm.new_password.length < 6) {
          ElMessage.error('新密码长度不能少于6个字符')
          return
        }

        state.submitting = true

        // 准备请求数据
        const requestData = {
          old_password: state.passwordForm.old_password,
          new_password: state.passwordForm.new_password,
          confirm_password: state.passwordForm.confirm_password
        }

        console.log('发送修改密码请求:', requestData)

        // 使用导入的changePassword函数发送请求
        // 这样可以确保使用与其他API请求相同的配置
        const response = await changePassword(requestData)

        console.log('修改密码响应:', response)

        if (response.code === 0 || response.status === 0) {
          ElMessage.success(response.msg || '密码修改成功，请重新登录')
          state.changePasswordDialogVisible = false

          // 退出登录
          store.dispatch('logout')
          router.push('/login')
        } else {
          // 处理错误信息
          console.error('密码修改失败，错误信息:', response.msg)

          // 如果错误信息是对象，提取具体错误信息
          if (typeof response.msg === 'object') {
            const errorMessages = []

            // 遍历错误对象的所有字段
            for (const field in response.msg) {
              const errors = response.msg[field]
              if (Array.isArray(errors)) {
                // 如果是数组，添加每个错误信息
                errors.forEach(error => {
                  errorMessages.push(`${field}: ${error}`)
                })
              } else if (typeof errors === 'string') {
                // 如果是字符串，直接添加
                errorMessages.push(`${field}: ${errors}`)
              }
            }

            // 显示所有错误信息
            if (errorMessages.length > 0) {
              ElMessage.error(errorMessages.join('\n'))
            } else {
              ElMessage.error('密码修改失败，请检查输入')
            }
          } else {
            // 如果错误信息是字符串，直接显示
            ElMessage.error(response.msg || '密码修改失败')
          }
        }
      } catch (error) {
        console.error('密码修改失败:', error)

        // 显示详细的错误信息
        if (error.response && error.response.data) {
          const responseData = error.response.data

          // 如果错误信息是对象，提取具体错误信息
          if (responseData && typeof responseData.msg === 'object') {
            const errorMessages = []

            // 遍历错误对象的所有字段
            for (const field in responseData.msg) {
              const errors = responseData.msg[field]
              if (Array.isArray(errors)) {
                // 如果是数组，添加每个错误信息
                errors.forEach(err => {
                  errorMessages.push(`${field}: ${err}`)
                })
              } else if (typeof errors === 'string') {
                // 如果是字符串，直接添加
                errorMessages.push(`${field}: ${errors}`)
              }
            }

            // 显示所有错误信息
            if (errorMessages.length > 0) {
              ElMessage.error(errorMessages.join('\n'))
            } else {
              ElMessage.error('密码修改失败，请检查输入')
            }
          } else {
            // 如果错误信息是字符串或未定义，显示默认消息
            ElMessage.error((responseData.msg) || '密码修改失败')
          }
        } else if (error.message) {
          ElMessage.error(`密码修改失败: ${error.message}`)
        } else {
          ElMessage.error('密码修改失败，请检查网络连接')
        }
      } finally {
        state.submitting = false
      }
    }

    // 组件挂载后执行
    onMounted(async () => {
      console.log('Profile组件挂载，开始获取用户信息')
      await fetchUserProfile()

      // 根据激活的标签页加载数据
      console.log('当前激活的标签页:', state.activeTab)
      if (state.activeTab === 'posts') {
        console.log('开始获取用户帖子')
        await fetchUserPosts()
      } else if (state.activeTab === 'comments') {
        console.log('开始获取用户评论')
        await fetchUserComments()
      } else if (state.activeTab === 'favorites') {
        console.log('开始获取用户收藏')
        await fetchUserFavorites()
      }

      // 无论当前标签页是什么，都预加载评论数据
      if (state.activeTab !== 'comments') {
        console.log('预加载用户评论数据')
        fetchUserComments()
      }
    })

    return {
      ...toRefs(state),
      userId,
      isCurrentUser,
      formatDate,
      handleTabClick,
      handlePostsPageChange,
      handleCommentsPageChange,
      handleFavoritesPageChange,
      viewPost,
      showEditProfileDialog,
      // handleNicknameInput 已移除
      beforeAvatarUpload,
      handleAvatarUpload,
      submitProfileForm,
      showChangePasswordDialog,
      submitPasswordForm
    }
  }
}
</script>

<style scoped>
.profile-container {
  padding: 20px;
}

.loading-container {
  padding: 20px 0;
}

.profile-card,
.content-card {
  margin-bottom: 20px;
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.avatar-container {
  margin-bottom: 15px;
}

.username {
  margin: 0 0 15px;
  font-size: 20px;
}

.user-meta {
  width: 100%;
  margin-bottom: 20px;
}

.meta-item {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  color: #606266;
}

.meta-item i {
  margin-right: 8px;
  width: 16px;
  text-align: center;
}

.user-stats {
  display: flex;
  justify-content: space-around;
  width: 100%;
  margin-bottom: 20px;
  padding: 15px 0;
  border-top: 1px solid #ebeef5;
  border-bottom: 1px solid #ebeef5;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  font-size: 14px;
  color: #606266;
}

.user-actions {
  display: flex;
  flex-direction: column;
  width: 100%;
  gap: 10px;
}

.empty-container {
  padding: 40px 0;
}

.post-list,
.comment-list,
.favorite-list {
  margin-bottom: 20px;
}

.post-item,
.favorite-item {
  padding: 15px;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
  transition: background-color 0.3s;
}

.post-item:hover,
.favorite-item:hover {
  background-color: #f5f7fa;
}

.post-item:last-child,
.favorite-item:last-child {
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

.post-board i,
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

.comment-item {
  padding: 15px;
  border-bottom: 1px solid #ebeef5;
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-content {
  margin-bottom: 10px;
  line-height: 1.5;
  white-space: pre-wrap;
}

.comment-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: #909399;
}

.comment-post {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #409eff;
}

.comment-post i {
  margin-right: 5px;
}

.pagination-container {
  text-align: center;
  margin-top: 20px;
}

.avatar-upload-container {
  display: flex;
  align-items: flex-start;
  margin-bottom: 15px;
}

.avatar-preview {
  margin-right: 20px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.upload-options {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.avatar-uploader {
  margin-bottom: 15px;
}

.url-input {
  margin-top: 10px;
}

.hint-text {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}

.debug-info {
  font-size: 12px;
  color: #409EFF;
  margin-top: 5px;
  padding: 5px;
  background-color: #f0f9ff;
  border-radius: 4px;
}

.simple-form {
  padding: 10px;
}

.form-item {
  margin-bottom: 20px;
}

.form-item label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
}

.simple-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.simple-input:focus {
  outline: none;
  border-color: #409EFF;
}
.user-actions-button{
  margin-left:0;
}
</style>
