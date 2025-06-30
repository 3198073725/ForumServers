import { createStore } from 'vuex'
import axios from '@/utils/request'
import notificationsModule from './modules/notifications'

import usersModule from './modules/users'

export default createStore({
  state: {
    token: localStorage.getItem('token') || '',
    user: JSON.parse(localStorage.getItem('userInfo') || '{}')
  },
  getters: {
    isLoggedIn: state => !!state.token,
    isAdmin: state => state.user && state.user.role === 'admin',
    isModerator: state => state.user && (state.user.role === 'moderator' || state.user.role === 'admin'),
    userId: state => state.user ? state.user.id : null,
    username: state => state.user ? state.user.username : '',
    userAvatar: state => state.user && state.user.avatar_url ? state.user.avatar_url : '',
    userRole: state => state.user ? state.user.role : '',
    currentUser: state => state.user
  },
  mutations: {
    // 用户认证相关
    setToken(state, token) {
      state.token = token;
      localStorage.setItem('token', token);
    },
    setUser(state, user) {
      state.user = user;
      localStorage.setItem('userInfo', JSON.stringify(user));
    },
    logout(state) {
      state.token = '';
      state.user = {};
      localStorage.removeItem('token');
      localStorage.removeItem('userInfo');
    }
  },
  actions: {
    // 用户认证相关
    login({ commit }, { token, userInfo }) {
      console.log('登录动作被调用，token:', token, '用户信息:', userInfo);
      commit('setToken', token);
      commit('setUser', userInfo);
      return userInfo;
    },
    async getUserInfo({ commit, state }) {
      try {
        if (!state.token) return null;
        const response = await axios.get('/api/v1/users/me/');
        if (response && response.data) {
          commit('setUser', response.data);
          return response.data;
        }
        return null;
      } catch (error) {
        console.error('获取用户信息失败:', error);
        return null;
      }
    },
    logout({ commit }) {
      commit('logout');
    }
  },
  modules: {
    notifications: notificationsModule,
    users: usersModule
  }
})
