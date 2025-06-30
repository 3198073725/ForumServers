import request from '@/utils/request'

// 是否启用调试日志
const DEBUG = false;

// 自定义日志函数，可以通过DEBUG开关控制
const log = (...args) => {
  if (DEBUG) {
    console.log(...args);
  }
};

// 获取评论列表
export function getCommentList(params) {
  return request({
    url: '/api/v1/comments/',
    method: 'get',
    params
  })
}

// 获取帖子的评论列表
export function getPostComments(postId, forceRefresh = false) {
  // 添加时间戳参数，避免浏览器缓存
  const timestamp = forceRefresh ? `&_t=${new Date().getTime()}` : ''
  log(`开始请求帖子评论API，ID: ${postId}, 强制刷新: ${forceRefresh}`);
  
  return request({
    url: `/api/v1/comments/?post=${postId}${timestamp}`,
    method: 'get'
  }).then(response => {
    log(`帖子评论API响应成功:`, response);
    
    // 如果响应成功且有数据，直接返回
    if (response && ((response.code === 0 || response.status === 0) && response.data)) {
      return response;
    }
    
    // 如果响应本身就是数据对象或数组
    if (response && (Array.isArray(response) || 
                    (response.results && Array.isArray(response.results)))) {
      return {
        code: 0,
        status: 0,
        data: response
      };
    }
    
    // 如果响应不成功或没有数据，返回空数组
    log('帖子评论API返回异常或空数据，返回空数组');
    return {
      code: 0,
      status: 0,
      data: {
        results: [],
        count: 0
      }
    };
  }).catch(error => {
    log(`获取帖子评论列表(ID: ${postId})失败`, error)
    // 返回空数据
    return {
      code: 0,
      status: 0,
      data: {
        results: [],
        count: 0
      }
    }
  })
}

// 获取评论详情
export function getCommentDetail(id) {
  return request({
    url: `/api/v1/comments/${id}/`,
    method: 'get'
  })
}

// 创建评论
export function createComment(data) {
  return request({
    url: '/api/v1/comments/',
    method: 'post',
    data
  })
}

// 回复评论
export function replyComment(postId, parentId, content) {
  return request({
    url: '/api/v1/comments/',
    method: 'post',
    data: {
      post: postId,
      parent: parentId,
      content
    }
  })
}

// 更新评论
export function updateComment(id, data) {
  return request({
    url: `/api/v1/comments/${id}/`,
    method: 'put',
    data
  })
}

// 删除评论
export function deleteComment(id) {
  log(`准备删除评论，ID: ${id}`)
  return request({
    url: `/api/v1/comments/${id}/`,
    method: 'delete'
  }).then(response => {
    log(`删除评论API响应:`, response)
    return response
  }).catch(error => {
    log(`删除评论API错误:`, error)
    throw error
  })
}
