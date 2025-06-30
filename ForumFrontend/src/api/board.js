import request from '@/utils/request'

// 是否启用调试日志
const DEBUG = false;

// 自定义日志函数，可以通过DEBUG开关控制
const log = (...args) => {
  if (DEBUG) {
    console.log(...args);
  }
};

// 获取板块列表
export function getBoardList(params) {
  // 关闭调试日志
  const DEBUG_THIS = false;
  
  if (DEBUG_THIS) console.log(`开始请求板块列表API，参数:`, params);
  
  return request({
    url: '/api/v1/boards/',
    method: 'get',
    params
  }).then(response => {
    if (DEBUG_THIS) console.log(`板块列表API原始响应:`, response);
    
    // 检查响应格式并统一处理
    let formattedResponse = {
      code: 0,
      status: 0,
      msg: '',
      data: []
    };
    
    // 如果响应是Django REST Framework的分页格式
    if (response && response.count !== undefined && Array.isArray(response.results)) {
      if (DEBUG_THIS) console.log('处理Django REST Framework分页格式响应');
      formattedResponse.data = response.results;
      return formattedResponse;
    }
    
    // 如果响应已经是我们期望的格式
    if (response && response.code === 0 && response.data) {
      if (DEBUG_THIS) console.log('响应已经是期望的格式');
      return response;
    }
    
    // 如果响应是直接的数组
    if (Array.isArray(response)) {
      if (DEBUG_THIS) console.log('响应是数组格式');
      formattedResponse.data = response;
      return formattedResponse;
    }
    
    // 如果响应是对象但格式不完全匹配
    if (response && typeof response === 'object') {
      if (DEBUG_THIS) console.log('响应是对象但格式不完全匹配');
      
      // 检查response.data是否存在且为数组
      if (response.data && Array.isArray(response.data)) {
        formattedResponse.data = response.data;
      } 
      // 检查response.results是否存在且为数组
      else if (response.results && Array.isArray(response.results)) {
        formattedResponse.data = response.results;
      }
      // 如果data存在但不是数组，尝试包装它
      else if (response.data) {
        formattedResponse.data = [response.data];
      }
      // 如果都不存在，尝试将整个response作为单个结果
      else {
        formattedResponse.data = [response];
      }
      
      if (DEBUG_THIS) console.log('格式化后的响应:', formattedResponse);
      return formattedResponse;
    }
    
    // 如果无法处理响应，返回空结果
    if (DEBUG_THIS) console.log('无法处理响应，返回空结果');
    return formattedResponse;
  }).catch(error => {
    console.error('获取板块列表失败', error);
    // 返回错误信息
    return {
      code: error?.response?.status || 500,
      status: error?.response?.status || 500,
      message: error?.message || '网络错误，请稍后再试',
      data: []
    };
  });
}

// 获取板块详情
export function getBoardDetail(id) {
  return request({
    url: `/api/v1/boards/${id}/`,
    method: 'get'
  }).catch(error => {
    console.error(`获取板块详情(ID: ${id})失败`, error)
    // 返回错误信息
    return {
      code: error?.response?.status || 500,
      status: error?.response?.status || 500,
      message: error?.message || '网络错误，请稍后再试',
      data: null
    }
  })
}

// 获取热门板块
export function getHotBoards(limit = 5) {
  return request({
    url: '/api/v1/boards/hot/',
    method: 'get',
    params: { limit }
  }).catch(error => {
    console.error('获取热门板块失败', error)
    // 返回错误信息
    return {
      code: error?.response?.status || 500,
      status: error?.response?.status || 500,
      message: error?.message || '网络错误，请稍后再试',
      data: []
    }
  })
}

// 创建板块 (管理员)
export function createBoard(data) {
  return request({
    url: '/api/v1/boards/',
    method: 'post',
    data
  })
}

// 更新板块 (管理员)
export function updateBoard(id, data) {
  return request({
    url: `/api/v1/boards/${id}/`,
    method: 'put',
    data
  })
}

// 删除板块 (管理员)
export function deleteBoard(id) {
  return request({
    url: `/api/v1/boards/${id}/`,
    method: 'delete'
  })
}

// 重新排序板块 (管理员)
export function reorderBoards(data) {
  return request({
    url: '/api/v1/boards/reorder/',
    method: 'post',
    data
  })
}

// 获取所有用户组 (管理员)
export function getGroups() {
  return request({
    url: '/api/v1/boards/groups/',
    method: 'get'
  })
}

// 获取所有用户 (管理员)
export function getUsers() {
  return request({
    url: '/api/v1/boards/users/',
    method: 'get'
  })
}
