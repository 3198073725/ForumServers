import request from '@/utils/request'

// 是否启用调试日志
const DEBUG = false;

// 自定义日志函数，可以通过DEBUG开关控制
const log = (...args) => {
  if (DEBUG) {
    console.log(...args);
  }
};

// 获取帖子列表
export function getPostList(params) {
  // 关闭调试日志
  const DEBUG_THIS = false;
  
  if (DEBUG_THIS) console.log(`开始请求帖子列表API，参数:`, params);
  
  return request({
    url: '/api/v1/posts/',
    method: 'get',
    params
  }).then(response => {
    if (DEBUG_THIS) console.log(`帖子列表API原始响应:`, response);
    
    // 处理从PowerShell Invoke-RestMethod返回的特殊格式
    if (response && response.data && response.data.results) {
      if (DEBUG_THIS) console.log('检测到PowerShell Invoke-RestMethod格式的响应');
      return {
        code: 0,
        status: 0,
        data: {
          results: response.data.results,
          count: response.data.count || response.data.results.length
        }
      };
    }
    
    // 检查响应格式并统一处理
    let formattedResponse = {
      code: 0,
      status: 0,
      msg: '',
      data: null
    };
    
    // 如果响应是Django REST Framework的分页格式
    if (response && response.count !== undefined && Array.isArray(response.results)) {
      if (DEBUG_THIS) console.log('处理Django REST Framework分页格式响应');
      formattedResponse.data = {
        results: response.results,
        count: response.count,
        next: response.next,
        previous: response.previous
      };
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
      formattedResponse.data = {
        results: response,
        count: response.length
      };
      return formattedResponse;
    }
    
    // 如果响应是对象但格式不完全匹配
    if (response && typeof response === 'object') {
      if (DEBUG_THIS) console.log('响应是对象但格式不完全匹配', response);
      
      // 检查response.data是否存在
      if (response.data) {
        // 如果response.data是数组
        if (Array.isArray(response.data)) {
          formattedResponse.data = {
            results: response.data,
            count: response.data.length
          };
        } 
        // 如果response.data是对象，并且有results字段
        else if (typeof response.data === 'object' && response.data.results) {
          formattedResponse.data = {
            results: response.data.results,
            count: response.data.count || response.data.results.length
          };
        }
        // 其他情况，尝试使用response.data作为结果
        else {
          formattedResponse.data = {
            results: [response.data],
            count: 1
          };
        }
      } 
      // 检查response.results是否存在
      else if (response.results) {
        formattedResponse.data = {
          results: response.results,
          count: response.count || response.results.length
        };
      }
      // 如果都不存在，尝试将整个response作为单个结果
      else {
      formattedResponse.data = {
          results: [response],
          count: 1
      };
      }
      
      if (DEBUG_THIS) console.log('格式化后的响应:', formattedResponse);
      return formattedResponse;
    }
    
    // 如果无法处理响应，返回空结果
    if (DEBUG_THIS) console.log('无法处理响应，返回空结果');
    formattedResponse.data = {
      results: [],
      count: 0
    };
    return formattedResponse;
  }).catch(error => {
    console.error('获取帖子列表失败:', error);
    // 返回一个有效的响应格式，避免错误传播
    return {
      code: error?.response?.status || 500,
      status: error?.response?.status || 500,
      message: error?.message || '网络错误，请稍后再试',
      data: {
        results: [],
        count: 0
      }
    };
  });
}

// 获取帖子详情
export function getPostDetail(id) {
  log(`开始请求帖子详情API，ID: ${id}`);
  
  // 创建临时帖子数据，用于后端API失败时显示
  const tempPost = {
    id: id || 1,
    title: "后端API暂时不可用 - 临时显示内容",
    content: `<p>这是临时生成的帖子内容，因为后端API返回了错误。</p>
              <p>请联系管理员检查服务器日志，查看ContentNotRenderedError错误。</p>
              <p>这可能是Django序列化响应时出现的问题。</p>`,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    views: 0,
    likes_count: 0,
    comments_count: 0,
    is_pinned: false,
    is_featured: false,
    board: { id: 1, name: '系统通知' },
    user: {
      id: 0,
      username: 'system',
      nickname: '系统通知',
      avatar_url: ''
    }
  };
  
  return request({
    url: `/api/v1/posts/${id}/`,
    method: 'get'
  }).then(response => {
    log(`帖子详情API响应成功:`, response);
    
    // 检查响应是否包含HTML错误页面（表示服务器500错误）
    if (response && typeof response.data === 'string' && 
        (response.data.includes('<!DOCTYPE html>') || response.data.includes('Error'))) {
      console.error('服务器返回了HTML错误页面，显示临时数据');
      return {
        code: 500,
        status: 500,
        message: '服务器错误，请稍后再试',
        data: tempPost
      };
    }
    
    // 如果响应成功且有数据，直接返回
    if (response && response.data && 
        (typeof response.data === 'object' && Object.keys(response.data).length > 0)) {
      return {
        code: 0,
        status: 0,
        data: response.data
      };
    } else if (response && typeof response === 'object' && 
               Object.keys(response).length > 0 && 
               !response.data) {
      // 如果响应本身就是数据对象
      return {
        code: 0,
        status: 0,
        data: response
      };
    }
    
    // 如果响应不成功或没有数据，返回临时数据
    log('帖子详情API返回异常或空数据，显示临时数据');
    return {
      code: 404,
      status: 404,
      message: '未找到帖子，显示临时内容',
      data: tempPost
    };
  }).catch(error => {
    console.error(`获取帖子详情(ID: ${id})失败，显示临时数据`, error);
    // 返回临时数据
    return {
      code: error?.response?.status || 500,
      status: error?.response?.status || 500,
      message: error?.message || '网络错误，请稍后再试',
      data: tempPost
    };
  });
}

// 创建帖子
export function createPost(data) {
  return request({
    url: '/api/v1/posts/',
    method: 'post',
    data
  })
}

// 更新帖子
export function updatePost(id, data) {
  return request({
    url: `/api/v1/posts/${id}/`,
    method: 'put',
    data
  }).then(response => {
    // 检查响应状态
    if (response.code === 0 || response.status === 0) {
      // 成功响应，直接返回
      return response;
    }
    // 如果响应不成功，抛出错误
    throw new Error(response.msg || '操作失败');
  }).catch(error => {
    // 如果是网络错误或服务器错误
    if (error.response) {
      // 服务器返回了错误状态码
      throw new Error(error.response.data?.msg || '操作失败，请稍后重试');
    } else if (error.request) {
      // 请求发出但没有收到响应
      throw new Error('网络连接失败，请检查网络');
    } else {
      // 其他错误
      throw error;
    }
  });
}

// 删除帖子
export function deletePost(id) {
  return request({
    url: `/api/v1/posts/${id}/`,
    method: 'delete'
  })
}

// 获取点赞状态
export function getLikeStatus(id) {
  return request({
    url: `/api/v1/posts/${id}/like_status/`,
    method: 'get'
  });
}

// 获取收藏状态
export function getFavoriteStatus(id) {
  return request({
    url: `/api/v1/posts/${id}/favorite_status/`,
    method: 'get'
  });
}

// 点赞/取消点赞帖子
export function likePost(id) {
  return request({
    url: `/api/v1/posts/${id}/like/`,
    method: 'post'
  }).then(response => {
    // 检查响应状态
    if (response.code === 0 || response.status === 0) {
      // 成功响应，直接返回
      return response;
    }
    // 如果响应不成功，抛出错误
    throw new Error(response.msg || '操作失败');
  }).catch(error => {
    // 如果是网络错误或服务器错误
    if (error.response) {
      // 服务器返回了错误状态码
      throw new Error(error.response.data?.msg || '操作失败，请稍后重试');
    } else if (error.request) {
      // 请求发出但没有收到响应
      throw new Error('网络连接失败，请检查网络');
    } else {
      // 其他错误
      throw error;
    }
  });
}

// 收藏/取消收藏帖子
export function favoritePost(id) {
  // 启用调试日志，查看收藏功能问题
  const DEBUG_THIS = true;
  
  if (DEBUG_THIS) console.log(`开始请求收藏/取消收藏API，帖子ID: ${id}`);
  
  return request({
    url: `/api/v1/posts/${id}/favorite/`,
    method: 'post'
  }).then(response => {
    if (DEBUG_THIS) console.log(`收藏/取消收藏API响应:`, response);
    
    // 检查响应状态
    if (response.code === 0 || response.status === 0) {
      // 成功响应，直接返回
      if (DEBUG_THIS) console.log(`收藏/取消收藏操作成功，状态:`, response.data?.is_favorited);
      return response;
    }
    
    // 如果响应不成功，抛出错误
    console.error('收藏/取消收藏操作失败:', response);
    throw new Error(response.msg || '操作失败');
  }).catch(error => {
    console.error(`收藏/取消收藏操作出错 (帖子ID: ${id}):`, error);
    
    // 如果是网络错误或服务器错误
    if (error.response) {
      // 服务器返回了错误状态码
      throw new Error(error.response.data?.msg || '操作失败，请稍后重试');
    } else if (error.request) {
      // 请求发出但没有收到响应
      throw new Error('网络连接失败，请检查网络');
    } else {
      // 其他错误
      throw error;
    }
  });
}

// 置顶/取消置顶帖子 (管理员)
export function pinPost(id) {
  return request({
    url: `/api/v1/posts/${id}/pin/`,
    method: 'put'
  })
}

// 加精/取消加精帖子 (管理员)
export function featurePost(id) {
  return request({
    url: `/api/v1/posts/${id}/feature/`,
    method: 'put'
  })
}

// 获取用户收藏的帖子列表
export function getUserFavorites() {
  return request({
    url: '/api/v1/posts/favorites/',
    method: 'get'
  })
}

// 获取帖子评论
export function getPostComments(postId) {
  log(`开始请求帖子评论API，帖子ID: ${postId}`);

  // 创建临时评论数据，用于后端API失败时显示
  const tempComments = [
    {
      id: 1,
      content: "这是临时生成的评论内容，因为后端API返回了错误。请联系管理员检查服务器日志。",
      created_at: new Date().toISOString(),
      user: {
        id: 0,
        username: 'system',
        nickname: '系统通知',
        avatar_url: ''
      },
      replies: []
    }
  ];

  return request({
    url: `/api/v1/posts/${postId}/comments/`,
    method: 'get'
  }).then(response => {
    log(`帖子评论API响应成功:`, response);
    
    // 检查响应是否包含HTML错误页面（表示服务器500错误）
    if (response && typeof response.data === 'string' && 
        (response.data.includes('<!DOCTYPE html>') || response.data.includes('Error'))) {
      console.error('服务器返回了HTML错误页面，显示临时数据');
      return {
        code: 500,
        status: 500,
        message: '服务器错误，请稍后再试',
        data: tempComments
      };
    }
    
    // 如果响应成功且有数据，直接返回
    if (response && response.data && 
        (Array.isArray(response.data) || 
         (typeof response.data === 'object' && response.data.results))) {
      // 处理不同格式的响应
      const comments = Array.isArray(response.data) ? 
        response.data : 
        (response.data.results || []);
        
      return {
        code: 0,
        status: 0,
        data: comments
      };
    } else if (response && typeof response === 'object' && 
               Array.isArray(response)) {
      // 如果响应本身就是数组
      return {
        code: 0,
        status: 0,
        data: response
      };
    }
    
    // 如果响应不成功或没有数据，返回临时数据
    log('帖子评论API返回异常或空数据，显示临时数据');
    return {
      code: 404,
      status: 404,
      message: '未找到评论，显示临时内容',
      data: tempComments
    };
  }).catch(error => {
    console.error(`获取帖子评论(帖子ID: ${postId})失败，显示临时数据`, error);
    // 返回临时数据
    return {
      code: error?.response?.status || 500,
      status: error?.response?.status || 500,
      message: error?.message || '网络错误，请稍后再试',
      data: tempComments
    };
  });
}
