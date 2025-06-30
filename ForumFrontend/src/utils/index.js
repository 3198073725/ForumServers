import dayjs from 'dayjs'

/**
 * 格式化日期时间
 * @param {string|number|Date} time - 要格式化的时间
 * @param {string} format - 格式化模式，默认为 YYYY-MM-DD HH:mm:ss
 * @returns {string} 格式化后的时间字符串
 */
export const formatDateTime = (time, format = 'YYYY-MM-DD HH:mm:ss') => {
  return time ? dayjs(new Date(time)).format(format) : 'N/A'
}

/**
 * 获取全局 CSS 变量值
 * @param {string} cssVariableName - CSS 变量名
 * @returns {string} CSS 变量值
 */
export const getCssVariableValue = (cssVariableName) => {
  let cssVariableValue = ''
  try {
    // 没有拿到值时，会返回空串
    cssVariableValue = getComputedStyle(document.documentElement).getPropertyValue(cssVariableName)
  } catch (error) {
    console.error(error)
  }
  return cssVariableValue
}

/**
 * 设置全局 CSS 变量
 * @param {string} cssVariableName - CSS 变量名
 * @param {string} cssVariableValue - CSS 变量值
 */
export const setCssVariableValue = (cssVariableName, cssVariableValue) => {
  try {
    document.documentElement.style.setProperty(cssVariableName, cssVariableValue)
  } catch (error) {
    console.error(error)
  }
}

/**
 * 防抖函数
 * @param {Function} fn - 要执行的函数
 * @param {number} delay - 延迟时间，单位毫秒
 * @returns {Function} 防抖后的函数
 */
export const debounce = (fn, delay) => {
  let timer = null
  return function() {
    const context = this
    const args = arguments
    clearTimeout(timer)
    timer = setTimeout(() => {
      fn.apply(context, args)
    }, delay)
  }
}

/**
 * 节流函数
 * @param {Function} fn - 要执行的函数
 * @param {number} delay - 延迟时间，单位毫秒
 * @returns {Function} 节流后的函数
 */
export const throttle = (fn, delay) => {
  let lastTime = 0
  return function() {
    const context = this
    const args = arguments
    const now = Date.now()
    if (now - lastTime >= delay) {
      fn.apply(context, args)
      lastTime = now
    }
  }
}

/**
 * 深拷贝对象
 * @param {Object} obj - 要拷贝的对象
 * @returns {Object} 拷贝后的对象
 */
export const deepClone = (obj) => {
  if (obj === null || typeof obj !== 'object') {
    return obj
  }
  
  const clone = Array.isArray(obj) ? [] : {}
  
  for (const key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      clone[key] = deepClone(obj[key])
    }
  }
  
  return clone
}
