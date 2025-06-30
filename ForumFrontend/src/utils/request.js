import axios from 'axios'
import router from '../router'
import { ElMessage } from 'element-plus'

// 是否启用调试日志
const DEBUG = false;

// 自定义日志函数，可以通过DEBUG开关控制
const log = (...args) => {
  if (DEBUG) {
    console.log(...args);
  }
};

// 增强的消息去重机制
const messageTracker = {
  lastMessage: '',
  lastTime: 0,
  messageQueue: [],
  showMessage(message, type, source = 'unknown') {
    const now = Date.now();
    const messageInfo = { message, type, time: now, source };
    
    log(`消息触发 [${source}]: ${message} (${type})`, messageInfo);
    
    // 如果相同消息在3秒内出现，则不重复显示
    if (message === this.lastMessage && now - this.lastTime < 3000) {
      log(`消息被去重: ${message} (上次显示时间: ${new Date(this.lastTime).toLocaleTimeString()})`);
      return;
    }
    
    // 清理过期的消息
    this.messageQueue = this.messageQueue.filter(msg => now - msg.time < 5000);
    
    // 检查队列中是否已有相同消息
    const duplicate = this.messageQueue.find(msg => msg.message === message);
    if (duplicate) {
      log(`队列中已存在相同消息: ${message} (来源: ${duplicate.source})`);
      return;
    }
    
    // 添加到消息队列
    this.messageQueue.push(messageInfo);
    this.lastMessage = message;
    this.lastTime = now;
    
    log(`显示消息: ${message}`);
    ElMessage.closeAll(); // 关闭所有现有消息
    ElMessage({
      message: message,
      type: type,
      duration: type === 'error' ? 5 * 1000 : 3000,
      onClose: () => {
        // 从队列中移除
        this.messageQueue = this.messageQueue.filter(msg => msg.message !== message);
      }
    });
  }
};

// 全局挂载消息追踪器，用于其他组件直接使用
window.messageTracker = messageTracker;

// 创建自定义消息显示函数，替代直接调用ElMessage
const showSafeMessage = (options) => {
  if (typeof options === 'string') {
    messageTracker.showMessage(options, 'info', 'safe-message');
  } else {
    messageTracker.showMessage(
      options.message, 
      options.type || 'info', 
      'safe-message-' + (options.type || 'info')
    );
  }
};

// 全局暴露，方便其他组件使用
window.showSafeMessage = showSafeMessage;

// 创建axios实例
const service = axios.create({
  baseURL: process.env.NODE_ENV === 'development' ? 'http://localhost:8000' : '',
  timeout: 15000, // 增加超时时间到15秒
  // 添加validateStatus选项，允许所有状态码通过，不抛出请求错误
  validateStatus: function (status) {
    return status < 600 // 所有HTTP状态码都作为成功处理，包括500错误
  }
})

// 请求拦截器
service.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    
    // 设置Authorization头
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }

    // 设置Content-Type头（如果没有设置）
    if (config.method === 'post' || config.method === 'put' || config.method === 'patch') {
      if (!config.headers['Content-Type'] && !(config.data instanceof FormData)) {
        config.headers['Content-Type'] = 'application/json'
      }
    }

    return config
  },
  error => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 辅助函数：判断是否为登出操作
function isLogoutOperation(config) {
  if (!config || !config.url || !config.method) {
    return false
  }
  
  const isPostMethod = config.method.toLowerCase() === 'post'
  const isLogoutUrl = config.url.includes('/api/v1/auth/logout/')
  
  log('请求拦截器检测登出操作:', {
    url: config.url,
    method: config.method,
    isLogoutUrl,
    isPostMethod,
    isLogout: isLogoutUrl && isPostMethod
  })
  
  return isLogoutUrl && isPostMethod
}

// 辅助函数：判断是否为公开内容请求（无需登录即可访问）
function isPublicContentRequest(config) {
  // 防止config为undefined
  if (!config || !config.url || !config.method) {
    log('无法判断是否为公开内容请求，配置不完整:', config)
    // 默认返回true，对于无法判断的请求，视为公开内容
    return true
  }
  
  // 默认所有GET请求都视为公开内容
  const isGetMethod = config.method.toLowerCase() === 'get'
  
  // 如果是GET请求，直接返回true，允许所有GET请求不需要登录
  if (isGetMethod) {
    log('请求拦截器: GET请求被视为公开内容', config.url);
    return true;
  }
  
  // 扩展公开URL匹配
  const isPostsUrl = config.url.includes('/api/v1/posts') 
  const isBoardsUrl = config.url.includes('/api/v1/boards')
  const isRankingUrl = config.url.includes('/api/v1/ranking')
  const isCommentsUrl = config.url.includes('/api/v1/comments')
  const isHomeUrl = config.url === '/' || config.url.endsWith('/index.html')
  const isProfileUrl = config.url.includes('/api/v1/users/profile')
  const isStaticUrl = config.url.includes('/static/') || config.url.includes('/media/')
  
  // 所有GET请求 + 特定POST请求路径 = 公开内容请求
  return isGetMethod || (
    (isPostsUrl || isBoardsUrl || isRankingUrl || 
    isCommentsUrl || isHomeUrl || isProfileUrl || isStaticUrl)
  )
}

// 响应拦截器
service.interceptors.response.use(
  response => {
    // 检查是否为HTML错误页面（Django错误页面）
    if (response.data && typeof response.data === 'string' && 
        (response.data.includes('<!DOCTYPE html>') || 
         response.data.includes('ContentNotRenderedError'))) {
      console.error('响应拦截器检测到HTML错误页面:', {
        url: response.config.url,
        method: response.config.method,
        status: response.status
      });
      
      // 提取错误信息
      let errorMessage = '服务器错误';
      if (response.data.includes('ContentNotRenderedError')) {
        errorMessage = 'Django序列化错误: ContentNotRenderedError';
        console.error('检测到Django ContentNotRenderedError，这通常是由于响应内容未正确渲染导致的');
      }
      
      // 对于公开内容请求，不显示错误消息
      const isPublic = isPublicContentRequest(response.config);
      if (!isPublic) {
        messageTracker.showMessage(errorMessage, 'error', 'html-error-page');
      } else {
        log('公开内容请求收到HTML错误页面，不显示错误消息');
      }
      
      // 返回一个标准格式的错误响应，让调用方处理
      return {
        code: 500,
        status: 500,
        msg: errorMessage,
        data: null
      };
    }
    
    // 处理空响应
    if (!response.data && response.status !== 204) {
      log('API返回空响应:', {
        url: response.config.url,
        method: response.config.method,
        status: response.status
      });
      
      return {
        code: 0,
        status: 0,
        msg: '',
        data: null
      };
    }
    
    // 处理非JSON响应
    if (response.data && typeof response.data === 'string' && response.headers['content-type'] && 
        !response.headers['content-type'].includes('application/json')) {
      log('非JSON响应:', {
        url: response.config.url,
        contentType: response.headers['content-type'],
        status: response.status
      });
      
      // 返回一个包装好的响应
      return {
        code: 0,
        status: response.status,
        msg: '',
        data: response.data
      };
    }
    
    const res = response.data
    log('响应拦截器收到响应:', res)
    
    // 检查是否为帖子创建请求
    const isCreatePost = response.config.url === '/api/v1/posts/' && 
                        response.config.method.toLowerCase() === 'post';
    if (isCreatePost) {
      log('检测到帖子创建请求，响应数据:', res);
      // 如果响应成功但没有返回帖子ID，尝试从响应中提取
      if ((res.status === 0 || res.code === 0) && res.data) {
        if (typeof res.data === 'object' && !res.data.id) {
          // 尝试从响应中提取帖子ID
          const postId = res.data.post_id || res.data.postId || res.post_id || res.postId;
          if (postId) {
            res.data.id = postId;
          }
        }
      }
    }
    
    // 检查是否为公开内容请求
    const isPublic = isPublicContentRequest(response.config);
    log('是否为公开内容请求:', isPublic);
    
    // 检查是否有明确的错误状态
    if ((res.status !== undefined && res.status !== 0 && res.status !== 200) || 
        (res.code !== undefined && res.code !== 0 && res.code !== 200)) {
      console.error('API错误响应:', res)
      
      // 401错误特殊处理 - 对于公开内容请求，不显示错误消息
      if ((res.status === 401 || res.code === 401) && isPublic) {
        log('公开内容401错误，不显示错误消息')
        // 直接返回一个成功的空数据，让调用方继续处理
        return {
          code: 0,
          status: 0,
          msg: '',
          data: null
        }
      }
      
      // 如果是登出操作，即使返回错误也不显示错误消息
      if (isLogoutOperation(response.config)) {
        log('登出操作返回错误，不显示错误消息')
        return res
      }

      // 如果不应该抑制消息，则显示错误消息
      if (!shouldSuppressMessage(response.config)) {
        const errorMsg = res.msg || res.message || '请求失败'
        messageTracker.showMessage(errorMsg, 'error', 'api-error')
      }
      
      return res
    }
    
    // 检查是否为删除评论操作
    if (isCommentDeleteOperation(response.config)) {
      log('检测到评论删除操作，不显示成功消息')
      return res
    }
    
    // 检查是否为帖子操作
    if (isPostOperation(response.config)) {
      log('检测到帖子操作，不显示成功消息')
      return res
    }
    
    // 如果有成功消息且不是GET请求，显示成功消息
    if (res.msg && response.config.method.toLowerCase() !== 'get' && !isPublic) {
      messageTracker.showMessage(res.msg, 'success', 'api-success')
    }
    
    return res
  },
  error => {
    console.error('请求错误:', error)
    
    // 如果请求被取消，不显示错误消息
    if (axios.isCancel(error)) {
      log('请求被取消')
      return Promise.reject(error)
    }

    // 检查是否为公开内容请求
    const isPublic = error.config ? isPublicContentRequest(error.config) : false
    
    // 如果不是公开内容请求，显示错误消息
    if (!isPublic && !shouldSuppressMessage(error.config)) {
      let errorMsg = '网络错误，请检查您的网络连接'
      
    if (error.response) {
        // 服务器返回了错误状态码
        switch (error.response.status) {
          case 401:
            errorMsg = '未授权，请重新登录'
            // 清除token和用户信息
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
        // 跳转到登录页
        router.push('/login')
            break
          case 403:
            errorMsg = '拒绝访问'
            break
          case 404:
            errorMsg = '请求的资源不存在'
            break
          case 500:
            errorMsg = '服务器错误'
            break
          default:
            errorMsg = `请求失败 (${error.response.status})`
      }
    } else if (error.request) {
        // 请求已发出，但没有收到响应
        errorMsg = '服务器无响应，请稍后重试'
      }
      
      messageTracker.showMessage(errorMsg, 'error', 'axios-error')
    }

    // 返回标准格式的错误对象
      return {
      code: -1,
      status: error.response ? error.response.status : 500,
      msg: error.message || '未知错误',
      data: null
    }
  }
)

// 辅助函数：判断是否应该抑制消息
function shouldSuppressMessage(config) {
  if (!config) return false
  
  // 检查是否有自定义标记
  return config.suppressErrorMessage === true || 
         (config.headers && config.headers['X-Suppress-Message'] === 'true')
}

// 辅助函数：判断是否为删除评论操作
function isCommentDeleteOperation(config) {
  if (!config || !config.url || !config.method) {
    return false
  }
  
  const isDeleteMethod = config.method.toLowerCase() === 'delete'
  const isCommentUrl = config.url.includes('/api/v1/comments/')
  
  return isDeleteMethod && isCommentUrl
}

// 辅助函数：判断是否为帖子操作
function isPostOperation(config) {
  if (!config || !config.url || !config.method) {
    return false
  }
  
  const isPostMethod = config.method.toLowerCase() === 'post'
  const isPutMethod = config.method.toLowerCase() === 'put'
  const isPostUrl = config.url.includes('/api/v1/posts')
  
  return (isPostMethod || isPutMethod) && isPostUrl
}

export default service
