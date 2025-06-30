<template>
  <div class="notification-bell">
    <el-badge :value="unreadCount" :max="99" :hidden="unreadCount <= 0" class="notification-badge">
      <el-dropdown trigger="click" @command="handleCommand">
        <el-button class="bell-button" :icon="Bell" circle />
        <template #dropdown>
          <el-dropdown-menu class="notification-dropdown">
            <div class="notification-header">
              <h3>通知</h3>
              <el-button v-if="hasUnread" text @click="markAllAsRead">全部已读</el-button>
            </div>
            <el-divider />
            <div v-if="loading" class="notification-loading">
              <el-icon class="is-loading"><Loading /></el-icon>
              <span>加载中...</span>
            </div>
            <template v-else>
              <div v-if="notifications.length === 0" class="no-notification">
                暂无通知
              </div>
              <template v-else>
                <el-dropdown-item 
                  v-for="notification in notifications.slice(0, 5)" 
                  :key="notification.id"
                  :class="{ 'notification-unread': !notification.is_read }"
                  :command="{ type: 'view', id: notification.id }"
                >
                  <div class="notification-item">
                    <div class="notification-title">
                      {{ notification.title || '系统通知' }}
                      <span v-if="!notification.is_read" class="unread-dot"></span>
                    </div>
                    <div class="notification-content">{{ notification.content || '' }}</div>
                    <div class="notification-time">{{ formatTime(notification.created_at) }}</div>
                  </div>
                </el-dropdown-item>
                <el-divider v-if="notifications.length > 5" />
                <el-dropdown-item v-if="notifications.length > 5" command="viewAll">
                  <div class="view-all">查看全部</div>
                </el-dropdown-item>
              </template>
            </template>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </el-badge>
  </div>
</template>

<script>
import { computed, onMounted, ref } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import { Bell, Loading } from '@element-plus/icons-vue'
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
  name: 'NotificationBell',
  components: {
    Loading
  },
  setup() {
    const store = useStore()
    const router = useRouter()
    const loading = ref(false)
    
    // 从Vuex获取通知数据，添加初始化空数组保证安全
    const notifications = computed(() => {
      const notificationsModule = store.state.notifications;
      if (!notificationsModule) {
        if (DEBUG) console.warn('通知模块未注册到Vuex store中');
        return [];
      }
      return notificationsModule.notifications || [];
    })
    
    const unreadCount = computed(() => {
      const notificationsModule = store.state.notifications;
      if (!notificationsModule) {
        return 0;
      }
      return notificationsModule.unreadCount || 0;
    })
    
    const hasUnread = computed(() => unreadCount.value > 0)
    
    // 初始化时获取通知
    onMounted(async () => {
      if (store.getters.isLoggedIn) {
        loading.value = true
        try {
          // 检查store中是否有notifications模块
          if (store.state.notifications) {
            await store.dispatch('notifications/fetchNotifications')
          } else {
            if (DEBUG) console.warn('通知模块未注册到Vuex store中')
          }
        } catch (error) {
          console.error('获取通知失败:', error)
          // 只在非网络错误时显示错误消息
          if (error.message !== 'Network Error') {
            ElMessage.error('获取通知失败')
          }
        } finally {
          loading.value = false
        }
      }
    })
    
    // 处理下拉菜单命令
    const handleCommand = (command) => {
      if (command === 'viewAll') {
        router.push('/notifications')
      } else if (command && command.type === 'view' && command.id) {
        // 标记为已读
        store.dispatch('notifications/markAsRead', command.id)
        
        // 根据通知类型跳转到不同页面
        const notification = notifications.value.find(n => n.id === command.id)
        if (notification) {
          navigateByNotification(notification)
        }
      }
    }
    
    // 根据通知类型导航
    const navigateByNotification = (notification) => {
      if (!notification) {
        router.push('/notifications');
        return;
      }
      
      if (notification.target_type === 'post' && notification.target_id) {
        router.push(`/posts/${notification.target_id}`)
      } else if (notification.target_type === 'comment' && notification.target_id) {
        // 评论通知可能需要先获取评论所属的帖子ID
        router.push(`/comments/${notification.target_id}`)
      } else {
        // 默认跳转到通知列表页
        router.push('/notifications')
      }
    }
    
    // 标记所有通知为已读
    const markAllAsRead = (event) => {
      if (event) {
        event.stopPropagation()
      }
      store.dispatch('notifications/markAllAsRead')
    }
    
    // 格式化时间
    const formatTime = (timestamp) => {
      if (!timestamp) {
        return '未知时间';
      }
      
      try {
        const date = new Date(timestamp)
        const now = new Date()
        const diff = now - date
        
        // 检查日期是否有效
        if (isNaN(date.getTime())) {
          return '未知时间';
        }
        
        // 小于1分钟
        if (diff < 60000) {
          return '刚刚'
        }
        // 小于1小时
        else if (diff < 3600000) {
          return `${Math.floor(diff / 60000)}分钟前`
        }
        // 小于24小时
        else if (diff < 86400000) {
          return `${Math.floor(diff / 3600000)}小时前`
        }
        // 小于30天
        else if (diff < 2592000000) {
          return `${Math.floor(diff / 86400000)}天前`
        }
        // 其他情况显示完整日期
        else {
          return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
        }
      } catch (error) {
        console.error('时间格式化错误:', error);
        return '未知时间';
      }
    }
    
    return {
      Bell,
      Loading,
      loading,
      notifications,
      unreadCount,
      hasUnread,
      handleCommand,
      markAllAsRead,
      formatTime
    }
  }
}
</script>

<style scoped>
.notification-bell {
  display: inline-block;
}

.notification-badge {
  margin-right: 10px;
}

.bell-button {
  font-size: 18px;
  padding: 8px;
}

.notification-dropdown {
  width: 320px;
  max-height: 400px;
  overflow-y: auto;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  font-weight: bold;
}

.notification-loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100px;
}

.notification-loading span {
  margin-left: 10px;
}

.no-notification {
  text-align: center;
  color: #909399;
  padding: 20px 0;
}

.notification-item {
  padding: 5px 0;
}

.notification-title {
  font-weight: bold;
  margin-bottom: 5px;
  display: flex;
  justify-content: space-between;
}

.notification-content {
  color: #606266;
  font-size: 13px;
  margin-bottom: 5px;
  white-space: normal;
  word-break: break-all;
  line-height: 1.4;
}

.notification-time {
  color: #909399;
  font-size: 12px;
  text-align: right;
}

.notification-unread {
  background-color: #f0f9ff;
}

.unread-dot {
  width: 8px;
  height: 8px;
  background-color: #409eff;
  border-radius: 50%;
  display: inline-block;
  margin-left: 5px;
}

.view-all {
  text-align: center;
  color: #409eff;
}
</style> 