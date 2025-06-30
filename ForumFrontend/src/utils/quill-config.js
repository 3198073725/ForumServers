/**
 * Quill编辑器全局配置
 * 用于解决Quill中的警告和配置问题
 */

// 默认的Quill配置选项
export const defaultQuillOptions = {
  theme: 'snow',
  modules: {
    toolbar: [
      ['bold', 'italic', 'underline', 'strike'],
      ['blockquote', 'code-block'],
      [{ 'header': 1 }, { 'header': 2 }],
      [{ 'list': 'ordered' }, { 'list': 'bullet' }],
      [{ 'script': 'sub' }, { 'script': 'super' }],
      [{ 'indent': '-1' }, { 'indent': '+1' }],
      [{ 'direction': 'rtl' }],
      [{ 'size': ['small', false, 'large', 'huge'] }],
      [{ 'header': [1, 2, 3, 4, 5, 6, false] }],
      [{ 'color': [] }, { 'background': [] }],
      [{ 'font': [] }],
      [{ 'align': [] }],
      ['clean'],
      ['link', 'image']
    ]
  },
  placeholder: '请输入内容...',
  scrollingContainer: 'html',
  bounds: document.body,
  // 使用 MutationObserver 替代已弃用的 DOM 事件
  experimental: {
    useModernScrollingApi: true,
    useMutationObserver: true
  }
};

// 初始化Quill，应用全局配置
export function initQuill() {
  if (typeof window === 'undefined') return;

  // 确保 Quill 对象存在
  window.Quill = window.Quill || {};
  
  // 设置默认配置
  const defaults = window.Quill.DEFAULTS || {};
  window.Quill.DEFAULTS = {
    ...defaults,
    experimental: {
      useModernScrollingApi: true,
      useMutationObserver: true
    }
  };

  // 禁用DOMNodeInserted事件
  if (typeof window.Element !== 'undefined') {
    const originalAddEventListener = window.Element.prototype.addEventListener;
    window.Element.prototype.addEventListener = function(type, listener, options) {
      if (type === 'DOMNodeInserted' || type === 'DOMNodeRemoved') {
        // 忽略已弃用的DOM变更事件
        return;
      }
      return originalAddEventListener.call(this, type, listener, options);
    };
  }
  
  // 重写Quill的DOM相关方法（如果存在）
  if (window.Quill && window.Quill.prototype) {
    // 保存原始方法引用
    const originalMethods = {};
    
    // 需要重写的方法列表
    const methodsToOverride = [
      'constructor', 
      'scroll', 
      'update', 
      'updateContents',
      'setContents'
    ];
    
    // 遍历Quill原型上的所有方法
    for (const method of methodsToOverride) {
      if (typeof window.Quill.prototype[method] === 'function') {
        // 保存原始方法
        originalMethods[method] = window.Quill.prototype[method];
        
        // 重写方法，包装在try-catch中
        window.Quill.prototype[method] = function(...args) {
          try {
            return originalMethods[method].apply(this, args);
          } catch (error) {
            // 忽略与DOM变更相关的错误
            if (error && error.message && 
                (error.message.includes('DOMNodeInserted') || 
                 error.message.includes('mutation event'))) {
              return;
            }
            throw error;
          }
        };
      }
    }
  }

  // 替换原生的 MutationObserver
  if (window.MutationObserver) {
    const originalMutationObserver = window.MutationObserver;
    window.MutationObserver = function(callback) {
      return new originalMutationObserver((mutations) => {
        // 过滤掉不需要的 DOM 变更事件
        const filteredMutations = mutations.filter(mutation => {
          return !mutation.target.classList?.contains('ql-clipboard');
        });
        if (filteredMutations.length > 0) {
          callback(filteredMutations);
        }
      });
    };
  }

  // 禁用控制台警告 - 在所有环境中都生效
  const originalWarn = console.warn;
  console.warn = function(msg, ...args) {
        // 过滤掉Quill的特定警告
        if (msg && typeof msg === 'string' && 
            (msg.includes('DOMNodeInserted') || 
             msg.includes('Listener added for a') ||
         msg.includes('mutation event') ||
         msg.includes('vue-quill') ||
         msg.includes('Quill') ||
         msg.includes('scroll'))) {
          return;
        }
        originalWarn.call(console, msg, ...args);
      };
} 