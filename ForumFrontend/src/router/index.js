import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'

// 是否启用调试日志
const DEBUG = false;

// 自定义日志函数，可以通过DEBUG开关控制
const log = (...args) => {
  if (DEBUG) {
    console.log(...args);
  }
};

// 路由懒加载
const Home = () => import('../views/Home.vue')
const Login = () => import('../views/Login.vue')
const Register = () => import('../views/Register.vue')
// 不再需要单独的邮箱验证注册页面
const ResetPassword = () => import('../views/ResetPassword.vue')
const NotFound = () => import('../views/NotFound.vue')

// 板块相关页面
const BoardList = () => import('../views/board/BoardList.vue')
const BoardDetail = () => import('../views/board/BoardDetail.vue')

// 帖子相关页面
const PostList = () => import('../views/post/PostList.vue')
const PostDetail = () => import('../views/post/PostDetail.vue')
const PostCreate = () => import('../views/post/PostCreate.vue')

// 用户中心相关页面
const UserProfile = () => import('../views/user/Profile.vue')


// 管理员相关页面
const AdminDashboard = () => import('../views/admin/Dashboard.vue')
const UserManagement = () => import('../views/admin/UserManagement.vue')

// 新增页面
const Ranking = () => import('../views/Ranking.vue')
const Complaints = () => import('../views/Complaints.vue')

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: {
      title: '首页 - 论坛系统'
    }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: {
      title: '登录 - 论坛系统'
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: {
      title: '注册 - 论坛系统'
    }
  },
  // 移除单独的邮箱验证注册路由，直接使用主注册页面
  {
    path: '/reset-password',
    name: 'ResetPassword',
    component: ResetPassword,
    meta: {
      title: '重置密码 - 论坛系统'
    }
  },
  // 板块相关路由
  {
    path: '/boards',
    name: 'BoardList',
    component: BoardList,
    meta: {
      title: '板块列表 - 论坛系统'
    }
  },
  {
    path: '/boards/:id',
    name: 'BoardDetail',
    component: BoardDetail,
    meta: {
      title: '板块详情 - 论坛系统'
    }
  },
  // 帖子相关路由
  {
    path: '/posts',
    name: 'PostList',
    component: PostList,
    meta: {
      title: '帖子列表 - 论坛系统'
    }
  },
  {
    path: '/posts/:id',
    name: 'PostDetail',
    component: PostDetail,
    meta: {
      title: '帖子详情 - 论坛系统'
    }
  },
  {
    path: '/post/create',
    name: 'PostCreate',
    component: PostCreate,
    meta: {
      title: '发布帖子 - 论坛系统',
      requiresAuth: true
    }
  },
  {
    path: '/post/edit/:id',
    name: 'PostEdit',
    component: PostCreate,
    meta: {
      title: '编辑帖子 - 论坛系统',
      requiresAuth: true
    }
  },
  // 用户中心相关路由
  {
    path: '/profile/:id',
    name: 'UserProfile',
    component: UserProfile,
    meta: {
      title: '用户中心 - 论坛系统'
    }
  },

  // 管理员相关路由
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: {
      title: '管理员仪表盘 - 论坛系统',
      requiresAuth: true,
      requiresAdmin: true
    }
  },
  {
    path: '/admin/users',
    name: 'UserManagement',
    component: UserManagement,
    meta: {
      title: '用户管理 - 论坛系统',
      requiresAuth: true,
      requiresAdmin: true
    }
  },
  // 新增路由
  {
    path: '/ranking',
    name: 'Ranking',
    component: Ranking,
    meta: {
      title: '排行榜 - 论坛系统'
    }
  },
  {
    path: '/complaints',
    name: 'Complaints',
    component: Complaints,
    meta: {
      title: '投诉中心 - 论坛系统'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: {
      title: '页面未找到 - 论坛系统'
    }
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// 全局前置守卫，设置页面标题和权限检查
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title || '论坛系统'

  // 检查是否需要登录
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin)
  const token = localStorage.getItem('token')

  // 安全地解析userInfo
  let userInfo = null
  try {
    const userInfoStr = localStorage.getItem('userInfo')
    if (userInfoStr) {
      userInfo = JSON.parse(userInfoStr)
    }
  } catch (error) {
    console.error('解析userInfo失败:', error)
    localStorage.removeItem('userInfo') // 清除无效的userInfo
  }

  log('路由检查:', {
    path: to.path,
    requiresAuth,
    requiresAdmin,
    hasToken: !!token,
    userInfo
  })

  if (requiresAuth && !token) {
    // 需要登录但未登录
    log('需要登录权限，跳转到登录页')
    // 将当前路径保存到查询参数中，登录成功后可以跳回
    next({
      path: '/login',
      query: { redirect: to.fullPath }
    })
  } else if (requiresAdmin && (!userInfo || userInfo.role !== 'admin')) {
    // 需要管理员权限但不是管理员
    log('需要管理员权限，跳转到首页')
    next({ path: '/' })
  } else {
    next()
  }
})

// 全局后置守卫，在路由跳转完成后执行
router.afterEach((to) => {
  // 如果跳转到发帖页面，清除所有消息
  if (to.name === 'PostCreate' || to.name === 'PostEdit') {
    // 使用导入的 ElMessage 清除所有消息
    log('路由跳转到发帖页面，清除所有消息')
    ElMessage.closeAll()

    // 添加延时清除，确保异步请求完成后也不会显示消息
    setTimeout(() => {
      log('延时清除消息')
      ElMessage.closeAll()
    }, 100)
  }
})

export default router
