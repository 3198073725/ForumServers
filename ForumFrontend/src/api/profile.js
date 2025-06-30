import request from '@/utils/request'

// 获取当前用户信息
export function getUserProfile() {
  return request({
    url: '/api/v1/users/profile/me/',
    method: 'get'
  })
}

// 获取指定用户信息
export function getUserById(id) {
  return request({
    url: `/api/v1/users/profile/${id}/`,
    method: 'get'
  })
}

// 获取热门用户
export function getHotUsers(limit = 5) {
  return request({
    url: '/api/v1/users/profile/hot/',
    method: 'get',
    params: { limit }
  })
}

// 更新用户信息
export function updateUserProfile(data) {
  return request({
    url: '/api/v1/users/profile/me/',
    method: 'put',
    data
  })
}

// 获取用户发布的帖子
export function getUserPosts(userId = 'me') {
  return request({
    url: `/api/v1/users/profile/${userId}/posts/`,
    method: 'get'
  })
}

// 获取用户的评论
export function getUserComments(userId = 'me') {
  return request({
    url: `/api/v1/users/profile/${userId}/comments/`,
    method: 'get'
  })
}

// 获取用户收藏的帖子
export function getUserFavorites(userId = 'me') {
  return request({
    url: `/api/v1/users/profile/${userId}/favorites/`,
    method: 'get'
  })
}

// 修改密码
export function changePassword(data) {
  return request({
    url: '/api/v1/users/me/password/',
    method: 'put',
    data
  })
}

// 上传头像
export function uploadAvatar(formData) {
  return request({
    url: '/api/v1/users/profile/me/avatar/',
    method: 'post',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
