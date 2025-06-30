import { getUserProfile } from '@/api/users';
import { DEFAULT_AVATAR } from '@/constants/default-avatar';

const state = {
  userCache: new Map() // 用户信息缓存
};

const getters = {
  getUserById: (state) => (userId) => {
    return state.userCache.get(userId);
  }
};

const mutations = {
  setUserInfo(state, { userId, userInfo }) {
    state.userCache.set(userId, userInfo);
  }
};

const actions = {
  async fetchUserInfo({ commit, state }, userId) {
    // 如果缓存中已有用户信息，直接返回
    if (state.userCache.has(userId)) {
      return state.userCache.get(userId);
    }

    try {
      const response = await getUserProfile(userId);
      // 确保response有正确的数据结构
      const userInfo = response.data || response;
      
      // 设置默认头像
      if (!userInfo.avatar_url) {
        userInfo.avatar_url = DEFAULT_AVATAR;
      }
      
      // 设置默认昵称
      if (!userInfo.nickname) {
        userInfo.nickname = userInfo.username;
      }
      
      commit('setUserInfo', { userId, userInfo });
      return userInfo;
    } catch (error) {
      console.error('获取用户信息失败:', error);
      // 返回一个默认的用户信息对象
      const defaultUserInfo = {
        id: userId,
        username: `用户${userId}`,
        nickname: `用户${userId}`,
        avatar_url: DEFAULT_AVATAR,
        email: ''
      };
      commit('setUserInfo', { userId, userInfo: defaultUserInfo });
      return defaultUserInfo;
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