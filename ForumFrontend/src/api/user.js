import request from '../utils/request'

// 用户登录
export function login(data) {
  return request({
    url: '/api/v1/auth/login/',
    method: 'post',
    data
  })
}

// 用户注册
export function register(data) {
  return request({
    url: '/api/v1/auth/register/',
    method: 'post',
    data
  })
}

// 用户登出
export function logout() {
  return request({
    url: '/api/v1/auth/logout/',
    method: 'post'
  })
}

// 获取当前用户信息
export function getUserInfo() {
  return request({
    url: '/api/v1/users/me/',
    method: 'get'
  })
}

// 修改用户信息
export function updateUserInfo(data) {
  return request({
    url: '/api/v1/users/me/',
    method: 'put',
    data
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

// 请求重置密码 (旧版本)
export function requestPasswordReset(data) {
  return request({
    url: '/api/v1/auth/password/reset/',
    method: 'post',
    data
  })
}

// 确认重置密码 (旧版本)
export function confirmPasswordReset(data) {
  return request({
    url: '/api/v1/auth/password/reset/confirm/',
    method: 'post',
    data
  })
}

// 发送验证码
export function sendVerificationCode(data) {
  return request({
    url: '/api/v1/auth/verification/send/',
    method: 'post',
    data
  })
}

// 验证验证码
export function verifyEmail(data) {
  return request({
    url: '/api/v1/auth/verification/verify/',
    method: 'post',
    data
  })
}

// 带验证码的注册
export function registerWithVerification(data) {
  return request({
    url: '/api/v1/auth/register/with-verification/',
    method: 'post',
    data
  })
}

// 带验证码的密码重置
export function resetPassword(data) {
  return request({
    url: '/api/v1/auth/password/reset/with-verification/',
    method: 'post',
    data
  })
}
