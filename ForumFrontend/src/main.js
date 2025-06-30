// 在最开始设置 Quill 的默认配置
if (typeof window !== 'undefined') {
  window.Quill = window.Quill || {};
  window.Quill.DEFAULTS = window.Quill.DEFAULTS || {};
  window.Quill.DEFAULTS.experimental = {
    useModernScrollingApi: true,
    useMutationObserver: true
  };
}

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import service from './utils/request'
import BackButton from './components/BackButton.vue'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import { initQuill } from './utils/quill-config'

// 导入Element Plus图标
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 是否启用调试日志
const DEBUG = false;

// 自定义日志函数，可以通过DEBUG开关控制
const log = (...args) => {
  if (DEBUG) {
    console.log(...args);
  }
};

// 全局挂载日志函数
if (typeof window !== 'undefined') {
  window.appLog = log;
}

// 在导入Quill之前设置警告拦截器
/**
 * 控制台警告过滤器
 * 
 * 这个过滤器用于减少控制台输出，过滤掉以下类型的警告：
 * 1. Quill编辑器相关的DOMNodeInserted弃用警告
 * 2. Vue组件渲染时的属性访问警告
 * 3. Element Plus的按钮type="text"弃用警告
 * 4. 浏览器的Intervention警告
 * 5. 其他常见的非关键警告
 * 
 * 这样可以保持控制台的整洁，只显示真正需要关注的警告信息
 */
const originalWarn = console.warn;
console.warn = function(msg, ...args) {
  // 如果是对象，转换为字符串以便进行过滤
  let msgStr = msg;
  if (typeof msg === 'object') {
    try {
      msgStr = JSON.stringify(msg);
    } catch (e) {
      msgStr = String(msg);
    }
  }

  // 过滤掉不需要的警告
  if (msg && (
      // Quill相关警告
      (typeof msgStr === 'string' && (
        msgStr.includes('DOMNodeInserted') || 
        msgStr.includes('Listener added for a') ||
        msgStr.includes('mutation event') ||
        msgStr.includes('[Deprecation]') ||
        msgStr.includes('Support for this event type has been removed') ||
        // 浏览器Intervention警告
        msgStr.includes('[Intervention]') ||
        msgStr.includes('Slow network is detected') ||
        msgStr.includes('Fallback font will be used')
      )) ||
      // Vue警告
      (typeof msgStr === 'string' && 
        ((msgStr.includes('Property') && msgStr.includes('was accessed during render but is not defined')) ||
         msgStr.includes('Template ref') && msgStr.includes('used on a non-ref value'))) ||
      // Element Plus警告
      (typeof msgStr === 'string' && 
        (msgStr.includes('ElementPlusError') || 
         msgStr.includes('type.text is about to be deprecated') ||
         msgStr.includes('please use link instead')))
  )) {
    // 忽略这些警告
    return;
  }
  originalWarn.call(console, msg, ...args);
};

// 拦截错误日志
const originalError = console.error;
console.error = function(msg, ...args) {
  // 过滤掉特定的错误信息
  if (msg && typeof msg === 'string' && (
      msg.includes('Failed to load resource') ||
      msg.includes('NetworkError') ||
      msg.includes('404 (Not Found)') ||
      msg.includes('Error loading')
  )) {
    return;
  }
  originalError.call(console, msg, ...args);
};

// 拦截普通日志
const originalLog = console.log;
console.log = function(msg, ...args) {
  // 过滤掉API相关的调试日志
  if (msg && typeof msg === 'string' && (
      msg.includes('API') || 
      msg.includes('api') ||
      msg.includes('请求') ||
      msg.includes('响应') ||
      msg.includes('帖子列表') ||
      msg.includes('板块列表') ||
      msg.includes('处理') ||
      msg.includes('获取板块详情') ||
      msg.includes('获取到的板块信息') ||
      msg.includes('获取帖子详情') ||
      msg.includes('获取到的帖子信息') ||
      msg.includes('获取评论') ||
      msg.includes('获取用户信息')
  )) {
    return;
  }
  originalLog.call(console, msg, ...args);
};

// 处理 ResizeObserver 警告
const debounce = (fn, delay) => {
  let timeoutId = null
  return (...args) => {
    clearTimeout(timeoutId)
    timeoutId = setTimeout(() => fn.apply(this, args), delay)
  }
}

const handleError = debounce((error) => {
  if (error.message.includes('ResizeObserver') || 
      error.message.includes('ResizeObserver loop completed with undelivered notifications.') ||
      error.message.includes('ResizeObserver loop limit exceeded')) {
    const resizeObserverError = error instanceof Error ? error : new Error('ResizeObserver error');
    const errorEvent = new ErrorEvent('error', {
      error: resizeObserverError,
      message: resizeObserverError.message,
      lineno: 0,
      colno: 0,
      filename: ''
    });
    window.dispatchEvent(errorEvent);
    return;
  }
  console.error(error);
}, 250);

window.addEventListener('error', (e) => {
  if (e.message.includes('ResizeObserver')) {
    e.stopImmediatePropagation();
  }
}, true);

window.addEventListener('unhandledrejection', (e) => {
  if (e.reason.message && e.reason.message.includes('ResizeObserver')) {
    e.stopImmediatePropagation();
  }
}, true);

// 初始化 Quill
initQuill();

const app = createApp(App)

app.use(store)
app.use(router)
app.use(ElementPlus)

// 注册所有Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 全局挂载axios
app.config.globalProperties.$axios = service

// 全局注册组件
app.component('BackButton', BackButton)
app.component('QuillEditor', QuillEditor)

// 全局挂载日志函数
app.config.globalProperties.$log = log;

// 添加全局错误处理
app.config.errorHandler = (err) => {
  handleError(err);
};

app.config.warnHandler = (msg) => {
  if (msg.includes('ResizeObserver')) {
    return;
  }
  console.warn(msg);
};

// 在路由准备就绪后挂载应用
router.isReady().then(() => {
  app.mount('#app')
})
