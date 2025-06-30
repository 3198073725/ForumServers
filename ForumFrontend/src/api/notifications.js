import request from '@/utils/request';

/**
 * 获取通知列表
 * @param {Object} params - 查询参数
 * @returns {Promise} - 请求Promise
 */
export function getNotifications(params) {
  return request({
    url: '/api/v1/notifications/',
    method: 'get',
    params
  });
}

/**
 * 获取未读通知数量
 * @returns {Promise} - 请求Promise
 */
export function getUnreadCount() {
  return request({
    url: '/api/v1/notifications/unread/count/',
    method: 'get'
  });
}

/**
 * 标记通知为已读
 * @param {number} id - 通知ID
 * @returns {Promise} - 请求Promise
 */
export function markNotificationRead(id) {
  return request({
    url: `/api/v1/notifications/${id}/read/`,
    method: 'put'
  });
}

/**
 * 标记所有通知为已读
 * @returns {Promise} - 请求Promise
 */
export function markAllNotificationsRead() {
  return request({
    url: '/api/v1/notifications/read/all/',
    method: 'put'
  });
}

/**
 * 删除通知
 * @param {number} id - 通知ID
 * @returns {Promise} - 请求Promise
 */
export function deleteNotification(id) {
  return request({
    url: `/api/v1/notifications/${id}/`,
    method: 'delete'
  });
} 