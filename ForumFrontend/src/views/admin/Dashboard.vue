<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <!-- 统计卡片 -->
      <el-col :span="6" v-for="(item, index) in statCards" :key="index">
        <el-card class="stat-card" :body-style="{ padding: '20px' }">
          <div class="stat-icon" :style="{ backgroundColor: item.color }">
            <i :class="item.icon"></i>
          </div>
          <div class="stat-info">
            <div class="stat-title">{{ item.title }}</div>
            <div class="stat-value">{{ item.value }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 最近注册用户 -->
      <el-col :span="12">
        <el-card class="box-card">
          <template #header>
            <div class="clearfix">
            <span>最近注册用户</span>
            <el-button style="float: right; padding: 3px 0" link @click="goToUserManagement">
              查看全部
            </el-button>
            </div>
          </template>
          <div v-if="loading" class="loading-container">
            <el-skeleton :rows="5" animated />
          </div>
          <div v-else>
            <el-table :data="recentUsers" style="width: 100%">
              <el-table-column prop="username" label="用户名" width="120"></el-table-column>
              <el-table-column prop="email" label="邮箱" width="180"></el-table-column>
              <el-table-column prop="created_at" label="注册时间">
                <template #default="scope">
                  {{ formatDate(scope.row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100" align="center">
                <template #default="scope">
                  <el-button size="small" link @click="viewUser(scope.row)">查看</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-col>

      <!-- 最新帖子 -->
      <el-col :span="12">
        <el-card class="box-card">
          <template #header>
            <div class="clearfix">
            <span>最新帖子</span>
            <el-button style="float: right; padding: 3px 0" text @click="goToPostList">
              查看更多
            </el-button>
            </div>
          </template>
          <div v-if="loading" class="loading-container">
            <el-skeleton :rows="5" animated />
          </div>
          <div v-else>
            <el-table :data="recentPosts" style="width: 100%">
              <el-table-column prop="title" label="标题" width="200"></el-table-column>
              <el-table-column prop="user.username" label="作者" width="100"></el-table-column>
              <el-table-column prop="created_at" label="发布时间">
                <template #default="scope">
                  {{ formatDate(scope.row.created_at) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100" align="center">
                <template #default="scope">
                  <el-button size="mini" text @click="viewPost(scope.row)">查看</el-button>
                  <el-button size="mini" type="danger" @click="deletePost(scope.row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 系统信息 -->
      <el-col :span="24">
        <el-card class="box-card">
          <template #header>
            <div class="clearfix">
            <span>系统信息</span>
            </div>
          </template>
          <div v-if="loading" class="loading-container">
            <el-skeleton :rows="5" animated />
          </div>
          <div v-else class="system-info">
            <el-descriptions title="基本信息" :column="3" border>
              <el-descriptions-item label="系统名称">论坛系统</el-descriptions-item>
              <el-descriptions-item label="版本">1.0.0</el-descriptions-item>
              <el-descriptions-item label="运行环境">Vue + Django + MySQL</el-descriptions-item>
              <el-descriptions-item label="数据库">MySQL</el-descriptions-item>
              <el-descriptions-item label="缓存">Redis</el-descriptions-item>
              <el-descriptions-item label="上传限制">10MB</el-descriptions-item>
            </el-descriptions>

            <el-descriptions title="管理员信息" :column="3" border style="margin-top: 20px;">
              <el-descriptions-item label="当前管理员">{{ userInfo?.username }}</el-descriptions-item>
              <el-descriptions-item label="登录时间">{{ formatDate(userInfo?.last_login) }}</el-descriptions-item>
              <el-descriptions-item label="IP地址">127.0.0.1</el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { formatDateTime } from '@/utils/index'

// 格式化日期函数
const formatDate = (date) => {
  return formatDateTime(date)
}

export default {
  name: 'AdminDashboard',
  setup() {
    const router = useRouter()
    const store = useStore()

    const loading = ref(false)

    // 用户信息
    const userInfo = computed(() => store.getters.userInfo)

    // 统计卡片数据
    const statCards = ref([
      {
        title: '用户总数',
        value: 128,
        icon: 'el-icon-user',
        color: '#409EFF'
      },
      {
        title: '帖子总数',
        value: 256,
        icon: 'el-icon-document',
        color: '#67C23A'
      },
      {
        title: '评论总数',
        value: 512,
        icon: 'el-icon-chat-dot-round',
        color: '#E6A23C'
      },
      {
        title: '今日访问',
        value: 64,
        icon: 'el-icon-view',
        color: '#F56C6C'
      }
    ])

    // 最近注册用户
    const recentUsers = ref([
      {
        id: 5,
        username: 'user3',
        email: 'user3@example.com',
        created_at: '2023-05-19T10:30:00Z'
      },
      {
        id: 4,
        username: 'user2',
        email: 'user2@example.com',
        created_at: '2023-05-18T14:20:00Z'
      },
      {
        id: 3,
        username: 'user1',
        email: 'user1@example.com',
        created_at: '2023-05-17T09:15:00Z'
      }
    ])

    // 最新帖子
    const recentPosts = ref([
      {
        id: 5,
        title: '如何使用Vue3的Composition API',
        user: { id: 3, username: 'user1' },
        created_at: '2023-05-19T11:30:00Z'
      },
      {
        id: 4,
        title: 'Django REST Framework最佳实践',
        user: { id: 2, username: 'moderator' },
        created_at: '2023-05-18T16:45:00Z'
      },
      {
        id: 3,
        title: 'MySQL性能优化技巧',
        user: { id: 1, username: 'admin' },
        created_at: '2023-05-17T14:20:00Z'
      }
    ])

    // 获取仪表盘数据
    const fetchDashboardData = async () => {
      loading.value = true
      try {
        // 模拟API调用
        setTimeout(() => {
          loading.value = false
        }, 500)

        // 实际API调用
        // const response = await getDashboardData()
        // if (response.code === 0) {
        //   statCards.value[0].value = response.data.users_count
        //   statCards.value[1].value = response.data.posts_count
        //   statCards.value[2].value = response.data.comments_count
        //   statCards.value[3].value = response.data.today_visits
        //   recentUsers.value = response.data.recent_users
        //   recentPosts.value = response.data.recent_posts
        // } else {
        //   ElMessage.error(response.msg || '获取仪表盘数据失败')
        // }
      } catch (error) {
        console.error('获取仪表盘数据失败:', error)
      } finally {
        loading.value = false
      }
    }

    // 查看用户
    const viewUser = (user) => {
      router.push({ name: 'UserProfile', params: { id: user.id } })
    }

    // 查看帖子
    const viewPost = (post) => {
      router.push({ name: 'PostDetail', params: { id: post.id } })
    }

    // 跳转到用户管理页面
    const goToUserManagement = () => {
      router.push({ name: 'UserManagement' })
    }

    // 跳转到帖子列表页面
    const goToPostList = () => {
      router.push({ name: 'PostList' })
    }

    // 生命周期钩子
    onMounted(() => {
      fetchDashboardData()
    })

    return {
      loading,
      userInfo,
      statCards,
      recentUsers,
      recentPosts,
      formatDate,
      viewUser,
      viewPost,
      goToUserManagement,
      goToPostList
    }
  }
}
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.stat-card {
  height: 120px;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 20px;
}

.stat-icon i {
  font-size: 40px;
  color: white;
}

.stat-info {
  flex: 1;
}

.stat-title {
  font-size: 16px;
  color: #606266;
  margin-bottom: 10px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.loading-container {
  padding: 20px 0;
}

.system-info {
  margin-top: 10px;
}
</style>
