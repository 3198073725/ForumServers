import request from '@/utils/request'

// 获取用户资料
export function getUserProfile(userId) {
  return request({
    url: `/api/v1/users/profile/${userId}/`,
    method: 'get'
  }).then(response => {
    // 确保返回的数据格式一致
    if (response.data && response.status === 0) {
      return response.data;
    }
    return response;
  });
}

// 获取当前用户信息
export function getCurrentUser() {
  return request({
    url: '/api/v1/users/me/',
    method: 'get'
  });
}

// 更新用户资料
export function updateUserProfile(data) {
  return request({
    url: '/api/v1/users/profile/update/',
    method: 'put',
    data
  });
}

// 更新用户头像
export function updateUserAvatar(formData) {
  return request({
    url: '/api/v1/users/profile/avatar/',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
} 