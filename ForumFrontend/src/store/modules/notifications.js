import { getNotifications, markNotificationRead, markAllNotificationsRead } from '@/api/notifications';

const state = {
  notifications: [],
  unreadCount: 0,
  loading: false,
  hasMore: true,
  currentPage: 1,
  pageSize: 10
};

const getters = {
  allNotifications: state => state.notifications,
  unreadNotifications: state => state.notifications.filter(n => !n.is_read),
  hasUnreadNotifications: state => state.unreadCount > 0
};

const mutations = {
  setNotifications(state, notifications) {
    state.notifications = notifications;
  },
  
  addNotification(state, notification) {
    // 避免重复添加
    const exists = state.notifications.some(n => n.id === notification.id);
    if (!exists) {
      state.notifications.unshift(notification);
    }
  },
  
  setUnreadCount(state, count) {
    state.unreadCount = count;
  },
  
  incrementUnreadCount(state) {
    state.unreadCount++;
  },
  
  markAsRead(state, notificationId) {
    const notification = state.notifications.find(n => n.id === notificationId);
    if (notification && !notification.is_read) {
      notification.is_read = true;
      state.unreadCount = Math.max(0, state.unreadCount - 1);
    }
  },
  
  markAllAsRead(state) {
    state.notifications.forEach(notification => {
      notification.is_read = true;
    });
    state.unreadCount = 0;
  },
  
  setLoading(state, status) {
    state.loading = status;
  },
  
  setHasMore(state, status) {
    state.hasMore = status;
  },
  
  setCurrentPage(state, page) {
    state.currentPage = page;
  }
};

const actions = {
  async fetchNotifications({ commit, state }) {
    commit('setLoading', true);
    try {
      const response = await getNotifications({
        page: state.currentPage,
        page_size: state.pageSize
      });
      
      // 检查响应格式
      if (!response) {
        console.warn('通知API返回空响应');
        commit('setNotifications', []);
        commit('setUnreadCount', 0);
        return;
      }
      
      // 兼容不同的响应格式
      let data = null;
      
      if (response.data !== undefined) {
        // 标准格式: { data: {...} }
        data = response.data;
      } else if (response.results !== undefined || Array.isArray(response)) {
        // 直接返回结果数组或带results的对象
        data = response;
      } else {
        console.warn('通知API响应格式不符合预期:', response);
        data = { results: [], count: 0 };
      }
      
      // 提取结果数组和计数
      let results = [];
      let count = 0;
      
      if (Array.isArray(data)) {
        // 如果直接是数组
        results = data;
        count = data.filter(item => !item.is_read).length;
      } else if (data.results !== undefined) {
        // 标准分页格式
        results = Array.isArray(data.results) ? data.results : [];
        count = data.count !== undefined ? data.count : results.length;
      } else if (data.notifications !== undefined) {
        // 某些API可能用notifications字段
        results = Array.isArray(data.notifications) ? data.notifications : [];
        count = data.unread_count !== undefined ? data.unread_count : 
               results.filter(item => !item.is_read).length;
      }
      
      if (state.currentPage === 1) {
        commit('setNotifications', results);
      } else {
        // 合并通知列表，避免重复
        const newNotifications = [...state.notifications];
        results.forEach(notification => {
          if (!newNotifications.some(n => n.id === notification.id)) {
            newNotifications.push(notification);
          }
        });
        commit('setNotifications', newNotifications);
      }
      
      // 更新分页信息
      commit('setHasMore', results.length > 0 && state.currentPage * state.pageSize < count);
      commit('setUnreadCount', count);
    } catch (error) {
      console.error('获取通知失败:', error);
      // 如果是网络错误，设置合适的状态
      commit('setNotifications', []);
      commit('setUnreadCount', 0);
      commit('setHasMore', false);
    } finally {
      commit('setLoading', false);
    }
  },
  
  async loadMoreNotifications({ commit, state }) {
    if (!state.hasMore || state.loading) return;
    
    commit('setCurrentPage', state.currentPage + 1);
    await this.dispatch('notifications/fetchNotifications');
  },
  
  async markAsRead({ commit }, notificationId) {
    try {
      const response = await markNotificationRead(notificationId);
      // 兼容不同的响应格式
      if (response) {
        commit('markAsRead', notificationId);
      }
    } catch (error) {
      console.error('标记通知已读失败:', error);
      // 如果是网络错误，可以选择乐观更新
      if (error.message === 'Network Error') {
        commit('markAsRead', notificationId);
      }
    }
  },
  
  async markAllAsRead({ commit }) {
    try {
      const response = await markAllNotificationsRead();
      // 兼容不同的响应格式
      if (response) {
        commit('markAllAsRead');
      }
    } catch (error) {
      console.error('标记所有通知已读失败:', error);
      // 如果是网络错误，可以选择乐观更新
      if (error.message === 'Network Error') {
        commit('markAllAsRead');
      }
    }
  }
};

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}; 